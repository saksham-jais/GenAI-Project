from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from chunker import recursive_split
from embedding import get_embeddings
from parser import parse_pdf
import chromadb
import json
import os
import uuid
from datetime import datetime, timezone

from typing import Any

app = FastAPI()

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,https://docuchatai-three.vercel.app",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok  = True)
CHROMA_FOLDER = 'chroma_db'
METADATA_FILE = 'documents.json'

vector_db = chromadb.PersistentClient(path=CHROMA_FOLDER)
collection = vector_db.get_or_create_collection(
    name="document_chunks",
    configuration={"hnsw": {"space": "cosine"}},
)


def load_documents() -> dict[str, dict[str, Any]]:
    if not os.path.exists(METADATA_FILE):
        return {}
    with open(METADATA_FILE, "r", encoding="utf-8") as metadata_file:
        return json.load(metadata_file)


def save_documents() -> None:
    with open(METADATA_FILE, "w", encoding="utf-8") as metadata_file:
        json.dump(documents, metadata_file, indent=2)


documents: dict[str, dict[str, Any]] = load_documents()


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    document_id: str | None = None


def cosine_score(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))

@app.get("/")
def home():
    return {
        "message" : "DocuChat AI Backend Is Running"
    }


@app.get("/documents")
def list_documents():
    return [
        {
            "id": document["id"],
            "filename": document["filename"],
            "pages": document["pages"],
            "characters": document["characters"],
            "chunks": document["chunks"],
            "created_at": document["created_at"],
        }
        for document in documents.values()
    ]

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported")

    document_id = str(uuid.uuid4())
    safe_filename = os.path.basename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, f"{document_id}_{safe_filename}")
    with open(file_path, "wb") as buffer :
        content = await file.read()
        buffer.write(content)

    blocks, metadata = parse_pdf(file_path)
    extracted_text = "\n\n".join(block.text for block in blocks)
    page_count = int(metadata["pages"])
    chunks = [chunk for block in blocks for chunk in recursive_split(block)]
    if not chunks:
        raise HTTPException(status_code=422, detail="The PDF does not contain extractable text")

    vectors = get_embeddings().embed_documents([chunk["text"] for chunk in chunks])
    collection.add(
        ids=[f"{document_id}-{index}" for index in range(len(chunks))],
        documents=[chunk["text"] for chunk in chunks],
        embeddings=vectors,
        metadatas=[
            {
                "document_id": document_id,
                "filename": safe_filename,
                "page": chunk["page"],
                "kind": chunk["kind"],
                "heading": chunk["heading"] or "",
            }
            for chunk in chunks
        ],
    )
    documents[document_id] = {
        "id": document_id,
        "filename": safe_filename,
        "pages": page_count,
        "characters": len(extracted_text),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "chunks": len(chunks),
    }
    save_documents()

    return {
        "id": document_id,
        "filename": safe_filename,
        "pages": page_count,
        "characters": len(extracted_text),
        "chunks": len(chunks),
        "text_preview": extracted_text[:1000],
    }


@app.post("/chat")
def chat(request: ChatRequest):
    if not documents or collection.count() == 0:
        raise HTTPException(status_code=400, detail="Upload a document before asking a question")

    query_vector = get_embeddings().embed_query(request.question)
    query: dict[str, Any] = {"query_embeddings": [query_vector], "n_results": 3}
    if request.document_id in documents:
        query["where"] = {"document_id": request.document_id}
    result = collection.query(**query)
    matches = [
        {
            "score": 1 - distance,
            "text": text,
            "page": metadata["page"],
            "filename": metadata["filename"],
        }
        for text, metadata, distance in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        )
    ]
    sources = matches[:3]
    answer = "I found these relevant passages in your document:\n\n" + "\n\n".join(
        f"{source['text']}" for source in sources
    )
    return {
        "answer": answer,
        "sources": [
            {"filename": source["filename"], "page": source["page"], "score": round(source["score"], 3)}
            for source in sources
        ],
    }