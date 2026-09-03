"""
PDF Processor service.
Handles downloading a PDF from a URL and extracting raw text using PyMuPDF.
"""
import os
import logging
import tempfile
import requests
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

DOWNLOAD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/pdf,*/*",
}


def download_and_extract(pdf_url: str, paper_id: str) -> list[Document]:
    """
    Downloads a PDF from the given URL, extracts text using PyMuPDF,
    and returns a list of LangChain Document objects — one per page.
    Each document has paper_id injected into its metadata.
    """
    logger.info(f"Downloading PDF [{paper_id}]: {pdf_url}")
    try:
        response = requests.get(pdf_url, stream=True, timeout=30, headers=DOWNLOAD_HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            raise ValueError(
                f"Access denied (403 Forbidden) to PDF. The paper may require authentication or institutional access. "
                f"URL: {pdf_url}"
            )
        raise

    # Validate we actually got a PDF
    content_type = response.headers.get("Content-Type", "")
    if "html" in content_type.lower():
        raise ValueError(
            f"Expected a PDF but received HTML. The URL may be a viewer page, not a direct PDF link. "
            f"Content-Type: {content_type}"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        tmp_path = tmp_file.name

    try:
        loader = PyMuPDFLoader(tmp_path)
        documents = loader.load()
        for doc in documents:
            doc.metadata["paper_id"] = paper_id
        logger.info(f"Extracted {len(documents)} pages from PDF [{paper_id}].")
        return documents
    finally:
        os.remove(tmp_path)
