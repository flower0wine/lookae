import os
from pathlib import Path
from vector.client import get_client, get_collection
from vector.embeddings import get_embedding_function
from vector.search import semantic_search_hybrid

PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", ".chroma"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "lookae-md")


def main():
    embed_fn = get_embedding_function()
    client = get_client(PERSIST_DIR)
    collection = get_collection(client, COLLECTION_NAME, embed_fn)

    print("Semantic search ready. Type a query (or 'exit'):")
    while True:
        try:
            q = input("query> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nMeet you next time!")
            break
        if not q or q.lower() in {"exit", "quit"}:
            print("\nGoodbye!")
            break
        # Recency-aware hybrid search by default (prefer newest)
        res = semantic_search_hybrid(collection, q, k=16, fetch_k=64, prefer_newest=True)
        for i, r in enumerate(res, 1):
            ts = r["metadata"].get("time_str")
            ts_part = f"  [{ts}]" if ts else ""
            print(f"\n[{i}] {r['metadata'].get('name')}  ({r['metadata'].get('path')}){ts_part}")
            snippet = (r["text"] or "").splitlines()
            print("   " + " ".join(snippet[:5])[:240] + ("..." if len(snippet) > 5 else ""))


if __name__ == "__main__":
    main()
