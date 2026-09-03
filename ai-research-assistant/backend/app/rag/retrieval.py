"""
RAG Retrieval module.
Handles similarity search against the vector store for a given paper.
"""
import logging
from langchain_postgres import PGVector
from langchain_core.documents import Document
from app.services.embeddings import get_embeddings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "research_papers"


def retrieve_relevant_chunks(
    question: str,
    paper_id: str,
    connection_string: str,
    k: int = 6,
) -> list[Document]:
    """
    Retrieves the top-k most semantically relevant chunks from the vector store
    for a given question, filtered strictly to the specified paper_id.
    """
    vector_store = PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=connection_string,
        use_jsonb=True,
    )
    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {"paper_id": {"$eq": paper_id}},
        }
    )
    docs = retriever.invoke(question)
    logger.info(f"Retrieved {len(docs)} chunks for paper_id={paper_id}")
    return docs
