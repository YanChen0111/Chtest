from __future__ import annotations

import re
from pathlib import Path


FIXTURE_PATH = Path(
    "docs/fixtures/42-generated-case-human-review-evidence-package-golden.md"
)
SLICE_PATH = Path(
    "docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md"
)
DATA_CONTRACT_PATH = Path("docs/contracts/01-data-model-contract.md")
API_CONTRACT_PATH = Path("docs/contracts/02-api-contract.md")
STATE_CONTRACT_PATH = Path("docs/contracts/03-state-machines.md")
ARTIFACT_CONTRACT_PATH = Path("docs/contracts/04-artifact-contract.md")
PROMPT_SKILL_CONTRACT_PATH = Path("docs/contracts/05-prompt-skill-contract.md")

EXPECTED_SURFACES = [
    "Generated Case Human Review Evidence Package",
    "build_generated_case_human_review_evidence_package",
    "generated_case_human_review_evidence_package",
    "GeneratedCaseCandidate",
    "candidate summary",
    "source_knowledge_evidence_ids",
    "knowledge_evidence_refs_json",
    "quality_score",
    "review_findings_json",
    "coverage_gap_notes",
    "automation_readiness",
    "dedup findings",
    "prompt context evidence artifact ids",
    "prompt context consumption artifact ids",
    "prompt context discrepancy resolution audit handoff artifact ids",
    "evidence chain completeness",
    "missing evidence summary",
    "conflicting evidence summary",
    "review blocker summary",
    "dedup/readiness summary",
    "human review checklist",
    "ReviewHistory",
    "failure behavior",
]

REQUIRED_TERMS = [
    "generated_case_human_review_evidence_package_action",
    (
        "generated_case_human_review_evidence_package_action="
        "build_generated_case_human_review_evidence_package"
    ),
    "build_generated_case_human_review_evidence_package",
    "generated case human review evidence package id",
    "generated case human review evidence package artifact id",
    "generated_case_human_review_evidence_package_artifact_id",
    "generated_case_human_review_evidence_package.json",
    "artifact_type=generated_case_human_review_evidence_package",
    "manifest_kind=generated_case_human_review_evidence_package",
    "created_by_component=GeneratedCaseHumanReviewEvidencePackage",
    "owner_entity_type=GeneratedCaseCandidate",
    "owner_entity_id=candidate_id",
    "owner_entity_type=AITask",
    "GeneratedCaseCandidate id",
    "candidate status",
    "candidate summary",
    "candidate title",
    "candidate priority",
    "candidate test type",
    "candidate precondition",
    "candidate steps",
    "candidate expected results",
    "candidate input data",
    "candidate tags",
    "requirement refs",
    "risk refs",
    "ai_reason",
    "generation reason",
    "covered risk ids",
    "duplicate-of case id",
    "source_knowledge_evidence_ids",
    "knowledge_evidence_refs_json",
    "quality_score",
    "review_findings_json",
    "coverage_gap_notes",
    "automation_readiness",
    "dedup findings",
    "duplicate candidate ids",
    "automation readiness blockers",
    "prompt context evidence artifact ids",
    "prompt context consumption artifact ids",
    "prompt context audit summary artifact ids",
    "prompt context audit review decision artifact ids",
    "prompt context audit review summary export artifact ids",
    "prompt context discrepancy resolution audit handoff artifact ids",
    "source manifest ids",
    "source hashes",
    "ReviewHistory ids",
    "ReviewHistory links",
    "evidence chain completeness",
    "complete",
    "incomplete",
    "blocked",
    "failed_validation",
    "missing evidence summary",
    "conflicting evidence summary",
    "review blocker summary",
    "dedup/readiness summary",
    "human review checklist",
    "included artifact ids",
    "excluded artifact reasons",
    "PromptVersion id",
    "SkillVersion id",
    "PromptVersion name/version",
    "SkillVersion name/version",
    "human-review evidence only",
    "review aids only",
    "not approval",
    "not rejection",
    "not TestCase promotion",
    "not automation draft creation",
    "used_knowledge=true",
    "prompt_input.json",
    "failure_code",
    "failure code",
    "visible_reason",
    "visible reason",
    "missing, stale, unsafe, cross-project",
    "candidate-missing",
    "candidate-mismatched",
    "candidate-status-invalid",
    "knowledge-evidence-missing",
    "prompt-context-evidence-missing",
    "review-findings-missing",
    "dedup-inconclusive",
    "readiness-unknown",
    "review-history-missing",
    "artifact-mismatched",
    "source-hash-mismatched",
    "credential-required",
    "runtime-required",
    "provider-required",
    "approval-required",
    "promotion-required",
]

