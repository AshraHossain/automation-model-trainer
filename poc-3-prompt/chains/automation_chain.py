"""
automation_chain.py
-------------------
LangGraph chain for automation test generation/review/conversion.
Architecture mirrors langgraph-hitl-agent with HITL checkpoint support.

Usage:
    python chains/automation_chain.py
    # → interactive CLI

    from chains.automation_chain import AutomationChain
    chain = AutomationChain()
    result = await chain.run(task="generate", framework="playwright", description="Login test")
"""

import os
import json
import asyncio
from pathlib import Path
from typing import TypedDict, Optional, Literal, Annotated

import anthropic
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# ── State ──────────────────────────────────────────────────────────────────────

Task = Literal["generate", "review", "convert", "qa"]
Framework = Literal["playwright", "selenium", "restassured", "postman", "testng"]

class AutomationState(TypedDict):
    # Input
    task: Task
    framework: Framework
    description: Optional[str]
    source_code: Optional[str]
    source_framework: Optional[Framework]
    error_message: Optional[str]
    question: Optional[str]

    # Prompt construction
    system_prompt: str
    few_shots: list[dict]
    user_message: str

    # Generation
    raw_output: str
    validated_output: str
    retry_count: int

    # HITL (from langgraph-hitl-agent pattern)
    hitl_enabled: bool
    human_feedback: Optional[str]
    human_approved: bool

    # Metadata
    context_sources: list[str]
    confidence: str


# ── Prompt Loader ──────────────────────────────────────────────────────────────

PROMPTS_DIR = Path(__file__).parent.parent / "system-prompts"
FEW_SHOTS_DIR = Path(__file__).parent.parent / "few-shots"

def load_system_prompt(framework: Framework, task: Task) -> str:
    base_path = PROMPTS_DIR / "base.md"
    framework_path = PROMPTS_DIR / f"{framework}.md"

    base = base_path.read_text() if base_path.exists() else DEFAULT_BASE_PROMPT
    framework_specific = framework_path.read_text() if framework_path.exists() else ""

    return f"{base}\n\n{framework_specific}".strip()


def load_few_shots(framework: Framework, task: Task) -> list[dict]:
    path = FEW_SHOTS_DIR / framework / f"{task}.json"
    if path.exists():
        return json.loads(path.read_text())
    return []


DEFAULT_BASE_PROMPT = """You are an expert software test automation engineer with deep knowledge of:
- Playwright (TypeScript/JavaScript) — Page Object Model, self-healing locators, fixtures
- Selenium WebDriver (Java) — TestNG integration, Page Factory, explicit waits
- RestAssured (Java) — API test chains, request specs, response validation
- Postman/Newman — Collection scripting, environment variables, test assertions
- TestNG (Java) — Suite XML, data providers, parallel execution, reporting

You generate production-quality test code that follows:
1. Page Object Model pattern for UI tests
2. AAA (Arrange-Act-Assert) structure
3. Descriptive test names using BDD-style naming
4. Proper error handling and wait strategies
5. Reusable helper methods and fixtures

When reviewing tests, identify: missing awaits, weak locators, hardcoded waits,
missing assertions, flaky patterns, and framework anti-patterns.

When converting between frameworks, preserve test intent, rename assertions
to target framework equivalents, and adapt locator strategies appropriately.
"""


# ── Nodes ──────────────────────────────────────────────────────────────────────

def load_prompt_node(state: AutomationState) -> AutomationState:
    """Load framework-specific system prompt and few-shots."""
    system_prompt = load_system_prompt(state["framework"], state["task"])
    few_shots = load_few_shots(state["framework"], state["task"])

    # Build user message based on task
    task = state["task"]
    if task == "generate":
        user_msg = f"Generate a {state['framework']} test for: {state['description']}"
        if state.get("source_framework"):
            user_msg += f"\nAdopt patterns from: {state['source_framework']}"
    elif task == "review":
        user_msg = f"Review this {state['framework']} test and identify issues:\n\n```\n{state['source_code']}\n```"
        if state.get("error_message"):
            user_msg += f"\n\nError observed: {state['error_message']}"
    elif task == "convert":
        user_msg = (
            f"Convert this {state['source_framework']} test to {state['framework']}:\n\n"
            f"```\n{state['source_code']}\n```"
        )
    else:  # qa
        user_msg = state.get("question", "")

    return {**state, "system_prompt": system_prompt, "few_shots": few_shots, "user_message": user_msg}


