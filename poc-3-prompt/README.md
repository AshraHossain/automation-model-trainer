# POC 3 — Prompt Engineering (Claude API + LangGraph)

Fastest path to production quality. Uses Claude Sonnet via Anthropic API with
carefully crafted system prompts and your project patterns as few-shot examples.
Orchestrated with LangGraph (mirrors langgraph-hitl-agent architecture).

## Why This POC First?

- Zero training time, zero GPU needed
- Highest output quality (frontier model)
- Your existing LangGraph + FastAPI experience applies directly
- Can be upgraded later with fine-tuned model as drop-in replacement

## Architecture

```
User Request
     │
     ▼
LangGraph Automation Chain
     │
     ├── Step 1: classify_task()     → generate | review | convert | qa
     │
     ├── Step 2: select_prompt()     → framework-specific system prompt
     │                                  + few-shot examples from your projects
     ├── Step 3: claude_generate()   → Claude Sonnet API call
     │
     ├── Step 4: validate_output()   → syntax check, completeness check
     │
     └── Step 5: hitl_review()       → optional human checkpoint
                                        (from langgraph-hitl-agent pattern)
```

## Directory Structure

```
poc-3-prompt/
├── system-prompts/
│   ├── base.md                 # Core automation expert persona
│   ├── playwright.md           # Playwright-specific instructions
│   ├── selenium.md             # Selenium Java instructions
│   ├── restassured.md          # RestAssured API test instructions
│   ├── postman.md              # Postman/Newman instructions
│   └── testng.md               # TestNG suite instructions
├── few-shots/
│   ├── playwright/             # Real examples from ai-web-automation
│   │   ├── generate.json
│   │   ├── review.json
│   │   └── convert.json
│   ├── selenium/               # From Jeppesen Java framework
│   ├── restassured/
│   ├── postman/
│   └── testng/                 # From Jeppesen TestNG patterns
├── chains/
│   ├── automation_chain.py     # Main LangGraph chain (mirrors hitl-agent)
│   ├── nodes.py                # Individual LangGraph node functions
│   ├── state.py                # AutomationState TypedDict
│   └── hitl.py                 # Human-in-the-loop checkpoint (reuse from hitl-agent)
├── evaluations/
│   ├── run_evals.py            # Compare against shared/test-cases/
│   └── llm_judge.py            # LLM-as-Judge (from ChartQA pipeline)
└── requirements.txt
```

## System Prompt Strategy

The base system prompt establishes the automation expert persona and is
**augmented** with framework-specific instructions and your project's
canonical patterns as few-shot examples.

See `system-prompts/base.md` for the master prompt and
`few-shots/playwright/generate.json` for example structure.

## Quickstart

```bash
cd poc-3-prompt
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

# Run the chain interactively
python chains/automation_chain.py

# Or via the shared FastAPI server
python ../../poc-2-rag/api/server.py --backend prompt
```

## LangGraph Chain States

```
START
  │
  ▼
[classify_task]          ─ classify: generate | review | convert | qa
  │
  ▼
[load_system_prompt]     ─ load framework prompt + few-shots
  │
  ▼
[claude_generate]        ─ Claude Sonnet API call
  │
  ▼
[validate_output]        ─ syntax check → retry if invalid (max 2x)
  │
  ├── valid ──────────►
  │                    │
  └── invalid → retry  │
                        ▼
               [hitl_checkpoint]  ─ optional: interrupt for human review
                        │
                        ▼
                      END
```

## Evaluation

Uses the same LLM-as-Judge pattern from your AeroSense ChartQA pipeline:

```bash
python evaluations/run_evals.py \
    --test-cases ../../shared/test-cases/ \
    --judge claude-sonnet-4-20250514
```

Outputs: accuracy per task type, framework, and comparison vs POC 1/2.
