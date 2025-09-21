from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse

import numpy as np

from .scraper import Document


CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
    return vectors / norms


def _site_id_from_url(root_url: str) -> str:
    parsed = urlparse(root_url)
    return parsed.netloc.replace(":", "_")


def _chunk_text(text: str, size: int, overlap: int) -> List[str]:
    if size <= 0:
        return [text]
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + size)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks


class SiteStore:
    def __init__(self, site_id: str, base_dir: Path) -> None:
        self.site_id = site_id
        self.dir = base_dir / site_id
        self.index_path = self.dir / "vectors.npy"
        self.meta_path = self.dir / "meta.json"
        self.dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_root_url(cls, root_url: str, data_dir: Path) -> "SiteStore":
        return cls(_site_id_from_url(root_url), data_dir)

    def exists(self) -> bool:
        return self.index_path.exists() and self.meta_path.exists()

    def _save_index(self, vectors: np.ndarray) -> None:
        np.save(self.index_path, vectors)

    def _load_index(self) -> np.ndarray:
        return np.load(self.index_path)

    def _save_meta(self, documents: List[Dict[str, Any]]) -> None:
        with self.meta_path.open("w", encoding="utf-8") as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)

    def _load_meta(self) -> List[Dict[str, Any]]:
        with self.meta_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def build_or_replace_index(self, documents: List[Document]) -> None:
        from .rag import embed_texts

        chunked_meta: List[Dict[str, Any]] = []
        chunk_texts: List[str] = []
        for doc in documents:
            chunks = _chunk_text(doc.text, CHUNK_SIZE, CHUNK_OVERLAP)
            for i, chunk in enumerate(chunks):
                chunked_meta.append({
                    "url": doc.url,
                    "title": doc.title,
                    "text": chunk,
                    "chunk_index": i,
                })
                chunk_texts.append(chunk)

        if not chunk_texts:
            raise ValueError("No text chunks to index")

        vectors_list: List[np.ndarray] = []
        batch_size = int(os.getenv("EMBED_BATCH_SIZE", "6"))
        for i in range(0, len(chunk_texts), batch_size):
            batch = chunk_texts[i:i + batch_size]
            vecs = embed_texts(batch)
            vectors_list.append(vecs)
        vectors = np.vstack(vectors_list).astype(np.float32)
        vectors = _normalize(vectors)

        self._save_index(vectors)
        self._save_meta(chunked_meta)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        query_vector = _normalize(query_vector.astype(np.float32))

        vectors = self._load_index()
        if vectors.size == 0:
            return []

        # Cosine similarity via dot product of normalized vectors
        sims = (vectors @ query_vector.T).reshape(-1)
        if top_k <= 0:
            top_k = 5
        top_k = min(top_k, sims.shape[0])
        idx = np.argpartition(-sims, top_k - 1)[:top_k]
        # Sort by score desc
        idx = idx[np.argsort(-sims[idx])]
        scores = sims[idx].tolist()

        meta = self._load_meta()
        results: List[Tuple[Dict[str, Any], float]] = []
        for i, s in zip(idx.tolist(), scores):
            if i < 0 or i >= len(meta):
                continue
            doc = meta[i]
            results.append((doc, float(s)))
        return results