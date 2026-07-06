from __future__ import annotations

import re
from pathlib import Path


FIXTURE_PATH = Path(
    "docs/fixtures/44-generated-case-human-review-decision-summary-export-golden.md"
)
SLICE_PATH = Path(
    "docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")

EXPECTED_SURFACES = [
    "Generated Case Human Review Decision Summary Export",
    "build_generated_case_human_review_decision_summary_export",
    "generated_case_human_review_decision_summary_export",
    "generated_case_human_review_decision_artifact_id",
    "generated_case_human_review_evidence_package_artifact_id",
    "exported decision groups",
    "included decision artifact ids",
    "excluded decision artifact ids",
    "excluded decision artifact reasons",
    "source traceability summary",
    "ReviewHistory",
    "failure behavior",
]

REQUIRED_TERMS = [
    "generated_case_human_review_decision_summary_export_action",
    (
        "generated_case_human_review_decision_summary_export_action="
        "build_generated_case_human_review_decision_summary_export"
    ),
    "build_generated_case_human_review_decision_summary_export",
    "generated case human review decision summary export id",
    "generated case human review decision summary export artifact id",
    "generated_case_human_review_decision_summary_export_artifact_id",
    "generated_case_human_review_decision_summary_export",
    "generated_case_human_review_decision_summary_export.json",
    "artifact_type=generated_case_human_review_decision_summary_export",
    "manifest_kind=generated_case_human_review_decision_summary_export",
    "created_by_component=GeneratedCaseHumanReviewDecisionSummaryExport",
    "owner_entity_type=GeneratedCaseCandidate",
    "owner_entity_id=candidate_id",
    "owner_entity_type=AITask",
    "owner_entity_type=Project",
    "generated_case_human_review_decision_artifact_id",
    "generated_case_human_review_decision_artifact_ids",
    "generated_case_human_review_evidence_package_artifact_id",
    "generated_case_human_review_evidence_package_artifact_ids",
    "GeneratedCaseCandidate id",
    "candidate status",
    "candidate summary",
    "decision label",
    "decision status",
    "reviewer label",
    "reviewer comment",
    "accepted constraints",
    "requested edit fields",
    "optimization request summary",
    "rejection reasons",
    "blocker reasons",
    "duplicate resolution notes",
    "source manifest ids",
    "source hashes",
    "ReviewHistory ids",
    "ReviewHistory links",
    "PromptVersion id",
    "SkillVersion id",
    "PromptVersion name/version",
    "SkillVersion name/version",
    "exported decision groups",
    "accepted_for_future_promotion",
    "accepted_with_required_edits",
    "needs_optimization",
    "rejected_for_insufficient_evidence",
    "blocked",
    "duplicate",
    "needs_more_evidence",
    "failed_validation",
    "included decision artifact ids",
    "excluded decision artifact ids",
    "excluded decision artifact reasons",
    "source traceability summary",
    "ReviewHistory summary",
    "summary export audit evidence only",
    "audit evidence only",
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
    "missing, stale, unsafe, cross-project",
    "decision-artifact-missing",
    "decision-artifact-invalid",
    "decision-artifact-mismatched",
    "evidence-package-missing",
    "evidence-package-mismatched",
    "candidate-missing",
    "candidate-mismatched",
    "candidate-status-invalid",
    "review-decision-missing",
    "review-decision-invalid",
    "decision-label-unsupported",
    "reviewer-missing",
    "source-hash-mismatched",
    "review-history-missing",
    "artifact-mismatched",
    "summary-export-invalid",
    "credential-required",
    "runtime-required",
    "provider-required",
    "approval-required",
    "optimization-required",
    "promotion-required",
]

API_PAYLOAD_FIELDS = [
    "project_id",
    "generated_case_human_review_decision_summary_export_action",
    "generated_case_human_review_decision_artifact_ids",
    "generated_case_human_review_evidence_package_artifact_ids",
    "decisions",
    "generated_case_human_review_decision_artifact_id",
    "generated_case_human_review_evidence_package_artifact_id",
    "generated_case_candidate_id",
    "candidate_status",
    "candidate_summary",
    "decision_label",
    "decision_status",
    "reviewer_label",
    "reviewer_comment",
    "accepted_constraints",
    "requested_edit_fields",
    "optimization_request_summary",
    "rejection_reasons",
    "blocker_reasons",
    "duplicate_resolution_notes",
    "review_history_links",
    "source_manifest_ids",
    "source_hashes",
    "generated_case_human_review_decision_summary_export_artifact_id",
    "generated_case_human_review_decision_summary_export",
    "summary_status",
    "exported_decision_groups",
    "accepted_for_future_promotion_summary",
    "accepted_with_required_edits_summary",
    "needs_optimization_summary",
    "rejected_for_insufficient_evidence_summary",
    "blocked_summary",
    "duplicate_summary",
    "needs_more_evidence_summary",
    "failed_validation_summary",
    "included_decision_artifact_ids",
    "excluded_decision_artifact_ids",
    "excluded_decision_artifact_reasons",
    "source_traceability_summary",
    "failure_code",
    "visible_reason",
]

