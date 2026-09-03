"""
API router for Research agent functionality (comparison, reports, gap analysis).
"""
import logging
from fastapi import APIRouter, HTTPException
from app.models.research import (
    CompareRequest, CompareResponse,
    ResearchReportRequest, ResearchReportResponse
)
from app.services.research_agent import compare_papers, generate_literature_review
from app.services.paper_search import search_papers

router = APIRouter(prefix="/research", tags=["Research Agent"])
logger = logging.getLogger(__name__)


@router.post("/compare", response_model=CompareResponse)
def compare_papers_endpoint(request: CompareRequest):
    """
    Compares multiple papers by fetching their details/abstracts.
    """
    if not request.paper_ids or len(request.paper_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 paper IDs are required for comparison.")
    
    # In a full flow, you can query papers by IDs from DB or OpenAlex.
    # For demonstration, we construct paper dicts.
    papers_data = []
    for pid in request.paper_ids:
        # Search or mock retrieval
        res = search_papers(pid, limit=1)
        if res:
            papers_data.append(res[0])
    
    if not papers_data:
        raise HTTPException(status_code=404, detail="No paper details could be retrieved.")
        
    comparison = compare_papers(papers_data, request.focus)
    return CompareResponse(comparison=comparison)


@router.post("/report", response_model=ResearchReportResponse)
def generate_report_endpoint(request: ResearchReportRequest):
    """
    Generates a structured literature review / research report.
    """
    if not request.topic:
        raise HTTPException(status_code=400, detail="Topic is required.")
        
    papers_data = search_papers(request.topic, limit=5)
    if not papers_data:
        raise HTTPException(status_code=404, detail="No relevant papers found for topic.")
        
    report = generate_literature_review(request.topic, papers_data)
    return ResearchReportResponse(report=report)
