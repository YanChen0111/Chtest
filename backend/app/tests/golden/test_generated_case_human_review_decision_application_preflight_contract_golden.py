from __future__ import annotations

import re
from pathlib import Path


FIXTURE_PATH = Path(
    "docs/fixtures/46-generated-case-human-review-decision-application-preflight-golden.md"
)
SLICE_PATH = Path(
    "docs/implementation/slices/slice-58-generated-case-human-review-decision-application-preflight-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")

EXPECTED_SURFACES = [
    "Generated Case Human Review Decision Application Preflight",
    "preflight_generated_case_human_review_decision_application",
    "generated_case_human_review_decision_application_preflight",
    "generated case human review decision audit handoff artifact",
    "generated case human review decision summary export artifact",
    "generated case human review decision artifact",
    "generated case human review evidence package artifact",
    "mapped review action",
    "eligibility status",
    "eligible candidate ids",
    "ineligible candidate ids",
    "blocked action reasons",
    "required edit summary",
    "required human confirmation summary",
    "ReviewHistory",
    "failure behavior",
]

REQUIRED_TERMS = [
    "generated_case_human_review_decision_application_preflight_action",
    (
        "generated_case_human_review_decision_application_preflight_action="
        "preflight_generated_case_human_review_decision_application"
    ),
    "preflight_generated_case_human_review_decision_application",
    "generated case human review decision application preflight id",
    "preflight artifact id",
    "generated_case_human_review_decision_application_preflight_artifact_id",
    "generated_case_human_review_decision_application_preflight",
    "generated_case_human_review_decision_application_preflight.json",
    "artifact_type=generated_case_human_review_decision_application_preflight",
    "manifest_kind=generated_case_human_review_decision_application_preflight",
    "created_by_component=GeneratedCaseHumanReviewDecisionApplicationPreflight",
    "owner_entity_type=GeneratedCaseCandidate",
    "owner_entity_id=candidate_id",
    "owner_entity_type=AITask",
    "owner_entity_type=Project",
    "same-project",
    "generated case human review decision audit handoff artifact id",
    "generated_case_human_review_decision_audit_handoff_artifact_id",
    "generated case human review decision summary export artifact id",
    "generated_case_human_review_decision_summary_export_artifact_id",
    "source generated_case_human_review_decision_artifact_id values",
    "generated_case_human_review_decision_artifact_id",
    "generated_case_human_review_decision_artifact_ids",
    "linked generated_case_human_review_evidence_package_artifact_id values",
    "generated_case_human_review_evidence_package_artifact_id",
    "generated_case_human_review_evidence_package_artifact_ids",
    "GeneratedCaseCandidate ids/statuses",
    "generated_case_candidate_id",
    "candidate_status",
    "candidate status",
    "decision_label",
    "decision labels",
    "requested_edit_fields",
    "requested edit fields",
    "accepted_constraints",
    "accepted constraints",
    "optimization_request_summary",
    "optimization request summary",
    "rejection_reasons",
    "rejection reasons",
    "blocker_reasons",
    "blocker reasons",
    "duplicate_resolution_notes",
    "duplicate resolution notes",
    "evidence_chain_status",
    "evidence chain status",
    "unresolved_follow_up_flags",
    "unresolved follow-up flags",
    "unresolved_blocker_summary",
    "unresolved blocker summary",
    "source_traceability_handoff_summary",
    "source traceability handoff summary",
    "review_history_handoff_links",
    "ReviewHistory handoff links",
    "source_manifest_ids",
    "source manifest ids",
    "source_hashes",
    "source hashes",
    "required_human_confirmation_summary",
    "required human confirmation summary",
    "PromptVersion id",
    "SkillVersion id",
    "PromptVersion name/version",
    "SkillVersion name/version",
    "accepted_for_future_promotion",
    "accepted_with_required_edits",
    "needs_optimization",
    "rejected_for_insufficient_evidence",
    "blocked",
    "duplicate",
    "needs_more_evidence",
    "failed_validation",
    "mapped_review_action",
    "approve",
    "approve_after_edit",
    "request_optimization",
    "reject",
    "none",
    "preflight summary",
    "accepted-for-future-promotion preflight summary",
    "accepted-with-required-edits preflight summary",
    "needs-optimization preflight summary",
    "rejected-for-insufficient-evidence preflight summary",
    "blocked preflight summary",
    "duplicate preflight summary",
    "needs-more-evidence preflight summary",
    "failed-validation preflight summary",
    "application preflight eligibility evidence only",
    "eligibility evidence only",
    "planned action labels only",
    "not approval",
    "not rejection",
    "not request optimization",
    "not TestCase promotion",
    "not automation draft creation",
    "not report rendering",
    "not export/download endpoint",
    "used_knowledge=true",
    "prompt_input.json",
    "failure_code",
    "failure code",
    "visible_reason",
    "visible reason",
    "invalid, stale, unsafe, cross-project",
    "audit-handoff-missing",
    "audit-handoff-invalid",
    "audit-handoff-mismatched",
    "summary-export-missing",
    "summary-export-invalid",
    "summary-export-mismatched",
    "decision-artifact-missing",
    "decision-artifact-invalid",
    "decision-artifact-mismatched",
    "evidence-package-missing",
    "evidence-package-mismatched",
    "candidate-missing",
    "candidate-mismatched",
    "candidate-status-invalid",
    "decision-label-unsupported",
    "mapped-action-unsupported",
    "required-edit-missing",
    "required-confirmation-missing",
    "review-history-missing",
    "source-hash-mismatched",
    "artifact-mismatched",
    "incomplete-required-input",
    "credential-required",
    "runtime-required",
    "provider-required",
    "approval-required",
    "optimization-required",
    "promotion-required",
]

