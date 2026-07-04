from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path("docs/fixtures/28-test-knowledge-card-retrieval-boundary-golden.md")
SLICE_PATH = Path(
    "docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")

EXPECTED_SURFACES = [
    "TestKnowledgeCard Retrieval Boundary",
    "select_prompt_eligible_cards",
    "allowed_for_prompt",
    "prompt_eligible",
    "safe_to_show",
    "redaction",
    "source evidence",
    "source manifest",
    "ReviewHistory",
    "prompt eligibility artifact",
    "retrieval evidence",
    "excluded_card_reason",
    "failure behavior",
]

REQUIRED_TERMS = [
    "selection inputs",
    "retrieval_boundary_action",
    "project_id",
    "prompt_request_id",
    "reviewed TestKnowledgeCard id",
    "candidate_test_knowledge_card_ids",
    "allowed_for_prompt=true",
    "allowed_for_prompt=false",
    "prompt_eligible",
    "prompt eligibility artifact id",
    "test_knowledge_card_prompt_eligibility.json",
    "test_knowledge_card_retrieval_boundary.json",
    "artifact_type=test_knowledge_card_retrieval_boundary",
    "creation artifact id",
    "reviewed_test_knowledge_card_creation.json",
    "source_manifest",
    "same-project source Artifact",
    "source_artifact_ids",
    "source_quote_or_hash",
    "source span",
    "redaction report artifact id",
    "safe_to_show=true",
    "redaction status reviewed",
    "ReviewHistory id",
    "unsupported claims",
    "selection reason",
    "selected_test_knowledge_card_ids",
    "excluded TestKnowledgeCard ids",
    "excluded_cards",
    "retrieval_evidence_artifact_id",
    "bounded snippet or source hash",
    "necessary but not sufficient",
    "prompt_eligibility_denied",
    "prompt_eligibility_revision_requested",
    "prompt_eligibility_revoked",
    "source manifest mismatch",
    "missing prompt eligibility artifact evidence",
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
    "card table change",
    "list/update/delete API",
    "prompt runtime retrieval implementation",
    "prompt runtime retrieval change",
    "deterministic retrieval behavior change",
    "deterministic retrieval ranking change",
    "vector index",
    "vector database",
    "embedding",
    "embeddings",
    "reranking",
    "background indexing",
    "graph job",
    "GraphRAG job",
    "MCP runtime",
    "provider call",
    "provider SDK",
    "credentials",
    "OAuth",
    "remote URL fetch",
    "queue",
    "scheduler",
    "background worker",
    "artifact upload",
    "Artifact mutation",
    "artifact delete",
    "source artifact mutation",
    "prompt eligibility artifact mutation",
    "historical evidence mutation",
    "historical ReviewHistory mutation",
    "FailureAnalysis mutation",
    "Report mutation",
    "TestRun mutation",
    "TestResult mutation",
    "TestCase mutation",
    "GeneratedCaseCandidate mutation",
    "KnowledgeEvidence mutation",
    "existing TestKnowledgeCard content mutation",
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
    "package upgrades",
]


def test_golden_test_knowledge_card_retrieval_boundary_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_test_knowledge_card_retrieval_boundary_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_test_knowledge_card_retrieval_boundary_forbids_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()
    data_contract = _read(DATA_CONTRACT_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)
    artifact_contract = _read(ARTIFACT_CONTRACT_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(slice_plan, "No prompt runtime retrieval implementation")
    _assert_normalized_contains(data_contract, "allowed_for_prompt=true")
    _assert_normalized_contains(data_contract, "necessary but not sufficient")
    _assert_normalized_contains(api_contract, "does not add an endpoint")
    _assert_normalized_contains(api_contract, "must not add prompt runtime retrieval")
    _assert_normalized_contains(state_contract, "retrieval_excluded")
    _assert_normalized_contains(
        state_contract, "Retrieval-excluded states record"
    )
    _assert_normalized_contains(
        artifact_contract, "artifact_type=test_knowledge_card_retrieval_boundary"
    )
    _assert_normalized_contains(contracts, "excluded_card_reason")
    _assert_normalized_contains(contracts, "safe_to_show=true")
    _assert_normalized_contains(contracts, "prompt eligibility artifact evidence")


def _alias(term: str) -> str:
    aliases = {
        "prompt eligibility artifact": "prompt eligibility artifact evidence",
        "failure behavior": "failure behavior",
        "selection inputs": "Selection input",
        "reviewed TestKnowledgeCard id": "reviewed TestKnowledgeCard id",
        "candidate_test_knowledge_card_ids": "candidate TestKnowledgeCard ids",
        "test_knowledge_card_prompt_eligibility.json": (
            "test_knowledge_card_prompt_eligibility.json"
        ),
        "test_knowledge_card_retrieval_boundary.json": (
            "test_knowledge_card_retrieval_boundary.json"
        ),
        "artifact_type=test_knowledge_card_retrieval_boundary": (
            "artifact_type=test_knowledge_card_retrieval_boundary"
        ),
        "reviewed_test_knowledge_card_creation.json": (
            "reviewed_test_knowledge_card_creation.json"
        ),
        "same-project source Artifact": "same-project source artifact",
        "redaction status reviewed": "reviewed redaction status",
        "selected_test_knowledge_card_ids": "selected TestKnowledgeCard ids",
        "retrieval_evidence_artifact_id": "retrieval_evidence_artifact_id",
        "necessary but not sufficient": "necessary but not sufficient",
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