API_PAYLOAD_FIELDS = [
    "project_id",
    "generated_case_human_review_evidence_package_action",
    "generated_case_candidate_id",
    "candidate_status",
    "candidate_title",
    "candidate_priority",
    "candidate_test_type",
    "candidate_precondition",
    "candidate_steps",
    "candidate_expected_results",
    "candidate_input_data",
    "candidate_tags",
    "requirement_refs",
    "risk_refs",
    "ai_reason",
    "generation_reason",
    "covered_risk_ids",
    "duplicate_of_case_id",
    "source_knowledge_evidence_ids",
    "knowledge_evidence_refs_json",
    "quality_score",
    "review_findings_json",
    "coverage_gap_notes",
    "automation_readiness",
    "dedup_findings",
    "duplicate_candidate_ids",
    "automation_readiness_blockers",
    "prompt_context_evidence_artifact_ids",
    "prompt_context_consumption_artifact_ids",
    "prompt_context_audit_summary_artifact_ids",
    "prompt_context_audit_review_decision_artifact_ids",
    "prompt_context_audit_review_summary_export_artifact_ids",
    "prompt_context_discrepancy_resolution_audit_handoff_artifact_ids",
    "source_manifest_ids",
    "source_hashes",
    "review_history_links",
    "generated_case_human_review_evidence_package_artifact_id",
    "generated_case_human_review_evidence_package",
    "candidate_summary",
    "evidence_chain_completeness",
    "missing_evidence_summary",
    "conflicting_evidence_summary",
    "review_blocker_summary",
    "dedup_readiness_summary",
    "human_review_checklist",
    "included_artifact_ids",
    "excluded_artifact_reasons",
    "failure_code",
    "visible_reason",
]

STATE_TRANSITIONS = [
    "generated -> generated_case_human_review_evidence_package_pending",
    "under_review -> generated_case_human_review_evidence_package_pending",
    "needs_optimization -> generated_case_human_review_evidence_package_pending",
    (
        "optimization_pending_review -> "
        "generated_case_human_review_evidence_package_pending"
    ),
    (
        "generated_case_human_review_evidence_package_pending -> "
        "generated_case_human_review_evidence_package_complete"
    ),
    (
        "generated_case_human_review_evidence_package_pending -> "
        "generated_case_human_review_evidence_package_incomplete"
    ),
    (
        "generated_case_human_review_evidence_package_pending -> "
        "generated_case_human_review_evidence_package_blocked"
    ),
    (
        "generated_case_human_review_evidence_package_pending -> "
        "generated_case_human_review_evidence_package_failed_validation"
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
    "automation draft creation",
    "AutomationDraft rows",
    "ToolInvocation creation",
    "TestRun/TestResult creation",
    "artifact upload",
    "Artifact mutation",
    "source artifact mutation",
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


def test_golden_generated_case_human_review_evidence_package_names_surfaces() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for surface in EXPECTED_SURFACES:
        _assert_normalized_contains(fixture, surface)
        _assert_any_contains([slice_plan, contracts], _alias(surface))


def test_golden_generated_case_human_review_evidence_package_has_required_terms() -> None:
    fixture = _read(FIXTURE_PATH)
    slice_plan = _read(SLICE_PATH)
    contracts = _contracts_text()

    for term in REQUIRED_TERMS:
        _assert_normalized_contains(fixture, term)
        _assert_any_contains([slice_plan, contracts], _alias(term))


def test_golden_generated_case_human_review_evidence_package_locks_api_payload_fields() -> None:
    fixture = _read(FIXTURE_PATH)
    api_contract = _read(API_CONTRACT_PATH)

    _assert_normalized_contains(
        api_contract,
        "Generated Case Human Review Evidence Package payload shape",
    )
    _assert_normalized_contains(
        api_contract,
        "Generated Case Human Review Evidence Package response shape",
    )

    for field in API_PAYLOAD_FIELDS:
        _assert_token_contains(fixture, field)
        _assert_token_contains(api_contract, field)


def test_golden_generated_case_human_review_evidence_package_forbids_runtime_side_effects() -> None:
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
        "created_by_component=GeneratedCaseHumanReviewEvidencePackage",
    )
    _assert_normalized_contains(
        data_contract,
        (
            "generated_case_human_review_evidence_package_action="
            "build_generated_case_human_review_evidence_package"
        ),
    )
    _assert_normalized_contains(
        data_contract,
        "artifact_type=generated_case_human_review_evidence_package",
    )
    _assert_normalized_contains(
        api_contract, "must not append a successful evidence package"
    )
    _assert_normalized_contains(api_contract, "human-review evidence only")
    _assert_normalized_contains(
        api_contract, "GeneratedCaseCandidate approve/reject mutation"
    )
    _assert_normalized_contains(
        state_contract,
        "generated_case_human_review_evidence_package_failed_validation",
    )
    for transition in STATE_TRANSITIONS:
        _assert_normalized_contains(state_contract, transition)
    _assert_normalized_contains(
        state_contract, "Existing human review transitions remain"
    )
    _assert_normalized_contains(
        artifact_contract,
        "artifact_type=generated_case_human_review_evidence_package",
    )
    _assert_normalized_contains(
        artifact_contract,
        "manifest_kind=generated_case_human_review_evidence_package",
    )
    _assert_normalized_contains(
        artifact_contract,
        "generated_case_human_review_evidence_package.json",
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
            "when the evidence package is produced by a prompt or skill"
        ),
    )
    _assert_normalized_contains(
        prompt_skill_contract, "review aids only"
    )
    _assert_normalized_contains(
        prompt_skill_contract, "Provider-specific payloads must not leak"
    )
    _assert_normalized_contains(
        prompt_skill_contract, "must not be auto-marked true"
    )
    _assert_normalized_contains(contracts, "mutate GeneratedCaseCandidate rows")
    _assert_normalized_contains(contracts, "promote TestCase rows")
    _assert_normalized_contains(contracts, "create AutomationDraft rows")
    _assert_normalized_contains(contracts, "used_knowledge=true")


