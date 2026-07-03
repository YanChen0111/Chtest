from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path("docs/fixtures/22-knowledge-feedback-contract-golden.md")
SLICE_PATH = Path("docs/implementation/slices/slice-34-knowledge-feedback-contract.md")
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")
PROMPT_PATH = Path("prompts/knowledge_feedback/v1.md")
SKILL_PATH = Path("skills/knowledge-feedback-skill/v1.md")

EXPECTED_SURFACES = [
    "KnowledgeFeedbackAgent",
    "knowledge_feedback:v1",
    "knowledge-feedback-skill:v1",
    "KnowledgeFeedbackDraft",
    "KnowledgeEvidence",
    "TestKnowledgeCard",
]

REQUIRED_TERMS = [
    "draft feedback",
    "accepted GeneratedCaseCandidate",
    "rejected GeneratedCaseCandidate",
    "reviewed TestCase",
    "ReviewHistory",
    "FailureAnalysis",
    "Report",
    "TestRun/TestResult summary",
    "KnowledgeEvidence",
    "existing TestKnowledgeCard",
    "feedback_type",
    "draft_knowledge_type",
    "source_entity_type",
    "source_entity_id",
    "source_quote_or_hash",
    "source_span",
    "recommendation",
    "confidence",
    "used_knowledge_evidence_ids",
    "unsupported_claims",
    "review_findings",
    "prompt_eligible=false",
    "human review",
    "prompt eligibility",
    "UNABLE_TO_CREATE_KNOWLEDGE_FEEDBACK",
]

FORBIDDEN_SIDE_EFFECTS = [
    "KnowledgeFeedbackAgent runtime",
    "TestKnowledgeCard CRUD",
    "TestKnowledgeCard auto-creation",
    "prompt-eligible auto-marking",
    "automatic knowledge ingestion",
    "historical ReviewHistory mutation",
    "FailureAnalysis mutation",
    "Report mutation",
    "TestRun mutation",
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


def test_golden_knowledge_feedback_contract_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()
    prompt = _read(PROMPT_PATH)
    skill = _read(SKILL_PATH)

    for surface in EXPECTED_SURFACES:
        _assert_any_contains([fixture, slice_plan, contracts, prompt, skill], surface)


def test_golden_knowledge_feedback_contract_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()
    prompt = _read(PROMPT_PATH)
    skill = _read(SKILL_PATH)

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts, prompt, skill], _alias(term))


def test_golden_knowledge_feedback_contract_forbids_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()
    prompt = _read(PROMPT_PATH)
    skill = _read(SKILL_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(slice_plan, "No KnowledgeFeedbackAgent runtime")
    _assert_normalized_contains(contracts, "must not create, approve")
    _assert_normalized_contains(contracts, "prompt_eligible=false")
    _assert_normalized_contains(contracts, "must not mutate ReviewHistory")
    _assert_normalized_contains(prompt, "Do not mark feedback as prompt-eligible")
    _assert_normalized_contains(skill, "Do not mark feedback as approved or prompt-eligible")


def _alias(term: str) -> str:
    aliases = {
        "accepted GeneratedCaseCandidate": "Accepted/rejected GeneratedCaseCandidate",
        "rejected GeneratedCaseCandidate": "Accepted/rejected GeneratedCaseCandidate",
        "TestRun/TestResult summary": "TestRun/TestResult",
        "prompt_eligible=false": "prompt_eligible=false",
        "prompt eligibility": "prompt eligibility",
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
            PROMPT_SKILL_CONTRACT_PATH,
        ]
    )


def _read(path: Path) -> str:
    assert path.exists(), f"{path} is missing"
    return path.read_text(encoding="utf-8")