API_PAYLOAD_FIELDS = [
    "project_id",
    "decisions",
    "generated_case_human_review_decision_application_preflight_action",
    "generated_case_human_review_decision_audit_handoff_artifact_id",
    "generated_case_human_review_decision_summary_export_artifact_id",
    "generated_case_human_review_decision_artifact_id",
    "generated_case_human_review_decision_artifact_ids",
    "generated_case_human_review_evidence_package_artifact_id",
    "generated_case_human_review_evidence_package_artifact_ids",
    "generated_case_candidate_id",
    "candidate_status",
    "decision_label",
    "requested_edit_fields",
    "accepted_constraints",
    "optimization_request_summary",
    "rejection_reasons",
    "blocker_reasons",
    "duplicate_resolution_notes",
    "evidence_chain_status",
    "unresolved_follow_up_flags",
    "unresolved_blocker_summary",
    "source_traceability_handoff_summary",
    "review_history_handoff_links",
    "source_manifest_ids",
    "source_hashes",
    "required_human_confirmation_summary",
    "generated_case_human_review_decision_application_preflight_artifact_id",
    "generated_case_human_review_decision_application_preflight",
    "preflight_summary",
    "eligibility_status",
    "mapped_review_action",
    "eligible_candidate_ids",
    "ineligible_candidate_ids",
    "blocked_action_reasons",
    "required_edit_summary",
    "accepted_for_future_promotion_preflight_summary",
    "accepted_with_required_edits_preflight_summary",
    "needs_optimization_preflight_summary",
    "rejected_for_insufficient_evidence_preflight_summary",
    "blocked_preflight_summary",
    "duplicate_preflight_summary",
    "needs_more_evidence_preflight_summary",
    "failed_validation_preflight_summary",
    "failure_code",
    "visible_reason",
]

STATE_TRANSITIONS = [
    (
        "generated_case_human_review_decision_audit_handoff_complete -> "
        "generated_case_human_review_decision_application_preflight_pending"
    ),
    (
        "generated_case_human_review_decision_audit_handoff_incomplete -> "
        "generated_case_human_review_decision_application_preflight_pending"
    ),
    (
        "generated_case_human_review_decision_audit_handoff_blocked -> "
        "generated_case_human_review_decision_application_preflight_pending"
    ),
    (
        "generated_case_human_review_decision_audit_handoff_failed_validation -> "
        "generated_case_human_review_decision_application_preflight_failed_validation"
    ),
    (
        "generated_case_human_review_decision_application_preflight_pending -> "
        "generated_case_human_review_decision_application_preflight_eligible"
    ),
    (
        "generated_case_human_review_decision_application_preflight_pending -> "
        "generated_case_human_review_decision_application_preflight_ineligible"
    ),
    (
        "generated_case_human_review_decision_application_preflight_pending -> "
        "generated_case_human_review_decision_application_preflight_blocked"
    ),
    (
        "generated_case_human_review_decision_application_preflight_pending -> "
        "generated_case_human_review_decision_application_preflight_failed_validation"
    ),
]