def _alias(term: str) -> str:
    aliases = {
        "generated_case_human_review_evidence_package": (
            "generated_case_human_review_evidence_package_action"
        ),
        "generated_case_human_review_evidence_package_action": (
            "build_generated_case_human_review_evidence_package"
        ),
        (
            "generated_case_human_review_evidence_package_action="
            "build_generated_case_human_review_evidence_package"
        ): (
            "generated_case_human_review_evidence_package_action="
            "build_generated_case_human_review_evidence_package"
        ),
        "generated case human review evidence package id": (
            "Generated case human review evidence package id or artifact id"
        ),
        "generated case human review evidence package artifact id": (
            "Generated case human review evidence package id or artifact id"
        ),
        "generated_case_human_review_evidence_package_artifact_id": (
            "generated_case_human_review_evidence_package_artifact_id"
        ),
        "candidate title": "candidate_title",
        "candidate priority": "candidate_priority",
        "candidate test type": "candidate_test_type",
        "candidate precondition": "candidate_precondition",
        "candidate steps": "candidate_steps",
        "candidate expected results": "candidate_expected_results",
        "candidate input data": "candidate_input_data",
        "candidate tags": "candidate_tags",
        "ai_reason": "ai_reason",
        "generation reason": "generation_reason",
        "duplicate-of case id": "duplicate-of case id",
        "prompt context artifact lineage": "prompt context artifact lineage",
        "artifact_type=generated_case_human_review_evidence_package": (
            "artifact_type=generated_case_human_review_evidence_package"
        ),
        "manifest_kind=generated_case_human_review_evidence_package": (
            "manifest_kind=generated_case_human_review_evidence_package"
        ),
        "created_by_component=GeneratedCaseHumanReviewEvidencePackage": (
            "created_by_component=GeneratedCaseHumanReviewEvidencePackage"
        ),
        "owner_entity_type=GeneratedCaseCandidate": (
            "owner_entity_type=GeneratedCaseCandidate"
        ),
        "owner_entity_id=candidate_id": "owner_entity_id=candidate_id",
        "owner_entity_type=AITask": "owner_entity_type=AITask",
        "not approval": "not be treated as approval",
        "not rejection": "not be treated as approval, rejection",
        "not TestCase promotion": "TestCase promotion",
        "not automation draft creation": "automation draft creation",
        "review aids only": "review aids only",
        "failure_code": "failure code",
        "visible_reason": "visible reason",
        "PromptVersion name/version": "PromptVersion id/name/version",
        "SkillVersion name/version": "SkillVersion id/name/version",
        "provider SDK": "provider SDK calls",
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
