# Website RAG Chatbot (Gemini)

Paste any website URL, the app will crawl same-domain pages, index the text with Gemini embeddings, and spin up a chatbot that only answers using that site's content. If a question is off-topic or not supported by the site's content, the bot replies with a short apology and provides the original link for more info.

## Requirements
- Python 3.10+
- Google API key for Gemini

## Environment
Create `.env` in the workspace root with:

```
GOOGLE_API_KEY=your_google_api_key
# Optional tuning
EMBEDDING_MODEL=text-embedding-004
GENERATION_MODEL=gemini-1.5-flash
REFUSAL_SIM_THRESHOLD=0.25
DATA_DIR=/workspace/data
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
EMBED_BATCH_SIZE=6
```

## Install
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000/`.

## Usage
1. Enter a site URL (e.g., `https://example.com`) and click Ingest.
2. After indexing completes, ask questions in the Chat box.
3. The bot uses RAG over the site's content. For unrelated questions, it replies with an apology and the site link.

## Notes
- Crawler limits to same-domain HTTP/HTTPS pages and skips binary assets.
- Index uses FAISS inner product with normalized vectors (cosine similarity).
- Text is chunked to improve retrieval granularity.
- If you change models, embedding dimension may differ; the app reads vectors from the API directly and initializes FAISS accordingly.

## API
- POST `/ingest` { "url": string, "max_pages"?: number }
- POST `/chat` { "site_url": string, "question": string, "top_k"?: number }

## Security and Respect
- Only crawl websites you have rights to access.
- Respect robots.txt and terms of service if required (this sample does not parse robots.txt by default).