FORBIDDEN_SIDE_EFFECTS = [
    "backend runtime API",
    "backend feature API",
    "endpoint",
    "router",
    "service",
    "worker",
    "queue",
    "scheduler",
    "migration",
    "package upgrade",
    "frontend page",
    "frontend store",
    "frontend component",
    "report generation behavior",
    "report renderer",
    "export/download endpoint",
    "provider integration",
    "provider SDK",
    "provider SDK call",
    "external call",
    "credentials",
    "API keys",
    "tokens",
    "OAuth",
    "remote URL fetch",
    "remote fetch payloads",
    "vector database",
    "vector index",
    "embedding",
    "embeddings",
    "embedding vectors",
    "reranking",
    "graph runtime",
    "GraphRAG job",
    "MCP runtime",
    "runtime retrieval",
    "provider-backed prompt context evidence",
    "prompt execution",
    "prompt assembly",
    "runtime prompt_input.json",
    "AITask orchestration",
    "execute AITasks",
    "automatic used_knowledge=true",
    "deterministic retrieval behavior change",
    "TestCase promotion",
    "GeneratedCaseCandidate approve/reject mutation",
    "GeneratedCaseCandidate content mutation",
    "GeneratedCaseCandidate status mutation",
    "request optimization mutation",
    "automation draft creation",
    "AutomationDraft rows",
    "ToolInvocation creation",
    "TestRun/TestResult creation",
    "artifact upload",
    "Artifact mutation",
    "artifact mutation outside declared application preflight evidence",
    "source artifact mutation",
    "source evidence mutation",
    "prompt context evidence mutation",
    "KnowledgeEvidence mutation",
    "TestKnowledgeCard mutation",
    "ReviewHistory mutation",
    "successful ReviewHistory decision",
    "historical evidence mutation",
    "runner behavior change",
    "remote CI provider behavior",
    "generated replacement evidence",
    "generated-case auto-approval",
    "review bypass",
    "application preflight artifact mutation",
    "generated case human review decision audit handoff artifact mutation",
    "generated case human review decision summary export artifact mutation",
    "generated case human review decision artifact mutation",
    "evidence package mutation",
    "raw LLM/provider payloads",
    "unbounded source text",
    "vector store payloads",
    "reranker traces",
    "graph runtime payloads",
    "executable prompt assembly payloads",
    "frontend-rendered markup",
    "report-rendered payloads",
    "export-rendered payloads",
    "downloadable provider payloads",
    "RBAC",
    "tenants",
    "permissions",
]


def test_golden_generated_case_human_review_decision_application_preflight_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_generated_case_human_review_decision_application_preflight_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_generated_case_human_review_decision_application_preflight_locks_api_payload_fields() -> None:
    fixture = _read(FIXTURE_PATH)
    api_contract = _read(API_CONTRACT_PATH)

    _assert_normalized_contains(
        api_contract,
        "Generated Case Human Review Decision Application Preflight payload shape",
    )
    _assert_normalized_contains(
        api_contract,
        "Generated Case Human Review Decision Application Preflight response shape",
    )

    for field in API_PAYLOAD_FIELDS:
        _assert_token_contains(fixture, field)
        _assert_token_contains(api_contract, field)


