"""
Pydantic models for Research/Chat data shapes.
"""
from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    paper_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str


class CompareRequest(BaseModel):
    paper_ids: list[str]
    focus: Optional[str] = "methodology, findings, and research gaps"


class CompareResponse(BaseModel):
    comparison: str


class ResearchReportRequest(BaseModel):
    topic: str
    paper_ids: list[str]


class ResearchReportResponse(BaseModel):
    report: str
