from __future__ import annotations

import re
import time
from collections import deque
from dataclasses import dataclass
from typing import List, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT_SECS = 15
SLEEP_BETWEEN_REQUESTS_SECS = 0.25


@dataclass
class Document:
    url: str
    title: str
    text: str


def _is_same_domain(url: str, root_netloc: str) -> bool:
    try:
        return urlparse(url).netloc == root_netloc
    except Exception:
        return False


def _clean_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form"]):
        tag.decompose()

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return title, text


def _should_skip_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return True
    if any(part in parsed.path.lower() for part in [
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf", ".zip", ".tar", ".gz", ".rar", ".7z", ".mp4", ".mp3", ".webm", ".avi"
    ]):
        return True
    return False


def crawl_site(root_url: str, max_pages: int = 20) -> List[Document]:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    parsed_root = urlparse(root_url)
    if parsed_root.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are supported")

    root_netloc = parsed_root.netloc

    visited: Set[str] = set()
    queue: deque[str] = deque([root_url])
    results: List[Document] = []

    while queue and len(results) < max_pages:
        url = queue.popleft()
        if url in visited or _should_skip_url(url):
            continue
        visited.add(url)

        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT_SECS)
            ctype = resp.headers.get("Content-Type", "")
            if resp.status_code != 200 or "text/html" not in ctype:
                continue
        except Exception:
            continue

        title, text = _clean_text(resp.text)
        if text and len(text) > 100:
            results.append(Document(url=url, title=title, text=text))

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("#"):
                continue
            absolute = urljoin(url, href)
            if _is_same_domain(absolute, root_netloc) and absolute not in visited:
                queue.append(absolute)

        time.sleep(SLEEP_BETWEEN_REQUESTS_SECS)

    return results