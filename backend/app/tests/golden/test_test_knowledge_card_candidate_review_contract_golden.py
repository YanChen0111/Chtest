from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path("docs/fixtures/25-test-knowledge-card-candidate-review-golden.md")
SLICE_PATH = Path(
    "docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")

EXPECTED_SURFACES = [
    "TestKnowledgeCard Candidate Review",
    "TestKnowledgeCard handoff",
    "TestKnowledgeCard handoff candidate",
    "TestKnowledgeCard candidate",
    "candidate review",
    "approve_candidate_for_creation",
    "reject_candidate",
    "request_candidate_revision",
    "flag_duplicate",
    "request_merge_review",
    "defer_prompt_eligibility",
    "ReviewHistory",
    "artifact evidence",
    "duplicate/merge handling",
    "prompt eligibility",
]

REQUIRED_TERMS = [
    "human review",
    "ReviewHistory id",
    "candidate review artifact",
    "evidence_artifact_ids",
    "source evidence",
    "same-project source Artifact",
    "reviewed source citations",
    "source_quote_or_hash",
    "unsupported claims",
    "safe_to_show",
    "allowed_for_prompt=false",
    "review_required=true",
    "duplicate_knowledge_card_ids",
    "duplicate candidates",
    "merge_hint",
    "merge recommendation",
    "duplicate review required",
    "merge review required",
    "prompt eligibility remains separate",
    "test_knowledge_card_handoff.json",
    "test_knowledge_card_candidate_review.json",
    "artifact_type=test_knowledge_card_candidate_review",
    "prompt_eligibility_decision=deferred",
]

FORBIDDEN_SIDE_EFFECTS = [
    "TestKnowledgeCard CRUD",
    "TestKnowledgeCard auto-creation",
    "automatic card creation",
    "automatic card approval",
    "automatic prompt eligibility",
    "allowed_for_prompt=true auto-marking",
    "automatic knowledge ingestion",
    "KnowledgeIngestionAgent runtime",
    "backend feature API",
    "frontend review page",
    "migration",
    "historical ReviewHistory mutation",
    "FailureAnalysis mutation",
    "Report mutation",
    "TestRun mutation",
    "TestResult mutation",
    "TestCase mutation",
    "GeneratedCaseCandidate mutation",
    "KnowledgeEvidence mutation",
    "Artifact mutation",
    "provider call",
    "vector index",
    "embedding",
    "reranking",
    "graph job",
    "MCP runtime",
    "review bypass",
    "automatic merge",
    "automatic archive",
    "automatic replace",
    "automatic relabel",
    "automatic delete",
    "generated-case auto-approval",
    "TestCase auto-promotion",
    "runner behavior change",
    "report generation behavior change",
    "remote CI provider behavior",
    "RBAC",
    "tenants",
    "permissions",
]


def test_golden_test_knowledge_card_candidate_review_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_test_knowledge_card_candidate_review_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_test_knowledge_card_candidate_review_forbids_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()
    data_contract = _read(DATA_CONTRACT_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)
    artifact_contract = _read(ARTIFACT_CONTRACT_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(slice_plan, "No TestKnowledgeCard CRUD")
    _assert_normalized_contains(data_contract, "allowed_for_prompt=false")
    _assert_normalized_contains(api_contract, "does not add an endpoint")
    _assert_normalized_contains(api_contract, "test_knowledge_card_id: null")
    _assert_normalized_contains(state_contract, "human reviewer actions")
    _assert_normalized_contains(state_contract, "candidate review")
    _assert_normalized_contains(
        artifact_contract, "artifact_type=test_knowledge_card_candidate_review"
    )
    _assert_normalized_contains(
        contracts, "merge, archive, replace, delete, relabel, or create"
    )


def _alias(term: str) -> str:
    aliases = {
        "TestKnowledgeCard handoff candidate": "TestKnowledgeCard handoff",
        "TestKnowledgeCard candidate": "handoff candidate",
        "artifact evidence": "candidate review artifact",
        "duplicate/merge handling": "duplicate/merge",
        "same-project source Artifact": "same-project source artifacts",
        "reviewed source citations": "reviewed source",
        "duplicate candidates": "duplicate_knowledge_card_ids",
        "merge recommendation": "merge_hint",
        "duplicate review required": "duplicate_review_required",
        "merge review required": "merge_review_required",
        "prompt eligibility remains separate": "prompt eligibility separation",
        "test_knowledge_card_handoff.json": "test_knowledge_card_handoff.json",
        "test_knowledge_card_candidate_review.json": (
            "test_knowledge_card_candidate_review.json"
        ),
        "artifact_type=test_knowledge_card_candidate_review": (
            "artifact_type=test_knowledge_card_candidate_review"
        ),
        "prompt_eligibility_decision=deferred": (
            "prompt_eligibility_decision=deferred"
        ),
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
