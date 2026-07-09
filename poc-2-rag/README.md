# POC 2 — RAG Pipeline (ChromaDB + Ollama + FastAPI)

Extends your existing `rag-system` repo with automation-specific corpus and
a dedicated API endpoint. No GPU required — runs fully on M4 MacBook Air.

## Architecture

```
Your 5 Project Patterns
        │
        ▼
  pipeline/ingest.py          ← Loads, chunks, embeds, stores
        │
        ▼
  ChromaDB (local)            ← Vector store (persistent on disk)
        │
        ▼
  pipeline/retriever.py       ← CrossEncoder reranking (matches rag-system)
        │
        ▼
  api/server.py (FastAPI)     ← REST endpoint :8000
        │
        ├── /generate          POST: spec → test code
        ├── /review            POST: broken test → diagnosis + fix
        ├── /convert           POST: code + target_framework → converted code
        └── /ask               POST: freeform question → answer
        │
        ▼
  ui/index.html               ← Optional Streamlit or plain HTML UI
```

## Directory Structure

```
poc-2-rag/
├── corpus/                     # Raw documents to index
│   ├── playwright/             # Playwright docs + your ai-web-automation patterns
│   ├── selenium/               # Selenium WebDriver docs + Jeppesen Java patterns
│   ├── restassured/            # RestAssured wiki + your Java test patterns
│   ├── postman/                # Postman learning center + Newman CLI docs
│   ├── testng/                 # TestNG docs + your Jeppesen TestNG patterns
│   └── custom-patterns/        # Your sanitized project patterns (highest priority)
├── pipeline/
│   ├── ingest.py              # Corpus → ChromaDB
│   ├── retriever.py           # Query → retrieve + rerank
│   └── generator.py           # Context + query → Ollama response
├── api/
│   ├── server.py              # FastAPI app
│   ├── models.py              # Pydantic request/response schemas
│   └── routes/
│       ├── generate.py
│       ├── review.py
│       ├── convert.py
│       └── ask.py
├── ui/
│   └── app.py                 # Streamlit UI (optional)
├── requirements.txt
└── docker-compose.yml         # ChromaDB + API containerized
```

## Corpus Loading Strategy

Priority tiers when retrieving context:

1. **custom-patterns/** — Your project code (highest relevance, always prefer)
2. **Framework docs** — Official Playwright/Selenium/etc docs
3. **Community patterns** — GitHub examples, best practices

Each document is tagged with metadata:
```python
{
    "framework": "playwright",
    "type": "custom_pattern",   # custom_pattern | official_doc | example
    "source_project": "ai-web-automation",
    "language": "typescript"
}
```

## Quickstart

```bash
cd poc-2-rag
pip install -r requirements.txt

# 1. Drop your project code into corpus/custom-patterns/
cp -r ../../shared/pattern-library/* corpus/custom-patterns/

# 2. Index everything (first run ~5 mins)
python pipeline/ingest.py

# 3. Start API
python api/server.py
# → http://localhost:8000/docs

# 4. Optional: Streamlit UI
streamlit run ui/app.py
```

## Example API Calls

```bash
# Generate a test
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "framework": "playwright",
    "description": "Login form with email, password, remember me checkbox",
    "url": "https://app.example.com/login",
    "language": "typescript"
  }'

# Review a broken test
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "page.click(\"#submit\")",
    "framework": "playwright",
    "error": "ElementNotFound"
  }'

# Convert framework
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "code": "await page.getByRole(\"button\", { name: \"Login\" }).click();",
    "source_framework": "playwright",
    "target_framework": "selenium-java"
  }'
```

## Ollama Model Options (M4 Mac)

| Model | Size | Notes |
|---|---|---|
| `qwen2.5-coder:7b` ✅ | 4.7GB | Best code quality |
| `qwen2.5-coder:3b` | 2.0GB | Fast, decent quality |
| `codellama:7b` | 3.8GB | Reliable fallback |
| `mistral:7b` | 4.1GB | Good for QA/explanation tasks |

```bash
ollama pull qwen2.5-coder:7b
```
