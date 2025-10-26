import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from rich import print as rprint


def _split_sentences_cn_en(text: str) -> List[str]:
    """Rudimentary sentence splitter for Chinese and English text.
    Splits on Chinese punctuation and English period/question/exclamation/semicolon, keeping delimiters.
    """
    if not text:
        return []
    # Ensure delimiters are kept by using capturing groups
    pieces = re.split(r"([。！？!?；;]+)\s*", text)
    sents: List[str] = []
    buf = ""
    for i in range(0, len(pieces), 2):
        seg = pieces[i] or ""
        delim = pieces[i + 1] if i + 1 < len(pieces) else ""
        if not seg and not delim:
            continue
        sent = (seg + delim).strip()
        if sent:
            sents.append(sent)
    # Further split long English runs by period if needed
    refined: List[str] = []
    for s in sents:
        subs = re.split(r"(\.[\s\n]+)", s)
        if len(subs) == 1:
            refined.append(s)
        else:
            acc = ""
            for j in range(0, len(subs), 2):
                seg = subs[j] or ""
                delim = subs[j + 1] if j + 1 < len(subs) else ""
                piece = (seg + delim).strip()
                if piece:
                    refined.append(piece)
    return refined if refined else ([text] if text.strip() else [])


def _pack_with_overlap(sents: List[str], max_chars: int, overlap: int) -> List[str]:
    parts: List[str] = []
    cur: List[str] = []
    cur_len = 0
    for s in sents:
        s_len = len(s)
        if cur_len + s_len <= max_chars:
            cur.append(s)
            cur_len += s_len
        else:
            if cur:
                parts.append("".join(cur).strip())
            # build next window with overlap characters from end of previous
            tail = ("".join(cur))[-overlap:] if overlap > 0 and cur else ""
            cur = [tail, s] if tail else [s]
            cur_len = len("".join(cur))
            if cur_len > max_chars:  # fallback split by hard length if a single sentence is too long
                parts.append("".join(cur)[:max_chars])
                remain = "".join(cur)[max_chars:]
                cur = [remain[-overlap:]] if overlap > 0 else []
                cur_len = len("".join(cur))
    if cur:
        parts.append("".join(cur).strip())
    return [p for p in parts if p]



_TS_LINE_RE = re.compile(r"^\s*(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2})\s*$", re.MULTILINE)


def extract_timestamp(text: str) -> Optional[Dict[str, Any]]:
    """Find a standalone line with format YYYY/MM/DD HH:MM and return ISO + epoch."""
    m = _TS_LINE_RE.search(text or "")
    if not m:
        return None
    raw = m.group(1)
    try:
        dt = datetime.strptime(raw, "%Y/%m/%d %H:%M").replace(tzinfo=timezone.utc)
        return {"time_str": raw, "iso": dt.isoformat(), "ts": int(dt.timestamp())}
    except Exception:
        return None
