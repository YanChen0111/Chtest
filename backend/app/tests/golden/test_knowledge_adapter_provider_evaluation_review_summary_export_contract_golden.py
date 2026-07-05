from __future__ import annotations

import re
from pathlib import Path


FIXTURE_PATH = Path(
    "docs/fixtures/40-knowledge-adapter-provider-evaluation-review-summary-export-golden.md"
)
SLICE_PATH = Path(
    "docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")

EXPECTED_SURFACES = [
    "KnowledgeAdapter Provider Evaluation Review Summary Export",
    "export_knowledge_adapter_provider_evaluation_review_summary",
    "knowledge_adapter_provider_evaluation_review_summary_export",
    "provider evaluation review summary export",
    "provider evaluation review decision artifact",
    "provider evaluation plan artifact",
    "review summary status",
    "exported decision groups",
    "accepted_for_planning",
    "accepted_with_constraints",
    "blocked",
    "needs_revision",
    "unsupported",
    "provider suitability status",
    "KnowledgeEvidence",
    "provider_state",
    "fallback behavior",
    "license review",
    "reference intake",
    "disabled by default policy",
    "ReviewHistory",
    "failure behavior",
]

REQUIRED_TERMS = [
    "knowledge_adapter_provider_evaluation_review_summary_export_action",
    (
        "knowledge_adapter_provider_evaluation_review_summary_export_action="
        "export_knowledge_adapter_provider_evaluation_review_summary"
    ),
    "export_knowledge_adapter_provider_evaluation_review_summary",
    "provider evaluation review decision artifact id",
    "knowledge_adapter_provider_evaluation_review_decision_artifact_id",
    "provider evaluation plan artifact id",
    "knowledge_adapter_provider_evaluation_plan_artifact_id",
    "created_by_component=KnowledgeAdapterProviderEvaluationReviewSummaryExport",
    "owner_entity_type=AITask",
    "owner_entity_type=Project",
    "same-project provider evaluation review decision artifact",
    "same-project provider evaluation plan artifact",
    "candidate provider name",
    "provider family",
    "adapter type",
    "provider version",
    "adapter version",
    "provider suitability status",
    "review decision",
    "review status",
    "review summary status",
    "exported decision groups",
    "reviewer label",
    "local reviewer id",
    "reviewer notes",
    "accepted constraints",
    "blocked reasons",
    "unsupported reasons",
    "requested revision fields",
    "unresolved safety questions",
    "decision rationale",
    "license name",
    "license URL",
    "license compatibility notes",
    "license review result",
    "license/reference summary",
    "reference intake summary",
    "reference intake URLs",
    "documentation snapshot artifact ids",
    "expected KnowledgeEvidence normalization fields",
    "KnowledgeEvidence normalization",
    "KnowledgeEvidence normalization notes",
    "KnowledgeEvidence normalization summary",
    "provider_state",
    "provider_state recommendation",
    "provider_state summary",
    "disabled by default policy",
    "disabled by default decision",
    "disabled by default summary",
    "fallback behavior summary",
    "fallback labels",
    "fallback summary",
    "metrics plan",
    "metric set",
    "metrics summary",
    "evidence normalization completeness",
    "source traceability coverage",
    "redaction safety status",
    "fallback coverage",
    "source traceability summary",
    "source manifest ids",
    "source hashes",
    "ReviewHistory ids",
    "ReviewHistory links",
    "ReviewHistory summary",
    "provider evaluation review summary export id",
    "provider evaluation review summary export artifact id",
    "knowledge_adapter_provider_evaluation_review_summary_export_artifact_id",
    "knowledge_adapter_provider_evaluation_review_summary_export.json",
    "artifact_type=knowledge_adapter_provider_evaluation_review_summary_export",
    "manifest_kind=knowledge_adapter_provider_evaluation_review_summary_export",
    "PromptVersion id",
    "SkillVersion id",
    "PromptVersion name/version",
    "SkillVersion name/version",
    "not_exported",
    "exported_for_planning",
    "failed_validation",
    "provider_evaluation_review_summary_export_pending",
    "provider_evaluation_review_summary_exported_for_planning",
    "provider_evaluation_review_summary_export_failed_validation",
    "accepted_for_planning",
    "accepted_with_constraints",
    "blocked",
    "needs_revision",
    "unsupported",
    "audit evidence only",
    "future planning",
    "not a report generator",
    "used_knowledge=true",
    "prompt_input.json",
    "failure_code",
    "failure code",
    "visible_reason",
    "visible reason",
    "missing, stale, unsafe, unlicensed",
    "license-unknown",
    "version-unknown",
    "reference-missing",
    "reference-mismatched",
    "normalization-unsupported",
    "provider-state-unsafe",
    "fallback-missing",
    "review-decision-missing",
    "review-decision-invalid",
    "summary-export-invalid",
    "evaluation-plan-mismatched",
    "review-decision-mismatched",
    "cross-project",
    "unbounded",
    "credential-required",
    "runtime-required",
]

