from dataclasses import asdict
from parser import DocumentBlock


def split_text(text, chunk_size=1000, overlap=200):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between zero and chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap

    return chunks


def chunk_quality(text: str, minimum_length: int = 40) -> bool:
    words = text.split()
    return len(text.strip()) >= minimum_length and len(words) >= 7


def recursive_split(block: DocumentBlock, chunk_size: int = 1000, overlap: int = 200) -> list[dict]:
    return [
        {**asdict(block), "text": text}
        for text in split_text(block.text, chunk_size, overlap)
        if chunk_quality(text) or block.kind == "table"
    ]