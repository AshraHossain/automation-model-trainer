# POC 3 Setup

## Prerequisites

1. **API Key** (required)
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```
   Get key from: https://console.anthropic.com/account/keys

2. **Dependencies** (done)
   ```bash
   pip install -r requirements.txt
   ```

## Quick Test

```bash
# From poc-3-prompt/ directory
python test_chain.py
```

Expected: generates and reviews test code using Claude Sonnet.

## Interactive CLI

```bash
python chains/automation_chain.py
```

Commands: `generate | review | convert | ask`

**Example:**
- Task: `generate`
- Framework: `playwright`
- Describe: `Login test for email+password form, redirect to /dashboard on success`

## Integration

The chain is ready for:
1. **Evaluation** — run against `shared/test-cases/golden_test_cases.json`
2. **FastAPI server** — endpoint at `/api/generate?task=...&framework=...`
3. **HITL upgrade** — pass `hitl=True` to AutomationChain for human review checkpoints

## Architecture

- **State**: AutomationState (task, framework, prompts, outputs)
- **Nodes**: load_prompt → generate → validate → hitl (optional) → end
- **Retry**: auto-retries generation if validation fails (max 2x)
- **Few-shots**: loaded from `few-shots/{framework}/{task}.json`
- **System prompt**: base.md + framework-specific instructions

## Next Steps

1. Enhance few-shots from pattern library
2. Run evaluation: `python evaluations/run_evals.py`
3. Compare vs POC 1 (fine-tune) and POC 2 (RAG)
