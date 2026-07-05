from __future__ import annotations

import re
from pathlib import Path


FIXTURE_PATH = Path(
    "docs/fixtures/39-knowledge-adapter-provider-evaluation-review-decision-golden.md"
)
SLICE_PATH = Path(
    "docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")

EXPECTED_SURFACES = [
    "KnowledgeAdapter Provider Evaluation Review Decision",
    "review_knowledge_adapter_provider_evaluation",
    "knowledge_adapter_provider_evaluation_review_decision",
    "provider evaluation review",
    "provider evaluation plan artifact",
    "provider candidate",
    "review decision",
    "review status",
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
    "knowledge_adapter_provider_evaluation_review_decision_action",
    (
        "knowledge_adapter_provider_evaluation_review_decision_action="
        "review_knowledge_adapter_provider_evaluation"
    ),
    "review_knowledge_adapter_provider_evaluation",
    "provider evaluation plan artifact id",
    "knowledge_adapter_provider_evaluation_plan_artifact_id",
    "created_by_component=KnowledgeAdapterProviderEvaluationReviewDecision",
    "owner_entity_type=AITask",
    "owner_entity_type=Project",
    "same-project plan artifact",
    "candidate provider name",
    "provider family",
    "adapter type",
    "provider version",
    "adapter version",
    "provider suitability status",
    "license name",
    "license URL",
    "license compatibility notes",
    "license review result",
    "reference intake summary",
    "reference intake URLs",
    "documentation snapshot artifact ids",
    "expected KnowledgeEvidence normalization fields",
    "KnowledgeEvidence normalization",
    "KnowledgeEvidence normalization notes",
    "provider_state",
    "provider_state recommendation",
    "disabled by default policy",
    "disabled by default decision",
    "fallback behavior summary",
    "fallback labels",
    "metrics plan",
    "metric set",
    "evidence normalization completeness",
    "source traceability coverage",
    "redaction safety status",
    "fallback coverage",
    "blocker reasons",
    "unresolved safety questions",
    "source manifest ids",
    "source hashes",
    "ReviewHistory ids",
    "ReviewHistory links",
    "provider evaluation review decision id",
    "provider evaluation review decision artifact id",
    "knowledge_adapter_provider_evaluation_review_decision_artifact_id",
    "knowledge_adapter_provider_evaluation_review_decision.json",
    "artifact_type=knowledge_adapter_provider_evaluation_review_decision",
    "manifest_kind=knowledge_adapter_provider_evaluation_review_decision",
    "reviewer label",
    "local reviewer id",
    "reviewer note",
    "accepted constraints",
    "blocked reasons",
    "unsupported reasons",
    "requested revision fields",
    "decision rationale",
    "reviewer_label",
    "local_reviewer_id",
    "reviewer_note",
    "accepted_constraints",
    "blocked_reasons",
    "unsupported_reasons",
    "requested_revision_fields",
    "unresolved_safety_questions",
    "decision_rationale",
    "review_history_links",
    "provider_state_recommendation",
    "disabled_by_default_decision",
    "license_review_result",
    "reference_intake_summary",
    "knowledge_evidence_normalization_notes",
    "fallback_behavior_summary",
    "fallback_labels",
    "metrics_plan",
    "source_manifest_ids",
    "source_hashes",
    "PromptVersion id",
    "SkillVersion id",
    "PromptVersion name/version",
    "SkillVersion name/version",
    "provider_candidate_disabled_by_default",
    "provider_evaluation_review_pending",
    "provider_evaluation_review_accepted_for_planning",
    "provider_evaluation_review_accepted_with_constraints",
    "provider_evaluation_review_blocked",
    "provider_evaluation_review_needs_revision",
    "provider_evaluation_review_unsupported",
    "provider_evaluation_review_failed_validation",
    "not_reviewed",
    "accepted_for_planning",
    "accepted_with_constraints",
    "blocked",
    "needs_revision",
    "unsupported",
    "failed_validation",
    "audit evidence only",
    "future planning",
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
    "review-decision-invalid",
    "evaluation-plan-mismatched",
    "cross-project",
    "unbounded",
    "credential-required",
    "runtime-required",
]

