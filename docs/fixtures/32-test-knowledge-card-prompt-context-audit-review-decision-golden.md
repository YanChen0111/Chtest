# TestKnowledgeCard Prompt Context Audit Review Decision Golden

This fixture proves Slice 44 remains a contract-only TestKnowledgeCard Prompt
Context Audit Review Decision definition. It is not a frontend page, not report
generation behavior, not prompt assembly implementation, not prompt runtime
execution, not a provider call, not retrieval ranking, not broad
TestKnowledgeCard CRUD, not a backend feature API, and not a migration.

## Prompt Context Audit Review Decision Scenario

A future human reviewer may review TestKnowledgeCard prompt context audit
summary evidence only from existing audit summary evidence. The decision must
preserve prompt context audit summary artifact id, prompt context consumption
artifact id, prompt context evidence artifact id, `used_knowledge`, usage
status, output citations, skipped evidence, unsupported claims, source hash,
context manifest, PromptVersion, SkillVersion, ReviewHistory, review action,
follow-up flags, failure behavior, and review decision evidence without
inventing citations or mutating evidence.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Prompt Context Audit Review Decision | Human review decision evidence |
| review_prompt_context_audit_summary | Future scoped review action only |
| prompt_context_audit_review_decision | Review artifact, not frontend/report runtime |
| prompt context audit summary artifact | Audit summary evidence is required |
| prompt context consumption artifact | Consumption evidence remains linked |
| prompt context evidence artifact | Prompt context evidence remains linked |
| used_knowledge | Copied from audit summary evidence |
| review action | Reviewer decision only |
| accepted | Accepts the audit summary evidence only |
| needs_clarification | Requests clarification without mutation |
| rejected_for_missing_evidence | Rejects missing evidence without rewriting |
| rejected_for_unsupported_claim | Rejects unsupported claims without promotion |
| rejected_for_citation_mismatch | Rejects citation mismatch without inventing citations |
| ReviewHistory | Review trace remains visible |
| follow-up flags | Future follow-up marker only |
| failure behavior | Invalid review input fails without successful ReviewHistory |

## Prompt Context Audit Review Decision Inputs

The contract must define:

- prompt_context_audit_review_decision_action.
- review_prompt_context_audit_summary.
- prompt request id.
- AITask id.
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
- unsupported claim summaries.
- review flags.
- failure reasons.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.
- ReviewHistory ids.
- prior ReviewHistory ids.

## Review Decision Outputs

Prompt context audit review decision may include:

- review decision id.
- review decision artifact id.
- prompt context audit review decision artifact id.
- test_knowledge_card_prompt_context_audit_review_decision.json.
- artifact_type=test_knowledge_card_prompt_context_audit_review_decision.
- prompt_context_audit_review_decision.
- reviewer label.
- local reviewer id.
- review action.
- reviewer comment.
- accepted citation ids.
- questioned citation ids.
- rejected citation ids.
- accepted citations.
- questioned citations.
- rejected citations.
- follow-up flags.
- requested clarification.
- ReviewHistory id.
- ReviewHistory decision.
- source manifest ids.
- source hashes.
- PromptVersion/SkillVersion trace.
- context manifest references.
- failure_code.
- failure code.
- visible reason.

Allowed review actions:

- accepted.
- needs_clarification.
- rejected_for_missing_evidence.
- rejected_for_unsupported_claim.
- rejected_for_citation_mismatch.
- rejected_for_stale_evidence.
- rejected_for_cross_project_evidence.

Review decisions are evidence about the audit summary. Accepted does not create
prompt eligibility, approve TestKnowledgeCard content, approve generated cases,
alter `used_knowledge`, or mark skipped evidence as cited.

Needs_clarification and rejected decisions preserve cited evidence, skipped
evidence, unsupported claims, source hashes, context manifest links,
PromptVersion/SkillVersion trace, and ReviewHistory links. They do not delete
or rewrite historical evidence.

## Failure Behavior

Prompt context audit review decision must fail without successful ReviewHistory
when input is:

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

## Runtime Boundary

The prompt context audit review decision contract is not runtime prompt
assembly, UI rendering, or report generation:

- no frontend page.
- no frontend rendering.
- no report generation behavior.
- no report renderer.
- no report export behavior.
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

TestKnowledgeCard Prompt Context Audit Review Decision remains human review
decision evidence. It preserves prompt context audit summary artifact id,
prompt context consumption artifact id, prompt context evidence artifact id,
context manifest, source hash, output citations, skipped evidence, unsupported
claims, PromptVersion, SkillVersion, ReviewHistory, failure behavior,
follow-up flags, review action, and `used_knowledge` without rendering UI,
generating reports, assembling prompts, calling providers, creating prompt
eligibility, approving TestKnowledgeCard content, or approving generated cases.
