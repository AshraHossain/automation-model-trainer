"""
evaluate_all.py
---------------
Runs all 7 golden test cases against all three POCs and produces a
comparison table. Uses LLM-as-Judge from the AeroSense ChartQA pipeline.

Usage:
    python shared/utils/evaluate_all.py
    python shared/utils/evaluate_all.py --pocs rag prompt   # skip finetune
    python shared/utils/evaluate_all.py --output results.md
"""

import os
import json
import asyncio
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

TEST_CASES_PATH = Path(__file__).parent.parent / "test-cases" / "golden_test_cases.json"

# ── Runners ────────────────────────────────────────────────────────────────────

async def run_poc2_rag(test_case: dict) -> Optional[str]:
    """Call POC 2 RAG API (must be running on :8000)."""
    import httpx
    task = test_case["task"]
    framework = test_case["framework"]
    inp = test_case["input"]

    url = f"http://localhost:8000/{task}"
    payload = {"framework": framework}

    if task == "generate":
        payload["description"] = inp["description"]
        payload["language"] = test_case.get("language", "typescript")
    elif task == "review":
        payload["code"] = inp["code"]
    elif task == "convert":
        payload["code"] = inp["source_code"]
        payload["source_framework"] = inp["source_framework"]
        payload["target_framework"] = inp["target_framework"] if "target_framework" in inp else framework
    elif task == "qa":
        url = "http://localhost:8000/ask"
        payload["question"] = inp["question"]

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            return resp.json().get("result")
    except Exception as e:
        return f"ERROR: {e}"


async def run_poc3_prompt(test_case: dict) -> Optional[str]:
    """Run POC 3 LangGraph chain."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "poc-3-prompt"))
    from chains.automation_chain import AutomationChain

    chain = AutomationChain(hitl=False)
    task = test_case["task"]
    framework = test_case["framework"]
    inp = test_case["input"]

    kwargs = {}
    if task == "generate":
        kwargs["description"] = inp.get("description")
    elif task == "review":
        kwargs["source_code"] = inp.get("code")
    elif task == "convert":
        kwargs["source_code"] = inp.get("source_code")
        kwargs["source_framework"] = inp.get("source_framework")
    elif task == "qa":
        kwargs["question"] = inp.get("question")

    try:
        result = await chain.run(task=task, framework=framework, **kwargs)
        return result["output"]
    except Exception as e:
        return f"ERROR: {e}"


async def run_poc1_finetune(test_case: dict) -> Optional[str]:
    """Run POC 1 fine-tuned model via Ollama (model must be exported first)."""
    import httpx
    task = test_case["task"]
    framework = test_case["framework"]
    inp = test_case["input"]

    prompt_map = {
        "generate": f"### Instruction:\nGenerate a {framework} test for: {inp.get('description', '')}\n\n### Input:\n\n### Response:\n",
        "review":   f"### Instruction:\nReview this {framework} test and identify issues.\n\n### Input:\n{inp.get('code', '')}\n\n### Response:\n",
        "convert":  f"### Instruction:\nConvert this {inp.get('source_framework')} test to {framework}.\n\n### Input:\n{inp.get('source_code', '')}\n\n### Response:\n",
        "qa":       f"### Instruction:\n{inp.get('question', '')}\n\n### Input:\n\n### Response:\n",
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post("http://localhost:11434/api/generate", json={
                "model": "automation-expert",  # your Ollama model name
                "prompt": prompt_map[task],
                "stream": False,
            })
            return resp.json().get("response")
    except Exception as e:
        return f"ERROR (model not loaded?): {e}"


# ── Judge ──────────────────────────────────────────────────────────────────────

def judge_output(output: str, test_case: dict) -> dict:
    """
    Heuristic judge — checks for expected markers.
    For full LLM-as-Judge, see poc-3-prompt/evaluations/llm_judge.py
    """
    if not output or output.startswith("ERROR"):
        return {"score": 0, "passed_checks": 0, "total_checks": 1, "error": output}

    markers = test_case.get("expected_markers", [])
    passed = sum(1 for m in markers if m in output)

    return {
        "score": round(passed / len(markers), 2) if markers else 0.5,
        "passed_checks": passed,
        "total_checks": len(markers),
        "error": None,
    }


# ── Main ───────────────────────────────────────────────────────────────────────

async def main(pocs: list[str], output_path: Optional[str]):
    test_cases = json.loads(TEST_CASES_PATH.read_text())
    print(f"📋 Running {len(test_cases)} test cases across POCs: {pocs}\n")

    rows = []
    for tc in test_cases:
        row = {
            "id": tc["id"],
            "task": tc["task"],
            "framework": tc["framework"],
        }

        if "finetune" in pocs:
            out = await run_poc1_finetune(tc)
            row["poc1_finetune"] = judge_output(out, tc)

        if "rag" in pocs:
            out = await run_poc2_rag(tc)
            row["poc2_rag"] = judge_output(out, tc)

        if "prompt" in pocs:
            out = await run_poc3_prompt(tc)
            row["poc3_prompt"] = judge_output(out, tc)

        rows.append(row)
        status = " | ".join([
            f"POC{i+1}:{row.get(k, {}).get('score', 'N/A')}"
            for i, k in enumerate(["poc1_finetune", "poc2_rag", "poc3_prompt"])
            if k in row
        ])
        print(f"  {tc['id']:20s}  {status}")

    # Summary table
    lines = [
        f"\n# Evaluation Results — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Test ID | Task | Framework | POC1 Fine-tune | POC2 RAG | POC3 Prompt |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        cols = [
            row["id"],
            row["task"],
            row["framework"],
            str(row.get("poc1_finetune", {}).get("score", "—")),
            str(row.get("poc2_rag", {}).get("score", "—")),
            str(row.get("poc3_prompt", {}).get("score", "—")),
        ]
        lines.append("| " + " | ".join(cols) + " |")

    # Averages
    for key, label in [("poc1_finetune", "POC1"), ("poc2_rag", "POC2"), ("poc3_prompt", "POC3")]:
        scores = [r[key]["score"] for r in rows if key in r and r[key]["error"] is None]
        if scores:
            print(f"\n  {label} average: {sum(scores)/len(scores):.2f}")

    table = "\n".join(lines)
    print(table)

    if output_path:
        Path(output_path).write_text(table)
        print(f"\n📄 Results saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pocs", nargs="+", default=["rag", "prompt"], choices=["finetune", "rag", "prompt"])
    parser.add_argument("--output", default=None, help="Save Markdown table to file")
    args = parser.parse_args()
    asyncio.run(main(args.pocs, args.output))
