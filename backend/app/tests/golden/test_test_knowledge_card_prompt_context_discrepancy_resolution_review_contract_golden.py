from __future__ import annotations

from pathlib import Path


FIXTURE_PATH = Path(
    "docs/fixtures/35-test-knowledge-card-prompt-context-discrepancy-resolution-review-golden.md"
)
SLICE_PATH = Path(
    "docs/implementation/slices/slice-47-test-knowledge-card-prompt-context-discrepancy-resolution-review-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")

EXPECTED_SURFACES = [
    "TestKnowledgeCard Prompt Context Discrepancy Resolution Review",
    "review_prompt_context_discrepancy_resolution",
    "prompt_context_discrepancy_resolution_review",
    "prompt context review discrepancy artifact",
    "review summary export artifact",
    "audit review decision artifact",
    "audit summary artifact",
    "prompt context consumption artifact",
    "prompt context evidence artifact",
    "resolution action",
    "accepted discrepancy ids",
    "rejected discrepancy ids",
    "acknowledged discrepancy ids",
    "clarification requested fields",
    "affected citation ids",
    "evidence gap summary",
    "mismatch reason",
    "reviewer note",
    "severity",
    "resolution status",
    "ReviewHistory",
    "failure behavior",
]

REQUIRED_TERMS = [
    "prompt_context_discrepancy_resolution_review_action",
    "review_prompt_context_discrepancy_resolution",
    "prompt request id",
    "AITask id",
    "prompt context review discrepancy artifact id",
    "test_knowledge_card_prompt_context_review_discrepancy.json",
    "prompt context audit review summary export artifact id",
    "test_knowledge_card_prompt_context_audit_review_summary_export.json",
    "prompt context audit review decision artifact id",
    "test_knowledge_card_prompt_context_audit_review_decision.json",
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
    "discrepancy type",
    "affected citation ids",
    "evidence gap summary",
    "mismatch reason",
    "reviewer note from discrepancy tracking",
    "severity",
    "current resolution status",
    "resolution review id",
    "resolution review artifact id",
    "prompt context discrepancy resolution review artifact id",
    "test_knowledge_card_prompt_context_discrepancy_resolution_review.json",
    "artifact_type=test_knowledge_card_prompt_context_discrepancy_resolution_review",
    "resolution review action",
    "resolution action",
    "acknowledge_discrepancy",
    "reject_discrepancy_resolution",
    "request_discrepancy_clarification",
    "mark_resolved_by_later_review",
    "accepted discrepancy ids",
    "rejected discrepancy ids",
    "acknowledged discrepancy ids",
    "clarification requested fields",
    "resulting resolution status",
    "open",
    "needs_clarification",
    "acknowledged",
    "rejected",
    "resolved_by_later_review",
    "unresolved follow-up flags",
    "unsupported claim references",
    "source hashes",
    "source hash",
    "source quote/hash pointer",
    "PromptVersion id",
    "SkillVersion id",
    "PromptVersion name/version",
    "SkillVersion name/version",
    "ReviewHistory ids",
    "discrepancy ReviewHistory id",
    "ReviewHistory links",
    "source manifest ids",
    "PromptVersion/SkillVersion trace",
    "context manifest references",
    "failure_code",
    "failure code",
    "visible reason",
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
    "endpoint",
    "router",
    "service",
    "worker",
    "queue",
    "scheduler",
    "background job",
    "frontend page",
    "frontend rendering",
    "report generation behavior",
    "report renderer",
    "report export behavior",
    "export/download endpoint",
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
    "artifact upload",
    "Artifact mutation",
    "artifact delete",
    "source artifact mutation",
    "discrepancy tracking evidence mutation",
    "prompt context review discrepancy artifact mutation",
    "review summary export mutation",
    "prompt context audit review summary export artifact mutation",
    "audit review decision mutation",
    "prompt context audit review decision artifact mutation",
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
    "automatic discrepancy resolution",
    "automatic discrepancy remediation",
    "auto-resolve discrepancies",
    "automatic duplicate merge",
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


def test_golden_test_knowledge_card_prompt_context_discrepancy_resolution_review_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_test_knowledge_card_prompt_context_discrepancy_resolution_review_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_test_knowledge_card_prompt_context_discrepancy_resolution_review_forbids_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    contracts = _contracts_text()
    data_contract = _read(DATA_CONTRACT_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)
    artifact_contract = _read(ARTIFACT_CONTRACT_PATH)
    prompt_skill_contract = _read(PROMPT_SKILL_CONTRACT_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(
        data_contract, "review_prompt_context_discrepancy_resolution"
    )
    _assert_normalized_contains(
        api_contract, "must not append a successful resolution review"
    )
    _assert_normalized_contains(
        state_contract, "prompt_context_discrepancy_resolution_review_failed"
    )
    _assert_normalized_contains(
        artifact_contract,
        "artifact_type=test_knowledge_card_prompt_context_discrepancy_resolution_review",
    )
    _assert_normalized_contains(
        prompt_skill_contract, "auto-resolve discrepancies"
    )
    _assert_normalized_contains(contracts, "accepted discrepancy ids")
    _assert_normalized_contains(contracts, "rejected discrepancy ids")
    _assert_normalized_contains(contracts, "acknowledged discrepancy ids")
    _assert_normalized_contains(contracts, "affected citation ids")
    _assert_normalized_contains(contracts, "evidence gap summary")
    _assert_normalized_contains(contracts, "mismatch reason")
    _assert_normalized_contains(contracts, "resolution status")
    _assert_normalized_contains(contracts, "rewrite `used_knowledge`")


def _alias(term: str) -> str:
    aliases = {
        "prompt_context_discrepancy_resolution_review": (
            "prompt_context_discrepancy_resolution_review_action"
        ),
        "prompt context review discrepancy artifact": (
            "prompt context review discrepancy artifact id"
        ),
        "review summary export artifact": (
            "prompt context audit review summary export artifact id"
        ),
        "audit review decision artifact": (
            "audit review decision artifact id"
        ),
        "audit summary artifact": "audit summary artifact id",
        "prompt context consumption artifact": (
            "prompt context consumption artifact id"
        ),
        "prompt context evidence artifact": (
            "prompt context evidence artifact id"
        ),
        "test_knowledge_card_prompt_context_review_discrepancy.json": (
            "test_knowledge_card_prompt_context_review_discrepancy"
        ),
        "test_knowledge_card_prompt_context_audit_review_summary_export.json": (
            "test_knowledge_card_prompt_context_audit_review_summary_export"
        ),
        "test_knowledge_card_prompt_context_audit_review_decision.json": (
            "test_knowledge_card_prompt_context_audit_review_decision"
        ),
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
        "PromptVersion name/version": "PromptVersion id/name/version",
        "SkillVersion name/version": "SkillVersion id/name/version",
        "resolution review id": "resolution review id or artifact id",
        "resolution review artifact id": "resolution review id or artifact id",
        "prompt context discrepancy resolution review artifact id": (
            "prompt_context_discrepancy_resolution_review_artifact_id"
        ),
        "test_knowledge_card_prompt_context_discrepancy_resolution_review.json": (
            "test_knowledge_card_prompt_context_discrepancy_resolution_review"
        ),
        "artifact_type=test_knowledge_card_prompt_context_discrepancy_resolution_review": (
            "artifact_type=test_knowledge_card_prompt_context_discrepancy_resolution_review"
        ),
        "failure_code": "failure code",
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
