"""
server.py
---------
FastAPI server for the automation RAG pipeline.
Mirrors the FastAPI serving pattern from langgraph-hitl-agent.

Endpoints:
  POST /generate  — spec → test code
  POST /review    — broken test → diagnosis + fix
  POST /convert   — code + target_framework → converted code
  POST /ask       — freeform question → answer
  GET  /health    — status check

Usage:
    python api/server.py
    # → http://localhost:8000
    # → http://localhost:8000/docs  (Swagger UI)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, Literal
import uvicorn

from pipeline.retriever import AutomationRetriever
from pipeline.generator import AutomationGenerator

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Automation Expert API",
    description="RAG-powered automation test assistant — Playwright, Selenium, RestAssured, Postman, TestNG",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ────────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent.parent / "chroma_db"
retriever: Optional[AutomationRetriever] = None
generator: Optional[AutomationGenerator] = None

@app.on_event("startup")
async def startup():
    global retriever, generator
    print(f"🚀 Loading ChromaDB from {DB_PATH}...")
    retriever = AutomationRetriever(db_path=DB_PATH)
    generator = AutomationGenerator(retriever=retriever)
    print("✅ Server ready")


# ── Schemas ────────────────────────────────────────────────────────────────────

Framework = Literal["playwright", "selenium", "restassured", "postman", "testng"]
Language  = Literal["typescript", "javascript", "java", "python", "json"]

class GenerateRequest(BaseModel):
    framework: Framework
    description: str = Field(..., description="What the test should cover")
    url: Optional[str] = Field(None, description="URL under test (for UI frameworks)")
    language: Language = "typescript"
    pattern: Optional[str] = Field(None, description="Preferred pattern: pom | bdd | simple")
    adopt_project: Optional[str] = Field(None, description="Adopt patterns from: ai-web-automation | jeppesen")

class ReviewRequest(BaseModel):
    code: str = Field(..., description="The test code to review")
    framework: Framework
    error: Optional[str] = Field(None, description="Error message or failure description")

class ConvertRequest(BaseModel):
    code: str = Field(..., description="Source test code")
    source_framework: Framework
    target_framework: Framework
    preserve_comments: bool = True

class AskRequest(BaseModel):
    question: str
    framework: Optional[Framework] = None

class AutomationResponse(BaseModel):
    result: str
    context_sources: list[str] = []
    confidence: str = "medium"
    framework: str


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "db_loaded": retriever is not None,
        "collection_count": retriever.count() if retriever else 0,
    }


@app.post("/generate", response_model=AutomationResponse)
async def generate_test(req: GenerateRequest):
    """Generate a test from a natural language description."""
    query = f"Generate {req.framework} test: {req.description}"
    if req.url:
        query += f" for URL {req.url}"
    if req.adopt_project:
        query += f" following {req.adopt_project} patterns"

    result, sources = await generator.generate(
        query=query,
        framework=req.framework,
        task="generate",
        language=req.language,
    )
    return AutomationResponse(result=result, context_sources=sources, framework=req.framework)


@app.post("/review", response_model=AutomationResponse)
async def review_test(req: ReviewRequest):
    """Review a test and diagnose issues."""
    query = f"Review this {req.framework} test code and identify bugs"
    if req.error:
        query += f". Error: {req.error}"

    result, sources = await generator.generate(
        query=query,
        framework=req.framework,
        task="review",
        context_code=req.code,
    )
    return AutomationResponse(result=result, context_sources=sources, framework=req.framework)


@app.post("/convert", response_model=AutomationResponse)
async def convert_test(req: ConvertRequest):
    """Convert test code between frameworks."""
    query = f"Convert this {req.source_framework} test to {req.target_framework}"

    result, sources = await generator.generate(
        query=query,
        framework=req.target_framework,
        task="convert",
        context_code=req.code,
        source_framework=req.source_framework,
    )
    return AutomationResponse(result=result, context_sources=sources, framework=req.target_framework)


@app.post("/ask", response_model=AutomationResponse)
async def ask_question(req: AskRequest):
    """Answer framework questions using the indexed docs."""
    result, sources = await generator.generate(
        query=req.question,
        framework=req.framework or "mixed",
        task="qa",
    )
    return AutomationResponse(result=result, context_sources=sources, framework=req.framework or "mixed")


# ── Entry ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
