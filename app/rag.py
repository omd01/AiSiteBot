from __future__ import annotations

import os
from typing import List, Tuple, Dict, Any

import numpy as np
import google.generativeai as genai

from .store import SiteStore


EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini-1.5-flash")


def _ensure_genai_configured() -> None:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set. See README.md")
    genai.configure(api_key=api_key)


def embed_texts(texts: List[str]) -> np.ndarray:
    _ensure_genai_configured()
    result = genai.embed_content(model=EMBEDDING_MODEL, content=texts)

    if isinstance(result, dict) and "embeddings" in result:
        vectors = [np.array(item["values"], dtype=np.float32) for item in result["embeddings"]]
    elif isinstance(result, dict) and "embedding" in result:
        vectors = [np.array(result["embedding"], dtype=np.float32)]
    else:
        try:
            vectors = [np.array(item.values, dtype=np.float32) for item in result.embeddings]
        except Exception as exc:
            raise RuntimeError(f"Unexpected embeddings response: {type(result)}; {exc}")

    norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
    vectors = np.asarray(vectors, dtype=np.float32) / norms
    return vectors


class RAGPipeline:
    def __init__(self, store: SiteStore) -> None:
        self.store = store

    def retrieve(self, query: str, top_k: int = 5) -> Tuple[List[Dict[str, Any]], List[float]]:
        query_vec = embed_texts([query])[0]
        docs_with_scores = self.store.search(query_vec, top_k=top_k)
        contexts = [d for d, _s in docs_with_scores]
        scores = [float(s) for _d, s in docs_with_scores]
        return contexts, scores

    def _build_system_prompt(self, site_url: str) -> str:
        return (
            "You are a helpful assistant that answers strictly using the provided website excerpts. "
            "If the user's question cannot be answered using the excerpts, politely refuse with a brief apology and "
            f"share this link for more info: {site_url}. "
            "Do not hallucinate or use outside knowledge. Cite the page titles when helpful."
        )

    def _build_user_prompt(self, question: str, contexts: List[Dict[str, Any]]) -> str:
        joined = "\n\n".join(
            [f"Title: {c.get('title','')}\nURL: {c.get('url')}\nExcerpt:\n{c.get('text','')[:2000]}" for c in contexts]
        )
        return (
            "Context from the website pages (use only this information):\n" + joined +
            "\n\nUser question: " + question
        )

    def _generate(self, system_prompt: str, user_prompt: str) -> str:
        _ensure_genai_configured()
        model = genai.GenerativeModel(GENERATION_MODEL)
        response = model.generate_content([
            {"role": "user", "parts": [system_prompt]},
            {"role": "user", "parts": [user_prompt]},
        ])
        return response.text or ""

    def answer_question(self, question: str, top_k: int, site_url: str) -> Tuple[str, List[Dict[str, Any]], bool]:
        contexts, scores = self.retrieve(question, top_k=top_k)
        refusal_threshold = float(os.getenv("REFUSAL_SIM_THRESHOLD", "0.25"))
        refused = False

        if len(scores) == 0 or max(scores) < refusal_threshold:
            refused = True
            apology = (
                "Sorry, I can only answer questions based on the provided site. "
                f"Please see this link for more info: {site_url}"
            )
            return apology, [], True

        system_prompt = self._build_system_prompt(site_url)
        user_prompt = self._build_user_prompt(question, contexts)
        answer = self._generate(system_prompt, user_prompt).strip()

        if not answer:
            refused = True
            answer = (
                "Sorry, I couldn't find relevant information on that site. "
                f"Please see this link for more info: {site_url}"
            )

        return answer, contexts, refused