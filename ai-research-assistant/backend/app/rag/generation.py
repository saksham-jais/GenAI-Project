"""
RAG Generation module.
Takes retrieved context chunks and uses the LLM to generate a cited answer.
"""
import logging
from langchain_core.documents import Document
from app.services.llm import chat_completion

logger = logging.getLogger(__name__)


def generate_answer(question: str, context_docs: list[Document]) -> str:
    """
    Constructs a RAG prompt from retrieved context and invokes the LLM.
    Returns the answer string.
    """
    if not context_docs:
        return (
            "I couldn't find relevant content in this paper to answer your question. "
            "The PDF may not have been processed yet, or it may not contain that information."
        )

    context_text = "\n\n---\n\n".join(
        [f"[Excerpt {i+1}]\n{doc.page_content}" for i, doc in enumerate(context_docs)]
    )

    prompt = (
        "You are an expert AI research assistant.\n"
        "Answer the user's question using ONLY the context excerpts below from the research paper.\n"
        "If the answer is not in the context, say: "
        "\"I don't have enough information from this paper to answer that.\"\n"
        "Be precise, concise, and cite excerpt numbers like [Excerpt 1] when referencing them.\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    logger.info("Generating RAG answer with LLM...")
    return chat_completion(prompt, temperature=0.2)
