# POC 1 — Fine-Tuning (Qwen2.5-Coder-7B + QLoRA)

Adapts your existing AeroSense ChartQA training pipeline to the automation domain.

## Model Choice

| Model | Params | M4 Mac VRAM | Notes |
|---|---|---|---|
| **Qwen2.5-Coder-7B** ✅ | 7B | ~8GB (4-bit) | Best code quality at size, TypeScript+Java strong |
| Qwen2.5-Coder-3B | 3B | ~4GB (4-bit) | Fast iteration, lower quality |
| DeepSeek-Coder-V2-Lite | 16B | ~12GB (4-bit) | Better but slower on M4 Air |
| CodeLlama-13B | 13B | ~10GB (4-bit) | Fallback option |

**Recommended:** Start with Qwen2.5-Coder-7B (matches your ChartQA pipeline exactly).

## Directory Structure

```
poc-1-finetune/
├── data/
│   ├── raw/                    # Source code files from your 5 projects
│   │   ├── playwright-ts/      # From ai-web-automation
│   │   ├── testng-java/        # From Jeppesen framework
│   │   ├── restassured-java/
│   │   ├── selenium-java/
│   │   └── postman/            # .json collections
│   ├── processed/              # JSONL files: {instruction, input, output}
│   │   ├── generate_train.jsonl
│   │   ├── review_train.jsonl
│   │   ├── convert_train.jsonl
│   │   └── qa_train.jsonl
│   └── synthetic/              # LLM-as-Judge generated pairs (Claude API)
│       ├── synthetic_playwright.jsonl
│       └── synthetic_java.jsonl
├── scripts/
│   ├── prepare_dataset.py      # Raw → processed JSONL
│   ├── generate_synthetic.py   # Claude API → synthetic training pairs
│   ├── train_qlora.py          # Main training entry point
│   ├── merge_adapter.py        # Merge LoRA weights into base model
│   └── run_evals.py            # Evaluate against shared/test-cases/
├── configs/
│   ├── qwen25_coder_7b.yaml    # Primary config (M4 Mac + Vast.ai)
│   └── qwen25_coder_3b.yaml    # Fast iteration config
├── models/                     # Saved adapters and merged models
└── evals/                      # Eval run outputs and metrics
```

## Training Data Schema

Each sample is a JSONL line in Alpaca/ChatML format:

```json
{
  "instruction": "Generate a Playwright TypeScript test for user login using Page Object Model",
  "input": "URL: https://app.example.com/login\nFields: email, password\nSuccess: redirect to /dashboard",
  "output": "import { test, expect } from '@playwright/test';\nimport { LoginPage } from '../pages/LoginPage';\n\ntest('user can log in with valid credentials', async ({ page }) => {\n  const loginPage = new LoginPage(page);\n  await loginPage.navigate();\n  await loginPage.login('user@example.com', 'password123');\n  await expect(page).toHaveURL('/dashboard');\n});"
}
```

### Task Types

| Type | Description | Source Projects |
|---|---|---|
| `generate` | Manual spec → automated test code | ai-web-automation, Jeppesen |
| `review` | Broken test → diagnosis + fix | ai-web-automation |
| `convert` | Framework A → Framework B | all 5 |
| `qa` | "How do I do X in Playwright?" | docs corpus |

## Training Config (`configs/qwen25_coder_7b.yaml`)

```yaml
model:
  base: Qwen/Qwen2.5-Coder-7B-Instruct
  quantization: 4bit
  dtype: bfloat16

lora:
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
    - gate_proj
    - up_proj
    - down_proj

training:
  epochs: 3
  batch_size: 2
  gradient_accumulation: 8   # effective batch = 16
  learning_rate: 2e-4
  warmup_ratio: 0.03
  lr_scheduler: cosine
  max_seq_length: 2048
  save_steps: 100
  eval_steps: 50

hardware:
  # M4 MacBook Air (local iteration)
  mac_backend: mlx          # or mps
  # Vast.ai A100 (full training run)
  cuda_backend: unsloth
```

## Data Pipeline

```
Your 5 projects
     │
     ▼
scripts/prepare_dataset.py
     │  ├── Extract functions, classes, test methods
     │  ├── Create instruction-output pairs
     │  └── Split: 80% train / 10% val / 10% test
     │
     ▼
data/processed/*.jsonl
     │
     ▼
scripts/generate_synthetic.py   ← Claude API (LLM-as-Judge from ChartQA pipeline)
     │  ├── Generate edge cases
     │  ├── Framework conversion pairs
     │  └── Review/debug pairs
     │
     ▼
data/synthetic/*.jsonl
     │
     ▼
scripts/train_qlora.py          ← Unsloth + PEFT (matches AeroSense ChartQA stack)
     │
     ▼
models/qwen25-automation-v1/    ← LoRA adapter
     │
     ▼
scripts/merge_adapter.py        ← Full merged model (for Ollama GGUF export)
```

## Hardware Strategy

| Phase | Machine | Time Estimate |
|---|---|---|
| Dataset prep | M4 MacBook Air | 1-2 hrs |
| Synthetic generation | M4 MacBook Air (Claude API) | 2-4 hrs |
| Iteration / debugging | M4 MacBook Air (MLX/MPS) | Real-time |
| Full training run | Vast.ai A100 40GB | ~4-8 hrs |
| Inference / eval | M4 MacBook Air (Ollama) | Real-time |

## Ollama Export

After merging adapter:
```bash
# Convert to GGUF for Ollama
python scripts/merge_adapter.py --output models/merged/
ollama create automation-expert -f models/Modelfile
ollama run automation-expert "Write a Playwright test for login"
```
