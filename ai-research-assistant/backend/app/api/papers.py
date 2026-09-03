"""
API router for paper search and AI summarization.
"""
import logging
from fastapi import APIRouter, HTTPException
from app.models.paper import SummarizeRequest, SummarizeResponse
from app.services.paper_search import search_papers
from app.services.llm import summarize_abstract

router = APIRouter(prefix="/papers", tags=["Papers"])
logger = logging.getLogger(__name__)


@router.get("/")
def get_papers(query: str, limit: int = 10):
    """Search for academic papers via OpenAlex API."""
    try:
        papers = search_papers(query, limit)
        return {"query": query, "papers": papers}
    except Exception as e:
        logger.error(f"Paper search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_paper(request: SummarizeRequest):
    """Generate a plain-language AI summary of a paper abstract."""
    if not request.abstract:
        raise HTTPException(status_code=400, detail="Abstract is required.")
    try:
        summary = summarize_abstract(request.title, request.abstract)
        return SummarizeResponse(summary=summary)
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
