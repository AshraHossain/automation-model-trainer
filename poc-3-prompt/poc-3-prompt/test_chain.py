#!/usr/bin/env python3
"""Quick test of POC 3 automation chain."""
import asyncio
import os
from chains.automation_chain import AutomationChain

async def test():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        print("   Set via: export ANTHROPIC_API_KEY=sk-ant-...")
        return

    print("✓ API key configured")
    print("🤖 Testing POC 3 chain...\n")

    chain = AutomationChain(hitl=False)

    # Test 1: Generate
    print("Test 1: Generate Playwright test")
    result = await chain.run(
        task="generate",
        framework="playwright",
        description="Login form with email, password, and submit button. After login, user should see dashboard."
    )
    print(f"Output (first 300 chars):\n{result['output'][:300]}...\n")

    # Test 2: Review
    print("Test 2: Review test code")
    result = await chain.run(
        task="review",
        framework="playwright",
        source_code="async function testLogin() { page.goto('/login'); page.fill('input[type=email]', 'test@ex.com'); page.fill('input[type=password]', 'pass'); page.click('button'); }"
    )
    print(f"Review (first 300 chars):\n{result['output'][:300]}...\n")

    print("✅ POC 3 chain working!")

if __name__ == "__main__":
    asyncio.run(test())
