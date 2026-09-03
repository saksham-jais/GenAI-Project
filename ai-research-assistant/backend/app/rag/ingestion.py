"""
RAG Ingestion module.
Handles chunking of documents and storing their embeddings in pgvector.
"""
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_postgres import PGVector
from app.services.embeddings import get_embeddings

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
COLLECTION_NAME = "research_papers"


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Splits documents into smaller overlapping chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} pages into {len(chunks)} chunks.")
    return chunks


def ingest_to_vector_store(chunks: list[Document], connection_string: str) -> int:
    """
    Embeds the chunks and stores them in the PostgreSQL pgvector store.
    Returns the number of chunks stored.
    """
    vector_store = PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=connection_string,
        use_jsonb=True,
    )
    vector_store.add_documents(chunks)
    logger.info(f"Stored {len(chunks)} chunks in pgvector.")
    return len(chunks)