async def claude_generate_node(state: AutomationState) -> AutomationState:
    """Call Claude Sonnet API with the constructed prompt."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Build messages with few-shots
    messages = []
    for shot in state["few_shots"][:3]:  # cap at 3 examples
        messages.append({"role": "user",      "content": shot["input"]})
        messages.append({"role": "assistant", "content": shot["output"]})
    messages.append({"role": "user", "content": state["user_message"]})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=state["system_prompt"],
        messages=messages,
    )

    raw_output = response.content[0].text
    return {**state, "raw_output": raw_output}


def validate_output_node(state: AutomationState) -> AutomationState:
    """Basic validation: check output isn't empty and contains expected markers."""
    output = state["raw_output"]
    framework = state["framework"]
    retry_count = state.get("retry_count", 0)

    FRAMEWORK_MARKERS = {
        "playwright":   ["test(", "expect(", "page."],
        "selenium":     ["@Test", "WebDriver", "driver."],
        "restassured":  ["given()", "when()", "then()"],
        "postman":      ["pm.test", "pm.expect"],
        "testng":       ["@Test", "Assert."],
    }

    markers = FRAMEWORK_MARKERS.get(framework, [])
    is_valid = any(m in output for m in markers) or state["task"] in ("qa", "review")

    if is_valid or retry_count >= 2:
        return {**state, "validated_output": output, "confidence": "high" if is_valid else "low"}
    else:
        # Signal retry via retry_count increment
        return {**state, "retry_count": retry_count + 1}


def should_retry(state: AutomationState) -> str:
    """Conditional edge: retry generation or proceed."""
    if state.get("validated_output"):
        return "hitl" if state.get("hitl_enabled") else "end"
    return "retry"


def hitl_node(state: AutomationState) -> AutomationState:
    """
    Human-in-the-loop checkpoint — mirrors langgraph-hitl-agent pattern.
    In async/API mode this interrupts for human review.
    In CLI mode it prompts inline.
    """
    if not state.get("hitl_enabled"):
        return {**state, "human_approved": True}

    print("\n" + "="*60)
    print("🔍 HITL Review — Generated Output:")
    print("="*60)
    print(state["validated_output"])
    print("="*60)
    feedback = input("Approve? (y/n/edit): ").strip().lower()

    if feedback == "y":
        return {**state, "human_approved": True}
    elif feedback == "n":
        return {**state, "human_approved": False, "human_feedback": "Rejected"}
    else:
        edited = input("Paste corrected output (end with '###'):\n")
        return {**state, "validated_output": edited, "human_approved": True, "human_feedback": "Edited"}


# ── Graph ──────────────────────────────────────────────────────────────────────

def build_graph(hitl: bool = False) -> StateGraph:
    builder = StateGraph(AutomationState)

    builder.add_node("load_prompt",   load_prompt_node)
    builder.add_node("generate",      claude_generate_node)
    builder.add_node("validate",      validate_output_node)
    builder.add_node("hitl",          hitl_node)

    builder.add_edge(START,          "load_prompt")
    builder.add_edge("load_prompt",  "generate")
    builder.add_edge("generate",     "validate")
    builder.add_conditional_edges("validate", should_retry, {
        "retry": "generate",
        "hitl":  "hitl",
        "end":   END,
    })
    builder.add_edge("hitl", END)

    checkpointer = MemorySaver()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["hitl"] if hitl else [],
    )


class AutomationChain:
    def __init__(self, hitl: bool = False):
        self.graph = build_graph(hitl=hitl)

    async def run(self, task: Task, framework: Framework, **kwargs) -> dict:
        initial_state: AutomationState = {
            "task": task,
            "framework": framework,
            "description":     kwargs.get("description"),
            "source_code":     kwargs.get("source_code"),
            "source_framework": kwargs.get("source_framework"),
            "error_message":   kwargs.get("error"),
            "question":        kwargs.get("question"),
            "system_prompt":   "",
            "few_shots":       [],
            "user_message":    "",
            "raw_output":      "",
            "validated_output": "",
            "retry_count":     0,
            "hitl_enabled":    kwargs.get("hitl", False),
            "human_feedback":  None,
            "human_approved":  False,
            "context_sources": [],
            "confidence":      "medium",
        }
        config = {"configurable": {"thread_id": "poc3-session"}}
        result = await self.graph.ainvoke(initial_state, config=config)
        return {
            "output":   result.get("validated_output", result.get("raw_output", "")),
            "sources":  result.get("context_sources", []),
            "confidence": result.get("confidence", "medium"),
        }


# ── CLI ────────────────────────────────────────────────────────────────────────

async def cli():
    print("🤖 Automation Expert (POC 3 — Claude Sonnet + LangGraph)")
    print("Commands: generate | review | convert | ask | quit\n")

    chain = AutomationChain(hitl=False)

    while True:
        task = input("Task [generate/review/convert/ask]: ").strip().lower()
        if task == "quit":
            break
        framework = input("Framework [playwright/selenium/restassured/postman/testng]: ").strip().lower()

        kwargs = {}
        if task == "generate":
            kwargs["description"] = input("Describe the test: ").strip()
        elif task in ("review", "convert"):
            print("Paste your code (end with '###' on a new line):")
            lines = []
            while True:
                line = input()
                if line == "###":
                    break
                lines.append(line)
            kwargs["source_code"] = "\n".join(lines)
            if task == "convert":
                kwargs["source_framework"] = input("Source framework: ").strip()
        elif task == "ask":
            kwargs["question"] = input("Question: ").strip()

        print("\n⏳ Generating...")
        result = await chain.run(task=task, framework=framework, **kwargs)
        print(f"\n{'='*60}")
        print(result["output"])
        print(f"{'='*60}")
        print(f"Confidence: {result['confidence']}\n")


if __name__ == "__main__":
    asyncio.run(cli())
