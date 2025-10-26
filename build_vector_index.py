import os
from pathlib import Path
from vector.client import get_client, get_collection
from vector.embeddings import get_embedding_function
from vector.loader import load_markdown_files
from vector.indexing import index_documents

# Configure sources
SOURCES = [
    Path("data/lookae"),
]

PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", ".chroma"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "lookae-md")


def main():
    embed_fn = get_embedding_function()
    client = get_client(PERSIST_DIR)
    collection = get_collection(client, COLLECTION_NAME, embed_fn)

    # Load docs
    docs = load_markdown_files(SOURCES)
    if not docs:
        print("No markdown files found in sources.")
        return

    # Index
    print(f"Indexing {len(docs)} docs into collection '{COLLECTION_NAME}' ...")
    index_documents(collection, docs)
    print("Done. Chroma persisted at:", PERSIST_DIR.resolve())


if __name__ == "__main__":
    main()
