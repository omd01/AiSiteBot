from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv

from .scraper import crawl_site
from .store import SiteStore
from .rag import RAGPipeline


load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "/workspace/data"))
STATIC_DIR = Path("/workspace/static")
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)


class IngestRequest(BaseModel):
    url: HttpUrl
    max_pages: int | None = 20


class ChatRequest(BaseModel):
    site_url: HttpUrl
    question: str
    top_k: int | None = 5


app = FastAPI(title="Site RAG Chatbot (Gemini)")


# Simple in-memory map from site_id to store
site_stores: Dict[str, SiteStore] = {}


@app.post("/ingest")
async def ingest(req: IngestRequest) -> Dict[str, Any]:
    root_url = str(req.url)
    try:
        documents = crawl_site(root_url, max_pages=req.max_pages or 20)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scraping error: {e}")

    if len(documents) == 0:
        raise HTTPException(status_code=400, detail="No textual content found to index.")

    store = SiteStore.from_root_url(root_url, data_dir=DATA_DIR)
    store.build_or_replace_index(documents)
    site_stores[store.site_id] = store

    return {
        "site_id": store.site_id,
        "pages_indexed": len(documents),
        "message": "Ingestion completed",
    }


@app.post("/chat")
async def chat(req: ChatRequest) -> Dict[str, Any]:
    root_url = str(req.site_url)
    store = SiteStore.from_root_url(root_url, data_dir=DATA_DIR)

    if not store.exists():
        raise HTTPException(status_code=404, detail="Site not indexed yet. Use /ingest first.")

    # Lazily load store into memory map
    site_stores.setdefault(store.site_id, store)

    rag = RAGPipeline(store=store)
    answer, used_context, refused = rag.answer_question(
        question=req.question,
        top_k=req.top_k or 5,
        site_url=root_url,
    )

    return {
        "answer": answer,
        "refused": refused,
        "context": used_context,
    }


# Serve minimal frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index() -> FileResponse:
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        content = """
<!doctype html>
<html>
  <head><meta charset=\"utf-8\"><title>RAG Chatbot</title></head>
  <body>
    <p>Static assets not found. Please ensure /workspace/static/index.html exists.</p>
  </body>
</html>
"""
        fallback = STATIC_DIR / "index.html"
        fallback.write_text(content)
    return FileResponse(index_file)