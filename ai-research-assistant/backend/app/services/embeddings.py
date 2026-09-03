"""
Embeddings service — initializes and exposes the HuggingFace embedding model.
Using a singleton pattern so the model is loaded once at startup.
"""
import logging
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_embeddings_instance = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Returns a singleton HuggingFaceEmbeddings instance.
    The model is downloaded on first call and cached locally by HuggingFace.
    """
    global _embeddings_instance
    if _embeddings_instance is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embeddings_instance = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        logger.info("Embedding model loaded.")
    return _embeddings_instance
