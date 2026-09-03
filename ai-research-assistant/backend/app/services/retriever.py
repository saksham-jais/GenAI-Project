"""
Vector store retriever service.
Returns a retriever scoped to a specific paper_id for RAG queries.
"""
import logging
from langchain_postgres import PGVector
from app.services.embeddings import get_embeddings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "research_papers"


def get_vector_store(connection_string: str) -> PGVector:
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=connection_string,
        use_jsonb=True,
    )


def get_paper_retriever(connection_string: str, paper_id: str, k: int = 6):
    """
    Returns a LangChain retriever filtered to only return chunks
    belonging to the given paper_id.
    """
    vector_store = get_vector_store(connection_string)
    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {"paper_id": {"$eq": paper_id}},
        }
    )
    logger.info(f"Retriever ready for paper_id={paper_id}, k={k}")
    return retriever
