"""
SQLAlchemy ORM models for database tables.
Tracks processed papers and their processing status.
"""
import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ProcessedPaper(Base):
    """
    Tracks which papers have had their PDFs ingested into the vector store.
    Avoids re-processing the same paper on every chat request.
    """
    __tablename__ = "processed_papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(Text, nullable=True)
    pdf_url = Column(String, nullable=True)
    chunks_stored = Column(Integer, default=0)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<ProcessedPaper id={self.paper_id} chunks={self.chunks_stored}>"
