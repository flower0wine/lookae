import os
from typing import Any

from chromadb.utils import embedding_functions


def get_embedding_function() -> Any:
    """Return an embedding function optimized for speed by default.
    Priority for smaller/faster models:
    1) OpenAI (if OPENAI_API_KEY set), default model text-embedding-3-small
    2) SentenceTransformer (LOCAL_EMBED_MODEL, default BAAI/bge-small-zh-v1.5)
    3) FastEmbed (fallback)

    Override via env:
      - OPENAI_EMBED_MODEL
      - LOCAL_EMBED_MODEL
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
        )

    # Prefer a smaller local model by default for speed
    local_model = os.getenv("LOCAL_EMBED_MODEL", "BAAI/bge-small-zh-v1.5")
    # Try FastEmbed first (fast CPU embedding), then fallback to SentenceTransformer
    try:
        return embedding_functions.FastEmbedEmbeddingFunction(
            model_name=local_model
        )
    except Exception:
        try:
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=local_model
            )
        except Exception:
            # Final fallback to a widely available small model
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
