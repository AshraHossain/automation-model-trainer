"""
ingest.py
---------
Loads automation framework docs and your project patterns into ChromaDB.
Mirrors the ingestion pipeline from your rag-system repo.

Usage:
    python pipeline/ingest.py
    python pipeline/ingest.py --corpus-dir ../corpus --db-path ../chroma_db --reset
"""

import os
import argparse
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    JSONLoader,
)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma


# ── Config ─────────────────────────────────────────────────────────────────────

CORPUS_DIR = Path("../corpus")
DB_PATH = Path("../chroma_db")
COLLECTION_NAME = "automation-expert"

# Map corpus subdirs to metadata
CORPUS_METADATA = {
    "playwright":        {"framework": "playwright",    "language": "typescript", "type": "official_doc"},
    "selenium":          {"framework": "selenium",      "language": "java",       "type": "official_doc"},
    "restassured":       {"framework": "restassured",   "language": "java",       "type": "official_doc"},
    "postman":           {"framework": "postman",       "language": "json",       "type": "official_doc"},
    "testng":            {"framework": "testng",        "language": "java",       "type": "official_doc"},
    "custom-patterns":   {"framework": "mixed",         "language": "mixed",      "type": "custom_pattern"},
}

# Splitter config — larger chunks preserve code context
CODE_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    separators=["\n\n", "\n", "}", "{", ";", " ", ""],
)

SUPPORTED_EXTENSIONS = [".ts", ".tsx", ".js", ".java", ".py", ".md", ".json", ".feature", ".xml"]


# ── Loaders ────────────────────────────────────────────────────────────────────

def load_corpus_dir(corpus_subdir: Path, metadata: dict) -> list:
    """Load all supported files from a corpus subdirectory."""
    docs = []
    for ext in SUPPORTED_EXTENSIONS:
        files = list(corpus_subdir.glob(f"**/*{ext}"))
        for f in files:
            try:
                loader = TextLoader(str(f), encoding="utf-8")
                loaded = loader.load()
                for doc in loaded:
                    doc.metadata.update(metadata)
                    doc.metadata["source_file"] = f.name
                    doc.metadata["source_path"] = str(f)
                docs.extend(loaded)
            except Exception as e:
                print(f"  ⚠️  Skipped {f.name}: {e}")
    return docs


def load_all_corpus(corpus_dir: Path) -> list:
    """Load all corpus subdirectories with priority ordering."""
    all_docs = []

    # Load custom patterns first (highest priority in retrieval)
    custom_dir = corpus_dir / "custom-patterns"
    if custom_dir.exists():
        meta = CORPUS_METADATA["custom-patterns"]
        docs = load_corpus_dir(custom_dir, meta)
        print(f"  📁 custom-patterns: {len(docs)} docs")
        all_docs.extend(docs)

    # Load framework-specific dirs
    for subdir_name, meta in CORPUS_METADATA.items():
        if subdir_name == "custom-patterns":
            continue
        subdir = corpus_dir / subdir_name
        if subdir.exists():
            docs = load_corpus_dir(subdir, meta)
            print(f"  📁 {subdir_name}: {len(docs)} docs")
            all_docs.extend(docs)

    return all_docs


# ── Ingestion ──────────────────────────────────────────────────────────────────

def ingest(corpus_dir: Path, db_path: Path, reset: bool = False):
    print(f"🔍 Loading corpus from {corpus_dir.resolve()}...")
    docs = load_all_corpus(corpus_dir)
    print(f"  Total raw docs: {len(docs)}")

    print("✂️  Chunking documents...")
    chunks = CODE_SPLITTER.split_documents(docs)
    print(f"  Total chunks: {len(chunks)}")

    print("🧠 Initializing embeddings (Ollama: nomic-embed-text)...")
    # nomic-embed-text is fast and excellent for code
    # Install: ollama pull nomic-embed-text
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    if reset and db_path.exists():
        import shutil
        shutil.rmtree(db_path)
        print(f"  🗑️  Reset: deleted {db_path}")

    print(f"💾 Storing in ChromaDB at {db_path.resolve()}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(db_path),
        collection_name=COLLECTION_NAME,
        collection_metadata={"hnsw:space": "cosine"},
    )
    vectorstore.persist()

    count = vectorstore._collection.count()
    print(f"\n✅ Ingestion complete: {count} chunks indexed in ChromaDB")
    print(f"   DB path: {db_path.resolve()}")
    print(f"   Collection: {COLLECTION_NAME}")
    print(f"\n💡 Next: python api/server.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-dir", default="../corpus")
    parser.add_argument("--db-path", default="../chroma_db")
    parser.add_argument("--reset", action="store_true", help="Delete and rebuild the vector DB")
    args = parser.parse_args()

    ingest(
        corpus_dir=Path(args.corpus_dir),
        db_path=Path(args.db_path),
        reset=args.reset
    )
