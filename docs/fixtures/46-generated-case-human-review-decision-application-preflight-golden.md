# Generated Case Human Review Decision Application Preflight Golden

This fixture proves Slice 58 remains a contract-only Generated Case Human
Review Decision Application Preflight definition. It is application preflight
eligibility evidence only, not approval, not rejection, not request
optimization, not TestCase promotion, not automation draft creation, not
backend runtime API, not a frontend page, not a report renderer, not an
export/download endpoint, not provider integration, not a provider SDK call,
not runtime retrieval, and not prompt execution.

## Generated Case Human Review Decision Application Preflight Scenario

A future workflow may read one Slice 57 audit handoff artifact, the linked
summary export artifact, source decision artifacts, and linked evidence
package artifacts to produce bounded eligibility evidence. The record must
preserve the generated case human review decision audit handoff artifact id,
generated case human review decision summary export artifact id,
generated_case_human_review_decision_artifact_id,
generated_case_human_review_evidence_package_artifact_id, mapped review
action, eligibility status, eligible candidate ids, ineligible candidate ids,
blocked action reasons, required edit summary, required human confirmation
summary, ReviewHistory handoff links, source traceability handoff summary,
source manifest ids, source hashes, failure_code, failure code,
visible_reason, visible reason, and failure behavior without applying any
review action.

| Surface | Required boundary |
|---|---|
| Generated Case Human Review Decision Application Preflight | Application preflight eligibility evidence only |
| preflight_generated_case_human_review_decision_application | Future scoped application preflight action only |
| generated_case_human_review_decision_application_preflight | Artifact and manifest naming only |
| generated case human review decision audit handoff artifact | Required audit handoff source |
| generated case human review decision summary export artifact | Required summary export source |
| generated case human review decision artifact | Required source decision artifact |
| generated case human review evidence package artifact | Required evidence package lineage |
| mapped review action | Planned action label only |
| eligibility status | Preflight label only |
| eligible candidate ids | Eligible evidence references only |
| ineligible candidate ids | Ineligible evidence references only |
| blocked action reasons | Blocking evidence remains visible |
| required edit summary | Future edit confirmation evidence only |
| required human confirmation summary | Explicit confirmation remains visible |
| ReviewHistory | Human review trace remains visible |
| failure behavior | Invalid input fails without successful application preflight |

## Generated Case Human Review Decision Application Preflight Inputs

The contract must define:

- generated_case_human_review_decision_application_preflight_action.
- generated_case_human_review_decision_application_preflight_action=preflight_generated_case_human_review_decision_application.
- preflight_generated_case_human_review_decision_application.
- generated case human review decision application preflight id.
- preflight artifact id.
- generated_case_human_review_decision_application_preflight_artifact_id.
- generated_case_human_review_decision_application_preflight.
- generated_case_human_review_decision_application_preflight.json.
- artifact_type=generated_case_human_review_decision_application_preflight.
- manifest_kind=generated_case_human_review_decision_application_preflight.
- created_by_component=GeneratedCaseHumanReviewDecisionApplicationPreflight.
- owner_entity_type=GeneratedCaseCandidate.
- owner_entity_id=candidate_id.
- owner_entity_type=AITask.
- owner_entity_type=Project.
- same-project.
- generated case human review decision audit handoff artifact id.
- generated_case_human_review_decision_audit_handoff_artifact_id.
- generated case human review decision summary export artifact id.
- generated_case_human_review_decision_summary_export_artifact_id.
- source generated_case_human_review_decision_artifact_id values.
- generated_case_human_review_decision_artifact_id.
- generated_case_human_review_decision_artifact_ids.
- linked generated_case_human_review_evidence_package_artifact_id values.
- generated_case_human_review_evidence_package_artifact_id.
- generated_case_human_review_evidence_package_artifact_ids.
- GeneratedCaseCandidate ids/statuses.
- generated_case_candidate_id.
- candidate_status.
- candidate status.
- decision_label.
- decision labels.
- requested_edit_fields.
- requested edit fields.
- accepted_constraints.
- accepted constraints.
- optimization_request_summary.
- optimization request summary.
- rejection_reasons.
- rejection reasons.
- blocker_reasons.
- blocker reasons.
- duplicate_resolution_notes.
- duplicate resolution notes.
- evidence_chain_status.
- evidence chain status.
- unresolved_follow_up_flags.
- unresolved follow-up flags.
- unresolved_blocker_summary.
- unresolved blocker summary.
- source_traceability_handoff_summary.
- source traceability handoff summary.
- review_history_handoff_links.
- ReviewHistory handoff links.
- source_manifest_ids.
- source manifest ids.
- source_hashes.
- source hashes.
- required_human_confirmation_summary.
- required human confirmation summary.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.

