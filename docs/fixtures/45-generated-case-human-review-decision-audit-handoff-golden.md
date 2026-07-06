# Generated Case Human Review Decision Audit Handoff Golden

This fixture proves Slice 57 remains a contract-only Generated Case Human
Review Decision Audit Handoff definition. It is audit handoff evidence only
and evidence-chain packages only, not approval, not rejection, not request
optimization, not TestCase promotion, not automation draft creation, not
backend runtime API, not a frontend page, not a report renderer, not an
export/download endpoint, not provider integration, not a provider SDK call,
not runtime retrieval, and not prompt execution.

## Generated Case Human Review Decision Audit Handoff Scenario

A future workflow may package one Slice 56 summary export artifact, source
decision artifacts, and linked evidence package artifacts into a bounded audit
handoff. The record must preserve the generated case human review decision
summary export artifact id, generated_case_human_review_decision_artifact_id,
generated_case_human_review_evidence_package_artifact_id, exported decision
groups, included decision artifact ids, excluded decision artifact ids,
excluded decision artifact reasons, included artifact ids, excluded artifact
reasons, evidence chain status, source traceability summary, source
traceability handoff summary, source manifest ids, source hashes,
ReviewHistory ids, ReviewHistory summary, ReviewHistory links, failure_code,
failure code, visible_reason, visible reason, and failure behavior without
approving or rejecting candidates.

| Surface | Required boundary |
|---|---|
| Generated Case Human Review Decision Audit Handoff | Audit handoff evidence only |
| build_generated_case_human_review_decision_audit_handoff | Future scoped audit handoff action only |
| generated_case_human_review_decision_audit_handoff | Artifact and manifest naming only |
| generated case human review decision summary export artifact | Required summary export source |
| generated case human review decision artifact | Required source decision artifact |
| generated case human review evidence package artifact | Required evidence package lineage |
| exported decision groups | Grouping labels only |
| evidence chain status | Audit label only |
| included artifact ids | Preserved chain references |
| excluded artifact reasons | Missing or invalid chain evidence remains visible |
| included decision artifact ids | Preserved source decision references |
| excluded decision artifact ids | Omitted decision references remain visible |
| excluded decision artifact reasons | Invalid decision evidence remains visible |
| unresolved follow-up flags | Future-planning follow-up only |
| unresolved blocker summary | Blocking evidence remains visible |
| source traceability summary | Source traceability rollup only |
| source traceability handoff summary | Handoff traceability rollup only |
| ReviewHistory | Human review trace remains visible |
| failure behavior | Invalid input fails without successful audit handoff |

## Generated Case Human Review Decision Audit Handoff Inputs

The contract must define:

- generated_case_human_review_decision_audit_handoff_action.
- generated_case_human_review_decision_audit_handoff_action=build_generated_case_human_review_decision_audit_handoff.
- build_generated_case_human_review_decision_audit_handoff.
- generated case human review decision audit handoff id.
- handoff artifact id.
- generated_case_human_review_decision_audit_handoff_artifact_id.
- generated_case_human_review_decision_audit_handoff.
- generated_case_human_review_decision_audit_handoff.json.
- artifact_type=generated_case_human_review_decision_audit_handoff.
- manifest_kind=generated_case_human_review_decision_audit_handoff.
- created_by_component=GeneratedCaseHumanReviewDecisionAuditHandoff.
- owner_entity_type=GeneratedCaseCandidate.
- owner_entity_id=candidate_id.
- owner_entity_type=AITask.
- owner_entity_type=Project.
- generated case human review decision summary export artifact id.
- generated_case_human_review_decision_summary_export_artifact_id.
- same-project.
- source generated_case_human_review_decision_artifact_id values.
- generated_case_human_review_decision_artifact_id.
- generated_case_human_review_decision_artifact_ids.
- linked generated_case_human_review_evidence_package_artifact_id values.
- generated_case_human_review_evidence_package_artifact_id.
- generated_case_human_review_evidence_package_artifact_ids.
- GeneratedCaseCandidate ids/statuses.
- candidate summaries.
- decision labels.
- decision statuses.
- source manifest ids.
- source hashes.
- ReviewHistory ids.
- ReviewHistory summary.
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

