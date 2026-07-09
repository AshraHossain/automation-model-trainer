"""
prepare_dataset.py
------------------
Extracts training pairs from your 5 source projects and converts them
into Alpaca-format JSONL for QLoRA fine-tuning.

Reuses the data pipeline pattern from AeroSense ChartQA.

Usage:
    python scripts/prepare_dataset.py \
        --source-dir ../../shared/pattern-library \
        --output-dir ../data/processed \
        --tasks generate review convert qa
"""

import os
import json
import argparse
import random
from pathlib import Path
from typing import Generator

# ── Schema ────────────────────────────────────────────────────────────────────

def make_sample(instruction: str, input_text: str, output: str, task: str, framework: str) -> dict:
    return {
        "instruction": instruction,
        "input": input_text,
        "output": output,
        "metadata": {
            "task": task,        # generate | review | convert | qa
            "framework": framework,  # playwright | selenium | restassured | postman | testng
            "source": "extracted"
        }
    }

# ── Extractors ─────────────────────────────────────────────────────────────────

def extract_playwright_ts(source_dir: Path) -> Generator[dict, None, None]:
    """Extract Playwright TypeScript patterns from ai-web-automation structure."""
    for ts_file in source_dir.glob("playwright-ts/**/*.ts"):
        content = ts_file.read_text(encoding="utf-8", errors="ignore")
        if "test(" not in content and "test.describe" not in content:
            continue
        # Each test file becomes a generation example
        # Strip test body → instruction; keep full content as output
        filename = ts_file.stem
        yield make_sample(
            instruction=f"Generate a Playwright TypeScript test suite for: {filename.replace('-', ' ').replace('_', ' ')}",
            input_text=f"File: {ts_file.name}\nFramework: Playwright TypeScript with Page Object Model",
            output=content,
            task="generate",
            framework="playwright"
        )


def extract_java_tests(source_dir: Path, framework: str, glob: str) -> Generator[dict, None, None]:
    """Extract Java test patterns (TestNG, RestAssured, Selenium)."""
    for java_file in source_dir.glob(f"{glob}/**/*.java"):
        content = java_file.read_text(encoding="utf-8", errors="ignore")
        if "@Test" not in content:
            continue
        classname = java_file.stem
        yield make_sample(
            instruction=f"Generate a {framework} test class for: {classname}",
            input_text=f"Class: {classname}.java\nFramework: {framework}",
            output=content,
            task="generate",
            framework=framework.lower().replace(" ", "")
        )


def extract_postman_collections(source_dir: Path) -> Generator[dict, None, None]:
    """Extract Postman collections as test generation targets."""
    for json_file in source_dir.glob("postman/**/*.json"):
        try:
            collection = json.loads(json_file.read_text())
        except json.JSONDecodeError:
            continue
        name = collection.get("info", {}).get("name", json_file.stem)
        yield make_sample(
            instruction=f"Generate Postman collection test scripts for: {name}",
            input_text=f"Collection: {name}\nSource: {json_file.name}",
            output=json.dumps(collection, indent=2),
            task="generate",
            framework="postman"
        )


def create_convert_pairs(samples: list[dict]) -> list[dict]:
    """
    Cross-framework conversion pairs.
    For each Playwright TS sample, create a 'convert to Java/Selenium' pair.
    """
    pairs = []
    playwright = [s for s in samples if s["metadata"]["framework"] == "playwright"]
    selenium = [s for s in samples if s["metadata"]["framework"] == "selenium"]

    for pw in playwright[:50]:  # cap to avoid dataset imbalance
        pairs.append(make_sample(
            instruction="Convert this Playwright TypeScript test to Selenium Java with TestNG",
            input_text=pw["output"][:1500],  # truncate long inputs
            output="// TODO: Fill from corresponding selenium pattern or generate via Claude API",
            task="convert",
            framework="playwright->selenium"
        ))

    for sel in selenium[:50]:
        pairs.append(make_sample(
            instruction="Convert this Selenium Java test to Playwright TypeScript",
            input_text=sel["output"][:1500],
            output="// TODO: Fill from corresponding playwright pattern or generate via Claude API",
            task="convert",
            framework="selenium->playwright"
        ))
    return pairs


def create_review_pairs(samples: list[dict]) -> list[dict]:
    """Create broken-test → fix pairs by injecting common bugs."""
    COMMON_BUGS = [
        ("await page.click(", "page.click("),        # missing await
        ("expect(", "assert("),                       # wrong assertion
        ("getByRole(", "locator(\"button\")"),        # weak locator
    ]
    pairs = []
    for sample in random.sample(samples, min(100, len(samples))):
        code = sample["output"]
        for correct, broken in COMMON_BUGS:
            if correct in code:
                broken_code = code.replace(correct, broken, 1)
                pairs.append(make_sample(
                    instruction="Review this test code and identify the bug, then provide the corrected version",
                    input_text=broken_code[:2000],
                    output=f"Bug identified: '{broken}' should be '{correct}'.\n\nCorrected code:\n\n{code[:2000]}",
                    task="review",
                    framework=sample["metadata"]["framework"]
                ))
                break
    return pairs


# ── Main ───────────────────────────────────────────────────────────────────────

def main(source_dir: str, output_dir: str, tasks: list[str]):
    src = Path(source_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("🔍 Extracting patterns from source projects...")
    all_samples = []

    all_samples.extend(extract_playwright_ts(src))
    all_samples.extend(extract_java_tests(src, "TestNG", "testng-java"))
    all_samples.extend(extract_java_tests(src, "RestAssured", "restassured-java"))
    all_samples.extend(extract_java_tests(src, "Selenium", "selenium-java"))
    all_samples.extend(extract_postman_collections(src))

    print(f"  ✅ Extracted {len(all_samples)} base samples")

    if "convert" in tasks:
        convert_pairs = create_convert_pairs(all_samples)
        all_samples.extend(convert_pairs)
        print(f"  ✅ Created {len(convert_pairs)} conversion pairs")

    if "review" in tasks:
        review_pairs = create_review_pairs(all_samples)
        all_samples.extend(review_pairs)
        print(f"  ✅ Created {len(review_pairs)} review/debug pairs")

    # Shuffle and split
    random.shuffle(all_samples)
    n = len(all_samples)
    train = all_samples[:int(n * 0.8)]
    val   = all_samples[int(n * 0.8):int(n * 0.9)]
    test  = all_samples[int(n * 0.9):]

    def write_jsonl(data, path):
        with open(path, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")
        print(f"  📄 {path} ({len(data)} samples)")

    write_jsonl(train, out / "train.jsonl")
    write_jsonl(val,   out / "val.jsonl")
    write_jsonl(test,  out / "test.jsonl")

    print(f"\n✅ Dataset ready: {n} total samples → {len(train)} train / {len(val)} val / {len(test)} test")
    print(f"   Output: {out.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", default="../../shared/pattern-library")
    parser.add_argument("--output-dir", default="../data/processed")
    parser.add_argument("--tasks", nargs="+", default=["generate", "review", "convert", "qa"])
    args = parser.parse_args()
    main(args.source_dir, args.output_dir, args.tasks)