## Decision-Label Mapping

The preflight contract must keep these decision labels as strict mapping
inputs:

- accepted_for_future_promotion.
- accepted_with_required_edits.
- needs_optimization.
- rejected_for_insufficient_evidence.
- blocked.
- duplicate.
- needs_more_evidence.
- failed_validation.

accepted_for_future_promotion may map only to mapped_review_action approve
when the evidence chain is complete, the candidate status is reviewable, and
required human confirmation summary is present. accepted_with_required_edits
may map only to mapped_review_action approve_after_edit when requested edit
fields are present and bounded. needs_optimization may map only to
mapped_review_action request_optimization when optimization request summary is
present and bounded. rejected_for_insufficient_evidence may map only to
mapped_review_action reject when rejection reasons and visible reason are
present. blocked, duplicate, needs_more_evidence, and failed_validation must
map to mapped_review_action none and remain ineligible until a later explicit
human action resolves them.

## Field-Level Keys

The application preflight request and response evidence keeps these explicit
payload fields:

- project_id.
- decisions.
- generated_case_human_review_decision_application_preflight_action.
- generated_case_human_review_decision_audit_handoff_artifact_id.
- generated_case_human_review_decision_summary_export_artifact_id.
- generated_case_human_review_decision_artifact_id.
- generated_case_human_review_decision_artifact_ids.
- generated_case_human_review_evidence_package_artifact_id.
- generated_case_human_review_evidence_package_artifact_ids.
- generated_case_candidate_id.
- candidate_status.
- decision_label.
- requested_edit_fields.
- accepted_constraints.
- optimization_request_summary.
- rejection_reasons.
- blocker_reasons.
- duplicate_resolution_notes.
- evidence_chain_status.
- unresolved_follow_up_flags.
- unresolved_blocker_summary.
- source_traceability_handoff_summary.
- review_history_handoff_links.
- source_manifest_ids.
- source_hashes.
- required_human_confirmation_summary.
- generated_case_human_review_decision_application_preflight_artifact_id.
- generated_case_human_review_decision_application_preflight.
- preflight_summary.
- eligibility_status.
- mapped_review_action.
- eligible_candidate_ids.
- ineligible_candidate_ids.
- blocked_action_reasons.
- required_edit_summary.
- accepted_for_future_promotion_preflight_summary.
- accepted_with_required_edits_preflight_summary.
- needs_optimization_preflight_summary.
- rejected_for_insufficient_evidence_preflight_summary.
- blocked_preflight_summary.
- duplicate_preflight_summary.
- needs_more_evidence_preflight_summary.
- failed_validation_preflight_summary.
- failure_code.
- visible_reason.

## Generated Case Human Review Decision Application Preflight Outputs

Generated case human review decision application preflight output may include:

- generated case human review decision application preflight id.
- preflight artifact id.
- generated_case_human_review_decision_application_preflight_artifact_id.
- generated_case_human_review_decision_application_preflight.
- generated_case_human_review_decision_application_preflight.json.
- artifact_type=generated_case_human_review_decision_application_preflight.
- manifest_kind=generated_case_human_review_decision_application_preflight.
- generated_case_human_review_decision_application_preflight_pending.
- generated_case_human_review_decision_application_preflight_eligible.
- generated_case_human_review_decision_application_preflight_ineligible.
- generated_case_human_review_decision_application_preflight_blocked.
- generated_case_human_review_decision_application_preflight_failed_validation.
- preflight summary.
- eligibility status.
- eligible.
- ineligible.
- blocked.
- failed_validation.
- mapped review action.
- approve.
- approve_after_edit.
- request_optimization.
- reject.
- none.
- eligible candidate ids.
- ineligible candidate ids.
- blocked action reasons.
- required edit summary.
- required human confirmation summary.
- accepted-for-future-promotion preflight summary.
- accepted-with-required-edits preflight summary.
- needs-optimization preflight summary.
- rejected-for-insufficient-evidence preflight summary.
- blocked preflight summary.
- duplicate preflight summary.
- needs-more-evidence preflight summary.
- failed-validation preflight summary.
- source traceability handoff summary.
- ReviewHistory handoff links.
- application preflight eligibility evidence only.
- eligibility evidence only.
- planned action labels only.
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

