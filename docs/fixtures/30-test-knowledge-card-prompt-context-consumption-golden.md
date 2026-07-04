# TestKnowledgeCard Prompt Context Consumption Golden

This fixture proves Slice 42 remains a contract-only TestKnowledgeCard Prompt
Context Consumption definition. It is not prompt assembly implementation, not
prompt runtime execution, not a provider call, not retrieval ranking, not broad
TestKnowledgeCard CRUD, not a backend feature API, not a frontend page, and not
a migration.

## Prompt Context Consumption Scenario

A future agent may claim TestKnowledgeCard knowledge was used only after prompt
context evidence has been built and the consumption contract has validated the
agent input and output citations. The consumption evidence must preserve the
prompt context evidence artifact id, context manifest, consumed
TestKnowledgeCard ids, source hash, output citations, PromptVersion,
SkillVersion, ReviewHistory, skipped evidence, failure behavior, and
`used_knowledge` decision before any result can be treated as knowledge-backed.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Prompt Context Consumption | Citation evidence for future outputs |
| consume_prompt_context_evidence | Future scoped consumption action only |
| prompt_context_consumption | Consumption artifact, not prompt execution |
| prompt context evidence artifact | Existing evidence is required |
| context manifest | Context links remain explicit |
| used_knowledge | True only with valid consumed citation |
| consumed TestKnowledgeCard ids | Consumed cards are explicit |
| source hash | Citation uses hash or quote/hash pointer |
| output citations | Output must point back to consumed evidence |
| PromptVersion | Prompt trace is required |
| SkillVersion | Skill trace is required |
| ReviewHistory | Review trace remains visible |
| skipped evidence | Invalid evidence is skipped with reason |
| failure behavior | Invalid consumption fails or stays unused |

## Prompt Context Consumption Inputs

The contract must define:

- prompt_context_consumption_action.
- consume_prompt_context_evidence.
- prompt request id.
- AITask id.
- consuming agent step.
- intended output artifact type.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.
- prompt context evidence artifact id.
- test_knowledge_card_prompt_context_evidence.json.
- context manifest artifact id.
- context_manifest.
- context_manifest.json.
- selected TestKnowledgeCard ids.
- consumed TestKnowledgeCard ids.
- consumed context entry ids.
- consumed source hashes.
- source hash.
- source quote/hash pointer.
- source artifact ids.
- source manifest ids.
- source sections.
- retrieval boundary artifact id.
- prompt eligibility artifact ids.
- ReviewHistory ids.
- omission summaries.
- unsupported claims.
- skipped evidence.
- skip reason.
- failure_code.

## Consumption Decision

Prompt context consumption may set:

- used_knowledge=false.
- used_knowledge=true.
- consumed knowledge citations.
- output citations.
- citation id.
- citation status.
- cited TestKnowledgeCard id.
- cited prompt context evidence artifact id.
- cited context entry id.
- cited source hash.
- cited source quote/hash pointer.
- source artifact id.
- source section.
- PromptVersion/SkillVersion trace.
- ReviewHistory id.
- unsupported claim marker.
- skipped evidence summaries.

`used_knowledge=true` is valid only when at least one output citation points to
consumed prompt context evidence, a consumed context entry id, a source hash or
source quote/hash pointer, a same-project source artifact, PromptVersion,
SkillVersion, and ReviewHistory.

`used_knowledge=false` is required when no valid prompt context evidence is
consumed or when citation evidence is missing, stale, unsafe, revoked,
cross-project, unbounded, redaction-failed, context-mismatched,
prompt-version-mismatched, skill-version-mismatched, citation-mismatched, or
evidence-mismatched.

## Evidence Outputs

Prompt context consumption must preserve:

- prompt context consumption artifact id.
- test_knowledge_card_prompt_context_consumption.json.
- artifact_type=test_knowledge_card_prompt_context_consumption.
- prompt_context_consumption.
- prompt context evidence artifact id.
- context manifest links.
- consumed TestKnowledgeCard ids.
- consumed context entry ids.
- consumed source hashes.
- output citations.
- source manifest ids.
- source hashes.
- PromptVersion/SkillVersion trace.
- ReviewHistory ids.
- skipped evidence.
- skip reasons.
- unsupported claims.
- failure code.

The artifact must use source hash or source quote/hash pointer in citations and
must not copy raw large source text.

## Runtime Boundary

The prompt context consumption contract is not runtime prompt assembly:

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
- report generation behavior change.
- remote CI provider behavior.
- RBAC.
- tenants.
- permissions.
- package upgrades.

TestKnowledgeCard Prompt Context Consumption remains auditable citation
evidence. It preserves prompt context evidence artifact id, context manifest,
source hash, consumed context entry ids, PromptVersion, SkillVersion,
ReviewHistory, skipped evidence, output citations, failure behavior, and
`used_knowledge` decision without assembling prompts or calling providers.