API_PAYLOAD_FIELDS = [
    "project_id",
    "knowledge_adapter_provider_evaluation_review_decision_artifact_id",
    "knowledge_adapter_provider_evaluation_plan_artifact_id",
    "candidate_provider_name",
    "provider_family",
    "adapter_type",
    "provider_version",
    "adapter_version",
    "provider_suitability_status",
    "review_decision",
    "review_status",
    "reviewer_notes",
    "accepted_constraints",
    "requested_revision_fields",
    "blocked_reasons",
    "unsupported_reasons",
    "unresolved_safety_questions",
    "license_review_result",
    "reference_intake_summary",
    "knowledge_evidence_normalization_notes",
    "provider_state_recommendation",
    "disabled_by_default_decision",
    "fallback_behavior_summary",
    "metrics_plan",
    "source_manifest_ids",
    "source_hashes",
    "review_history_links",
    "knowledge_adapter_provider_evaluation_review_summary_export_artifact_id",
    "review_summary_status",
    "exported_decision_groups",
    "provider_suitability_summary",
    "license_reference_summary",
    "knowledge_evidence_normalization_summary",
    "provider_state_summary",
    "disabled_by_default_summary",
    "fallback_summary",
    "metrics_summary",
    "source_traceability_summary",
    "review_history_summary",
    "failure_code",
    "visible_reason",
]

STATE_TRANSITIONS = [
    (
        "provider_evaluation_review_accepted_for_planning -> "
        "provider_evaluation_review_summary_export_pending"
    ),
    (
        "provider_evaluation_review_accepted_with_constraints -> "
        "provider_evaluation_review_summary_export_pending"
    ),
    "provider_evaluation_review_blocked -> provider_evaluation_review_summary_export_pending",
    (
        "provider_evaluation_review_needs_revision -> "
        "provider_evaluation_review_summary_export_pending"
    ),
    (
        "provider_evaluation_review_unsupported -> "
        "provider_evaluation_review_summary_export_pending"
    ),
    (
        "provider_evaluation_review_summary_export_pending -> "
        "provider_evaluation_review_summary_exported_for_planning"
    ),
    (
        "provider_evaluation_review_summary_export_pending -> "
        "provider_evaluation_review_summary_export_failed_validation"
    ),
]

FORBIDDEN_SIDE_EFFECTS = [
    "provider enablement",
    "automatic provider enablement",
    "Haystack provider integration",
    "LlamaIndex provider integration",
    "GraphRAG provider integration",
    "provider SDK",
    "provider SDK call",
    "external provider call",
    "API key handling",
    "credentials",
    "OAuth",
    "OAuth state",
    "OAuth material",
    "remote URL fetch",
    "remote fetch payloads",
    "external call",
    "network retrieval",
    "provider runtime",
    "runtime retrieval",
    "provider-backed prompt context evidence",
    "raw provider payloads",
    "API keys",
    "tokens",
    "provider request payloads",
    "provider-specific payloads",
    "prompt assembly implementation",
    "prompt runtime execution",
    "runtime prompt_input.json",
    "automatic used_knowledge=true marking",
    "deterministic retrieval behavior change",
    "prompt eligibility change",
    "vector database",
    "vector index",
    "embedding model",
    "embedding service",
    "embedding vectors",
    "embedding",
    "embeddings",
    "semantic index",
    "ANN search",
    "reranking service",
    "reranking",
    "background indexing job",
    "crawler",
    "document chunking pipeline",
    "graph runtime",
    "GraphRAG job",
    "MCP runtime",
    "frontend page",
    "report generation behavior",
    "report generator",
    "export/download endpoint",
    "download endpoint",
    "backend feature API",
    "endpoint",
    "router",
    "service",
    "worker",
    "queue",
    "scheduler",
    "migration",
    "package upgrade",
    "broad KnowledgeAdapter CRUD",
    "KnowledgeAdapterConfig runtime state mutation",
    "KnowledgeAdapterConfig.status mutation",
    "automatic knowledge ingestion",
    "TestKnowledgeCard CRUD",
    "automatic prompt eligibility",
    "artifact upload",
    "Artifact mutation",
    "artifact mutation outside declared summary export evidence",
    "artifact delete",
    "provider evaluation review decision artifact mutation",
    "provider evaluation plan artifact mutation",
    "historical evidence mutation",
    "KnowledgeEvidence mutation",
    "TestKnowledgeCard mutation",
    "GeneratedCaseCandidate mutation",
    "TestCase auto-promotion",
    "generated-case auto-approval",
    "ToolInvocation creation",
    "execute AITasks",
    "runner behavior change",
    "remote CI provider behavior",
    "retrieval evidence",
    "reports",
    "secrets",
    "vector store payloads",
    "reranker traces",
    "graph payloads",
    "executable prompt assembly payloads",
    "frontend-rendered markup",
    "report-rendered payloads",
    "export-rendered payloads",
    "downloadable provider payloads",
    "generated replacement evidence",
    "RBAC",
    "tenants",
    "permissions",
    "review bypass",
]