Eligibility status values eligible, ineligible, blocked, and failed_validation
are preflight labels only. They do not approve candidates, reject candidates,
request optimization, promote TestCase rows, create AutomationDraft rows,
execute automation, render reports, expose export/download endpoints, or set
used_knowledge=true.

## State Transitions

The application preflight state contract preserves these planning-only
transitions:

- generated_case_human_review_decision_audit_handoff_complete -> generated_case_human_review_decision_application_preflight_pending.
- generated_case_human_review_decision_audit_handoff_incomplete -> generated_case_human_review_decision_application_preflight_pending.
- generated_case_human_review_decision_audit_handoff_blocked -> generated_case_human_review_decision_application_preflight_pending.
- generated_case_human_review_decision_audit_handoff_failed_validation -> generated_case_human_review_decision_application_preflight_failed_validation.
- generated_case_human_review_decision_application_preflight_pending -> generated_case_human_review_decision_application_preflight_eligible.
- generated_case_human_review_decision_application_preflight_pending -> generated_case_human_review_decision_application_preflight_ineligible.
- generated_case_human_review_decision_application_preflight_pending -> generated_case_human_review_decision_application_preflight_blocked.
- generated_case_human_review_decision_application_preflight_pending -> generated_case_human_review_decision_application_preflight_failed_validation.

Existing human review transitions remain the only approval,
rejection, or request-optimization path. The preflight must not call the
existing case-review action.

## Failure Behavior

Generated case human review decision application preflight must fail without a
successful application preflight when input is invalid, stale, unsafe,
cross-project, unbounded, audit-handoff-missing, audit-handoff-invalid,
audit-handoff-mismatched, summary-export-missing, summary-export-invalid,
summary-export-mismatched, decision-artifact-missing,
decision-artifact-invalid, decision-artifact-mismatched,
evidence-package-missing, evidence-package-mismatched, candidate-missing,
candidate-mismatched, candidate-status-invalid, decision-label-unsupported,
mapped-action-unsupported, required-edit-missing,
required-confirmation-missing, review-history-missing,
source-hash-mismatched, artifact-mismatched, incomplete-required-input,
credential-required, runtime-required, provider-required, approval-required,
optimization-required, or promotion-required.

Invalid generated case human review decision application preflight input must
produce failure_code, failure code, visible_reason, and visible reason. It
must not append a successful application preflight, append a successful
ReviewHistory decision, approve a candidate, reject a candidate, request
optimization, promote a TestCase, create an AutomationDraft, mutate
GeneratedCaseCandidate content, mutate GeneratedCaseCandidate status, mutate
generated case human review decision audit handoff artifacts, mutate
generated case human review decision summary export artifacts, mutate
generated case human review decision artifacts, mutate evidence packages,
mutate TestCase rows, mutate ReviewHistory, mutate KnowledgeEvidence, mutate
prompt context evidence, mutate source evidence, render reports, expose
export/download endpoints, or set used_knowledge=true.

## Runtime Boundary

The Generated Case Human Review Decision Application Preflight contract is
not runtime prompt assembly, UI rendering, report generation, report
rendering, export endpoint behavior, provider runtime, retrieval runtime, or
automatic review behavior:

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
- no GeneratedCaseCandidate status mutation.
- no request optimization mutation.
- no automation draft creation.
- no AutomationDraft rows.
- no ToolInvocation creation.
- no TestRun/TestResult creation.
- no artifact upload.
- no Artifact mutation.
- no artifact mutation outside declared application preflight evidence.
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
- no application preflight artifact mutation.
- no generated case human review decision audit handoff artifact mutation.
- no generated case human review decision summary export artifact mutation.
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