def test_golden_generated_case_human_review_decision_application_preflight_forbids_runtime_side_effects() -> None:
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
        data_contract,
        "created_by_component=GeneratedCaseHumanReviewDecisionApplicationPreflight",
    )
    _assert_normalized_contains(
        data_contract,
        (
            "generated_case_human_review_decision_application_preflight_action="
            "preflight_generated_case_human_review_decision_application"
        ),
    )
    _assert_normalized_contains(
        data_contract,
        "artifact_type=generated_case_human_review_decision_application_preflight",
    )
    _assert_normalized_contains(
        api_contract, "must not append a successful application preflight"
    )
    _assert_normalized_contains(api_contract, "successful ReviewHistory decision")
    _assert_normalized_contains(
        api_contract, "Eligibility status values may include"
    )
    _assert_normalized_contains(
        api_contract, "must not call the existing `case-review` action"
    )
    _assert_normalized_contains(
        api_contract, "GeneratedCaseCandidate approve/reject mutation"
    )
    _assert_normalized_contains(api_contract, "request optimization mutation")
    for transition in STATE_TRANSITIONS:
        _assert_normalized_contains(state_contract, transition)
    _assert_normalized_contains(
        state_contract, "Existing human review transitions remain"
    )
    _assert_normalized_contains(
        state_contract,
        "generated_case_human_review_decision_application_preflight_failed_validation",
    )
    _assert_normalized_contains(
        artifact_contract,
        "artifact_type=generated_case_human_review_decision_application_preflight",
    )
    _assert_normalized_contains(
        artifact_contract,
        "manifest_kind=generated_case_human_review_decision_application_preflight",
    )
    _assert_normalized_contains(
        artifact_contract,
        "generated_case_human_review_decision_application_preflight.json",
    )
    _assert_normalized_contains(artifact_contract, "raw LLM/provider payloads")
    _assert_normalized_contains(artifact_contract, "unbounded source text")
    _assert_normalized_contains(artifact_contract, "API keys")
    _assert_normalized_contains(artifact_contract, "OAuth state")
    _assert_normalized_contains(artifact_contract, "remote fetch payloads")
    _assert_normalized_contains(artifact_contract, "vector store payloads")
    _assert_normalized_contains(artifact_contract, "embedding vectors")
    _assert_normalized_contains(artifact_contract, "reranker traces")
    _assert_normalized_contains(artifact_contract, "graph runtime payloads")
    _assert_normalized_contains(
        artifact_contract, "executable prompt assembly payloads"
    )
    _assert_normalized_contains(artifact_contract, "runtime `prompt_input.json`")
    _assert_normalized_contains(artifact_contract, "frontend-rendered markup")
    _assert_normalized_contains(artifact_contract, "report-rendered payloads")
    _assert_normalized_contains(artifact_contract, "export-rendered payloads")
    _assert_normalized_contains(artifact_contract, "downloadable provider payloads")
    _assert_normalized_contains(
        prompt_skill_contract,
        (
            "PromptVersion id/name/version and SkillVersion id/name/version "
            "when the application preflight evidence is produced by a prompt or skill"
        ),
    )
    _assert_normalized_contains(
        prompt_skill_contract,
        "Application preflight records are eligibility evidence only",
    )
    _assert_normalized_contains(
        prompt_skill_contract, "Provider-specific payloads must not leak"
    )
    _assert_normalized_contains(
        prompt_skill_contract, "must not be auto-marked true"
    )
    _assert_normalized_contains(contracts, "promote TestCase rows")
    _assert_normalized_contains(contracts, "create AutomationDraft rows")
    _assert_normalized_contains(contracts, "export/download endpoints")
    _assert_normalized_contains(contracts, "used_knowledge=true")


def _alias(term: str) -> str:
    aliases = {
        "generated_case_human_review_decision_application_preflight": (
            "generated_case_human_review_decision_application_preflight_action"
        ),
        "generated case human review decision application preflight id": (
            "Generated case human review decision application preflight id or preflight"
        ),
        "preflight artifact id": "preflight artifact id",
        "generated case human review decision audit handoff artifact": (
            "generated_case_human_review_decision_audit_handoff_artifact_id"
        ),
        "generated case human review decision audit handoff artifact id": (
            "generated_case_human_review_decision_audit_handoff_artifact_id"
        ),
        "generated case human review decision summary export artifact": (
            "generated_case_human_review_decision_summary_export_artifact_id"
        ),
        "generated case human review decision summary export artifact id": (
            "generated_case_human_review_decision_summary_export_artifact_id"
        ),
        "generated case human review decision artifact": (
            "generated_case_human_review_decision_artifact_id"
        ),
        "generated case human review evidence package artifact": (
            "generated_case_human_review_evidence_package_artifact_id"
        ),
        "source generated_case_human_review_decision_artifact_id values": (
            "generated_case_human_review_decision_artifact_id` values"
        ),
        "linked generated_case_human_review_evidence_package_artifact_id values": (
            "generated_case_human_review_evidence_package_artifact_id` values"
        ),
        "PromptVersion name/version": "PromptVersion id/name/version",
        "SkillVersion name/version": "SkillVersion id/name/version",
        "accepted-for-future-promotion preflight summary": (
            "accepted_for_future_promotion_preflight_summary"
        ),
        "accepted-with-required-edits preflight summary": (
            "accepted_with_required_edits_preflight_summary"
        ),
        "needs-optimization preflight summary": (
            "needs_optimization_preflight_summary"
        ),
        "rejected-for-insufficient-evidence preflight summary": (
            "rejected_for_insufficient_evidence_preflight_summary"
        ),
        "blocked preflight summary": "blocked_preflight_summary",
        "duplicate preflight summary": "duplicate_preflight_summary",
        "needs-more-evidence preflight summary": (
            "needs_more_evidence_preflight_summary"
        ),
        "failed-validation preflight summary": (
            "failed_validation_preflight_summary"
        ),
        "not approval": "not be treated as approval",
        "not rejection": "not be treated as approval, rejection",
        "not request optimization": "request optimization",
        "not TestCase promotion": "TestCase promotion",
        "not automation draft creation": "automation draft creation",
        "not report rendering": "render reports",
        "not export/download endpoint": "export/download endpoint",
        "failure_code": "failure code",
        "visible_reason": "visible reason",
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
