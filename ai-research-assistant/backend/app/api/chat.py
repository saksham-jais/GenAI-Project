"""
API router for PDF ingestion and RAG-based chat with a paper.
"""
import logging
from fastapi import APIRouter, HTTPException
from app.models.paper import ProcessPdfRequest, ProcessPdfResponse
from app.models.research import ChatRequest, ChatResponse
from app.services.pdf_processor import download_and_extract
from app.rag.ingestion import chunk_documents, ingest_to_vector_store
from app.rag.retrieval import retrieve_relevant_chunks
from app.rag.generation import generate_answer
from app.database.connection import DATABASE_URL
from app.database.connection import SessionLocal
from app.database.models import ProcessedPaper

router = APIRouter(tags=["Chat"])
logger = logging.getLogger(__name__)


@router.post("/process_pdf", response_model=ProcessPdfResponse)
def process_pdf(request: ProcessPdfRequest):
    """
    Downloads the PDF, chunks it, embeds it, and stores it in pgvector.
    Skips processing if the paper has already been ingested (idempotent).
    """
    db = SessionLocal()
    try:
        existing = db.query(ProcessedPaper).filter_by(paper_id=request.paper_id, is_processed=True).first()
        if existing:
            logger.info(f"Paper {request.paper_id} already processed ({existing.chunks_stored} chunks). Skipping.")
            return ProcessPdfResponse(status="already_processed", chunks_processed=existing.chunks_stored)

        documents = download_and_extract(request.pdf_url, request.paper_id)
        chunks = chunk_documents(documents)
        num_chunks = ingest_to_vector_store(chunks, DATABASE_URL)

        record = ProcessedPaper(
            paper_id=request.paper_id,
            pdf_url=request.pdf_url,
            chunks_stored=num_chunks,
            is_processed=True,
        )
        db.add(record)
        db.commit()

        return ProcessPdfResponse(status="success", chunks_processed=num_chunks)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/chat", response_model=ChatResponse)
def chat_with_paper(request: ChatRequest):
    """
    Performs RAG: retrieves relevant chunks from the paper and asks the LLM.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        context_docs = retrieve_relevant_chunks(
            question=request.question,
            paper_id=request.paper_id,
            connection_string=DATABASE_URL,
        )
        answer = generate_answer(request.question, context_docs)
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
