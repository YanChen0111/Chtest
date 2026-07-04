# TestKnowledgeCard Prompt Context Evidence Golden

This fixture proves Slice 41 remains a contract-only TestKnowledgeCard Prompt
Context Evidence definition. It is not prompt assembly implementation, not
prompt runtime execution, not a provider call, not retrieval ranking, not broad
TestKnowledgeCard CRUD, not a backend feature API, not a frontend page, and not
a migration.

## Prompt Context Evidence Scenario

A future prompt workflow may use selected TestKnowledgeCard evidence only after
the retrieval boundary has selected the card and the prompt context evidence
contract has shaped a bounded, safe, traceable context entry. The evidence must
preserve PromptVersion, SkillVersion, retrieval boundary artifact, source
manifest, ReviewHistory, prompt eligibility artifact, context manifest links,
bounded snippet or source hash, omission reason, and failure behavior before
any provider or prompt runtime can use it.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Prompt Context Evidence | Bounded evidence for future prompt context |
| build_prompt_context_evidence | Future scoped evidence action only |
| prompt_context_evidence | Evidence artifact, not prompt execution |
| bounded snippet | Text must be bounded and safe |
| source hash | Hash replaces text when safety cannot be proven |
| retrieval boundary artifact | Selection evidence is required |
| PromptVersion | Prompt trace is required |
| SkillVersion | Skill trace is required |
| context manifest | Context links remain explicit |
| ReviewHistory | Review trace remains visible |
| omission reason | Omitted cards explain why |
| failure behavior | Invalid evidence fails or omits without mutation |

## Prompt Context Inputs

The contract must define:

- prompt_context_evidence_action.
- build_prompt_context_evidence.
- prompt request id.
- AITask id.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.
- retrieval boundary artifact id.
- test_knowledge_card_retrieval_boundary.json.
- selected TestKnowledgeCard ids.
- omitted TestKnowledgeCard ids.
- prompt eligibility artifact ids.
- ReviewHistory ids.
- source manifest ids.
- source artifact ids.
- source hash values.
- source trace labels.
- context manifest artifact id.
- safe_to_show=true.
- reviewed redaction.
- unsupported claims.
- omission reason.
- failure_code.

## Context Entries

Prompt context evidence entries may include:

- TestKnowledgeCard id.
- knowledge_type.
- title.
- summary.
- safe bounded snippet.
- bounded snippet.
- source hash.
- source quote/hash pointer.
- source artifact ids.
- source section.
- retrieval boundary artifact id.
- prompt eligibility artifact id.
- ReviewHistory id.
- selection reason.
- source trace label.
- omission reason.

Text enters prompt context only when `safe_to_show=true`, reviewed redaction,
source evidence, retrieval boundary evidence, and prompt eligibility artifact
evidence are present.

## Evidence Outputs

Prompt context evidence must preserve:

- prompt context evidence artifact id.
- test_knowledge_card_prompt_context_evidence.json.
- artifact_type=test_knowledge_card_prompt_context_evidence.
- selected context entries.
- omitted card summaries.
- source manifest ids.
- source hashes.
- PromptVersion/SkillVersion trace.
- context manifest links.
- context_manifest.
- context_manifest.json.
- prompt_input.json boundary.
- omission reason.
- failure code.

The artifact must use source hash or source quote/hash pointer when snippet
bounds, redaction, or display safety cannot be proven.

## Runtime Boundary

The prompt context evidence contract is not runtime prompt assembly:

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
- no used_knowledge=true auto-marking.
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
- report generation behavior change.
- remote CI provider behavior.
- RBAC.
- tenants.
- permissions.
- package upgrades.

TestKnowledgeCard Prompt Context Evidence remains auditable bounded evidence.
It preserves retrieval boundary evidence, safe_to_show, redaction, source
manifest, source hash, bounded snippet metadata, PromptVersion, SkillVersion,
context manifest links, ReviewHistory, omission reasons, and failure behavior
without assembling prompts or calling providers.
