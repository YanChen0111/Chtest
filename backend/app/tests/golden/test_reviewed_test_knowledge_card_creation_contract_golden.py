from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path("docs/fixtures/26-reviewed-test-knowledge-card-creation-golden.md")
SLICE_PATH = Path(
    "docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")

EXPECTED_SURFACES = [
    "Reviewed TestKnowledgeCard Creation",
    "approved candidate review",
    "create_reviewed_test_knowledge_card",
    "candidate review artifact",
    "source manifest",
    "TestKnowledgeCard fields",
    "ReviewHistory",
    "duplicate/merge preconditions",
    "prompt eligibility",
]

REQUIRED_TERMS = [
    "approved candidate",
    "candidate_approved_for_future_creation",
    "candidate_card_json",
    "source_handoff_artifact_id",
    "source_feedback_id",
    "source evidence",
    "same-project source Artifact",
    "source_artifact_ids",
    "source_quote_or_hash",
    "source_manifest",
    "ReviewHistory id",
    "unsupported claims",
    "project_id",
    "knowledge_type",
    "summary",
    "source_type",
    "source_section",
    "related_requirement_ids",
    "related_risk_ids",
    "related_test_case_ids",
    "safe_to_show",
    "allowed_for_prompt=false",
    "evidence_artifact_ids",
    "reviewed_test_knowledge_card_creation.json",
    "artifact_type=reviewed_test_knowledge_card_creation",
    "creation_artifact_id",
    "duplicate_merge_preconditions",
    "prompt_eligibility_decision=deferred",
    "failure_code",
]

FORBIDDEN_SIDE_EFFECTS = [
    "broad TestKnowledgeCard CRUD",
    "TestKnowledgeCard CRUD",
    "TestKnowledgeCard auto-creation",
    "automatic card creation from model output",
    "automatic card creation",
    "automatic card approval",
    "automatic prompt eligibility",
    "allowed_for_prompt=true auto-marking",
    "automatic knowledge ingestion",
    "KnowledgeIngestionAgent runtime",
    "backend feature API",
    "frontend page",
    "migration",
    "list/update/delete API",
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


def test_golden_reviewed_test_knowledge_card_creation_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_reviewed_test_knowledge_card_creation_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_reviewed_test_knowledge_card_creation_forbids_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()
    data_contract = _read(DATA_CONTRACT_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)
    artifact_contract = _read(ARTIFACT_CONTRACT_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(slice_plan, "No broad TestKnowledgeCard CRUD")
    _assert_normalized_contains(data_contract, "allowed_for_prompt=false")
    _assert_normalized_contains(api_contract, "does not add an endpoint")
    _assert_normalized_contains(state_contract, "prompt_eligibility_deferred")
    _assert_normalized_contains(
        artifact_contract, "artifact_type=reviewed_test_knowledge_card_creation"
    )
    _assert_normalized_contains(contracts, "source manifest")
    _assert_normalized_contains(
        contracts, "must not automatically merge, archive, replace, delete"
    )


def _alias(term: str) -> str:
    aliases = {
        "approved candidate": "approved candidate review",
        "TestKnowledgeCard fields": "TestKnowledgeCard fields",
        "duplicate/merge preconditions": "duplicate/merge precondition",
        "same-project source Artifact": "same-project source artifacts",
        "source_manifest": "source manifest",
        "source_artifact_ids": "source_artifact_ids",
        "reviewed_test_knowledge_card_creation.json": (
            "reviewed_test_knowledge_card_creation.json"
        ),
        "artifact_type=reviewed_test_knowledge_card_creation": (
            "artifact_type=reviewed_test_knowledge_card_creation"
        ),
        "duplicate_merge_preconditions": "duplicate_merge_preconditions",
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
