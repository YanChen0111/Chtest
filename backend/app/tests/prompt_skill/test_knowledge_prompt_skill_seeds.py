from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parents[4]
PROMPT_ROOT = ROOT / "prompts"
SKILL_ROOT = ROOT / "skills"

EXPECTED_PROMPTS = {
    "knowledge_card_extraction": "KnowledgeIngestionAgent",
    "evidence_case_generation": "CaseGenerationAgent",
    "evidence_case_review": "CaseReviewAgent",
    "automation_readiness": "AutomationReadinessAgent",
    "knowledge_feedback": "KnowledgeFeedbackAgent",
}

EXPECTED_SKILLS = {
    "knowledge-ingestion-skill": ["KnowledgeIngestionAgent"],
    "coverage-analysis-skill": ["CoverageAnalysisAgent"],
    "test-design-skill": ["TestDesignAgent"],
    "knowledge-feedback-skill": ["KnowledgeFeedbackAgent"],
}

PROMPT_REQUIRED_SECTIONS = [
    "Agent",
    "Purpose",
    "Input Schema",
    "Output Schema",
    "Instructions",
    "Failure Output",
]

SKILL_REQUIRED_SECTIONS = [
    "Applies To",
    "Methodology",
    "Input Contract",
    "Output Contract",
    "Quality Gates",
    "Forbidden Actions",
    "Tool Permissions",
]


def section_body(content: str, section: str) -> str:
    pattern = rf"^## {re.escape(section)}\s*(.*?)\n(?=## |\Z)"
    match = re.search(pattern, content, flags=re.MULTILINE | re.DOTALL)
    assert match is not None, f"missing section {section}"
    body = match.group(1).strip()
    assert body, f"empty section {section}"
    return body


def bullet_items(content: str, section: str) -> list[str]:
    body = section_body(content, section)
    return [line.removeprefix("- ").strip() for line in body.splitlines() if line.startswith("- ")]


def test_knowledge_driven_prompt_seeds_exist_and_follow_contract() -> None:
    for prompt_name, expected_agent in EXPECTED_PROMPTS.items():
        path = PROMPT_ROOT / prompt_name / "v1.md"
        assert path.is_file()

        content = path.read_text(encoding="utf-8")

        assert content.startswith(f"# Prompt: {prompt_name} v1")
        for section in PROMPT_REQUIRED_SECTIONS:
            assert section_body(content, section)
        assert section_body(content, "Agent") == expected_agent
        assert "KnowledgeEvidence" in content
        assert "used_knowledge_evidence_ids" in content
        assert "unsupported_claims" in content
        assert "Return JSON only" in content


def test_knowledge_driven_skill_seeds_exist_and_follow_contract() -> None:
    for skill_name, expected_agents in EXPECTED_SKILLS.items():
        path = SKILL_ROOT / skill_name / "v1.md"
        assert path.is_file()

        content = path.read_text(encoding="utf-8")

        assert content.startswith(f"# Skill: {skill_name} v1")
        for section in SKILL_REQUIRED_SECTIONS:
            assert section_body(content, section)
        assert bullet_items(content, "Applies To") == expected_agents
        assert "KnowledgeEvidence" in content
        assert "TestKnowledgeCard" in content
        assert "Quality Gates" in content
        assert "Forbidden Actions" in content


def test_knowledge_prompt_skill_seeds_keep_runtime_boundaries_explicit() -> None:
    files = [
        PROMPT_ROOT / prompt_name / "v1.md" for prompt_name in EXPECTED_PROMPTS
    ] + [
        SKILL_ROOT / skill_name / "v1.md" for skill_name in EXPECTED_SKILLS
    ]

    for path in files:
        content = path.read_text(encoding="utf-8")

        assert "Do not call external providers" in content
        assert "Do not create vector indexes" in content
        assert "Do not trigger MCP runtime" in content
        assert "Do not promote generated cases" in content
