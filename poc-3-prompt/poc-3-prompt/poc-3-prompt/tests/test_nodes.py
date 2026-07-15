"""Unit tests for POC 3 chain nodes."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from chains.automation_chain import (
    load_system_prompt, load_few_shots, load_prompt_node,
    validate_output_node, should_retry, AutomationState
)


class TestPromptLoading:
    """Test system prompt and few-shot loading."""

    def test_load_system_prompt_base(self):
        """Base prompt should contain automation principles."""
        prompt = load_system_prompt("playwright", "generate")
        assert "Page Object Model" in prompt
        assert "AAA Structure" in prompt
        assert "explicit waits" in prompt

    def test_load_system_prompt_framework_specific(self):
        """Framework-specific prompts should augment base."""
        prompt_pw = load_system_prompt("playwright", "generate")
        prompt_se = load_system_prompt("selenium", "generate")
        # Both should have base + framework specific content
        assert len(prompt_pw) > 0
        assert len(prompt_se) > 0

    def test_load_few_shots_playwright_generate(self):
        """Few-shots should load from JSON files."""
        shots = load_few_shots("playwright", "generate")
        assert isinstance(shots, list)
        if shots:  # If file exists
            assert all("input" in s and "output" in s for s in shots)


class TestLoadPromptNode:
    """Test prompt construction node."""

    def test_generate_task_constructs_message(self, sample_state):
        """Generate task should construct appropriate user message."""
        sample_state["task"] = "generate"
        sample_state["description"] = "Login test"
        result = load_prompt_node(sample_state)

        assert "system_prompt" in result
        assert "user_message" in result
        assert "Login test" in result["user_message"]
        assert "Generate" in result["user_message"]

    def test_review_task_includes_code(self, sample_state):
        """Review task should include source code in message."""
        sample_state["task"] = "review"
        sample_state["source_code"] = "test('example', () => {})"
        result = load_prompt_node(sample_state)

        assert "test('example'" in result["user_message"]
        assert "Review" in result["user_message"]

    def test_convert_task_includes_source_framework(self, sample_state):
        """Convert task should name source framework."""
        sample_state["task"] = "convert"
        sample_state["source_framework"] = "playwright"
        sample_state["framework"] = "selenium"
        sample_state["source_code"] = "test code"
        result = load_prompt_node(sample_state)

        assert "playwright" in result["user_message"]
        assert "selenium" in result["user_message"]


class TestValidateOutput:
    """Test output validation node."""

    def test_playwright_marker_detection(self, sample_state):
        """Should detect Playwright-specific markers."""
        sample_state["framework"] = "playwright"
        sample_state["raw_output"] = "test('example', async ({page}) => { expect(page).toHaveURL('/'); })"
        result = validate_output_node(sample_state)

        assert result["validated_output"] != ""
        assert result["confidence"] == "high"

    def test_selenium_marker_detection(self, sample_state):
        """Should detect Selenium markers."""
        sample_state["framework"] = "selenium"
        sample_state["raw_output"] = "@Test public void testLogin() { WebDriver driver; driver.findElement(By.id(\"email\")); }"
        result = validate_output_node(sample_state)

        assert result["validated_output"] != ""
        assert result["confidence"] == "high"

    def test_restassured_marker_detection(self, sample_state):
        """Should detect RestAssured markers."""
        sample_state["framework"] = "restassured"
        sample_state["raw_output"] = "given().when().get('/users').then().statusCode(200);"
        result = validate_output_node(sample_state)

        assert result["validated_output"] != ""

    def test_invalid_output_triggers_retry(self, sample_state):
        """Invalid output should signal retry."""
        sample_state["framework"] = "playwright"
        sample_state["raw_output"] = "This is not valid Playwright code"
        sample_state["retry_count"] = 0
        result = validate_output_node(sample_state)

        assert result["retry_count"] == 1
        assert result["confidence"] == "low"

    def test_max_retries_caps_at_2(self, sample_state):
        """Should stop retrying after 2 attempts."""
        sample_state["framework"] = "playwright"
        sample_state["raw_output"] = "invalid"
        sample_state["retry_count"] = 2
        result = validate_output_node(sample_state)

        assert result["validated_output"] == "invalid"  # Accept low-quality output
        assert result["confidence"] == "low"

    def test_qa_task_always_valid(self, sample_state):
        """Q&A responses should always be valid."""
        sample_state["task"] = "qa"
        sample_state["raw_output"] = "Page Object Model is a pattern where..."
        result = validate_output_node(sample_state)

        assert result["confidence"] == "high"


class TestShouldRetry:
    """Test retry logic."""

    def test_valid_output_ends(self, sample_state):
        """Valid output should route to end (or HITL if enabled)."""
        sample_state["validated_output"] = "valid code"
        sample_state["hitl_enabled"] = False
        result = should_retry(sample_state)

        assert result == "end"

    def test_valid_with_hitl_routes_to_hitl(self, sample_state):
        """Valid output with HITL enabled should route to HITL."""
        sample_state["validated_output"] = "valid code"
        sample_state["hitl_enabled"] = True
        result = should_retry(sample_state)

        assert result == "hitl"

    def test_invalid_triggers_retry(self, sample_state):
        """Invalid output should trigger retry."""
        sample_state["validated_output"] = ""
        result = should_retry(sample_state)

        assert result == "retry"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_description_generates_message(self, sample_state):
        """Should handle empty descriptions gracefully."""
        sample_state["task"] = "generate"
        sample_state["description"] = ""
        result = load_prompt_node(sample_state)

        assert "user_message" in result
        assert len(result["user_message"]) > 0

    def test_multiline_code_validation(self, sample_state):
        """Should validate multiline code."""
        sample_state["framework"] = "playwright"
        code = """
test('example', async ({page}) => {
  await page.goto('/');
  await expect(page).toHaveURL('/');
});
"""
        sample_state["raw_output"] = code
        result = validate_output_node(sample_state)

        assert result["confidence"] == "high"