API_PAYLOAD_FIELDS = [
    "project_id",
    "knowledge_adapter_provider_evaluation_plan_artifact_id",
    "candidate_provider_name",
    "provider_family",
    "adapter_type",
    "provider_version",
    "adapter_version",
    "provider_suitability_status",
    "provider_state_recommendation",
    "disabled_by_default_decision",
    "license_review_result",
    "reference_intake_summary",
    "knowledge_evidence_normalization_notes",
    "fallback_behavior_summary",
    "metrics_plan",
    "blocker_reasons",
    "unresolved_safety_questions",
    "source_manifest_ids",
    "source_hashes",
    "review_history_ids",
    "review_decision",
    "review_status",
    "reviewer_label",
    "reviewer_note",
    "accepted_constraints",
    "requested_revision_fields",
    "blocked_reasons",
    "unsupported_reasons",
    "review_history_links",
    "failure_code",
    "visible_reason",
]

STATE_TRANSITIONS = [
    "provider_candidate_disabled_by_default -> provider_evaluation_review_pending",
    (
        "provider_evaluation_review_pending -> "
        "provider_evaluation_review_accepted_for_planning"
    ),
    (
        "provider_evaluation_review_pending -> "
        "provider_evaluation_review_accepted_with_constraints"
    ),
    "provider_evaluation_review_pending -> provider_evaluation_review_blocked",
    "provider_evaluation_review_pending -> provider_evaluation_review_needs_revision",
    "provider_evaluation_review_pending -> provider_evaluation_review_unsupported",
    (
        "provider_evaluation_review_pending -> "
        "provider_evaluation_review_failed_validation"
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
    "export/download endpoint",
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
    "artifact mutation outside declared review decision evidence",
    "artifact delete",
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
    "generated replacement evidence",
    "RBAC",
    "tenants",
    "permissions",
    "review bypass",
]


def test_golden_knowledge_adapter_provider_evaluation_review_decision_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_knowledge_adapter_provider_evaluation_review_decision_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_knowledge_adapter_provider_evaluation_review_decision_locks_api_payload_fields() -> None:
    fixture = _read(FIXTURE_PATH)
    api_contract = _read(API_CONTRACT_PATH)

    _assert_normalized_contains(
        api_contract,
        "KnowledgeAdapter provider evaluation review decision payload shape",
    )
    _assert_normalized_contains(
        api_contract,
        "KnowledgeAdapter provider evaluation review decision response shape",
    )

    for field in API_PAYLOAD_FIELDS:
        _assert_token_contains(fixture, field)
        _assert_token_contains(api_contract, field)


def test_golden_knowledge_adapter_provider_evaluation_review_decision_forbids_runtime_side_effects() -> None:
    fixture = _read(FIXTURE_PATH)
    contracts = _contracts_text()
    data_contract = _read(DATA_CONTRACT_PATH)
    api_contract = _read(API_CONTRACT_PATH)
    state_contract = _read(STATE_CONTRACT_PATH)
    artifact_contract = _read(ARTIFACT_CONTRACT_PATH)
    prompt_skill_contract = _read(PROMPT_SKILL_CONTRACT_PATH)

    for side_effect in FORBIDDEN_SIDE_EFFECTS:
        _assert_normalized_contains(fixture, side_effect)

    _assert_normalized_contains(data_contract, "review_knowledge_adapter_provider_evaluation")
    _assert_normalized_contains(data_contract, "metadata_json` must include")
    _assert_normalized_contains(data_contract, "must not create TestKnowledgeCard rows")
    _assert_normalized_contains(
        data_contract,
        "created_by_component=KnowledgeAdapterProviderEvaluationReviewDecision",
    )
    _assert_normalized_contains(
        data_contract,
        (
            "knowledge_adapter_provider_evaluation_review_decision_action="
            "review_knowledge_adapter_provider_evaluation"
        ),
    )
    _assert_normalized_contains(api_contract, "must not install packages")
    _assert_normalized_contains(api_contract, "provider-backed prompt context evidence")
    _assert_normalized_contains(api_contract, "same-project provider evaluation plan artifact")
    _assert_normalized_contains(
        state_contract, "provider_evaluation_review_failed_validation"
    )
    for transition in STATE_TRANSITIONS:
        _assert_normalized_contains(state_contract, transition)
    _assert_normalized_contains(state_contract, "accepted for future planning only")
    _assert_normalized_contains(
        state_contract, "must not append a successful review decision"
    )
    _assert_normalized_contains(
        artifact_contract,
        "artifact_type=knowledge_adapter_provider_evaluation_review_decision",
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
    _assert_normalized_contains(artifact_contract, "generated replacement evidence")
    _assert_normalized_contains(artifact_contract, "runtime `prompt_input.json`")
    _assert_normalized_contains(
        prompt_skill_contract, "must not write runtime `prompt_input.json`"
    )
    _assert_normalized_contains(
        prompt_skill_contract,
        (
            "PromptVersion id/name/version and SkillVersion id/name/version "
            "when the review decision is produced by a prompt or skill"
        ),
    )
    _assert_normalized_contains(
        prompt_skill_contract, "Provider-specific payloads must not leak"
    )
    _assert_normalized_contains(
        prompt_skill_contract, "used_knowledge` must not be auto-marked true"
    )
    _assert_normalized_contains(contracts, "mutate the reviewed provider evaluation plan artifact")
    _assert_normalized_contains(contracts, "display/health metadata")
    _assert_normalized_contains(contracts, "used_knowledge=true")


def _alias(term: str) -> str:
    aliases = {
        "provider candidate": "candidate provider",
        "knowledge_adapter_provider_evaluation_review_decision": (
            "knowledge_adapter_provider_evaluation_review_decision_action"
        ),
        "knowledge_adapter_provider_evaluation_review_decision_action": (
            "review_knowledge_adapter_provider_evaluation"
        ),
        (
            "knowledge_adapter_provider_evaluation_review_decision_action="
            "review_knowledge_adapter_provider_evaluation"
        ): (
            "knowledge_adapter_provider_evaluation_review_decision_action="
            "review_knowledge_adapter_provider_evaluation"
        ),
        "created_by_component=KnowledgeAdapterProviderEvaluationReviewDecision": (
            "created_by_component=KnowledgeAdapterProviderEvaluationReviewDecision"
        ),
        "provider evaluation plan artifact": "provider evaluation plan artifact id",
        "same-project plan artifact": "same-project provider evaluation plan artifact",
        "provider evaluation review decision artifact id": (
            "provider evaluation review decision id or artifact id"
        ),
        "knowledge_adapter_provider_evaluation_review_decision_artifact_id": (
            "provider evaluation review decision id or artifact id"
        ),
        "knowledge_adapter_provider_evaluation_review_decision.json": (
            "knowledge_adapter_provider_evaluation_review_decision"
        ),
        "accepted_for_planning": "accepted for future planning",
        "accepted with constraints": "accepted_with_constraints",
        "review status": "review status values",
        "blocked reasons": "blocked reasons",
        "KnowledgeEvidence normalization": "KnowledgeEvidence normalization fields",
        "redaction safety status": "redaction_safety_status",
        "fallback coverage": "fallback_coverage",
        "failure_code": "failure code",
        "visible_reason": "visible_reason",
        "KnowledgeAdapterConfig runtime state mutation": (
            "mutate KnowledgeAdapterConfig"
        ),
        "KnowledgeAdapterConfig.status mutation": "KnowledgeAdapterConfig.status",
        "provider_state_recommendation": "provider_state_recommendation",
        "disabled_by_default_decision": "disabled_by_default_decision",
        "license_review_result": "license_review_result",
        "reference_intake_summary": "reference_intake_summary",
        "knowledge_evidence_normalization_notes": (
            "knowledge_evidence_normalization_notes"
        ),
        "fallback_behavior_summary": "fallback behavior summary",
        "fallback_labels": "fallback labels",
        "metrics_plan": "metrics plan",
        "source_manifest_ids": "source_manifest_ids",
        "source_hashes": "source_hashes",
        "reviewer_label": "reviewer_label",
        "local_reviewer_id": "local reviewer id",
        "reviewer_note": "reviewer note",
        "accepted_constraints": "accepted_constraints",
        "requested_revision_fields": "requested_revision_fields",
        "blocked_reasons": "blocked reasons",
        "unsupported_reasons": "unsupported reasons",
        "unresolved_safety_questions": "unresolved safety questions",
        "decision_rationale": "decision rationale",
        "review_history_links": "ReviewHistory links",
        "PromptVersion name/version": "PromptVersion id/name/version",
        "SkillVersion name/version": "SkillVersion id/name/version",
        "graph payloads": "graph runtime payloads",
        "provider SDK": "provider SDKs",
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
