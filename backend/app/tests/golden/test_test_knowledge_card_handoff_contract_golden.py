from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path("docs/fixtures/24-test-knowledge-card-handoff-golden.md")
SLICE_PATH = Path(
    "docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")

EXPECTED_SURFACES = [
    "TestKnowledgeCard handoff",
    "KnowledgeFeedbackDraft",
    "create_knowledge_card_candidate",
    "handoff payload",
    "handoff_payload_json",
    "TestKnowledgeCard candidate",
    "ReviewHistory",
    "feedback review artifact",
    "KnowledgeEvidence",
    "source Artifact",
    "safe_to_show",
    "allowed_for_prompt",
]

REQUIRED_TERMS = [
    "approved KnowledgeFeedbackDraft",
    "approved_by_human",
    "human review",
    "source evidence",
    "same-project source Artifact",
    "source_entity_type",
    "source_entity_id",
    "source_artifact_id",
    "source_quote_or_hash",
    "source_span",
    "source_section",
    "knowledge_type",
    "summary",
    "confidence",
    "evidence_artifact_ids",
    "used_knowledge_evidence_ids",
    "related_requirement_ids",
    "related_risk_ids",
    "duplicate/merge hints",
    "safe_to_show",
    "allowed_for_prompt=false",
    "prompt eligibility gate",
    "reviewed source citations",
    "unsupported claims",
    "ReviewHistory id",
    "review_required=true",
    "test_knowledge_card_handoff.json",
    "artifact_type=test_knowledge_card_handoff",
]

FORBIDDEN_SIDE_EFFECTS = [
    "TestKnowledgeCard CRUD",
    "TestKnowledgeCard auto-creation",
    "automatic card creation",
    "automatic prompt eligibility",
    "allowed_for_prompt=true auto-marking",
    "automatic knowledge ingestion",
    "KnowledgeIngestionAgent runtime",
    "backend feature API",
    "frontend review page",
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
    "remote CI provider behavior",
    "RBAC",
    "tenants",
    "permissions",
]


def test_golden_test_knowledge_card_handoff_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_test_knowledge_card_handoff_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_test_knowledge_card_handoff_forbids_side_effects() -> None:
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
    _assert_normalized_contains(api_contract, "does not add an endpoint")
    _assert_normalized_contains(api_contract, "test_knowledge_card_id: null")
    _assert_normalized_contains(data_contract, "allowed_for_prompt=false")
    _assert_normalized_contains(state_contract, "payload boundary")
    _assert_normalized_contains(state_contract, "human reviewer action")
    _assert_normalized_contains(
        artifact_contract, "artifact_type=test_knowledge_card_handoff"
    )
    _assert_normalized_contains(
        contracts, "must not create, approve, archive, delete, or mutate"
    )


def _alias(term: str) -> str:
    aliases = {
        "TestKnowledgeCard candidate": "TestKnowledgeCard handoff",
        "source Artifact": "source Artifact",
        "same-project source Artifact": "same-project source artifact",
        "source_artifact_id": "source_artifact_ids",
        "duplicate/merge hints": "duplicate/merge",
        "prompt eligibility gate": "prompt eligibility",
        "test_knowledge_card_handoff.json": "test_knowledge_card_handoff.json",
        "artifact_type=test_knowledge_card_handoff": (
            "artifact_type=test_knowledge_card_handoff"
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
