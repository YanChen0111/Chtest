# TestKnowledgeCard Prompt Context Discrepancy Resolution Review Golden

This fixture proves Slice 47 remains a contract-only TestKnowledgeCard Prompt
Context Discrepancy Resolution Review definition. It is not a frontend page,
not report generation behavior, not an export/download endpoint, not prompt
assembly implementation, not prompt runtime execution, not a provider call,
not retrieval ranking, not broad TestKnowledgeCard CRUD, not a backend feature
API, and not a migration.

## Prompt Context Discrepancy Resolution Scenario

A future workflow may record resolution review evidence only from existing
prompt context review discrepancy, review summary export, audit review
decision, audit summary, prompt context consumption, and prompt context
evidence. The resolution review record must preserve prompt context review
discrepancy artifact id, prompt context audit review summary export artifact
id, prompt context audit review decision artifact id, prompt context audit
summary artifact id, prompt context consumption artifact id, prompt context
evidence artifact id, `used_knowledge`, usage status, discrepancy type,
affected citation ids, evidence gap summary, mismatch reason, reviewer note
from discrepancy tracking, severity, current resolution status, resolution
action, accepted discrepancy ids, rejected discrepancy ids, acknowledged
discrepancy ids, clarification requested fields, resulting resolution status,
unresolved follow-up flags, unsupported claim references, source hash, context
manifest, PromptVersion, SkillVersion, ReviewHistory, and failure behavior
without inventing citations or mutating evidence.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Prompt Context Discrepancy Resolution Review | Human resolution review evidence |
| review_prompt_context_discrepancy_resolution | Future scoped resolution review action only |
| prompt_context_discrepancy_resolution_review | Resolution review artifact, not frontend/report/export runtime |
| prompt context review discrepancy artifact | Discrepancy evidence is required |
| review summary export artifact | Summary export evidence remains linked |
| audit review decision artifact | Review decision evidence remains linked |
| audit summary artifact | Audit summary evidence remains linked |
| prompt context consumption artifact | Consumption evidence remains linked |
| prompt context evidence artifact | Context evidence remains linked |
| resolution action | Human review action only |
| accepted discrepancy ids | Existing discrepancies remain visible |
| rejected discrepancy ids | Existing discrepancies remain visible |
| acknowledged discrepancy ids | Existing discrepancies remain visible |
| clarification requested fields | Clarification evidence remains visible |
| affected citation ids | Existing citations remain visible |
| evidence gap summary | Explains missing or weak evidence |
| mismatch reason | Explains the discrepancy |
| reviewer note | Human note, not mutation |
| severity | Audit label only |
| resolution status | Status label only |
| ReviewHistory | Review trace remains visible |
| failure behavior | Invalid resolution review input fails without successful record |

## Prompt Context Discrepancy Resolution Review Inputs

The contract must define:

- prompt_context_discrepancy_resolution_review_action.
- review_prompt_context_discrepancy_resolution.
- prompt request id.
- AITask id.
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
- discrepancy type.
- affected citation ids.
- evidence gap summary.
- mismatch reason.
- reviewer note from discrepancy tracking.
- severity.
- current resolution status.
- unresolved follow-up flags.
- unsupported claim references.
- source hashes.
- source hash.
- source quote/hash pointer.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.
- ReviewHistory ids.
- discrepancy ReviewHistory id.

## Resolution Review Outputs

Prompt context discrepancy resolution review may include:

- resolution review id.
- resolution review artifact id.
- prompt context discrepancy resolution review artifact id.
- test_knowledge_card_prompt_context_discrepancy_resolution_review.json.
- artifact_type=test_knowledge_card_prompt_context_discrepancy_resolution_review.
- prompt_context_discrepancy_resolution_review.
- resolution review action.
- resolution action.
- acknowledge_discrepancy.
- reject_discrepancy_resolution.
- request_discrepancy_clarification.
- mark_resolved_by_later_review.
- accepted discrepancy ids.
- rejected discrepancy ids.
- acknowledged discrepancy ids.
- clarification requested fields.
- reviewer note.
- resulting resolution status.
- open.
- needs_clarification.
- acknowledged.
- rejected.
- resolved_by_later_review.
- follow-up flags.
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

Resolution review records are evidence about human review of mismatches.
Resolution actions and resulting resolution status values do not create prompt
eligibility, approve TestKnowledgeCard content, approve generated cases, alter
`used_knowledge`, mark skipped evidence as cited, invent citations, or
auto-resolve discrepancies.

Accepted discrepancy ids, rejected discrepancy ids, acknowledged discrepancy
ids, affected citation ids, questioned citation group, rejected citation group,
unresolved follow-up flags, skipped evidence, unsupported claim references,
evidence gap summary, mismatch reason, source hashes, context manifest links,
PromptVersion/SkillVersion trace, and ReviewHistory links remain visible. They
are not deleted, filtered, rewritten, or converted into cited knowledge.

## Failure Behavior

Prompt context discrepancy resolution review must fail without successful
resolution review record when input is:

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
- evidence-mismatched input.
- audit summary-mismatched input.
- review-decision-mismatched input.
- summary-export-mismatched input.

## Runtime Boundary

The prompt context discrepancy resolution review contract is not runtime prompt
assembly, UI rendering, report generation, export endpoint behavior, or
automatic remediation:

- no frontend page.
- no frontend rendering.
- no report generation behavior.
- no report renderer.
- no report export behavior.
- no export/download endpoint.
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

TestKnowledgeCard Prompt Context Discrepancy Resolution Review remains human
resolution review evidence. It preserves prompt context review discrepancy
artifact id, review summary export artifact id, audit review decision artifact
id, audit summary artifact id, prompt context consumption artifact id, prompt
context evidence artifact id, context manifest, source hash, discrepancy type,
affected citation ids, evidence gap summary, mismatch reason, reviewer note,
severity, current resolution status, resolution action, accepted discrepancy
ids, rejected discrepancy ids, acknowledged discrepancy ids, clarification
requested fields, resulting resolution status, unresolved follow-up flags,
unsupported claim references, PromptVersion, SkillVersion, ReviewHistory,
failure behavior, and `used_knowledge` without rendering UI, generating
reports, exposing export/download endpoints, assembling prompts, calling
providers, creating prompt eligibility, approving TestKnowledgeCard content,
auto-resolving discrepancies, or approving generated cases.
