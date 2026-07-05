# Generated Case Human Review Decision Golden

This fixture proves Slice 55 remains a contract-only Generated Case Human
Review Decision definition. It is human-review decision evidence only, audit
evidence only, not approval, not rejection, not request optimization, not
TestCase promotion, not automation draft creation, not backend runtime API,
not a frontend page, not provider integration, not a provider SDK call, not
runtime retrieval, not prompt execution, not report generation behavior, and
not an export/download endpoint.

## Generated Case Human Review Decision Scenario

A future workflow may record a human decision over a
Generated Case Human Review Evidence Package. The record must preserve
generated_case_human_review_evidence_package_artifact_id,
GeneratedCaseCandidate id, candidate status, candidate summary, evidence chain
completeness, missing evidence summary, conflicting evidence summary, review
blocker summary, dedup/readiness summary, human review checklist,
quality_score, review_findings_json, coverage_gap_notes, automation_readiness,
dedup findings, duplicate candidate ids, duplicate-of case id, prompt context
lineage artifact ids, source manifest ids, source hashes, ReviewHistory ids,
ReviewHistory links, failure_code, failure code, visible_reason, visible
reason, and failure behavior without approving or rejecting candidates.

| Surface | Required boundary |
|---|---|
| Generated Case Human Review Decision | Human-review decision evidence only |
| review_generated_case_human_review_evidence_package | Future scoped decision action only |
| generated_case_human_review_decision | Artifact and manifest naming only |
| generated_case_human_review_evidence_package_artifact_id | Required source evidence package artifact |
| GeneratedCaseCandidate | Source candidate remains unchanged |
| candidate summary | Reviewer-facing summary only |
| evidence chain completeness | Evidence completeness label only |
| missing evidence summary | Missing evidence remains visible |
| conflicting evidence summary | Conflicting evidence remains visible |
| review blocker summary | Blockers remain visible |
| dedup/readiness summary | Dedup/readiness rollup only |
| human review checklist | Checklist, not mutation |
| decision labels | Review labels only |
| reviewer label/comment | Human attribution only |
| requested edit fields | Requested edits, not content mutation |
| optimization request summary | Request evidence, not request optimization mutation |
| rejection/blocker reasons | Visible review reasons only |
| duplicate resolution notes | Duplicate evidence only |
| ReviewHistory | Human review trace remains visible |
| failure behavior | Invalid input fails without successful decision |

## Generated Case Human Review Decision Inputs

The contract must define:

- generated_case_human_review_decision_action.
- generated_case_human_review_decision_action=review_generated_case_human_review_evidence_package.
- review_generated_case_human_review_evidence_package.
- generated case human review decision id.
- generated case human review decision artifact id.
- generated_case_human_review_decision_artifact_id.
- generated_case_human_review_decision.
- generated_case_human_review_decision.json.
- artifact_type=generated_case_human_review_decision.
- manifest_kind=generated_case_human_review_decision.
- created_by_component=GeneratedCaseHumanReviewDecision.
- owner_entity_type=GeneratedCaseCandidate.
- owner_entity_id=candidate_id.
- owner_entity_type=AITask.
- generated_case_human_review_evidence_package_artifact_id.
- GeneratedCaseCandidate id.
- candidate status.
- candidate summary.
- evidence chain completeness.
- missing evidence summary.
- conflicting evidence summary.
- review blocker summary.
- dedup/readiness summary.
- human review checklist.
- quality_score.
- review_findings_json.
- coverage_gap_notes.
- automation_readiness.
- dedup findings.
- duplicate candidate ids.
- duplicate-of case id.
- prompt context lineage artifact ids.
- source manifest ids.
- source hashes.
- ReviewHistory ids.
- ReviewHistory links.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.

## Decision Labels

The contract must keep these decision labels as evidence-only values:

- accepted_for_future_promotion.
- accepted_with_required_edits.
- needs_optimization.
- rejected_for_insufficient_evidence.
- blocked.
- duplicate.
- needs_more_evidence.
- failed_validation.

accepted_for_future_promotion does not promote a TestCase.
accepted_with_required_edits preserves requested edit fields but does not
mutate GeneratedCaseCandidate content. needs_optimization preserves
optimization request summary but does not perform request optimization.
rejected_for_insufficient_evidence preserves rejection reasons but does not
reject a candidate. blocked preserves blocker reasons and visible reason.
duplicate preserves duplicate resolution notes but does not merge or delete
cases. needs_more_evidence preserves missing evidence summary.
failed_validation preserves failure_code, failure code, visible_reason, and
visible reason.

## Field-Level Keys

The decision request and response evidence keeps these explicit payload fields:

- project_id.
- generated_case_human_review_decision_action.
- generated_case_human_review_evidence_package_artifact_id.
- generated_case_candidate_id.
- candidate_status.
- candidate_summary.
- evidence_chain_completeness.
- missing_evidence_summary.
- conflicting_evidence_summary.
- review_blocker_summary.
- dedup_readiness_summary.
- human_review_checklist.
- quality_score.
- review_findings_json.
- coverage_gap_notes.
- automation_readiness.
- dedup_findings.
- duplicate_candidate_ids.
- duplicate_of_case_id.
- prompt_context_lineage_artifact_ids.
- source_manifest_ids.
- source_hashes.
- review_history_links.
- review_decision.
- decision_label.
- reviewer_label.
- reviewer_comment.
- accepted_constraints.
- requested_edit_fields.
- optimization_request_summary.
- rejection_reasons.
- blocker_reasons.
- duplicate_resolution_notes.
- generated_case_human_review_decision_artifact_id.
- generated_case_human_review_decision.
- decision_status.
- allowed_decision_labels.
- failure_code.
- visible_reason.

