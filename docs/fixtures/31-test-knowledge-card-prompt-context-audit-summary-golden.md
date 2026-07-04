# TestKnowledgeCard Prompt Context Audit Summary Golden

This fixture proves Slice 43 remains a contract-only TestKnowledgeCard Prompt
Context Audit Summary definition. It is not a frontend page, not report
generation behavior, not prompt assembly implementation, not prompt runtime
execution, not a provider call, not retrieval ranking, not broad
TestKnowledgeCard CRUD, not a backend feature API, and not a migration.

## Prompt Context Audit Summary Scenario

A future review or report surface may summarize TestKnowledgeCard prompt
context consumption only from existing prompt context consumption evidence. The
summary must preserve prompt context consumption artifact id, prompt context
evidence artifact id, `used_knowledge`, output citations, skipped evidence,
unsupported claims, source hash, context manifest, PromptVersion, SkillVersion,
ReviewHistory, failure behavior, and review flags without inventing citations
or mutating evidence.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Prompt Context Audit Summary | Read-only usage summary |
| summarize_prompt_context_consumption | Future scoped summary action only |
| prompt_context_audit_summary | Audit artifact, not frontend/report runtime |
| prompt context consumption artifact | Consumption evidence is required |
| prompt context evidence artifact | Evidence source remains linked |
| used_knowledge | Copied from consumption evidence |
| output citations | Existing citations are summarized only |
| skipped evidence | Skipped entries stay skipped |
| unsupported claims | Unsupported claims stay visible |
| source hash | Summary cites hash or quote/hash pointer |
| context manifest | Context links remain explicit |
| PromptVersion | Prompt trace is required |
| SkillVersion | Skill trace is required |
| ReviewHistory | Review trace remains visible |
| failure behavior | Invalid summary fails or flags without mutation |

## Prompt Context Audit Summary Inputs

The contract must define:

- prompt_context_audit_summary_action.
- summarize_prompt_context_consumption.
- prompt request id.
- AITask id.
- consuming agent step.
- intended output artifact type.
- prompt context consumption artifact id.
- test_knowledge_card_prompt_context_consumption.json.
- prompt context evidence artifact id.
- test_knowledge_card_prompt_context_evidence.json.
- context manifest artifact id.
- context_manifest.
- context_manifest.json.
- used_knowledge decision.
- used_knowledge=true.
- used_knowledge=false.
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
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.
- ReviewHistory ids.
- failure_code.

## Audit Summary Outputs

Prompt context audit summary may include:

- prompt context audit summary artifact id.
- test_knowledge_card_prompt_context_audit_summary.json.
- artifact_type=test_knowledge_card_prompt_context_audit_summary.
- prompt_context_audit_summary.
- usage status.
- knowledge_used.
- knowledge_not_used.
- knowledge_skipped.
- knowledge_failed.
- cited entries.
- cited evidence summaries.
- skipped entries.
- skipped evidence summaries.
- unsupported claim summaries.
- review flags.
- failure reasons.
- source manifest ids.
- source hashes.
- PromptVersion/SkillVersion trace.
- context manifest links.
- ReviewHistory links.

Audit summaries are read-only. They must not invent citations, rewrite
`used_knowledge`, promote unsupported claims, turn skipped evidence into cited
evidence, or mark knowledge used when prompt context consumption kept
`used_knowledge=false`.

## Failure Behavior

Prompt context audit summary must fail or flag:

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

## Runtime Boundary

The prompt context audit summary contract is not runtime prompt assembly or UI
rendering:

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

TestKnowledgeCard Prompt Context Audit Summary remains read-only audit
evidence. It preserves prompt context consumption artifact id, prompt context
evidence artifact id, context manifest, source hash, output citations, skipped
evidence, unsupported claims, PromptVersion, SkillVersion, ReviewHistory,
failure behavior, review flags, and `used_knowledge` without rendering UI,
generating reports, assembling prompts, or calling providers.
