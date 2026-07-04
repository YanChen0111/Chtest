# TestKnowledgeCard Prompt Context Review Discrepancy Tracking Golden

This fixture proves Slice 46 remains a contract-only TestKnowledgeCard Prompt
Context Review Discrepancy Tracking definition. It is not a frontend page, not
report generation behavior, not an export/download endpoint, not prompt
assembly implementation, not prompt runtime execution, not a provider call, not
retrieval ranking, not broad TestKnowledgeCard CRUD, not a backend feature API,
and not a migration.

## Prompt Context Review Discrepancy Scenario

A future workflow may record discrepancy evidence only from existing prompt
context review summary export, audit review decision, audit summary, and prompt
context consumption evidence. The discrepancy record must preserve review
summary export artifact id, prompt context audit review decision artifact id,
prompt context audit summary artifact id, prompt context consumption artifact
id, prompt context evidence artifact id, `used_knowledge`, usage status,
discrepancy type, affected citation ids, evidence gap summary, mismatch
reason, reviewer note, severity, resolution status, unresolved follow-up flags,
unsupported claim references, source hash, context manifest, PromptVersion,
SkillVersion, ReviewHistory, and failure behavior without inventing citations
or mutating evidence.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Prompt Context Review Discrepancy Tracking | Reviewable discrepancy evidence |
| track_prompt_context_review_discrepancy | Future scoped discrepancy action only |
| prompt_context_review_discrepancy | Discrepancy artifact, not frontend/report/export runtime |
| review summary export artifact | Summary export evidence is required |
| audit review decision artifact | Review decision evidence remains linked |
| audit summary artifact | Audit summary evidence remains linked |
| prompt context consumption artifact | Consumption evidence remains linked |
| discrepancy type | Classifies mismatch only |
| affected citation ids | Existing citations remain visible |
| evidence gap summary | Explains missing or weak evidence |
| mismatch reason | Explains the discrepancy |
| reviewer note | Human note, not mutation |
| severity | Audit label only |
| resolution status | Status label only |
| ReviewHistory | Review trace remains visible |
| failure behavior | Invalid discrepancy input fails without successful record |

## Prompt Context Review Discrepancy Inputs

The contract must define:

- prompt_context_review_discrepancy_action.
- track_prompt_context_review_discrepancy.
- prompt request id.
- AITask id.
- review summary export artifact id.
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
- review action.
- review outcome summary.
- accepted citation group.
- questioned citation group.
- rejected citation group.
- affected citation ids.
- skipped evidence ids.
- skipped evidence.
- skip reasons.
- unsupported claim references.
- unresolved follow-up flags.
- source hashes.
- source hash.
- source quote/hash pointer.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.
- ReviewHistory ids.
- review decision ReviewHistory id.

## Discrepancy Outputs

Prompt context review discrepancy tracking may include:

- discrepancy id.
- discrepancy artifact id.
- prompt context review discrepancy artifact id.
- test_knowledge_card_prompt_context_review_discrepancy.json.
- artifact_type=test_knowledge_card_prompt_context_review_discrepancy.
- prompt_context_review_discrepancy.
- discrepancy type.
- citation_mismatch.
- missing_evidence.
- unsupported_claim.
- stale_evidence.
- cross_project_evidence.
- context_manifest_mismatch.
- prompt_version_mismatch.
- skill_version_mismatch.
- used_knowledge_mismatch.
- unresolved_follow_up.
- affected citation ids.
- evidence gap summary.
- mismatch reason.
- reviewer note.
- severity.
- resolution status.
- open.
- needs_clarification.
- acknowledged.
- rejected.
- resolved_by_later_review.
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

Discrepancy records are evidence about mismatches. Resolution status values do
not create prompt eligibility, approve TestKnowledgeCard content, approve
generated cases, alter `used_knowledge`, mark skipped evidence as cited, or
auto-resolve discrepancies.

Affected citation ids, questioned citation group, rejected citation group,
unresolved follow-up flags, skipped evidence, unsupported claim references,
evidence gap summary, mismatch reason, source hashes, context manifest links,
PromptVersion/SkillVersion trace, and ReviewHistory links remain visible. They
are not deleted, filtered, rewritten, or converted into cited knowledge.

## Failure Behavior

Prompt context review discrepancy tracking must fail without successful
discrepancy record when input is:

- missing review summary export artifact.
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
- evidence-mismatched input.
- audit summary-mismatched input.
- review-decision-mismatched input.
- summary-export-mismatched input.

## Runtime Boundary

The prompt context review discrepancy tracking contract is not runtime prompt
assembly, UI rendering, report generation, export endpoint behavior, or
automatic remediation:

- no frontend page.
- no frontend rendering.
- no report generation behavior.
- no report renderer.
- no report export behavior.
- no export/download endpoint.
- no prompt assembly implementation.
- no prompt runtime execution.
- no LLM/provider call.
- no provider call.
- no provider SDK.
- no credentials.
- no OAuth.
- no remote URL fetch.
- no prompt runner.
- no queue.
- no scheduler.
- no background worker.
- no AITask execution behavior change.
- no runtime prompt_input.json.
- no automatic used_knowledge=true marking.
- no model output behavior implementation.
- no automatic citation generation.
- no prompt input generation.
- no prompt template rendering.
- no retrieval ranking change.
- no deterministic retrieval behavior change.
- no deterministic retrieval ranking change.
- no prompt runtime retrieval implementation.
- no vector index.
- no vector database.
- no embedding.
- no embeddings.
- no reranking.
- no graph job.
- no GraphRAG job.
- no MCP runtime.
- no automatic discrepancy resolution.
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
- frontend page.
- frontend rendering.
- report generation behavior.
- report renderer.
- report export behavior.
- export/download endpoint.
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
- queue.
- scheduler.
- background worker.
- artifact upload.
- Artifact mutation.
- artifact delete.
- source artifact mutation.
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
- auto-resolve discrepancies.
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

TestKnowledgeCard Prompt Context Review Discrepancy Tracking remains
discrepancy evidence. It preserves review summary export artifact id, prompt
context audit review decision artifact id, prompt context audit summary
artifact id, prompt context consumption artifact id, prompt context evidence
artifact id, context manifest, source hash, discrepancy type, affected citation
ids, evidence gap summary, mismatch reason, reviewer note, severity,
resolution status, unresolved follow-up flags, unsupported claim references,
PromptVersion, SkillVersion, ReviewHistory, failure behavior, and
`used_knowledge` without rendering UI, generating reports, exposing
export/download endpoints, assembling prompts, calling providers, creating
prompt eligibility, approving TestKnowledgeCard content, auto-resolving
discrepancies, or approving generated cases.
