"""
train_qlora.py
--------------
QLoRA fine-tuning for Qwen2.5-Coder-7B on automation test data.
Mirrors the AeroSense ChartQA training pipeline.

M4 MacBook Air: use --backend mlx (fast iteration, smaller batches)
Vast.ai A100:   use --backend unsloth (full training run)

Usage:
    # Local M4 Mac iteration
    python scripts/train_qlora.py --config configs/qwen25_coder_7b.yaml --backend mlx

    # Vast.ai full run
    python scripts/train_qlora.py --config configs/qwen25_coder_7b.yaml --backend unsloth
"""

import os
import yaml
import argparse
from pathlib import Path
from datetime import datetime

def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)

def train_unsloth(cfg: dict, data_dir: Path, output_dir: Path):
    """Full QLoRA training via Unsloth — use on Vast.ai A100."""
    from unsloth import FastLanguageModel
    from datasets import load_dataset
    from trl import SFTTrainer
    from transformers import TrainingArguments

    print("🚀 Loading model with Unsloth...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=cfg["model"]["base"],
        max_seq_length=cfg["training"]["max_seq_length"],
        dtype=None,
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=cfg["lora"]["r"],
        target_modules=cfg["lora"]["target_modules"],
        lora_alpha=cfg["lora"]["alpha"],
        lora_dropout=cfg["lora"]["dropout"],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    dataset = load_dataset("json", data_files={
        "train": str(data_dir / "train.jsonl"),
        "validation": str(data_dir / "val.jsonl"),
    })

    def format_sample(sample):
        return {
            "text": (
                f"### Instruction:\n{sample['instruction']}\n\n"
                f"### Input:\n{sample['input']}\n\n"
                f"### Response:\n{sample['output']}"
            )
        }

    dataset = dataset.map(format_sample)

    run_name = f"automation-expert-{datetime.now().strftime('%Y%m%d_%H%M')}"
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        dataset_text_field="text",
        max_seq_length=cfg["training"]["max_seq_length"],
        args=TrainingArguments(
            output_dir=str(output_dir / run_name),
            num_train_epochs=cfg["training"]["epochs"],
            per_device_train_batch_size=cfg["training"]["batch_size"],
            gradient_accumulation_steps=cfg["training"]["gradient_accumulation"],
            learning_rate=cfg["training"]["learning_rate"],
            warmup_ratio=cfg["training"]["warmup_ratio"],
            lr_scheduler_type=cfg["training"]["lr_scheduler"],
            save_steps=cfg["training"]["save_steps"],
            eval_steps=cfg["training"]["eval_steps"],
            evaluation_strategy="steps",
            logging_steps=10,
            fp16=False,
            bf16=True,
            report_to=["wandb"],  # swap for mlflow if preferred (matches ChartQA)
            run_name=run_name,
        ),
    )

    print("🏋️  Training started...")
    trainer.train()
    model.save_pretrained(str(output_dir / run_name / "adapter"))
    tokenizer.save_pretrained(str(output_dir / run_name / "adapter"))
    print(f"✅ Adapter saved to {output_dir / run_name / 'adapter'}")


def train_mlx(cfg: dict, data_dir: Path, output_dir: Path):
    """
    MLX fine-tuning for M4 Mac — fast iteration without GPU.
    Uses mlx-lm which supports Qwen2.5 natively.

    Install: pip install mlx-lm
    """
    import subprocess

    run_name = f"automation-expert-mlx-{datetime.now().strftime('%Y%m%d_%H%M')}"
    adapter_dir = output_dir / run_name / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python", "-m", "mlx_lm.lora",
        "--model", cfg["model"]["base"],
        "--train",
        "--data", str(data_dir),
        "--adapter-path", str(adapter_dir),
        "--num-layers", str(cfg["lora"]["r"]),
        "--batch-size", str(cfg["training"]["batch_size"]),
        "--iters", "1000",       # quick iteration on M4
        "--val-batches", "10",
        "--learning-rate", str(cfg["training"]["learning_rate"]),
        "--save-every", "100",
        "--max-seq-length", str(cfg["training"]["max_seq_length"]),
    ]

    print(f"🍎 Running MLX training on M4 Mac...")
    print(f"   Command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"✅ MLX adapter saved to {adapter_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/qwen25_coder_7b.yaml")
    parser.add_argument("--backend", choices=["unsloth", "mlx"], default="mlx")
    parser.add_argument("--data-dir", default="../data/processed")
    parser.add_argument("--output-dir", default="../models")
    args = parser.parse_args()

    cfg = load_config(args.config)
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📋 Config: {args.config}")
    print(f"📦 Model: {cfg['model']['base']}")
    print(f"🖥️  Backend: {args.backend}")
    print(f"📁 Data: {data_dir}")

    if args.backend == "unsloth":
        train_unsloth(cfg, data_dir, output_dir)
    else:
        train_mlx(cfg, data_dir, output_dir)


if __name__ == "__main__":
    main()
