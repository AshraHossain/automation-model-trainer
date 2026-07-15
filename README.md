# automation-model-trainer

> Train, augment, or prompt-engineer an AI model that is expert in software test automation —
> Playwright (TypeScript), Selenium (Java), RestAssured (Java), Postman/Newman, and TestNG.

## Architecture Overview

Three parallel POCs, each independently runnable, sharing a common pattern library drawn from
your existing projects:

| Source Project | Patterns Contributed |
|---|---|
| `ai-web-automation` | Playwright TS POM, self-healing locators, object repository |
| `langgraph-hitl-agent` | LangGraph orchestration, FastAPI serving, HITL review loops |
| `rag-system` | ChromaDB ingestion, CrossEncoder reranking, Ollama integration |
| `AeroSense ChartQA` | Qwen2.5 QLoRA pipeline, Unsloth/PEFT configs, LLM-as-Judge |
| `Jeppesen TestNG/Java` | TestNG suites, Appium patterns, BDD/Cucumber, enterprise Java |

---

## POC Summary

### POC 1 — Fine-Tuning (`poc-1-finetune/`)
Fine-tune **Qwen2.5-Coder-7B** with QLoRA on a curated automation dataset.
The model learns to generate, review, and convert test code natively (offline capable).
- **Stack:** Unsloth + PEFT + MLX (M4 Mac) → Vast.ai A100 for full runs
- **Best for:** Offline use, AgentForge product, privacy-sensitive codebases

### POC 2 — RAG Pipeline (`poc-2-rag/`)
Index automation framework docs + your codebase patterns into **ChromaDB**.
Serve via **Ollama** (local) with a **FastAPI** endpoint and optional Streamlit UI.
- **Stack:** LangChain + ChromaDB + CrossEncoder + Ollama + FastAPI
- **Best for:** Always up-to-date, zero GPU required, production-ready fastest

### POC 3 — Prompt Engineering (`poc-3-prompt/`)
System prompt + few-shot chains targeting **Claude API** (or any frontier model).
Uses your existing patterns as few-shot examples. LangGraph orchestration for
multi-step tasks (generate → review → fix loop).
- **Stack:** Claude Sonnet / Anthropic API + LangGraph + FastAPI
- **Best for:** Highest quality output, fastest to ship, easiest to iterate

---

## Shared Assets (`shared/`)

- `pattern-library/` — Canonical code patterns extracted from all 5 source projects
- `test-cases/` — Golden input→output pairs used to evaluate all three POCs
- `utils/` — Shared data cleaning, tokenization, and evaluation utilities

---

## Quickstart (M4 MacBook Air)

```bash
# Clone and set up
git clone <your-repo> automation-model-trainer
cd automation-model-trainer

# POC 2 is fastest to start — run RAG first
cd poc-2-rag
pip install -r requirements.txt
python pipeline/ingest.py          # indexes corpus
python api/server.py               # FastAPI on :8000
# open ui/ in browser or curl the API

# POC 3 next — requires ANTHROPIC_API_KEY
cd ../poc-3-prompt
export ANTHROPIC_API_KEY=sk-...
python chains/automation_chain.py

# POC 1 last — requires Unsloth + MLX
cd ../poc-1-finetune
pip install -r requirements.txt
python scripts/prepare_dataset.py
python scripts/train_qlora.py --config configs/qwen25_coder_7b.yaml
```

---

## Evaluation

All three POCs share the same golden test cases in `shared/test-cases/`.
Run the unified evaluator to compare all three side-by-side:

```bash
python shared/utils/evaluate_all.py
```

Outputs a Markdown table: task → POC1 score → POC2 score → POC3 score.

---

## Project Roadmap

- [x] Phase 1: Populate pattern library from source projects
      — 20 files harvested (playwright-ts: 4, selenium-java: 9, restassured-java: 7).
      `testng-java/` and `postman/` are empty: no Jeppesen TestNG code or Postman
      collections exist on this machine — add them when available.
- [ ] Phase 2: POC 2 (RAG) — corpus built (`poc-2-rag/corpus/custom-patterns/`, 20 files).
      **Blocked on:** `ollama` install (+ `ollama pull nomic-embed-text`) and
      `pip install -r poc-2-rag/requirements.txt`. Then: `python pipeline/ingest.py` → `python api/server.py`.
      Note: `ingest.py` uses deprecated LangChain APIs (`OllamaEmbeddings`, `.persist()`) — pin old
      versions or update imports on first run.
- [ ] Phase 3: POC 3 (Prompt) — chain, prompts, and few-shots complete.
      **Blocked on:** `ANTHROPIC_API_KEY` and `pip install -r poc-3-prompt/requirements.txt`.
- [x] Phase 4 (dataset half): POC 1 dataset prepared — 37 samples
      (29 train / 4 val / 4 test) in `poc-1-finetune/data/processed/`.
      Convert-pair outputs are TODO placeholders — fill via Claude API before training.
- [ ] Phase 4 (training half): **Blocked on:** GPU (Vast.ai A100 path; MLX path is Mac-only,
      dead on this Windows machine).
- [ ] Phase 5: Comparative evaluation — golden test cases ready
      (`shared/test-cases/golden_test_cases.json`, 7 cases). Runs once Phases 2–3 are live:
      `python shared/utils/evaluate_all.py`
- [ ] Phase 6: Best POC → AgentForge product packaging
