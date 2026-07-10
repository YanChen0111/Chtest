from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parents[4]
SKILL_ROOT = ROOT / "skills"

EXPECTED_SKILLS = {
    "requirement-review-skill": ["RequirementReviewAgent"],
    "test-case-generation-skill": ["CaseGenerationAgent"],
    "testcase-review-skill": ["CaseReviewAgent"],
    "automation-plan-skill": ["AutomationPlanAgent"],
    "automation-draft-skill": ["AutomationDraftAgent"],
    "unit-test-generation-skill": ["UnitTestAgent"],
    "regression-selection-skill": ["CICDChangeAnalysisAgent", "RegressionAgent"],
    "tool-execution-skill": ["ToolExecutionAgent"],
    "failure-analysis-skill": ["FailureAnalysisAgent"],
    "report-generation-skill": ["ReportAgent"],
}

REQUIRED_SECTIONS = [
    "Applies To",
    "Methodology",
    "Input Contract",
    "Output Contract",
    "Quality Gates",
    "Forbidden Actions",
    "Tool Permissions",
]

FORBIDDEN_CONTENT_PATTERNS = [
    re.compile(r"sk-[a-z0-9]{12,}"),
    re.compile(r"api[_-]?key\s*[:=]"),
    re.compile(r"password\s*[:=]"),
    re.compile(r"secret\s*[:=]"),
    re.compile(r"customer[_-]?(id|name|email)\s*[:=]"),
]


def section_body(content: str, section: str) -> str:
    pattern = rf"^## {re.escape(section)}\s*(.*?)\n(?=## |\Z)"
    match = re.search(pattern, content, flags=re.MULTILINE | re.DOTALL)
    assert match is not None, f"missing section {section}"
    return match.group(1).strip()


def bullet_items(content: str, section: str) -> list[str]:
    body = section_body(content, section)
    return [line.removeprefix("- ").strip() for line in body.splitlines() if line.startswith("- ")]


def test_all_builtin_skill_files_exist() -> None:
    for skill_name in EXPECTED_SKILLS:
        assert (SKILL_ROOT / skill_name / "v1.md").is_file()


def test_skill_files_follow_contract_sections_and_agent_mapping() -> None:
    for skill_name, expected_agents in EXPECTED_SKILLS.items():
        content = (SKILL_ROOT / skill_name / "v1.md").read_text(encoding="utf-8")

        assert content.startswith(f"# Skill: {skill_name} v1")
        for section in REQUIRED_SECTIONS:
            assert section_body(content, section)

        assert bullet_items(content, "Applies To") == expected_agents


def test_skill_list_sections_are_non_empty() -> None:
    for skill_name in EXPECTED_SKILLS:
        content = (SKILL_ROOT / skill_name / "v1.md").read_text(encoding="utf-8")

        assert bullet_items(content, "Methodology")
        assert bullet_items(content, "Quality Gates")
        assert bullet_items(content, "Forbidden Actions")
        assert bullet_items(content, "Tool Permissions")


def test_skill_files_do_not_contain_secret_or_customer_placeholders() -> None:
    for skill_name in EXPECTED_SKILLS:
        content = (SKILL_ROOT / skill_name / "v1.md").read_text(encoding="utf-8").lower()

        for forbidden_pattern in FORBIDDEN_CONTENT_PATTERNS:
            assert forbidden_pattern.search(content) is None


def test_automation_plan_skill_quality_gates_require_evidence_and_approval_gate() -> None:
    content = (SKILL_ROOT / "automation-plan-skill" / "v1.md").read_text(encoding="utf-8")
    quality_gates = " ".join(bullet_items(content, "Quality Gates")).lower()
    forbidden_actions = " ".join(bullet_items(content, "Forbidden Actions")).lower()
    tool_permissions = " ".join(bullet_items(content, "Tool Permissions")).lower()

    assert "approved testcase" in quality_gates
    assert "requirement evidence" in quality_gates
    assert "requirement review evidence" in quality_gates
    assert "knowledge evidence" in quality_gates
    assert "approval before automationdraft or code generation" in quality_gates
    assert "arbitrary shell commands" in quality_gates
    assert "unapproved testcase" in forbidden_actions
    assert "execute arbitrary commands" in forbidden_actions
    assert "no execution tools" in tool_permissions
