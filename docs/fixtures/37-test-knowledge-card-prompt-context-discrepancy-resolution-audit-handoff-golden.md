# TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff Golden

This fixture proves Slice 49 remains a contract-only TestKnowledgeCard Prompt
Context Discrepancy Resolution Audit Handoff definition. It is not a frontend
page, not report generation behavior, not an export/download endpoint, not
external archive integration, not prompt assembly implementation, not prompt
runtime execution, not a provider call, not retrieval ranking, not broad
TestKnowledgeCard CRUD, not a backend feature API, and not a migration.

## Prompt Context Discrepancy Resolution Audit Handoff Scenario

A future workflow may package audit handoff evidence only from existing prompt
context discrepancy resolution summary export, prompt context discrepancy
resolution review, prompt context review discrepancy, review summary export,
audit review decision, audit summary, prompt context consumption, and prompt
context evidence. The audit handoff record must preserve prompt context
discrepancy resolution summary export artifact id, prompt context discrepancy
resolution review artifact id, prompt context review discrepancy artifact id,
prompt context audit review summary export artifact id, prompt context audit
review decision artifact id, prompt context audit summary artifact id, prompt
context consumption artifact id, prompt context evidence artifact id,
`used_knowledge`, usage status, resolution outcome summary, accepted
discrepancy group, rejected discrepancy group, acknowledged discrepancy group,
clarification requested fields, clarification requested field group, resulting
resolution status group, affected citation ids, evidence gap summary, mismatch
reason, unresolved follow-up flags, unsupported claim references, source hash,
source hashes, context manifest, PromptVersion, SkillVersion, ReviewHistory,
and failure behavior without inventing citations or mutating evidence.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff | Audit handoff evidence package |
| build_prompt_context_discrepancy_resolution_audit_handoff | Future scoped audit handoff action only |
| prompt_context_discrepancy_resolution_audit_handoff | Audit handoff artifact, not frontend/report/export runtime |
| prompt context discrepancy resolution summary export artifact | Resolution summary export evidence is required |
| prompt context discrepancy resolution review artifact | Resolution review evidence remains linked |
| prompt context review discrepancy artifact | Discrepancy evidence remains linked |
| review summary export artifact | Audit review summary export evidence remains linked |
| audit review decision artifact | Review decision evidence remains linked |
| audit summary artifact | Audit summary evidence remains linked |
| prompt context consumption artifact | Consumption evidence remains linked |
| prompt context evidence artifact | Context evidence remains linked |
| handoff summary | Human-readable handoff summary only |
| evidence chain status | Audit label only |
| included artifact ids | Persisted artifact references remain visible |
| excluded artifact reasons | Omission reasons remain visible |
| unresolved evidence gaps | Remaining evidence gaps remain visible |
| unresolved follow-up flags | Remaining follow-up flags remain visible |
| ReviewHistory | Review trace remains visible |
| failure behavior | Invalid audit handoff input fails without successful record |

## Prompt Context Discrepancy Resolution Audit Handoff Inputs

The contract must define:

- prompt_context_discrepancy_resolution_audit_handoff_action.
- build_prompt_context_discrepancy_resolution_audit_handoff.
- prompt request id.
- AITask id.
- prompt context discrepancy resolution summary export artifact id.
- test_knowledge_card_prompt_context_discrepancy_resolution_summary_export.json.
- prompt context discrepancy resolution review artifact id.
- test_knowledge_card_prompt_context_discrepancy_resolution_review.json.
- prompt context review discrepancy artifact id.
- test_knowledge_card_prompt_context_review_discrepancy.json.
- prompt context audit review summary export artifact id.
- test_knowledge_card_prompt_context_audit_review_summary_export.json.
- prompt context audit review decision artifact id.
- test_knowledge_card_prompt_context_audit_review_decision.json.
- prompt context audit summary artifact id.
- test_knowledge_card_prompt_context_audit_summary.json.
- prompt context consumption artifact id.
- test_knowledge_card_prompt_context_consumption.json.
- prompt context evidence artifact id.
- test_knowledge_card_prompt_context_evidence.json.
- context manifest artifact id.
- context_manifest.
- context_manifest.json.
- used_knowledge decision.
- usage status.
- resolution outcome summary.
- accepted discrepancy group.
- rejected discrepancy group.
- acknowledged discrepancy group.
- clarification requested fields.
- clarification requested field group.
- resulting resolution status group.
- affected citation ids.
- evidence gap summary.
- mismatch reason.
- unresolved follow-up flags.
- unsupported claim references.
- source hashes.
- source hash.
- source quote/hash pointer.
- source quote/hash pointers.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.
- ReviewHistory ids.
- discrepancy ReviewHistory id.
- resolution review ReviewHistory id.
- summary export ReviewHistory id.

