import math
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import jieba
from rank_bm25 import BM25Okapi
from rich import print as rprint
from FlagEmbedding import FlagReranker

# Optional reranker (install: pip install -U FlagEmbedding)
_RERANKER = FlagReranker("BAAI/bge-reranker-base", use_fp16=True)

def semantic_search(collection: Any, query: str, k: int = 5, start_ts: Optional[int] = None, end_ts: Optional[int] = None):
    where: Dict[str, Any] = {}
    if start_ts is not None or end_ts is not None:
        rng: Dict[str, Any] = {}
        if start_ts is not None:
            rng["$gte"] = start_ts
        if end_ts is not None:
            rng["$lte"] = end_ts
        where["ts"] = rng
    try:
        res = collection.query(query_texts=[query], n_results=k, where=where or None)
    except Exception as e:
        rprint(f"[red]Query failed:[/] {e}")
        return []
    results: List[Dict[str, Any]] = []
    for i in range(len(res.get("ids", [[]])[0])):
        results.append({
            "id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "metadata": res["metadatas"][0][i],
            "distance": res.get("distances", [[None]])[0][i] if res.get("distances") else None,
        })
    return results


# ---------------------------
# CN-friendly normalization & tokenization
# ---------------------------

_HAN_RE = re.compile(r"[\u4e00-\u9fff]")


def _to_half_width(s: str) -> str:
    # Convert full-width to half-width
    res_chars = []
    for ch in s:
        code = ord(ch)
        if code == 0x3000:
            code = 32
        elif 0xFF01 <= code <= 0xFF5E:
            code -= 0xFEE0
        res_chars.append(chr(code))
    return "".join(res_chars)


def _normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    s = _to_half_width(s)
    s = re.sub(r"\s+", " ", s)
    return s


def _char_ngrams(s: str, n_list: Tuple[int, ...] = (2, 3)) -> List[str]:
    """Generate character n-grams over Chinese characters; include ASCII fallback."""
    toks: List[str] = []
    # Keep both Han-only ngrams and general sliding window ngrams for robustness
    chars = list(s)
    length = len(chars)
    for n in n_list:
        if n <= 0 or length < n:
            continue
        for i in range(0, length - n + 1):
            piece = "".join(chars[i : i + n])
            # Prioritize those containing at least one Han char, but keep all
            if _HAN_RE.search(piece) or piece.strip():
                toks.append(piece.lower())
    return toks


def _tokenize_cn(text: str) -> List[str]:
    text = _normalize_text(text)
    if not text:
        return []
    seg = [tok for tok in jieba.lcut(text) if tok and tok.strip()]
    # Add char ngrams to handle OOV and domain terms
    seg += _char_ngrams(text)
    # Add ASCII word tokens
    seg += re.findall(r"\w+", text.lower())
    # Dedup while keeping order
    seen = set()
    out: List[str] = []
    for t in seg:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _overlap_score(query: str, text: str) -> float:
    q = set(_tokenize_cn(query))
    toks = set(_tokenize_cn(text or ""))
    if not q or not toks:
        return 0.0
    base = len(q & toks) / (len(q) + 1e-6)
    boost = 0.25 if _normalize_text(query).lower() in _normalize_text(text).lower() else 0.0
    return base + boost


def _tokenize_for_bm25(text: str) -> List[str]:
    return _tokenize_cn(text)


def _expand_query(query: str) -> Dict[str, Any]:
    # Hook for future synonym/translation expansion if needed
    qn = _normalize_text(query)
    toks = _tokenize_cn(qn)
    return {"expanded": qn, "tokens": toks, "synonyms": []}


def semantic_search_hybrid(
    collection: Any,
    query: str,
    k: int = 5,
    fetch_k: int = int(os.getenv("FETCH_K", "40")),
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None,
    prefer_newest: bool = bool(int(os.getenv("PREFER_NEWEST", "1"))),
    w_semantic: float = float(os.getenv("W_SEMANTIC", "0.7")),
    w_bm25: float = float(os.getenv("W_BM25", "0.3")),
    w_overlap: float = float(os.getenv("W_OVERLAP", "0.15")),
    w_time: float = float(os.getenv("W_TIME", "0.1")),
):
    where: Dict[str, Any] = {}
    if start_ts is not None or end_ts is not None:
        rng: Dict[str, Any] = {}
        if start_ts is not None:
            rng["$gte"] = start_ts
        if end_ts is not None:
            rng["$lte"] = end_ts
        where["ts"] = rng
    qx = _expand_query(query)
    try:
        res = collection.query(
            query_texts=[qx["expanded"]],
            n_results=fetch_k,
            where=where or None,
            include=["distances", "metadatas", "documents"],
        )
    except Exception as e:
        rprint(f"[red]Query failed:[/] {e}")
        return []

    cands: List[Dict[str, Any]] = []
    for i in range(len(res.get("ids", [[]])[0])):
        item = {
            "id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "metadata": res["metadatas"][0][i],
            "distance": res.get("distances", [[None]])[0][i] if res.get("distances") else None,
        }
        cands.append(item)

    corp_tokens = [_tokenize_for_bm25(c.get("text", "")) for c in cands]
    bm25 = BM25Okapi(corp_tokens) if corp_tokens else None
    q_tokens = _tokenize_for_bm25(qx["expanded"]) if bm25 else []
    bm25_scores = bm25.get_scores(q_tokens).tolist() if bm25 else [0.0] * len(cands)
    max_bm25 = max(bm25_scores) if bm25_scores else 1.0
    max_ts = max([(c.get("metadata", {}).get("ts") or 0) for c in cands] + [1])

    dist_list = [c.get("distance") if c.get("distance") is not None else 1.0 for c in cands]
    dist_min = min(dist_list) if dist_list else 0.0
    dist_max = max(dist_list) if dist_list else 1.0

    def dist_to_sim(d: Optional[float]) -> float:
        if d is None:
            return 0.0
        rng = (dist_max - dist_min) or 1.0
        norm = (d - dist_min) / rng
        return 1.0 - norm

    scored: List[Tuple[float, Dict[str, Any]]] = []
    for c, b in zip(cands, bm25_scores):
        ov = _overlap_score(query, c.get("text", ""))
        ts_val = (c.get("metadata", {}).get("ts") or 0)
        time_part = (ts_val / max_ts) if (prefer_newest and max_ts > 0) else 0.0
        bm25_part = (b / max_bm25) if max_bm25 > 0 else 0.0
        sem_part = dist_to_sim(c.get("distance"))
        score = w_semantic * sem_part + w_bm25 * bm25_part + w_overlap * ov + w_time * time_part
        scored.append((score, c))

    scored = [sc for sc in scored if sc[0] >= 0.05]
    scored.sort(key=lambda x: x[0], reverse=True)

    if _RERANKER is None or not scored:
        return [c for _, c in scored[:k]]
    topn = min(len(scored), int(os.getenv("RERANK_TOPN", "20")))
    pairs = [[query, scored[i][1].get("text", "")] for i in range(topn)]
    try:
        rr_scores = _RERANKER.compute_score(pairs, normalize=True)
        reranked = list(zip(rr_scores, [scored[i][1] for i in range(topn)]))
        reranked.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in reranked[:k]]
    except Exception as e:  # pragma: no cover
        rprint(f"[yellow]Rerank failed, fallback original ranking:[/] {e}")
        return [c for _, c in scored[:k]]
