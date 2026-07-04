# TestKnowledgeCard Prompt Context Audit Review Summary Export Golden

This fixture proves Slice 45 remains a contract-only TestKnowledgeCard Prompt
Context Audit Review Summary Export definition. It is not a frontend page, not
report generation behavior, not an export/download endpoint, not prompt
assembly implementation, not prompt runtime execution, not a provider call, not
retrieval ranking, not broad TestKnowledgeCard CRUD, not a backend feature API,
and not a migration.

## Prompt Context Audit Review Summary Export Scenario

A future workflow may package TestKnowledgeCard prompt context audit review
decision evidence into an exportable summary only from existing review decision
evidence. The summary export must preserve prompt context audit review decision
artifact id, prompt context audit summary artifact id, prompt context
consumption artifact id, prompt context evidence artifact id, `used_knowledge`,
usage status, review outcome summary, accepted citation group, questioned
citation group, rejected citation group, unresolved follow-up flags,
unsupported claim references, source hash, context manifest, PromptVersion,
SkillVersion, ReviewHistory, failure behavior, and summary export evidence
without inventing citations or mutating evidence.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Prompt Context Audit Review Summary Export | Summary export evidence package |
| export_prompt_context_audit_review_summary | Future scoped summary export action only |
| prompt_context_audit_review_summary_export | Summary export artifact, not frontend/report/export runtime |
| audit review decision artifact | Review decision evidence is required |
| audit summary artifact | Audit summary evidence remains linked |
| prompt context consumption artifact | Consumption evidence remains linked |
| prompt context evidence artifact | Prompt context evidence remains linked |
| review outcome summary | Summarizes review outcome only |
| accepted citation group | Accepted reviewed citations stay grouped |
| questioned citation group | Questioned citations stay visible |
| rejected citation group | Rejected citations stay visible |
| unresolved follow-up flags | Follow-up remains unresolved evidence |
| unsupported claim references | Unsupported claims stay visible |
| ReviewHistory | Review trace remains visible |
| failure behavior | Invalid export input fails without successful summary export |

## Prompt Context Audit Review Summary Export Inputs

The contract must define:

- prompt_context_audit_review_summary_export_action.
- export_prompt_context_audit_review_summary.
- prompt request id.
- AITask id.
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
- accepted citation ids.
- questioned citation ids.
- rejected citation ids.
- output citation ids.
- cited TestKnowledgeCard ids.
- cited context entry ids.
- cited source hashes.
- source hash.
- source quote/hash pointer.
- skipped evidence ids.
- skipped evidence.
- skip reasons.
- unsupported claims.
- unsupported claim references.
- unresolved follow-up flags.
- requested clarification.
- failure reasons.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.
- ReviewHistory ids.
- review decision ReviewHistory id.

## Summary Export Outputs

Prompt context audit review summary export may include:

- summary export id.
- summary export artifact id.
- prompt context audit review summary export artifact id.
- test_knowledge_card_prompt_context_audit_review_summary_export.json.
- artifact_type=test_knowledge_card_prompt_context_audit_review_summary_export.
- prompt_context_audit_review_summary_export.
- review outcome summary.
- accepted citation group.
- questioned citation group.
- rejected citation group.
- unresolved follow-up flag group.
- unresolved follow-up flags.
- unsupported claim references.
- reviewer comment summary.
- ReviewHistory links.
- source manifest ids.
- source hashes.
- PromptVersion/SkillVersion trace.
- context manifest references.
- failure_code.
- failure code.
- visible reason.

Summary exports are evidence packages about review decisions. Accepted citation
groups do not create prompt eligibility, approve TestKnowledgeCard content,
approve generated cases, alter `used_knowledge`, or mark skipped evidence as
cited.

Questioned citation groups, rejected citation groups, needs_clarification,
unresolved follow-up flags, skipped evidence, and unsupported claim references
preserve source hashes, context manifest links, PromptVersion/SkillVersion
trace, and ReviewHistory links. They are not deleted, filtered, rewritten, or
converted into cited knowledge.

## Failure Behavior

Prompt context audit review summary export must fail without successful summary
export when input is:

- missing prompt context audit review decision artifact.
- missing prompt context audit summary artifact.
- missing prompt context consumption artifact.
- missing prompt context evidence artifact.
- missing context manifest.
- missing output citations.
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

## Runtime Boundary

The prompt context audit review summary export contract is not runtime prompt
assembly, UI rendering, report generation, or export endpoint behavior:

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

TestKnowledgeCard Prompt Context Audit Review Summary Export remains summary
export evidence. It preserves prompt context audit review decision artifact id,
prompt context audit summary artifact id, prompt context consumption artifact
id, prompt context evidence artifact id, context manifest, source hash, review
outcome summary, accepted citation group, questioned citation group, rejected
citation group, unresolved follow-up flags, unsupported claim references,
PromptVersion, SkillVersion, ReviewHistory, failure behavior, and
`used_knowledge` without rendering UI, generating reports, exposing
export/download endpoints, assembling prompts, calling providers, creating
prompt eligibility, approving TestKnowledgeCard content, or approving generated
cases.
