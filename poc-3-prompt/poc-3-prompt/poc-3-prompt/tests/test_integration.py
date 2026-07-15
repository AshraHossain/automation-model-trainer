"""Integration tests for POC 3 chain."""
import pytest
import asyncio
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from chains.automation_chain import AutomationChain, AutomationState


@pytest.mark.asyncio
async def test_chain_generate_flow(mock_anthropic_client):
    """Test complete generate flow."""
    chain = AutomationChain(hitl=False)

    result = await chain.run(
        task="generate",
        framework="playwright",
        description="Login test"
    )

    assert "output" in result
    assert "confidence" in result
    assert len(result["output"]) > 0


@pytest.mark.asyncio
async def test_chain_review_flow(mock_anthropic_client):
    """Test complete review flow."""
    chain = AutomationChain(hitl=False)

    result = await chain.run(
        task="review",
        framework="playwright",
        source_code="test('example', () => {})"
    )

    assert "output" in result
    assert len(result["output"]) > 0


@pytest.mark.asyncio
async def test_chain_convert_flow(mock_anthropic_client):
    """Test complete convert flow."""
    chain = AutomationChain(hitl=False)

    result = await chain.run(
        task="convert",
        framework="selenium",
        source_framework="playwright",
        source_code="test code here"
    )

    assert "output" in result


def test_chain_initialization():
    """Chain should initialize with/without HITL."""
    chain_no_hitl = AutomationChain(hitl=False)
    chain_with_hitl = AutomationChain(hitl=True)

    assert chain_no_hitl.graph is not None
    assert chain_with_hitl.graph is not None
