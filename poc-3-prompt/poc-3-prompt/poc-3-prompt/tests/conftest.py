"""Pytest fixtures for POC 3."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic API client."""
    with patch('anthropic.Anthropic') as mock:
        client = MagicMock()
        client.messages.create = MagicMock(return_value=MagicMock(
            content=[MagicMock(text='test("example", async ({page}) => { await page.goto("/"); })')]
        ))
        mock.return_value = client
        yield client


@pytest.fixture
def sample_state():
    """Sample automation state."""
    return {
        "task": "generate",
        "framework": "playwright",
        "description": "Login test",
        "source_code": None,
        "source_framework": None,
        "error_message": None,
        "question": None,
        "system_prompt": "",
        "few_shots": [],
        "user_message": "",
        "raw_output": "",
        "validated_output": "",
        "retry_count": 0,
        "hitl_enabled": False,
        "human_feedback": None,
        "human_approved": False,
        "context_sources": [],
        "confidence": "medium",
    }
