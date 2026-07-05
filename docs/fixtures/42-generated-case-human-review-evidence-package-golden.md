# Generated Case Human Review Evidence Package Golden

This fixture proves Slice 54 remains a contract-only Generated Case Human
Review Evidence Package definition. It is human-review evidence only, not
approval, not rejection, not TestCase promotion, not automation draft
creation, not backend runtime API, not a frontend page, not provider
integration, not a provider SDK call, not runtime retrieval, not prompt
execution, not report generation behavior, and not an export/download
endpoint.

## Generated Case Human Review Evidence Package Scenario

A future workflow may package GeneratedCaseCandidate review evidence into a
human-review evidence bundle. The record must preserve GeneratedCaseCandidate
id, candidate status, candidate summary, candidate title, candidate priority,
candidate test type, candidate precondition, candidate steps, candidate
expected results, candidate input data, candidate tags, requirement refs, risk
refs, ai_reason, generation reason, covered risk ids, duplicate-of case id,
source_knowledge_evidence_ids, knowledge_evidence_refs_json, quality_score,
review_findings_json, coverage_gap_notes, automation_readiness, dedup
findings, duplicate candidate ids, automation readiness blockers, prompt
context evidence artifact ids, prompt context consumption artifact ids, prompt
context audit summary artifact ids, prompt context audit review decision
artifact ids, prompt context audit review summary export artifact ids, prompt
context discrepancy resolution audit handoff artifact ids, source manifest
ids, source hashes, ReviewHistory ids, ReviewHistory links, failure_code,
failure code, visible_reason, visible reason, and failure behavior without
approving or rejecting candidates.

| Surface | Required boundary |
|---|---|
| Generated Case Human Review Evidence Package | Human-review evidence package only |
| build_generated_case_human_review_evidence_package | Future scoped package action only |
| generated_case_human_review_evidence_package | Artifact and manifest naming only |
| GeneratedCaseCandidate | Source candidate remains unchanged |
| candidate summary | Reviewer-facing summary only |
| source_knowledge_evidence_ids | Preserved knowledge evidence ids |
| knowledge_evidence_refs_json | Bounded display cache only |
| quality_score | Review aid only |
| review_findings_json | Review aid only |
| coverage_gap_notes | Review aid only |
| automation_readiness | Review aid only |
| dedup findings | Review aid only |
| prompt context evidence artifact ids | Prompt-context lineage only |
| prompt context consumption artifact ids | Prompt-context lineage only |
| prompt context discrepancy resolution audit handoff artifact ids | Prompt-context lineage only |
| evidence chain completeness | Evidence completeness label only |
| missing evidence summary | Missing evidence remains visible |
| conflicting evidence summary | Conflicting evidence remains visible |
| review blocker summary | Blockers remain visible |
| dedup/readiness summary | Dedup/readiness rollup only |
| human review checklist | Checklist, not a decision |
| ReviewHistory | Human review trace remains visible |
| failure behavior | Invalid input fails without successful package |

## Generated Case Human Review Evidence Package Inputs

The contract must define:

- generated_case_human_review_evidence_package_action.
- generated_case_human_review_evidence_package_action=build_generated_case_human_review_evidence_package.
- build_generated_case_human_review_evidence_package.
- generated case human review evidence package id.
- generated case human review evidence package artifact id.
- generated_case_human_review_evidence_package_artifact_id.
- generated_case_human_review_evidence_package.
- generated_case_human_review_evidence_package.json.
- artifact_type=generated_case_human_review_evidence_package.
- manifest_kind=generated_case_human_review_evidence_package.
- created_by_component=GeneratedCaseHumanReviewEvidencePackage.
- owner_entity_type=GeneratedCaseCandidate.
- owner_entity_id=candidate_id.
- owner_entity_type=AITask.
- GeneratedCaseCandidate id.
- candidate status.
- candidate summary.
- candidate title.
- candidate priority.
- candidate test type.
- candidate precondition.
- candidate steps.
- candidate expected results.
- candidate input data.
- candidate tags.
- requirement refs.
- risk refs.
- ai_reason.
- generation reason.
- covered risk ids.
- duplicate-of case id.
- source_knowledge_evidence_ids.
- knowledge_evidence_refs_json.
- quality_score.
- review_findings_json.
- coverage_gap_notes.
- automation_readiness.
- dedup findings.
- duplicate candidate ids.
- automation readiness blockers.
- prompt context evidence artifact ids.
- prompt context consumption artifact ids.
- prompt context audit summary artifact ids.
- prompt context audit review decision artifact ids.
- prompt context audit review summary export artifact ids.
- prompt context discrepancy resolution audit handoff artifact ids.
- source manifest ids.
- source hashes.
- ReviewHistory ids.
- ReviewHistory links.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.

## Field-Level Keys

The evidence package request and response keeps these explicit payload fields:

- project_id.
- generated_case_human_review_evidence_package_action.
- generated_case_candidate_id.
- candidate_status.
- candidate_title.
- candidate_priority.
- candidate_test_type.
- candidate_precondition.
- candidate_steps.
- candidate_expected_results.
- candidate_input_data.
- candidate_tags.
- requirement_refs.
- risk_refs.
- ai_reason.
- generation_reason.
- covered_risk_ids.
- duplicate_of_case_id.
- source_knowledge_evidence_ids.
- knowledge_evidence_refs_json.
- quality_score.
- review_findings_json.
- coverage_gap_notes.
- automation_readiness.
- dedup_findings.
- duplicate_candidate_ids.
- automation_readiness_blockers.
- prompt_context_evidence_artifact_ids.
- prompt_context_consumption_artifact_ids.
- prompt_context_audit_summary_artifact_ids.
- prompt_context_audit_review_decision_artifact_ids.
- prompt_context_audit_review_summary_export_artifact_ids.
- prompt_context_discrepancy_resolution_audit_handoff_artifact_ids.
- source_manifest_ids.
- source_hashes.
- review_history_links.
- generated_case_human_review_evidence_package_artifact_id.
- generated_case_human_review_evidence_package.
- candidate_summary.
- evidence_chain_completeness.
- missing_evidence_summary.
- conflicting_evidence_summary.
- review_blocker_summary.
- dedup_readiness_summary.
- human_review_checklist.
- included_artifact_ids.
- excluded_artifact_reasons.
- failure_code.
- visible_reason.

## Generated Case Human Review Evidence Package Outputs

Generated case human review evidence package output may include:

- generated case human review evidence package id.
- generated case human review evidence package artifact id.
- generated_case_human_review_evidence_package_artifact_id.
- generated_case_human_review_evidence_package.
- generated_case_human_review_evidence_package.json.
- artifact_type=generated_case_human_review_evidence_package.
- manifest_kind=generated_case_human_review_evidence_package.
- generated_case_human_review_evidence_package_pending.
- generated_case_human_review_evidence_package_complete.
- generated_case_human_review_evidence_package_incomplete.
- generated_case_human_review_evidence_package_blocked.
- generated_case_human_review_evidence_package_failed_validation.
- candidate summary.
- evidence chain completeness.
- complete.
- incomplete.
- blocked.
- failed_validation.
- missing evidence summary.
- conflicting evidence summary.
- review blocker summary.
- dedup/readiness summary.
- human review checklist.
- included artifact ids.
- excluded artifact reasons.
- human-review evidence only.
- review aids only.
- not approval.
- not rejection.
- not TestCase promotion.
- not automation draft creation.
- used_knowledge=true.
- prompt_input.json.
- failure_code.
- failure code.
- visible_reason.
- visible reason.

Evidence chain completeness, missing evidence summary, conflicting evidence
summary, review blocker summary, dedup/readiness summary, human review
checklist, source hashes, source manifest ids, and ReviewHistory links are
evidence labels. They do not approve candidates, reject candidates, request
optimization, promote TestCase rows, create AutomationDraft rows, execute
automation, generate reports, or set used_knowledge=true.

Included artifact ids, excluded artifact reasons, source_knowledge_evidence_ids,
knowledge_evidence_refs_json, quality_score, review_findings_json,
coverage_gap_notes, automation_readiness, dedup findings, prompt-context
artifact lineage, source hashes, source manifest ids, and ReviewHistory links
remain visible. They are not deleted, filtered, rewritten, or converted into
approval decisions.

## Failure Behavior

Generated case human review evidence package must fail without a successful
evidence package when input is missing, stale, unsafe, cross-project,
unbounded, evidence-missing, candidate-missing, candidate-mismatched,
candidate-status-invalid, knowledge-evidence-missing,
prompt-context-evidence-missing, review-findings-missing, dedup-inconclusive,
readiness-unknown, review-history-missing, artifact-mismatched,
source-hash-mismatched, credential-required, runtime-required,
provider-required, approval-required, or promotion-required.

Invalid generated case human review evidence package input must produce
failure_code, failure code, visible_reason, and visible reason. It must not
append a successful evidence package, approve a candidate, reject a candidate,
request optimization, promote a TestCase, create an AutomationDraft, mutate
GeneratedCaseCandidate content, mutate ReviewHistory, mutate KnowledgeEvidence,
mutate prompt context evidence, generate reports, expose export/download
endpoints, or set used_knowledge=true.

## Runtime Boundary

The Generated Case Human Review Evidence Package contract is not runtime
prompt assembly, UI rendering, report generation, export endpoint behavior,
provider runtime, retrieval runtime, or automatic review behavior:

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
- no automation draft creation.
- no AutomationDraft rows.
- no ToolInvocation creation.
- no TestRun/TestResult creation.
- no artifact upload.
- no Artifact mutation.
- no source artifact mutation.
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
mutation, GeneratedCaseCandidate content mutation, automation draft creation,
ToolInvocation creation, TestRun/TestResult creation, artifact upload,
Artifact mutation, source artifact mutation, prompt context evidence mutation,
KnowledgeEvidence mutation, TestKnowledgeCard mutation, ReviewHistory
mutation, historical evidence mutation, runner behavior changes, remote CI
provider behavior, generated replacement evidence, generated-case
auto-approval, review bypass, RBAC, tenants, or permissions.

Generated Case Human Review Evidence Package remains human-review evidence. It
preserves GeneratedCaseCandidate id, candidate status, candidate summary,
source_knowledge_evidence_ids, knowledge_evidence_refs_json, quality_score,
review_findings_json, coverage_gap_notes, automation_readiness, dedup
findings, prompt-context artifact lineage, evidence chain completeness,
missing evidence summary, conflicting evidence summary, review blocker
summary, dedup/readiness summary, human review checklist, included artifact
ids, excluded artifact reasons, source hashes, source manifest ids,
ReviewHistory links, failure behavior, failure_code, visible_reason, and
visible reason without approving or rejecting candidates, promoting TestCases,
creating automation drafts, running prompts, calling providers, creating
vector infrastructure, generating reports, exposing export/download endpoints,
or bypassing review.