def test_golden_knowledge_adapter_provider_evaluation_review_summary_export_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_knowledge_adapter_provider_evaluation_review_summary_export_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_knowledge_adapter_provider_evaluation_review_summary_export_locks_api_payload_fields() -> None:
    fixture = _read(FIXTURE_PATH)
    api_contract = _read(API_CONTRACT_PATH)

    _assert_normalized_contains(
        api_contract,
        "KnowledgeAdapter provider evaluation review summary export payload shape",
    )
    _assert_normalized_contains(
        api_contract,
        "KnowledgeAdapter provider evaluation review summary export response shape",
    )

    for field in API_PAYLOAD_FIELDS:
        _assert_token_contains(fixture, field)
        _assert_token_contains(api_contract, field)


def test_golden_knowledge_adapter_provider_evaluation_review_summary_export_forbids_runtime_side_effects() -> None:
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
        data_contract, "metadata_json` must include"
    )
    _assert_normalized_contains(
        data_contract,
        "created_by_component=KnowledgeAdapterProviderEvaluationReviewSummaryExport",
    )
    _assert_normalized_contains(
        data_contract,
        (
            "knowledge_adapter_provider_evaluation_review_summary_export_action="
            "export_knowledge_adapter_provider_evaluation_review_summary"
        ),
    )
    _assert_normalized_contains(
        data_contract,
        "artifact_type=knowledge_adapter_provider_evaluation_review_summary_export",
    )
    _assert_normalized_contains(api_contract, "not a report generator")
    _assert_normalized_contains(api_contract, "must not append a successful summary export")
    _assert_normalized_contains(api_contract, "provider-backed prompt context evidence")
    _assert_normalized_contains(api_contract, "expose export/download endpoints")
    _assert_normalized_contains(
        state_contract, "provider_evaluation_review_summary_export_failed_validation"
    )
    for transition in STATE_TRANSITIONS:
        _assert_normalized_contains(state_contract, transition)
    _assert_normalized_contains(state_contract, "accepted for future planning only")
    _assert_normalized_contains(
        state_contract, "must not append a successful summary export"
    )
    _assert_normalized_contains(
        artifact_contract,
        "artifact_type=knowledge_adapter_provider_evaluation_review_summary_export",
    )
    _assert_normalized_contains(
        artifact_contract,
        "manifest_kind=knowledge_adapter_provider_evaluation_review_summary_export",
    )
    _assert_normalized_contains(artifact_contract, "owner_entity_type=AITask")
    _assert_normalized_contains(artifact_contract, "owner_entity_type=Project")
    _assert_normalized_contains(artifact_contract, "raw provider payloads")
    _assert_normalized_contains(artifact_contract, "API keys")
    _assert_normalized_contains(artifact_contract, "OAuth state")
    _assert_normalized_contains(artifact_contract, "remote fetch payloads")
    _assert_normalized_contains(artifact_contract, "vector store payloads")
    _assert_normalized_contains(artifact_contract, "reranker traces")
    _assert_normalized_contains(artifact_contract, "graph runtime payloads")
    _assert_normalized_contains(
        artifact_contract, "executable prompt assembly payloads"
    )
    _assert_normalized_contains(artifact_contract, "frontend-rendered markup")
    _assert_normalized_contains(artifact_contract, "report-rendered payloads")
    _assert_normalized_contains(artifact_contract, "export-rendered payloads")
    _assert_normalized_contains(artifact_contract, "downloadable provider payloads")
    _assert_normalized_contains(artifact_contract, "runtime `prompt_input.json`")
    _assert_normalized_contains(
        prompt_skill_contract,
        (
            "PromptVersion id/name/version and SkillVersion id/name/version "
            "when the summary export is produced by a prompt or skill"
        ),
    )
    _assert_normalized_contains(
        prompt_skill_contract, "Review summary exports are audit evidence only"
    )
    _assert_normalized_contains(
        prompt_skill_contract, "Provider-specific payloads must not leak"
    )
    _assert_normalized_contains(
        prompt_skill_contract, "used_knowledge` must not be auto-marked true"
    )
    _assert_normalized_contains(
        contracts, "mutate the reviewed provider evaluation review decision artifact"
    )
    _assert_normalized_contains(contracts, "display/health metadata")
    _assert_normalized_contains(contracts, "used_knowledge=true")


