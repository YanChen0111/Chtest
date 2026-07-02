from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path("docs/fixtures/20-agent-workflow-contract-golden.md")
SLICE_PATH = Path("docs/implementation/slices/slice-32-agent-workflow-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")

EXPECTED_AGENTS = [
    "RequirementUnderstandingAgent",
    "RiskAnalysisAgent",
    "CoverageAnalysisAgent",
    "TestDesignAgent",
    "CaseGenerationAgent",
    "CaseReviewAgent",
    "DedupAgent",
    "AutomationReadinessAgent",
]

REQUIRED_STEP_FIELDS = [
    "PromptVersion",
    "SkillVersion",
    "Input evidence",
    "Output contract",
    "Write permission",
    "Human gate",
    "Failure behavior",
    "Trace requirement",
]

CONTRACT_FIELD_ALIASES = {
    "PromptVersion": ["PromptVersion", "prompt_version", "prompt/skill versions"],
    "SkillVersion": ["SkillVersion", "skill_version", "prompt/skill versions"],
    "Input evidence": ["Input evidence", "Inputs"],
    "Output contract": ["Output contract", "Outputs/artifacts"],
    "Write permission": ["Write permission"],
    "Human gate": ["Human gate"],
    "Failure behavior": ["Failure behavior", "failure behavior and fallback"],
    "Trace requirement": [
        "Trace requirement",
        "Required trace fields",
        "Trace fields",
        "future AITask trace",
        "trace refs",
        "traceability refs",
    ],
}

FORBIDDEN_RUNTIME_SIDE_EFFECTS = [
    "TestCase auto-promotion",
    "TestRun",
    "Report",
    "provider call",
    "vector index",
    "graph job",
    "MCP runtime",
    "Artifact mutation",
    "runtime orchestration",
    "remote CI provider behavior",
]


def test_golden_agent_workflow_contract_names_all_steps() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)
    prompt_skill_contract = _read(PROMPT_SKILL_CONTRACT_PATH)

    for agent in EXPECTED_AGENTS:
        assert agent in fixture
        assert agent in slice_plan
        assert agent in api_contract
        assert agent in state_contract
        assert agent in prompt_skill_contract


def test_golden_agent_workflow_contract_has_required_step_fields() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    prompt_skill_contract = _read(PROMPT_SKILL_CONTRACT_PATH)

    for field in REQUIRED_STEP_FIELDS:
        assert field in fixture
        _assert_any_alias(slice_plan, CONTRACT_FIELD_ALIASES[field], field)
        _assert_any_alias(api_contract, CONTRACT_FIELD_ALIASES[field], field)
        _assert_any_alias(prompt_skill_contract, CONTRACT_FIELD_ALIASES[field], field)


def test_golden_agent_workflow_contract_has_no_runtime_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)

    for side_effect in FORBIDDEN_RUNTIME_SIDE_EFFECTS:
        assert side_effect in fixture

    assert "GeneratedCaseCandidate remains review-gated" in fixture
    assert "GeneratedCaseCandidate may become TestCase only through the existing human" in api_contract
    _assert_normalized_contains(
        api_contract,
        "automatically promote, approve, reject, archive, merge, execute, or report",
    )
    _assert_normalized_contains(api_contract, "external provider calls, vector indexes")
    _assert_normalized_contains(api_contract, "graph extraction")
    _assert_normalized_contains(api_contract, "MCP runtime")
    _assert_normalized_contains(api_contract, "remote CI/CD provider behavior")
    _assert_normalized_contains(
        slice_plan,
        "No agent orchestration runtime, workflow engine, queue graph, scheduler",
    )
    assert "waiting_human_review" in state_contract
    assert "must not create AutomationDraft, ToolInvocation, or TestRun" in state_contract


def _assert_normalized_contains(text: str, expected: str) -> None:
    normalized_text = " ".join(text.split())
    normalized_expected = " ".join(expected.split())
    assert normalized_expected in normalized_text


def _assert_any_alias(text: str, aliases: list[str], field: str) -> None:
    normalized_text = text.lower()
    assert any(alias.lower() in normalized_text for alias in aliases), field


def _read(path: Path) -> str:
    assert path.exists(), f"{path} is missing"
    return path.read_text(encoding="utf-8")
