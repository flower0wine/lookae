from pathlib import Path
from typing import Any, Dict, List

from rich import print as rprint
from tqdm import tqdm

from .chunking import extract_timestamp


def load_markdown_files(root_dirs: List[Path]) -> List[Dict[str, Any]]:
    """Load each markdown file as ONE document (no chunking)."""
    docs: List[Dict[str, Any]] = []
    for root in root_dirs:
        if not root.exists():
            rprint(f"[yellow]Skip missing directory:[/] {root}")
            continue
        paths = list(root.rglob("*.md"))
        for p in tqdm(paths, desc=f"Scanning {root}"):
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                rprint(f"[red]Failed to read[/] {p}: {e}")
                continue
            ts_info = extract_timestamp(text)
            docs.append({
                "id": str(p.resolve()),
                "text": text,
                "path": str(p),
                "name": p.name,
                "ts": ts_info.get("ts") if ts_info else None,
                "time_str": ts_info.get("time_str") if ts_info else None,
            })
    return docs
