# Generated Case Human Review Decision Summary Export Golden

This fixture proves Slice 56 remains a contract-only Generated Case Human
Review Decision Summary Export definition. It is summary export audit evidence
only, not approval, not rejection, not request optimization, not TestCase
promotion, not automation draft creation, not backend runtime API, not a
frontend page, not a report renderer, not an export/download endpoint, not
provider integration, not a provider SDK call, not runtime retrieval, and not
prompt execution.

## Generated Case Human Review Decision Summary Export Scenario

A future workflow may group one or more generated case human review decision
artifacts into a bounded audit summary. The record must preserve
generated_case_human_review_decision_artifact_id,
generated_case_human_review_evidence_package_artifact_id,
GeneratedCaseCandidate id, candidate status, candidate summary, decision
label, decision status, reviewer label, reviewer comment, accepted
constraints, requested edit fields, optimization request summary, rejection
reasons, blocker reasons, duplicate resolution notes, source manifest ids,
source hashes, ReviewHistory ids, ReviewHistory links, failure_code, failure
code, visible_reason, visible reason, and failure behavior without approving
or rejecting candidates.

| Surface | Required boundary |
|---|---|
| Generated Case Human Review Decision Summary Export | Summary export audit evidence only |
| build_generated_case_human_review_decision_summary_export | Future scoped summary export action only |
| generated_case_human_review_decision_summary_export | Artifact and manifest naming only |
| generated_case_human_review_decision_artifact_id | Required source decision artifact |
| generated_case_human_review_evidence_package_artifact_id | Required evidence package lineage |
| exported decision groups | Grouping labels only |
| included decision artifact ids | Preserved source decision references |
| excluded decision artifact ids | Omitted decision references remain visible |
| excluded decision artifact reasons | Missing or invalid decision evidence remains visible |
| source traceability summary | Source traceability rollup only |
| ReviewHistory | Human review trace remains visible |
| failure behavior | Invalid input fails without successful summary export |

## Generated Case Human Review Decision Summary Export Inputs

The contract must define:

- generated_case_human_review_decision_summary_export_action.
- generated_case_human_review_decision_summary_export_action=build_generated_case_human_review_decision_summary_export.
- build_generated_case_human_review_decision_summary_export.
- generated case human review decision summary export id.
- generated case human review decision summary export artifact id.
- generated_case_human_review_decision_summary_export_artifact_id.
- generated_case_human_review_decision_summary_export.
- generated_case_human_review_decision_summary_export.json.
- artifact_type=generated_case_human_review_decision_summary_export.
- manifest_kind=generated_case_human_review_decision_summary_export.
- created_by_component=GeneratedCaseHumanReviewDecisionSummaryExport.
- owner_entity_type=GeneratedCaseCandidate.
- owner_entity_id=candidate_id.
- owner_entity_type=AITask.
- owner_entity_type=Project.
- generated_case_human_review_decision_artifact_id.
- generated_case_human_review_decision_artifact_ids.
- generated_case_human_review_evidence_package_artifact_id.
- generated_case_human_review_evidence_package_artifact_ids.
- GeneratedCaseCandidate id.
- candidate status.
- candidate summary.
- decision label.
- decision status.
- reviewer label.
- reviewer comment.
- accepted constraints.
- requested edit fields.
- optimization request summary.
- rejection reasons.
- blocker reasons.
- duplicate resolution notes.
- source manifest ids.
- source hashes.
- ReviewHistory ids.
- ReviewHistory links.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.

## Decision Groups

The contract must keep these exported decision groups as evidence-only values:

- accepted_for_future_promotion.
- accepted_with_required_edits.
- needs_optimization.
- rejected_for_insufficient_evidence.
- blocked.
- duplicate.
- needs_more_evidence.
- failed_validation.

accepted_for_future_promotion summary does not promote a TestCase.
accepted_with_required_edits summary preserves requested edit fields but does
not mutate GeneratedCaseCandidate content. needs_optimization summary
preserves optimization request summary but does not perform request
optimization. rejected_for_insufficient_evidence summary preserves rejection
reasons but does not reject a candidate. blocked summary preserves blocker
reasons and visible reason. duplicate summary preserves duplicate resolution
notes but does not merge or delete cases. needs_more_evidence summary
preserves missing evidence. failed_validation summary preserves failure_code,
failure code, visible_reason, and visible reason.

## Field-Level Keys

The summary export request and response evidence keeps these explicit payload
fields:

- project_id.
- generated_case_human_review_decision_summary_export_action.
- generated_case_human_review_decision_artifact_ids.
- generated_case_human_review_evidence_package_artifact_ids.
- decisions.
- generated_case_human_review_decision_artifact_id.
- generated_case_human_review_evidence_package_artifact_id.
- generated_case_candidate_id.
- candidate_status.
- candidate_summary.
- decision_label.
- decision_status.
- reviewer_label.
- reviewer_comment.
- accepted_constraints.
- requested_edit_fields.
- optimization_request_summary.
- rejection_reasons.
- blocker_reasons.
- duplicate_resolution_notes.
- review_history_links.
- source_manifest_ids.
- source_hashes.
- generated_case_human_review_decision_summary_export_artifact_id.
- generated_case_human_review_decision_summary_export.
- summary_status.
- exported_decision_groups.
- accepted_for_future_promotion_summary.
- accepted_with_required_edits_summary.
- needs_optimization_summary.
- rejected_for_insufficient_evidence_summary.
- blocked_summary.
- duplicate_summary.
- needs_more_evidence_summary.
- failed_validation_summary.
- included_decision_artifact_ids.
- excluded_decision_artifact_ids.
- excluded_decision_artifact_reasons.
- source_traceability_summary.
- failure_code.
- visible_reason.

