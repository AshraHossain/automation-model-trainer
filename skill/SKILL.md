---
name: automation-model-trainer
description: >
  Expert guide for training, augmenting, or prompt-engineering an AI model specialized in
  software test automation: Playwright (TypeScript), Selenium (Java), RestAssured (Java),
  Postman/Newman, and TestNG. Use this skill whenever the user wants to build or run any of
  the three POC approaches (fine-tuning, RAG pipeline, or prompt engineering) for an
  automation-expert model. Also triggers for: adding new framework patterns to the corpus,
  generating synthetic training data, evaluating model output against golden test cases,
  converting test code between frameworks, exporting a fine-tuned model to Ollama, or
  onboarding a new source project into the pattern library. Closely related to the
  AeroSense ChartQA fine-tuning pipeline, the rag-system repo, and the langgraph-hitl-agent.
---

# Automation Model Trainer

Three parallel POCs for building an automation-expert AI model from Ash's five existing
projects. Each POC is independent and runnable on M4 MacBook Air.

## Project Layout

```
automation-model-trainer/
├── poc-1-finetune/     ← Qwen2.5-Coder-7B QLoRA (mirrors AeroSense ChartQA pipeline)
├── poc-2-rag/          ← ChromaDB + Ollama + FastAPI (mirrors rag-system)
├── poc-3-prompt/       ← Claude API + LangGraph (mirrors langgraph-hitl-agent)
└── shared/
    ├── pattern-library/ ← Code patterns from all 5 source projects
    ├── test-cases/      ← Golden input→output pairs (7 cases, all frameworks)
    └── utils/           ← evaluate_all.py (cross-POC comparison)
```

## Source Projects → Patterns

| Project | Contribution |
|---|---|
| `ai-web-automation` | Playwright TS POM, self-healing locators, object repository |
| `langgraph-hitl-agent` | LangGraph orchestration, HITL checkpoint, FastAPI serving |
| `rag-system` | ChromaDB ingestion, CrossEncoder reranking, Ollama integration |
| `AeroSense ChartQA` | Qwen2.5 QLoRA pipeline, Unsloth/PEFT, LLM-as-Judge |
| `Jeppesen TestNG/Java` | TestNG suites, Appium, BDD/Cucumber, enterprise Java patterns |

## Recommended Start Order

1. **POC 3 first** (fastest, highest quality) — needs only `ANTHROPIC_API_KEY`
2. **POC 2 second** (no GPU, offline-capable) — needs `ollama pull qwen2.5-coder:7b`
3. **POC 1 last** (full training) — needs dataset + Vast.ai A100 or MLX for M4

## Quick Commands

```bash
# POC 3 — Interactive CLI
cd poc-3-prompt && python chains/automation_chain.py

# POC 2 — Ingest + serve
cd poc-2-rag
python pipeline/ingest.py        # first run only
python api/server.py             # http://localhost:8000/docs

# POC 1 — Dataset prep + training
cd poc-1-finetune
python scripts/prepare_dataset.py
python scripts/train_qlora.py --backend mlx    # M4 Mac
python scripts/train_qlora.py --backend unsloth # Vast.ai

# Evaluate all POCs
python shared/utils/evaluate_all.py --pocs rag prompt
```

## Adding a New Source Project

1. Copy sanitized code into `shared/pattern-library/<framework>/`
2. Re-run `poc-2-rag/pipeline/ingest.py --reset` to rebuild the vector index
3. Add few-shot examples to `poc-3-prompt/few-shots/<framework>/generate.json`
4. Add representative samples to `poc-1-finetune/data/raw/<framework>/`
5. Re-run `poc-1-finetune/scripts/prepare_dataset.py`

## Supported Tasks

| Task | Input | Output |
|---|---|---|
| `generate` | Natural language spec | Complete runnable test code |
| `review` | Broken/suboptimal test + optional error | Diagnosis + corrected code |
| `convert` | Test code + source/target framework | Converted test code |
| `qa` | Freeform question | Answer with code example |

## Supported Frameworks

`playwright` · `selenium` · `restassured` · `postman` · `testng`

## Key Files to Know

| File | Purpose |
|---|---|
| `poc-1-finetune/configs/qwen25_coder_7b.yaml` | Training config (edit batch size, LR, etc.) |
| `poc-1-finetune/scripts/prepare_dataset.py` | Raw code → training JSONL |
| `poc-1-finetune/scripts/train_qlora.py` | QLoRA training entry point |
| `poc-2-rag/pipeline/ingest.py` | Index corpus into ChromaDB |
| `poc-2-rag/api/server.py` | FastAPI serving all four endpoints |
| `poc-3-prompt/chains/automation_chain.py` | LangGraph chain + HITL |
| `poc-3-prompt/system-prompts/base.md` | Master system prompt |
| `poc-3-prompt/few-shots/*/generate.json` | Per-framework few-shot examples |
| `shared/test-cases/golden_test_cases.json` | 7 golden test cases for evaluation |
| `shared/utils/evaluate_all.py` | Cross-POC comparison table |

## References

Read these for deep-dives:
- `poc-1-finetune/README.md` — Model selection, data schema, hardware strategy
- `poc-2-rag/README.md` — Corpus tiers, API examples, Ollama model options
- `poc-3-prompt/README.md` — LangGraph state machine, evaluation setup

## Model Export (POC 1 → Ollama)

After a successful fine-tuning run:
```bash
python poc-1-finetune/scripts/merge_adapter.py --output models/merged/
# Creates models/Modelfile → ollama create automation-expert -f models/Modelfile
# Then usable by POC 2 RAG as drop-in Ollama model
```

## Hardware Notes (M4 MacBook Air)

- POC 3 and POC 2 run natively with no GPU
- POC 1 local iteration: `--backend mlx` (mlx-lm, ~1000 steps in reasonable time)
- POC 1 full training: Vast.ai A100 40GB (`--backend unsloth`), ~4-8 hrs
- Recommended Ollama model for POC 2: `qwen2.5-coder:7b` (~8GB RAM)