## Audit Handoff Outputs

Prompt context discrepancy resolution audit handoff may include:

- audit handoff id.
- audit handoff artifact id.
- prompt context discrepancy resolution audit handoff artifact id.
- test_knowledge_card_prompt_context_discrepancy_resolution_audit_handoff.json.
- artifact_type=test_knowledge_card_prompt_context_discrepancy_resolution_audit_handoff.
- manifest_kind=test_knowledge_card_prompt_context_discrepancy_resolution_audit_handoff.
- prompt_context_discrepancy_resolution_audit_handoff.
- audit handoff action.
- handoff summary.
- evidence chain status.
- complete.
- incomplete.
- blocked.
- failed_validation.
- included artifact ids.
- excluded artifact reasons.
- unresolved evidence gaps.
- unresolved follow-up flags.
- unsupported claim references.
- ReviewHistory links.
- source manifest ids.
- source hashes.
- PromptVersion/SkillVersion trace.
- context manifest references.
- failure_code.
- failure code.
- visible reason.
- prompt_input.json.

Audit handoff records are evidence packages about a discrepancy resolution
evidence chain. Handoff summary, evidence chain status, included artifact ids,
excluded artifact reasons, unresolved evidence gaps, unresolved follow-up
flags, and unsupported claim references do not create prompt eligibility,
approve TestKnowledgeCard content, approve generated cases, alter
`used_knowledge`, mark skipped evidence as cited, invent citations, upload
artifacts, integrate with an external archive, or auto-resolve discrepancies.

Included artifact ids, excluded artifact reasons, accepted discrepancy group,
rejected discrepancy group, acknowledged discrepancy group, clarification
requested fields, clarification requested field group, resulting resolution
status group, affected citation ids, unresolved evidence gaps, unresolved
follow-up flags, skipped evidence, unsupported claim references, evidence gap
summary, mismatch reason, source hashes, context manifest references,
PromptVersion/SkillVersion trace, and ReviewHistory links remain visible. They
are not deleted, filtered, rewritten, or converted into cited knowledge.

## Failure Behavior

Prompt context discrepancy resolution audit handoff must fail without a
successful audit handoff record when input is:

- missing prompt context discrepancy resolution summary export artifact.
- missing prompt context discrepancy resolution review artifact.
- missing prompt context review discrepancy artifact.
- missing review summary export artifact.
- missing prompt context audit review summary export artifact.
- missing prompt context audit review decision artifact.
- missing prompt context audit summary artifact.
- missing prompt context consumption artifact.
- missing prompt context evidence artifact.
- missing context manifest.
- missing affected citation ids.
- missing source hash.
- stale evidence.
- unsafe evidence.
- revoked evidence.
- cross-project evidence.
- unsupported evidence.
- unbounded evidence.
- citation-mismatched evidence.
- context-mismatched evidence.
- prompt-version-mismatched evidence.
- skill-version-mismatched evidence.
- redaction-failed evidence.
- discrepancy-mismatched input.
- resolution-review-mismatched input.
- summary-export-mismatched input.
- audit-summary-mismatched input.
- review-decision-mismatched input.
- audit-handoff-mismatched input.
- evidence-mismatched input.
- incomplete required input.

Missing, stale, unsafe, revoked, cross-project, unsupported, unbounded,
citation-mismatched, context-mismatched, prompt-version-mismatched,
skill-version-mismatched, redaction-failed, discrepancy-mismatched,
resolution-review-mismatched, summary-export-mismatched,
audit-summary-mismatched, review-decision-mismatched,
audit-handoff-mismatched, evidence-mismatched, and incomplete required input
must produce a failure code and visible reason and must not append a successful
audit handoff.

## Runtime Boundary

The prompt context discrepancy resolution audit handoff contract is not runtime
prompt assembly, UI rendering, report generation, export endpoint behavior,
external archive integration, artifact upload, or automatic remediation:

- no frontend page.
- no frontend rendering.
- no report generation behavior.
- no report renderer.
- no report export behavior.
- no export/download endpoint.
- no external archive integration.
- no external archive payloads.
- no backend feature API.
- no endpoint.
- no router.
- no service.
- no worker.
- no queue.
- no scheduler.
- no background job.
- no migration.
- no card table change.
- no prompt assembly implementation.
- no prompt runtime execution.
- no runtime prompt_input.json.
- no prompt input generation.
- no prompt template rendering.
- no AITask execution behavior change.
- no LLM/provider call.
- no provider call.
- no provider SDK.
- no credentials.
- no OAuth.
- no remote URL fetch.
- no prompt runner.
- no model output behavior implementation.
- no automatic citation generation.
- no automatic used_knowledge=true marking.
- no rewrite `used_knowledge`.
- no prompt runtime retrieval implementation.
- no retrieval ranking change.
- no deterministic retrieval behavior change.
- no deterministic retrieval ranking change.
- no vector index.
- no vector database.
- no embedding.
- no embeddings.
- no reranking.
- no background indexing.
- no graph job.
- no GraphRAG job.
- no MCP runtime.
- no automatic discrepancy resolution.
- no automatic discrepancy remediation.
- no auto-resolve discrepancies.

## Forbidden Side Effects

The contract must not create or trigger:

- broad TestKnowledgeCard CRUD.
- TestKnowledgeCard CRUD.
- TestKnowledgeCard auto-creation.
- automatic card creation from model output.
- automatic card creation.
- automatic card approval.
- automatic prompt eligibility.
- allowed_for_prompt=true auto-marking.
- automatic knowledge ingestion.
- KnowledgeIngestionAgent runtime.
- backend feature API.
- endpoint.
- router.
- service.
- worker.
- queue.
- scheduler.
- background job.
- frontend page.
- frontend rendering.
- report generation behavior.
- report renderer.
- report export behavior.
- export/download endpoint.
- external archive integration.
- external archive payloads.
- migration.
- card table change.
- list/update/delete API.
- prompt assembly implementation.
- prompt runtime execution.
- prompt runtime retrieval implementation.
- deterministic retrieval behavior change.
- deterministic retrieval ranking change.
- retrieval ranking change.
- vector index.
- vector database.
- embedding.
- embeddings.
- reranking.
- background indexing.
- graph job.
- GraphRAG job.
- MCP runtime.
- provider call.
- provider SDK.
- credentials.
- OAuth.
- remote URL fetch.
- prompt runner.
- artifact upload.
- Artifact mutation.
- artifact delete.
- source artifact mutation.
- resolution summary export mutation.
- prompt context discrepancy resolution summary export artifact mutation.
- resolution review mutation.
- prompt context discrepancy resolution review artifact mutation.
- discrepancy tracking evidence mutation.
- prompt context review discrepancy artifact mutation.
- review summary export mutation.
- prompt context audit review summary export artifact mutation.
- audit review decision mutation.
- prompt context audit review decision artifact mutation.
- audit summary mutation.
- prompt context audit summary artifact mutation.
- prompt context consumption artifact mutation.
- prompt context evidence artifact mutation.
- retrieval boundary artifact mutation.
- prompt eligibility artifact mutation.
- historical evidence mutation.
- historical ReviewHistory mutation.
- PromptVersion mutation.
- SkillVersion mutation.
- FailureAnalysis mutation.
- Report mutation.
- TestRun mutation.
- TestResult mutation.
- TestCase mutation.
- GeneratedCaseCandidate mutation.
- KnowledgeEvidence mutation.
- existing TestKnowledgeCard content mutation.
- review bypass.
- automatic discrepancy resolution.
- automatic discrepancy remediation.
- auto-resolve discrepancies.
- automatic duplicate merge.
- automatic merge.
- automatic archive.
- automatic replace.
- automatic relabel.
- automatic delete.
- generated-case auto-approval.
- TestCase auto-promotion.
- runner behavior change.
- remote CI provider behavior.
- RBAC.
- tenants.
- permissions.
- package upgrades.

TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff remains
audit handoff evidence. It preserves prompt context discrepancy resolution
summary export artifact id, prompt context discrepancy resolution review
artifact id, prompt context review discrepancy artifact id, review summary
export artifact id, audit review decision artifact id, audit summary artifact
id, prompt context consumption artifact id, prompt context evidence artifact
id, context manifest, source hash, resolution outcome summary, accepted
discrepancy group, rejected discrepancy group, acknowledged discrepancy group,
clarification requested fields, clarification requested field group, resulting
resolution status group, handoff summary, evidence chain status, included
artifact ids, excluded artifact reasons, unresolved follow-up flags,
unresolved evidence gaps, unsupported claim references, PromptVersion,
SkillVersion, ReviewHistory, failure behavior, and `used_knowledge` without
rendering UI, generating reports, exposing export/download endpoints,
assembling prompts, calling providers, creating prompt eligibility, approving
TestKnowledgeCard content, auto-resolving discrepancies, uploading artifacts,
integrating with an external archive, or approving generated cases.