STATE_TRANSITIONS = [
    (
        "generated_case_human_review_decision_recorded -> "
        "generated_case_human_review_decision_summary_export_pending"
    ),
    (
        "generated_case_human_review_decision_summary_export_pending -> "
        "generated_case_human_review_decision_summary_exported_for_human_review_audit"
    ),
    (
        "generated_case_human_review_decision_summary_export_pending -> "
        "generated_case_human_review_decision_summary_export_incomplete"
    ),
    (
        "generated_case_human_review_decision_summary_export_pending -> "
        "generated_case_human_review_decision_summary_export_failed_validation"
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
    "automatic used_knowledge=true",
    "deterministic retrieval behavior change",
    "TestCase promotion",
    "GeneratedCaseCandidate approve/reject mutation",
    "GeneratedCaseCandidate content mutation",
    "request optimization mutation",
    "automation draft creation",
    "AutomationDraft rows",
    "ToolInvocation creation",
    "TestRun/TestResult creation",
    "artifact upload",
    "Artifact mutation",
    "source artifact mutation",
    "source evidence mutation",
    "prompt context evidence mutation",
    "KnowledgeEvidence mutation",
    "TestKnowledgeCard mutation",
    "ReviewHistory mutation",
    "historical evidence mutation",
    "runner behavior change",
    "remote CI provider behavior",
    "generated replacement evidence",
    "generated-case auto-approval",
    "review bypass",
    "RBAC",
    "tenants",
    "permissions",
]


def test_golden_generated_case_human_review_decision_summary_export_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_generated_case_human_review_decision_summary_export_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_generated_case_human_review_decision_summary_export_locks_api_payload_fields() -> None:
    fixture = _read(FIXTURE_PATH)
    api_contract = _read(API_CONTRACT_PATH)

    _assert_normalized_contains(
        api_contract,
        "Generated Case Human Review Decision Summary Export payload shape",
    )
    _assert_normalized_contains(
        api_contract,
        "Generated Case Human Review Decision Summary Export response shape",
    )

    for field in API_PAYLOAD_FIELDS:
        _assert_token_contains(fixture, field)
        _assert_token_contains(api_contract, field)


def test_golden_generated_case_human_review_decision_summary_export_forbids_runtime_side_effects() -> None:
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
        "created_by_component=GeneratedCaseHumanReviewDecisionSummaryExport",
    )
    _assert_normalized_contains(
        data_contract,
        (
            "generated_case_human_review_decision_summary_export_action="
            "build_generated_case_human_review_decision_summary_export"
        ),
    )
    _assert_normalized_contains(
        data_contract,
        "artifact_type=generated_case_human_review_decision_summary_export",
    )
    _assert_normalized_contains(
        api_contract, "must not append a successful summary export"
    )
    _assert_normalized_contains(api_contract, "summary export audit evidence only")
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
        "generated_case_human_review_decision_summary_export_failed_validation",
    )
    _assert_normalized_contains(
        artifact_contract,
        "artifact_type=generated_case_human_review_decision_summary_export",
    )
    _assert_normalized_contains(
        artifact_contract,
        "manifest_kind=generated_case_human_review_decision_summary_export",
    )
    _assert_normalized_contains(
        artifact_contract,
        "generated_case_human_review_decision_summary_export.json",
    )
    _assert_normalized_contains(artifact_contract, "raw LLM/provider payloads")
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
            "when the summary export evidence is produced by a prompt or skill"
        ),
    )
    _assert_normalized_contains(prompt_skill_contract, "audit evidence only")
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
        "generated_case_human_review_decision_summary_export": (
            "generated_case_human_review_decision_summary_export_action"
        ),
        "generated case human review decision summary export id": (
            "Generated case human review decision summary export id or artifact id"
        ),
        "generated case human review decision summary export artifact id": (
            "Generated case human review decision summary export id or artifact id"
        ),
        "generated_case_human_review_decision_summary_export_artifact_id": (
            "generated_case_human_review_decision_summary_export_artifact_id"
        ),
        "artifact_type=generated_case_human_review_decision_summary_export": (
            "artifact_type=generated_case_human_review_decision_summary_export"
        ),
        "manifest_kind=generated_case_human_review_decision_summary_export": (
            "manifest_kind=generated_case_human_review_decision_summary_export"
        ),
        "created_by_component=GeneratedCaseHumanReviewDecisionSummaryExport": (
            "created_by_component=GeneratedCaseHumanReviewDecisionSummaryExport"
        ),
        "owner_entity_type=GeneratedCaseCandidate": (
            "owner_entity_type=GeneratedCaseCandidate"
        ),
        "owner_entity_id=candidate_id": "owner_entity_id=candidate_id",
        "owner_entity_type=AITask": "owner_entity_type=AITask",
        "owner_entity_type=Project": "owner_entity_type=Project",
        "PromptVersion name/version": "PromptVersion id/name/version",
        "SkillVersion name/version": "SkillVersion id/name/version",
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