## Generated Case Human Review Decision Outputs

Generated case human review decision output may include:

- generated case human review decision id.
- generated case human review decision artifact id.
- generated_case_human_review_decision_artifact_id.
- generated_case_human_review_decision.
- generated_case_human_review_decision.json.
- artifact_type=generated_case_human_review_decision.
- manifest_kind=generated_case_human_review_decision.
- generated_case_human_review_decision_pending.
- generated_case_human_review_decision_recorded.
- generated_case_human_review_decision_failed_validation.
- review decision.
- decision status.
- decision label.
- accepted_for_future_promotion.
- accepted_with_required_edits.
- needs_optimization.
- rejected_for_insufficient_evidence.
- blocked.
- duplicate.
- needs_more_evidence.
- failed_validation.
- reviewer label.
- reviewer comment.
- accepted constraints.
- requested edit fields.
- optimization request summary.
- rejection reasons.
- blocker reasons.
- duplicate resolution notes.
- ReviewHistory links.
- human-review decision evidence only.
- audit evidence only.
- not approval.
- not rejection.
- not request optimization.
- not TestCase promotion.
- not automation draft creation.
- used_knowledge=true.
- prompt_input.json.
- failure_code.
- failure code.
- visible_reason.
- visible reason.

Decision labels, review decision, decision status, reviewer label, reviewer
comment, accepted constraints, requested edit fields, optimization request
summary, rejection reasons, blocker reasons, duplicate resolution notes,
source hashes, source manifest ids, and ReviewHistory links are evidence
labels. They do not approve candidates, reject candidates, request
optimization, promote TestCase rows, create AutomationDraft rows, execute
automation, generate reports, or set used_knowledge=true.

## Failure Behavior

Generated case human review decision must fail without a successful human
review decision when input is missing, stale, unsafe, cross-project,
unbounded, evidence-package-missing, evidence-package-mismatched,
candidate-missing, candidate-mismatched, candidate-status-invalid,
evidence-chain-incomplete, review-blocked, dedup-conflict,
duplicate-resolution-missing, review-history-missing, artifact-mismatched,
source-hash-mismatched, credential-required, runtime-required,
provider-required, approval-required, optimization-required, or
promotion-required.

Invalid generated case human review decision input must produce failure_code,
failure code, visible_reason, and visible reason. It must not append a
successful decision, append a successful ReviewHistory decision, approve a
candidate, reject a candidate, request optimization, promote a TestCase,
create an AutomationDraft, mutate GeneratedCaseCandidate content, mutate
ReviewHistory, mutate KnowledgeEvidence, mutate prompt context evidence,
mutate source evidence, generate reports, expose export/download endpoints, or
set used_knowledge=true.

## Runtime Boundary

The Generated Case Human Review Decision contract is not runtime prompt
assembly, UI rendering, report generation, export endpoint behavior, provider
runtime, retrieval runtime, or automatic review behavior:

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

## Forbidden Side Effects

The contract must not create or trigger backend runtime APIs, endpoints,
routers, services, workers, queues, schedulers, migrations, frontend pages,
reports, export/download endpoints, provider integrations, provider SDK calls,
external calls, credentials, remote URL fetches, vector indexes, embeddings,
reranking, graph jobs, MCP runtime calls, prompt execution, AITask
orchestration, TestCase promotion, GeneratedCaseCandidate approve/reject
mutation, request optimization mutation, GeneratedCaseCandidate content
mutation, automation draft creation, ToolInvocation creation,
TestRun/TestResult creation, artifact upload, Artifact mutation, source
artifact mutation, source evidence mutation, prompt context evidence mutation,
KnowledgeEvidence mutation, TestKnowledgeCard mutation, ReviewHistory
mutation, historical evidence mutation, runner behavior changes, remote CI
provider behavior, generated replacement evidence, generated-case
auto-approval, review bypass, RBAC, tenants, or permissions.

Generated Case Human Review Decision remains human-review decision evidence.
It preserves generated_case_human_review_evidence_package_artifact_id,
GeneratedCaseCandidate id, candidate status, candidate summary, evidence chain
completeness, missing evidence summary, conflicting evidence summary, review
blocker summary, dedup/readiness summary, human review checklist,
quality_score, review_findings_json, coverage_gap_notes, automation_readiness,
dedup findings, duplicate candidate ids, duplicate-of case id, prompt-context
lineage artifact ids, source hashes, source manifest ids, ReviewHistory
links, review decision, decision status, decision label, reviewer label,
reviewer comment, accepted constraints, requested edit fields, optimization
request summary, rejection reasons, blocker reasons, duplicate resolution
notes, failure behavior, failure_code, visible_reason, and visible reason
without approving or rejecting candidates, requesting optimization, promoting
TestCases, creating automation drafts, running prompts, calling providers,
creating vector infrastructure, generating reports, exposing export/download
endpoints, or bypassing review.