## Generated Case Human Review Decision Summary Export Outputs

Generated case human review decision summary export output may include:

- generated case human review decision summary export id.
- generated case human review decision summary export artifact id.
- generated_case_human_review_decision_summary_export_artifact_id.
- generated_case_human_review_decision_summary_export.
- generated_case_human_review_decision_summary_export.json.
- artifact_type=generated_case_human_review_decision_summary_export.
- manifest_kind=generated_case_human_review_decision_summary_export.
- generated_case_human_review_decision_summary_export_pending.
- generated_case_human_review_decision_summary_exported_for_human_review_audit.
- generated_case_human_review_decision_summary_export_incomplete.
- generated_case_human_review_decision_summary_export_failed_validation.
- summary status.
- exported decision groups.
- accepted_for_future_promotion.
- accepted_with_required_edits.
- needs_optimization.
- rejected_for_insufficient_evidence.
- blocked.
- duplicate.
- needs_more_evidence.
- failed_validation.
- accepted-for-future-promotion summary.
- accepted-with-required-edits summary.
- needs-optimization summary.
- rejected-for-insufficient-evidence summary.
- blocked summary.
- duplicate summary.
- needs-more-evidence summary.
- failed-validation summary.
- included decision artifact ids.
- excluded decision artifact ids.
- excluded decision artifact reasons.
- source traceability summary.
- ReviewHistory summary.
- summary export audit evidence only.
- audit evidence only.
- not approval.
- not rejection.
- not request optimization.
- not TestCase promotion.
- not automation draft creation.
- not report rendering.
- not export/download endpoint.
- used_knowledge=true.
- prompt_input.json.
- failure_code.
- failure code.
- visible_reason.
- visible reason.

Exported decision groups, included decision artifact ids, excluded decision
artifact ids, excluded decision artifact reasons, source traceability summary,
source hashes, source manifest ids, and ReviewHistory links are evidence
labels. They do not approve candidates, reject candidates, request
optimization, promote TestCase rows, create AutomationDraft rows, execute
automation, render reports, expose export/download endpoints, or set
used_knowledge=true.

## Failure Behavior

Generated case human review decision summary export must fail without a
successful summary export when input is missing, stale, unsafe, cross-project,
unbounded, decision-artifact-missing, decision-artifact-invalid,
decision-artifact-mismatched, evidence-package-missing,
evidence-package-mismatched, candidate-missing, candidate-mismatched,
candidate-status-invalid, review-decision-missing, review-decision-invalid,
decision-label-unsupported, reviewer-missing, source-hash-mismatched,
review-history-missing, artifact-mismatched, summary-export-invalid,
credential-required, runtime-required, provider-required, approval-required,
optimization-required, or promotion-required.

Invalid generated case human review decision summary export input must
produce failure_code, failure code, visible_reason, and visible reason. It
must not append a successful summary export, append a successful ReviewHistory
decision, approve a candidate, reject a candidate, request optimization,
promote a TestCase, create an AutomationDraft, mutate GeneratedCaseCandidate
content, mutate generated case human review decision artifacts, mutate
evidence packages, mutate ReviewHistory, mutate KnowledgeEvidence, mutate
prompt context evidence, mutate source evidence, render reports, expose
export/download endpoints, or set used_knowledge=true.

## Runtime Boundary

The Generated Case Human Review Decision Summary Export contract is not
runtime prompt assembly, UI rendering, report generation, report rendering,
export endpoint behavior, provider runtime, retrieval runtime, or automatic
review behavior:

- no backend runtime API.
- no backend feature API.
- no endpoint.
- no router.
- no service.
- no worker.
- no queue.
- no scheduler.
- no migration.
- no package upgrade.
- no frontend page.
- no frontend store.
- no frontend component.
- no report generation behavior.
- no report renderer.
- no export/download endpoint.
- no provider integration.
- no provider SDK.
- no provider SDK call.
- no external call.
- no credentials.
- no API keys.
- no tokens.
- no OAuth.
- no remote URL fetch.
- no remote fetch payloads.
- no vector database.
- no vector index.
- no embedding.
- no embeddings.
- no embedding vectors.
- no reranking.
- no graph runtime.
- no GraphRAG job.
- no MCP runtime.
- no runtime retrieval.
- no provider-backed prompt context evidence.
- no prompt execution.
- no prompt assembly.
- no runtime prompt_input.json.
- no AITask orchestration.
- no automatic used_knowledge=true.
- no deterministic retrieval behavior change.
- no TestCase promotion.
- no GeneratedCaseCandidate approve/reject mutation.
- no GeneratedCaseCandidate content mutation.
- no request optimization mutation.
- no automation draft creation.
- no AutomationDraft rows.
- no ToolInvocation creation.
- no TestRun/TestResult creation.
- no artifact upload.
- no Artifact mutation.
- no source artifact mutation.
- no source evidence mutation.
- no prompt context evidence mutation.
- no KnowledgeEvidence mutation.
- no TestKnowledgeCard mutation.
- no ReviewHistory mutation.
- no historical evidence mutation.
- no runner behavior change.
- no remote CI provider behavior.
- no generated replacement evidence.
- no generated-case auto-approval.
- no review bypass.
- no RBAC.
- no tenants.
- no permissions.
