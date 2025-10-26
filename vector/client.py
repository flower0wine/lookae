from pathlib import Path

import chromadb
from rich import print as rprint


def get_client(persist_dir: Path) -> chromadb.Client:
    persist_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist_dir))
    return client


def get_collection(client: chromadb.Client, name: str, embedding_fn):
    """Get or create a Chroma collection and ALWAYS bind the embedding function.
    This ensures query_texts uses the same embedding behavior across runs.
    """
    try:
        # Pass embedding_function even when getting existing collection to avoid mismatches
        col = client.get_collection(name=name, embedding_function=embedding_fn)
    except Exception:
        rprint(f"[cyan]Collection '{name}' not found, creating...[/]")
        col = client.create_collection(name=name, embedding_function=embedding_fn)
    return col
