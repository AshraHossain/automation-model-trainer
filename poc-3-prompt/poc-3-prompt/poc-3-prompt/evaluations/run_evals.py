#!/usr/bin/env python3
"""POC 3 Evaluation Runner — test generation quality on golden test cases."""
import asyncio
import json
from pathlib import Path
from typing import Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from chains.automation_chain import AutomationChain
from llm_judge import judge_test_output


GOLDEN_CASES_PATH = Path(__file__).parent.parent.parent / "shared" / "test-cases" / "golden_test_cases.json"
RESULTS_PATH = Path(__file__).parent / "results.json"


async def run_evaluation(
    test_cases_path: Optional[Path] = None,
    limit: Optional[int] = None,
    verbose: bool = False
) -> dict:
    """Run POC 3 on golden test cases and score outputs."""
    test_cases_path = test_cases_path or GOLDEN_CASES_PATH

    if not test_cases_path.exists():
        print(f"❌ Test cases not found at {test_cases_path}")
        print("   Expected: shared/test-cases/golden_test_cases.json")
        return {}

    with open(test_cases_path) as f:
        test_cases = json.load(f)

    if limit:
        test_cases = test_cases[:limit]

    print(f"📊 POC 3 Evaluation")
    print(f"   Test cases: {len(test_cases)}")
    print(f"   Path: {test_cases_path}\n")

    chain = AutomationChain(hitl=False)
    results = {
        "metadata": {
            "total": len(test_cases),
            "model": "claude-sonnet-4-20250514",
            "timestamp": str(Path.ctime(RESULTS_PATH) if RESULTS_PATH.exists() else ""),
        },
        "results": [],
        "summary": {}
    }

    for i, case in enumerate(test_cases):
        task = case.get("task", "generate")
        framework = case.get("framework", "playwright")
        description = case.get("description", "")

        if verbose:
            print(f"[{i+1}/{len(test_cases)}] {framework} / {task}: {description[:50]}...")

        # Generate
        try:
            gen_result = await chain.run(
                task=task,
                framework=framework,
                description=description if task == "generate" else None,
                source_code=case.get("source_code") if task in ("review", "convert") else None,
                source_framework=case.get("source_framework") if task == "convert" else None,
            )
            generated = gen_result["output"]
        except Exception as e:
            if verbose:
                print(f"   ❌ Generation failed: {e}")
            results["results"].append({
                "case": case,
                "generated": "",
                "score": {"overall": 0, "issues": [str(e)]},
            })
            continue

        # Judge
        score = await judge_test_output(generated, task, framework, description)

        results["results"].append({
            "case": case,
            "generated": generated[:300] if len(generated) > 300 else generated,
            "score": score,
        })

        if verbose:
            print(f"   ✓ Score: {score['overall']}/100 ({score.get('issues', [])})")

    # Summary
    scores = [r["score"]["overall"] for r in results["results"]]
    results["summary"] = {
        "mean_score": sum(scores) / len(scores) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "passed": len([s for s in scores if s >= 70]),
    }

    # Save
    Path(__file__).parent.mkdir(exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    return results


def print_summary(results: dict):
    """Print evaluation summary."""
    if not results.get("results"):
        print("No results to display")
        return

    summary = results["summary"]
    print("\n" + "="*60)
    print("📈 EVALUATION SUMMARY")
    print("="*60)
    print(f"Mean Score:  {summary['mean_score']:.1f}/100")
    print(f"Range:       {summary['min_score']} — {summary['max_score']}")
    print(f"Passed (≥70): {summary['passed']}/{summary.get('total', len(results['results']))}")
    print(f"Results:     {RESULTS_PATH}")
    print("="*60)

    # By framework
    by_framework = {}
    for r in results["results"]:
        fw = r["case"].get("framework", "unknown")
        if fw not in by_framework:
            by_framework[fw] = []
        by_framework[fw].append(r["score"]["overall"])

    print("\nBy Framework:")
    for fw, scores in sorted(by_framework.items()):
        avg = sum(scores) / len(scores)
        print(f"  {fw:15} {avg:6.1f}/100 (n={len(scores)})")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="POC 3 Evaluation Runner")
    parser.add_argument("--test-cases", type=Path, help="Path to test cases JSON")
    parser.add_argument("--limit", type=int, help="Limit number of test cases")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    results = await run_evaluation(
        test_cases_path=args.test_cases,
        limit=args.limit,
        verbose=args.verbose
    )
    print_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
