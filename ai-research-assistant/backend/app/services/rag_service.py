import os
import logging
import requests
import tempfile
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from sqlalchemy import create_engine, text
from app.services.llm_service import client as groq_client

logger = logging.getLogger(__name__)

DB_CONNECTION = "postgresql+psycopg2://myuser:mypassword@localhost:5432/research_db"
COLLECTION_NAME = "research_papers"

# Initialize embeddings model (runs locally, no API key needed)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def init_db():
    """Ensure pgvector extension is created on first run."""
    engine = create_engine(DB_CONNECTION)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    engine.dispose()


# Initialize DB on module load
try:
    init_db()
    logger.info("pgvector extension ready.")
except Exception as e:
    logger.warning(f"Could not init pgvector extension: {e}")


def get_vector_store():
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DB_CONNECTION,
        use_jsonb=True,
    )


def process_and_store_pdf(pdf_url: str, paper_id: str):
    """Downloads PDF, extracts text, chunks it, and stores in pgvector."""

    logger.info(f"Downloading PDF from: {pdf_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf,*/*",
    }
    response = requests.get(pdf_url, stream=True, timeout=30, headers=headers)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        tmp_file_path = tmp_file.name

    try:
        # Extract text
        loader = PyMuPDFLoader(tmp_file_path)
        documents = loader.load()
        logger.info(f"Extracted {len(documents)} pages from PDF.")

        # Tag each chunk with paper_id for filtered retrieval
        for doc in documents:
            doc.metadata["paper_id"] = paper_id

        # Chunk the text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks.")

        # Store in pgvector
        vector_store = get_vector_store()
        vector_store.add_documents(chunks)
        logger.info("Stored chunks in pgvector successfully.")

        return {"status": "success", "chunks_processed": len(chunks)}

    finally:
        os.remove(tmp_file_path)


def query_paper(paper_id: str, question: str) -> str:
    """Retrieves relevant chunks for the paper and answers with Groq."""

    vector_store = get_vector_store()

    # langchain-postgres uses MongoDB-style filter operators
    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 6,
            "filter": {"paper_id": {"$eq": paper_id}},
        }
    )

    context_docs = retriever.invoke(question)
    logger.info(f"Retrieved {len(context_docs)} chunks for paper_id={paper_id}")

    if not context_docs:
        return (
            "I couldn't find relevant context in this paper. "
            "The PDF may not have been processed yet, or the paper contains no open-access text."
        )

    context_text = "\n\n---\n\n".join([doc.page_content for doc in context_docs])

    prompt = f"""You are an expert AI research assistant. \
Answer the user's question strictly using the context extracted from the research paper below. \
If the answer is not in the context, say "I don't have enough information from this paper to answer that." \
Be concise and precise.

Context:
{context_text}

Question: {question}

Answer:"""

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {str(e)}"