accepted_for_future_promotion handoff summary is a future-planning label only
and does not promote a TestCase. accepted_with_required_edits handoff summary
preserves requested edit fields but does not mutate GeneratedCaseCandidate
content. needs_optimization handoff summary preserves optimization request
summary but does not perform request optimization. rejected_for_insufficient
evidence handoff summary preserves rejection reasons but does not reject a
candidate. blocked handoff summary preserves blocker reasons and visible
reason. duplicate handoff summary preserves duplicate resolution notes but
does not merge or delete cases. needs_more_evidence handoff summary preserves
missing evidence. failed_validation handoff summary preserves failure_code,
failure code, visible_reason, and visible reason.

## Field-Level Keys

The audit handoff request and response evidence keeps these explicit payload
fields:

- project_id.
- generated_case_human_review_decision_audit_handoff_action.
- generated_case_human_review_decision_summary_export_artifact_id.
- generated_case_human_review_decision_artifact_ids.
- generated_case_human_review_evidence_package_artifact_ids.
- exported_decision_groups.
- included_decision_artifact_ids.
- excluded_decision_artifact_ids.
- excluded_decision_artifact_reasons.
- source_traceability_summary.
- review_history_summary.
- review_history_links.
- source_manifest_ids.
- source_hashes.
- failure_code.
- visible_reason.
- generated_case_human_review_decision_audit_handoff_artifact_id.
- generated_case_human_review_decision_audit_handoff.
- handoff_summary.
- evidence_chain_status.
- included_artifact_ids.
- excluded_artifact_reasons.
- accepted_for_future_promotion.
- accepted_with_required_edits.
- needs_optimization.
- rejected_for_insufficient_evidence.
- blocked.
- duplicate.
- needs_more_evidence.
- failed_validation.
- accepted_for_future_promotion_handoff_summary.
- accepted_with_required_edits_handoff_summary.
- needs_optimization_handoff_summary.
- rejected_for_insufficient_evidence_handoff_summary.
- blocked_handoff_summary.
- duplicate_handoff_summary.
- needs_more_evidence_handoff_summary.
- failed_validation_handoff_summary.
- unresolved_follow_up_flags.
- unresolved_blocker_summary.
- source_traceability_handoff_summary.

## Generated Case Human Review Decision Audit Handoff Outputs

Generated case human review decision audit handoff output may include:

- generated case human review decision audit handoff id.
- handoff artifact id.
- generated_case_human_review_decision_audit_handoff_artifact_id.
- generated_case_human_review_decision_audit_handoff.
- generated_case_human_review_decision_audit_handoff.json.
- artifact_type=generated_case_human_review_decision_audit_handoff.
- manifest_kind=generated_case_human_review_decision_audit_handoff.
- generated_case_human_review_decision_audit_handoff_pending.
- generated_case_human_review_decision_audit_handoff_complete.
- generated_case_human_review_decision_audit_handoff_incomplete.
- generated_case_human_review_decision_audit_handoff_blocked.
- generated_case_human_review_decision_audit_handoff_failed_validation.
- handoff summary.
- evidence chain status.
- complete.
- incomplete.
- blocked.
- failed_validation.
- included artifact ids.
- excluded artifact reasons.
- included decision artifact ids.
- excluded decision artifact ids.
- excluded decision artifact reasons.
- accepted-for-future-promotion handoff summary.
- accepted-with-required-edits handoff summary.
- needs-optimization handoff summary.
- rejected-for-insufficient-evidence handoff summary.
- blocked handoff summary.
- duplicate handoff summary.
- needs-more-evidence handoff summary.
- failed-validation handoff summary.
- unresolved follow-up flags.
- unresolved blocker summary.
- source traceability summary.
- source traceability handoff summary.
- ReviewHistory summary.
- ReviewHistory links.
- audit handoff evidence only.
- evidence-chain packages only.
- future-planning labels only.
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

