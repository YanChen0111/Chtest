from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path("docs/fixtures/23-knowledge-feedback-review-gate-golden.md")
SLICE_PATH = Path(
    "docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")

EXPECTED_SURFACES = [
    "KnowledgeFeedbackDraft",
    "approve_feedback",
    "reject_feedback",
    "request_revision",
    "mark_prompt_eligible",
    "create_knowledge_card_candidate",
    "ReviewHistory",
    "feedback review artifact",
    "prompt eligibility",
    "TestKnowledgeCard",
]

REQUIRED_TERMS = [
    "human review",
    "ReviewHistory",
    "feedback review artifact",
    "prompt eligibility",
    "prompt eligibility reason",
    "TestKnowledgeCard handoff",
    "unsupported claims",
    "safe_to_show evidence",
    "reviewed source citations",
    "ReviewHistory id",
    "evidence artifact ids",
]

FORBIDDEN_SIDE_EFFECTS = [
    "feedback review runtime API",
    "frontend review page",
    "TestKnowledgeCard CRUD",
    "TestKnowledgeCard auto-creation",
    "prompt-eligible auto-marking",
    "automatic prompt eligibility",
    "automatic knowledge ingestion",
    "historical ReviewHistory mutation",
    "FailureAnalysis mutation",
    "Report mutation",
    "TestRun mutation",
    "TestResult mutation",
    "TestCase mutation",
    "GeneratedCaseCandidate mutation",
    "Artifact mutation",
    "provider call",
    "vector index",
    "embedding",
    "reranking",
    "graph job",
    "MCP runtime",
    "review bypass",
    "generated-case auto-approval",
    "TestCase auto-promotion",
    "runner behavior change",
    "report generation behavior change",
    "RBAC",
    "tenants",
    "permissions",
]


def test_golden_knowledge_feedback_review_gate_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_knowledge_feedback_review_gate_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_knowledge_feedback_review_gate_forbids_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()
    state_contract = _read(STATE_CONTRACT_PATH)
    api_contract = _read(API_CONTRACT_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(slice_plan, "No feedback review runtime API")
    _assert_normalized_contains(contracts, "must not add a runtime review API")
    _assert_normalized_contains(contracts, "must not create TestKnowledgeCard rows")
    _assert_normalized_contains(api_contract, "must not be inferred from model confidence")
    _assert_normalized_contains(state_contract, "human review actions")
    _assert_normalized_contains(state_contract, "Invalid transitions and validation failures")


def _alias(term: str) -> str:
    aliases = {
        "create_knowledge_card_candidate": "TestKnowledgeCard handoff",
        "feedback review artifact": "feedback review artifact",
        "TestKnowledgeCard handoff": "handoff payload",
        "safe_to_show evidence": "safe-to-show evidence",
        "ReviewHistory id": "ReviewHistory id",
        "evidence artifact ids": "evidence artifact ids",
    }
    return aliases.get(term, term)


def _assert_any_contains(texts: list[str], expected: str) -> None:
    if any(_normalized_contains(text, expected) for text in texts):
        return
    raise AssertionError(expected)


def _assert_normalized_contains(text: str, expected: str) -> None:
    assert _normalized_contains(text, expected), expected


def _normalized_contains(text: str, expected: str) -> bool:
    normalized_text = " ".join(text.split()).lower()
    normalized_expected = " ".join(expected.split()).lower()
    return normalized_expected in normalized_text


def _contracts_text() -> str:
    return "\n".join(
        _read(path)
        for path in [
            DATA_CONTRACT_PATH,
            API_CONTRACT_PATH,
            STATE_CONTRACT_PATH,
            ARTIFACT_CONTRACT_PATH,
        ]
    )


def _read(path: Path) -> str:
    assert path.exists(), f"{path} is missing"
    return path.read_text(encoding="utf-8")
