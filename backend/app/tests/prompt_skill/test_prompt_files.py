from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).parents[4]
PROMPT_ROOT = ROOT / "prompts"

EXPECTED_PROMPTS = {
    "requirement_review": "RequirementReviewAgent",
    "risk_matrix": "RequirementReviewAgent",
    "case_generation": "CaseGenerationAgent",
    "case_review": "CaseReviewAgent",
    "automation_draft_generation": "AutomationDraftAgent",
    "cicd_change_analysis": "CICDChangeAnalysisAgent",
    "unit_test_generation": "UnitTestAgent",
    "regression_selection": "RegressionAgent",
    "tool_execution": "ToolExecutionAgent",
    "failure_analysis": "FailureAnalysisAgent",
    "report_generation": "ReportAgent",
}

REQUIRED_SECTIONS = [
    "Agent",
    "Purpose",
    "Input Schema",
    "Output Schema",
    "Instructions",
    "Failure Output",
]


def section_body(content: str, section: str) -> str:
    pattern = rf"^## {re.escape(section)}\s*(.*?)\n(?=## |\Z)"
    match = re.search(pattern, content, flags=re.MULTILINE | re.DOTALL)
    assert match is not None, f"missing section {section}"
    return match.group(1).strip()


def json_section(content: str, section: str) -> dict:
    body = section_body(content, section)
    match = re.search(r"```json\s*(.*?)\s*```", body, flags=re.DOTALL)
    assert match is not None, f"{section} must contain a json code block"
    parsed = json.loads(match.group(1))
    assert isinstance(parsed, dict), f"{section} must parse as a JSON object"
    return parsed


def test_all_builtin_prompt_files_exist() -> None:
    for prompt_name in EXPECTED_PROMPTS:
        assert (PROMPT_ROOT / prompt_name / "v1.md").is_file()


def test_prompt_files_follow_contract_sections_and_agent_mapping() -> None:
    for prompt_name, agent_name in EXPECTED_PROMPTS.items():
        content = (PROMPT_ROOT / prompt_name / "v1.md").read_text(encoding="utf-8")

        assert content.startswith(f"# Prompt: {prompt_name} v1")
        for section in REQUIRED_SECTIONS:
            assert f"## {section}" in content

        assert section_body(content, "Agent") == agent_name
        assert json_section(content, "Input Schema").get("type") == "object"
        assert json_section(content, "Output Schema").get("type") == "object"


def test_prompt_instructions_require_json_only_without_markdown_fences() -> None:
    for prompt_name in EXPECTED_PROMPTS:
        content = (PROMPT_ROOT / prompt_name / "v1.md").read_text(encoding="utf-8")
        instructions = section_body(content, "Instructions").lower()

        assert "json only" in instructions
        assert "do not include markdown fences" in instructions


def test_prompt_failure_outputs_are_json_objects() -> None:
    for prompt_name in EXPECTED_PROMPTS:
        content = (PROMPT_ROOT / prompt_name / "v1.md").read_text(encoding="utf-8")
        failure_output = json_section(content, "Failure Output")

        assert {"error_code", "message", "recoverable"}.issubset(failure_output)