Evidence chain status values complete, incomplete, blocked, and
failed_validation are audit labels only. They do not approve candidates,
reject candidates, request optimization, promote TestCase rows, create
AutomationDraft rows, execute automation, render reports, expose
export/download endpoints, or set used_knowledge=true.

## State Transitions

The audit handoff state contract preserves these planning-only transitions:

- generated_case_human_review_decision_summary_exported_for_human_review_audit -> generated_case_human_review_decision_audit_handoff_pending.
- generated_case_human_review_decision_summary_export_incomplete -> generated_case_human_review_decision_audit_handoff_pending.
- generated_case_human_review_decision_summary_export_failed_validation -> generated_case_human_review_decision_audit_handoff_failed_validation.
- generated_case_human_review_decision_audit_handoff_pending -> generated_case_human_review_decision_audit_handoff_complete.
- generated_case_human_review_decision_audit_handoff_pending -> generated_case_human_review_decision_audit_handoff_incomplete.
- generated_case_human_review_decision_audit_handoff_pending -> generated_case_human_review_decision_audit_handoff_blocked.
- generated_case_human_review_decision_audit_handoff_pending -> generated_case_human_review_decision_audit_handoff_failed_validation.

Existing human review transitions remain the only approval, rejection, or
request-optimization path.

## Failure Behavior

Generated case human review decision audit handoff must fail without a
successful audit handoff when input is invalid, stale, unsafe, cross-project,
unbounded, summary-export-missing, summary-export-invalid,
summary-export-mismatched, decision-artifact-missing,
decision-artifact-invalid, decision-artifact-mismatched,
evidence-package-missing, evidence-package-mismatched, candidate-missing,
candidate-mismatched, candidate-status-invalid, review-decision-missing,
review-decision-invalid, decision-label-unsupported, review-history-missing,
source-hash-mismatched, artifact-mismatched, incomplete-required-input,
credential-required, runtime-required, provider-required, approval-required,
optimization-required, or promotion-required.

Invalid generated case human review decision audit handoff input must produce
failure_code, failure code, visible_reason, and visible reason. It must not
append a successful audit handoff, append a successful ReviewHistory decision,
approve a candidate, reject a candidate, request optimization, promote a
TestCase, create an AutomationDraft, mutate GeneratedCaseCandidate content,
mutate generated case human review decision summary export artifacts, mutate
generated case human review decision artifacts, mutate evidence packages,
mutate ReviewHistory, mutate KnowledgeEvidence, mutate prompt context
evidence, mutate source evidence, render reports, expose export/download
endpoints, or set used_knowledge=true.

## Runtime Boundary

The Generated Case Human Review Decision Audit Handoff contract is not runtime
prompt assembly, UI rendering, report generation, report rendering, export
endpoint behavior, provider runtime, retrieval runtime, or automatic review
behavior:

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
- no execute AITasks.
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
- no artifact mutation outside declared audit handoff evidence.
- no source artifact mutation.
- no source evidence mutation.
- no prompt context evidence mutation.
- no KnowledgeEvidence mutation.
- no TestKnowledgeCard mutation.
- no ReviewHistory mutation.
- no successful ReviewHistory decision.
- no historical evidence mutation.
- no runner behavior change.
- no remote CI provider behavior.
- no generated replacement evidence.
- no generated-case auto-approval.
- no review bypass.
- no summary export artifact mutation.
- no generated case human review decision artifact mutation.
- no evidence package mutation.
- no raw LLM/provider payloads.
- no unbounded source text.
- no vector store payloads.
- no reranker traces.
- no graph runtime payloads.
- no executable prompt assembly payloads.
- no frontend-rendered markup.
- no report-rendered payloads.
- no export-rendered payloads.
- no downloadable provider payloads.
- no RBAC.
- no tenants.
- no permissions.
