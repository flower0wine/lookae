from typing import Any, Dict, List

from rich import print as rprint
from tqdm import tqdm


def index_documents(collection: Any, docs: List[Dict[str, Any]], batch_size: int = 64):
    """Index full documents without any chunk merging. Each item in docs is one file."""
    total = len(docs)
    if total == 0:
        rprint("[yellow]No documents to index.[/]")
        return
    with tqdm(total=total, desc="Indexing", unit="doc") as bar:
        for i in range(0, total, batch_size):
            chunk = docs[i:i + batch_size]
            try:
                collection.upsert(
                    ids=[d["id"] for d in chunk],
                    documents=[d["text"] for d in chunk],
                    metadatas=[
                        {
                            "path": d["path"],
                            "name": d["name"],
                            "ts": d.get("ts"),
                            "time_str": d.get("time_str"),
                        }
                        for d in chunk
                    ],
                )
            except Exception as e:
                rprint(f"[red]Batch upsert failed ({len(chunk)} docs). Falling back, error: {e}[/]")
                for d in chunk:
                    try:
                        collection.upsert(
                            ids=[d["id"]],
                            documents=[d["text"]],
                            metadatas=[
                                {
                                    "path": d["path"],
                                    "name": d["name"],
                                    "ts": d.get("ts"),
                                    "time_str": d.get("time_str"),
                                }
                            ],
                        )
                    except Exception as e2:
                        rprint(f"[red]Failed doc:[/] {d['path']} -> {e2}")
            finally:
                bar.update(len(chunk))