def _alias(term: str) -> str:
    aliases = {
        "knowledge_adapter_provider_evaluation_review_summary_export": (
            "knowledge_adapter_provider_evaluation_review_summary_export_action"
        ),
        "knowledge_adapter_provider_evaluation_review_summary_export_action": (
            "export_knowledge_adapter_provider_evaluation_review_summary"
        ),
        (
            "knowledge_adapter_provider_evaluation_review_summary_export_action="
            "export_knowledge_adapter_provider_evaluation_review_summary"
        ): (
            "knowledge_adapter_provider_evaluation_review_summary_export_action="
            "export_knowledge_adapter_provider_evaluation_review_summary"
        ),
        "provider evaluation review decision artifact": (
            "provider evaluation review decision artifact id"
        ),
        "provider evaluation plan artifact": "provider evaluation plan artifact id",
        "provider evaluation review summary export artifact id": (
            "provider evaluation review summary export id or artifact id"
        ),
        "knowledge_adapter_provider_evaluation_review_summary_export_artifact_id": (
            "knowledge_adapter_provider_evaluation_review_summary_export_artifact_id"
        ),
        "knowledge_adapter_provider_evaluation_review_summary_export.json": (
            "knowledge_adapter_provider_evaluation_review_summary_export.json"
        ),
        "same-project provider evaluation review decision artifact": (
            "same-project provider evaluation review decision artifact"
        ),
        "same-project provider evaluation plan artifact": (
            "same-project provider evaluation plan artifact"
        ),
        "review summary status": "Review summary status values",
        "not_exported": "not_exported",
        "exported_for_planning": "exported_for_planning",
        "exported decision groups": "Exported decision groups",
        "provider_state recommendation": "provider_state recommendation",
        "provider_state summary": "provider_state summary",
        "license/reference summary": "license/reference summary",
        "KnowledgeEvidence normalization": "KnowledgeEvidence normalization fields",
        "KnowledgeEvidence normalization summary": (
            "KnowledgeEvidence normalization summary"
        ),
        "redaction safety status": "redaction_safety_status",
        "fallback coverage": "fallback_coverage",
        "failure_code": "failure_code",
        "visible_reason": "visible_reason",
        "KnowledgeAdapterConfig runtime state mutation": (
            "KnowledgeAdapterConfig runtime state"
        ),
        "KnowledgeAdapterConfig.status mutation": "KnowledgeAdapterConfig.status",
        "provider SDK": "provider SDKs",
        "graph payloads": "graph runtime payloads",
        "vector database": "vector indexes",
        "package upgrade": "package upgrades",
    }
    return aliases.get(term, term)


def _assert_any_contains(texts: list[str], expected: str) -> None:
    if any(_normalized_contains(text, expected) for text in texts):
        return
    raise AssertionError(expected)


def _assert_normalized_contains(text: str, expected: str) -> None:
    assert _normalized_contains(text, expected), expected


def _assert_token_contains(text: str, expected: str) -> None:
    assert _token_contains(text, expected), expected


def _normalized_contains(text: str, expected: str) -> bool:
    normalized_text = " ".join(text.split()).lower()
    normalized_expected = " ".join(expected.split()).lower()
    return normalized_expected in normalized_text


def _token_contains(text: str, expected: str) -> bool:
    normalized_text = " ".join(text.split())
    normalized_expected = " ".join(expected.split())
    pattern = rf"(?<![A-Za-z0-9_]){re.escape(normalized_expected)}(?![A-Za-z0-9_])"
    return re.search(pattern, normalized_text, flags=re.IGNORECASE) is not None


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
