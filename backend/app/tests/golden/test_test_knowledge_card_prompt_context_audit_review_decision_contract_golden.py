from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path(
    "docs/fixtures/32-test-knowledge-card-prompt-context-audit-review-decision-golden.md"
)
SLICE_PATH = Path(
    "docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")

EXPECTED_SURFACES = [
    "TestKnowledgeCard Prompt Context Audit Review Decision",
    "review_prompt_context_audit_summary",
    "prompt_context_audit_review_decision",
    "prompt context audit summary artifact",
    "prompt context consumption artifact",
    "prompt context evidence artifact",
    "used_knowledge",
    "review action",
    "accepted",
    "needs_clarification",
    "rejected_for_missing_evidence",
    "rejected_for_unsupported_claim",
    "rejected_for_citation_mismatch",
    "ReviewHistory",
    "follow-up flags",
    "failure behavior",
]

REQUIRED_TERMS = [
    "prompt_context_audit_review_decision_action",
    "review_prompt_context_audit_summary",
    "prompt request id",
    "AITask id",
    "prompt context audit summary artifact id",
    "test_knowledge_card_prompt_context_audit_summary.json",
    "prompt context consumption artifact id",
    "test_knowledge_card_prompt_context_consumption.json",
    "prompt context evidence artifact id",
    "test_knowledge_card_prompt_context_evidence.json",
    "context manifest artifact id",
    "context_manifest",
    "context_manifest.json",
    "used_knowledge decision",
    "usage status",
    "output citation ids",
    "cited TestKnowledgeCard ids",
    "cited context entry ids",
    "cited source hashes",
    "source hash",
    "source quote/hash pointer",
    "skipped evidence ids",
    "skipped evidence",
    "skip reasons",
    "unsupported claims",
    "unsupported claim summaries",
    "review flags",
    "failure reasons",
    "PromptVersion id",
    "SkillVersion id",
    "PromptVersion name/version",
    "SkillVersion name/version",
    "ReviewHistory ids",
    "prior ReviewHistory ids",
    "review decision id",
    "review decision artifact id",
    "prompt context audit review decision artifact id",
    "test_knowledge_card_prompt_context_audit_review_decision.json",
    "artifact_type=test_knowledge_card_prompt_context_audit_review_decision",
    "reviewer label",
    "local reviewer id",
    "review action",
    "reviewer comment",
    "accepted citation ids",
    "questioned citation ids",
    "rejected citation ids",
    "follow-up flags",
    "requested clarification",
    "ReviewHistory id",
    "ReviewHistory decision",
    "source manifest ids",
    "source hashes",
    "PromptVersion/SkillVersion trace",
    "context manifest references",
    "failure_code",
    "accepted",
    "needs_clarification",
    "rejected_for_missing_evidence",
    "rejected_for_unsupported_claim",
    "rejected_for_citation_mismatch",
    "rejected_for_stale_evidence",
    "rejected_for_cross_project_evidence",
    "prompt_input.json",
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
    "frontend rendering",
    "report generation behavior",
    "report renderer",
    "report export behavior",
    "migration",
    "card table change",
    "list/update/delete API",
    "prompt assembly implementation",
    "prompt runtime execution",
    "prompt runtime retrieval implementation",
    "deterministic retrieval behavior change",
    "deterministic retrieval ranking change",
    "retrieval ranking change",
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
    "prompt runner",
    "queue",
    "scheduler",
    "background worker",
    "artifact upload",
    "Artifact mutation",
    "artifact delete",
    "source artifact mutation",
    "audit summary mutation",
    "prompt context audit summary artifact mutation",
    "prompt context consumption artifact mutation",
    "prompt context evidence artifact mutation",
    "retrieval boundary artifact mutation",
    "prompt eligibility artifact mutation",
    "historical evidence mutation",
    "historical ReviewHistory mutation",
    "PromptVersion mutation",
    "SkillVersion mutation",
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
    "remote CI provider behavior",
    "RBAC",
    "tenants",
    "permissions",
    "package upgrades",
]


def test_golden_test_knowledge_card_prompt_context_audit_review_decision_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_test_knowledge_card_prompt_context_audit_review_decision_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_test_knowledge_card_prompt_context_audit_review_decision_forbids_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    contracts = _contracts_text()
    data_contract = _read(DATA_CONTRACT_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)
    artifact_contract = _read(ARTIFACT_CONTRACT_PATH)
    prompt_skill_contract = _read(PROMPT_SKILL_CONTRACT_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(data_contract, "review_prompt_context_audit_summary")
    _assert_normalized_contains(
        api_contract, "must not append a successful ReviewHistory decision"
    )
    _assert_normalized_contains(
        state_contract, "prompt_context_audit_review_failed"
    )
    _assert_normalized_contains(
        artifact_contract,
        "artifact_type=test_knowledge_card_prompt_context_audit_review_decision",
    )
    _assert_normalized_contains(
        prompt_skill_contract, "create prompt eligibility"
    )
    _assert_normalized_contains(contracts, "accepted citation ids")
    _assert_normalized_contains(contracts, "questioned citation ids")
    _assert_normalized_contains(contracts, "rejected citation ids")
    _assert_normalized_contains(contracts, "follow-up flags")
    _assert_normalized_contains(contracts, "rewrite `used_knowledge`")


def _alias(term: str) -> str:
    aliases = {
        "prompt_context_audit_review_decision": (
            "prompt_context_audit_review_decision_action"
        ),
        "prompt context audit summary artifact": (
            "prompt context audit summary artifact id"
        ),
        "prompt context consumption artifact": (
            "prompt context consumption artifact id"
        ),
        "prompt context evidence artifact": "prompt context evidence artifact id",
        "used_knowledge": "used_knowledge",
        "failure behavior": "failure behavior",
        "test_knowledge_card_prompt_context_audit_summary.json": (
            "test_knowledge_card_prompt_context_audit_summary"
        ),
        "test_knowledge_card_prompt_context_consumption.json": (
            "test_knowledge_card_prompt_context_consumption"
        ),
        "test_knowledge_card_prompt_context_evidence.json": (
            "test_knowledge_card_prompt_context_evidence"
        ),
        "context_manifest.json": "context_manifest",
        "used_knowledge decision": "`used_knowledge` decision",
        "cited source hashes": "cited source hash",
        "PromptVersion name/version": "PromptVersion id/name/version",
        "SkillVersion name/version": "SkillVersion id/name/version",
        "review decision artifact id": "review decision id or artifact id",
        "prompt context audit review decision artifact id": (
            "prompt_context_audit_review_decision_artifact_id"
        ),
        "failure_code": "failure code",
        "ReviewHistory decision": "successful ReviewHistory decision",
        "test_knowledge_card_prompt_context_audit_review_decision.json": (
            "test_knowledge_card_prompt_context_audit_review_decision.json"
        ),
        "artifact_type=test_knowledge_card_prompt_context_audit_review_decision": (
            "artifact_type=test_knowledge_card_prompt_context_audit_review_decision"
        ),
        "PromptVersion/SkillVersion trace": "PromptVersion/SkillVersion trace",
        "prompt_input.json": "prompt_input.json",
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
