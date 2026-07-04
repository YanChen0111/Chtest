# TestKnowledgeCard Retrieval Boundary Golden

This fixture proves Slice 40 remains a contract-only TestKnowledgeCard
Retrieval Boundary definition. It is not prompt runtime retrieval, not
deterministic retrieval behavior change, not broad TestKnowledgeCard CRUD, not
a backend feature API, not a frontend page, and not a migration.

## Retrieval Boundary Scenario

A future prompt-context workflow may consider a reviewed TestKnowledgeCard only
after human prompt eligibility has already granted `allowed_for_prompt=true`.
That flag is necessary but not sufficient. The retrieval boundary must also
validate `prompt_eligible` state evidence, safe_to_show, redaction, source
evidence, source manifest, ReviewHistory, and prompt eligibility artifact
evidence before recording retrieval evidence for a selected card.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Retrieval Boundary | Read-only prompt-context selection contract |
| select_prompt_eligible_cards | Future scoped selection action only |
| allowed_for_prompt | Necessary but not sufficient for selection |
| prompt_eligible | Current eligibility state is required |
| safe_to_show | Display safety must remain true |
| redaction | Redaction status must be reviewed |
| source evidence | Evidence must remain same-project and bounded |
| source manifest | Source manifest must still match the card evidence |
| ReviewHistory | ReviewHistory ids preserve review trace |
| prompt eligibility artifact | Eligibility artifact evidence is required |
| retrieval evidence | Selection/exclusion evidence is recorded only |
| excluded_card_reason | Every excluded card records why |
| failure behavior | Invalid evidence excludes without mutation |

## Selection Inputs

The contract must define:

- select_prompt_eligible_cards.
- retrieval_boundary_action.
- project_id.
- prompt_request_id.
- reviewed TestKnowledgeCard id.
- candidate_test_knowledge_card_ids.
- allowed_for_prompt=true.
- prompt_eligible.
- prompt eligibility artifact id.
- test_knowledge_card_prompt_eligibility.json.
- test_knowledge_card_retrieval_boundary.json.
- artifact_type=test_knowledge_card_retrieval_boundary.
- creation artifact id.
- reviewed_test_knowledge_card_creation.json.
- source_manifest.
- same-project source Artifact.
- source_artifact_ids.
- source_quote_or_hash.
- source span.
- redaction report artifact id.
- safe_to_show=true.
- redaction status reviewed.
- ReviewHistory id.
- unsupported claims.

## Eligibility Filters

Selection requires all of:

- current `prompt_eligible` state.
- `allowed_for_prompt=true`.
- `safe_to_show=true`.
- reviewed redaction status.
- same-project source evidence.
- source manifest.
- reviewed source citations.
- ReviewHistory.
- prompt eligibility artifact evidence.
- selection reason.

`allowed_for_prompt=true` is necessary but not sufficient for future
prompt-context selection.

## Exclusion Behavior

The contract must exclude cards for:

- allowed_for_prompt=false.
- prompt_eligibility_denied.
- prompt_eligibility_revision_requested.
- prompt_eligibility_revoked.
- stale evidence.
- cross-project evidence.
- unsafe evidence.
- missing source evidence.
- unbounded evidence.
- unsupported claims.
- redaction failure.
- source manifest mismatch.
- missing ReviewHistory.
- missing prompt eligibility artifact evidence.
- evidence-mismatched.
- excluded_card_reason.
- failure_code.

Excluded cards must not revoke prompt eligibility, delete cards, mutate
artifacts, rewrite source evidence, or rewrite ReviewHistory.

## Retrieval Evidence Outputs

Retrieval boundary evidence must preserve:

- selected_test_knowledge_card_ids.
- excluded TestKnowledgeCard ids.
- excluded_cards.
- excluded_card_reason.
- retrieval evidence.
- retrieval_evidence_artifact_id.
- test_knowledge_card_retrieval_boundary.json.
- artifact_type=test_knowledge_card_retrieval_boundary.
- prompt eligibility artifact ids.
- creation artifact ids.
- source evidence ids.
- source manifest artifact id.
- source quote/hash.
- ReviewHistory ids.
- safe_to_show.
- redaction status.
- prompt_eligible.
- allowed_for_prompt.
- selection reason.
- bounded snippet or source hash.

Retrieval evidence must not include raw large source text, unsafe provider
payloads, vector store payloads, embedding vectors, reranker traces, graph
runtime payloads, or prompt assembly payloads.

## Runtime Boundary

The retrieval boundary is not runtime retrieval:

- no retrieval endpoint.
- no prompt runtime retrieval implementation.
- no deterministic retrieval behavior change.
- no deterministic retrieval ranking change.
- no prompt assembly.
- no semantic search.
- no vector index.
- no vector database.
- no embedding.
- no embeddings.
- no reranking.
- no background indexing.
- no graph job.
- no GraphRAG job.
- no MCP runtime.
- no provider call.

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
- prompt runtime retrieval implementation.
- prompt runtime retrieval change.
- deterministic retrieval behavior change.
- deterministic retrieval ranking change.
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
- queue.
- scheduler.
- background worker.
- artifact upload.
- Artifact mutation.
- artifact delete.
- source artifact mutation.
- prompt eligibility artifact mutation.
- historical evidence mutation.
- historical ReviewHistory mutation.
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

TestKnowledgeCard Retrieval Boundary remains auditable read-only selection
evidence. It preserves prompt eligibility, safe_to_show, source manifest,
redaction, ReviewHistory, prompt eligibility artifact evidence, exclusion
reasons, failure behavior, and retrieval evidence outputs without implementing
prompt runtime retrieval.
