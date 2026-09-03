"""
Pydantic models for Paper data shapes (requests/responses).
"""
from typing import Optional
from pydantic import BaseModel


class PaperSearchResponse(BaseModel):
    id: str
    title: Optional[str] = None
    publication_year: Optional[int] = None
    publication_date: Optional[str] = None
    doi: Optional[str] = None
    authors: list[str] = []
    abstract: Optional[str] = None
    journal: Optional[str] = None
    cited_by_count: Optional[int] = 0
    pdf_url: Optional[str] = None
    topics: list[str] = []
    is_open_access: bool = False


class SummarizeRequest(BaseModel):
    title: str
    abstract: str


class SummarizeResponse(BaseModel):
    summary: str


class ProcessPdfRequest(BaseModel):
    paper_id: str
    pdf_url: str


class ProcessPdfResponse(BaseModel):
    status: str
    chunks_processed: int
