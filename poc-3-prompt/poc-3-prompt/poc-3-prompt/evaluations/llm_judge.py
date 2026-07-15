"""LLM-as-Judge for POC 3 evaluation (from AeroSense ChartQA pattern)."""
import os
import json
import anthropic

async def judge_test_output(
    generated_code: str,
    task: str,
    framework: str,
    description: str,
) -> dict:
    """Score generated test code using Claude as judge."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""You are a senior test automation QA engineer evaluating AI-generated test code.

Generated {framework} test for task: {task}
Description: {description}

Code to evaluate:
```
{generated_code}
```

Score this on:
1. **Syntax** (0-100): Is it syntactically valid? No obvious errors?
2. **Completeness** (0-100): Does it implement the full requirement?
3. **Best Practices** (0-100): Does it follow framework conventions? POM pattern? AAA structure?
4. **Robustness** (0-100): Proper waits? Good locators? Error handling?

Respond with JSON only (no markdown):
{{"syntax": N, "completeness": N, "best_practices": N, "robustness": N, "issues": ["issue1", "issue2"], "overall": N}}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        result["overall"] = (result["syntax"] + result["completeness"] + result["best_practices"] + result["robustness"]) // 4
        return result
    except json.JSONDecodeError:
        return {"syntax": 0, "completeness": 0, "best_practices": 0, "robustness": 0, "overall": 0, "issues": ["Failed to parse judge response"]}
