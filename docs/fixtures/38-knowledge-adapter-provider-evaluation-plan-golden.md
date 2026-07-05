# KnowledgeAdapter Provider Evaluation Plan Golden

This fixture proves Slice 50 remains a contract-only KnowledgeAdapter Provider
Evaluation Plan definition. It is planning evidence only for future provider
evaluation, not a Haystack provider integration, not a LlamaIndex provider
integration, not a GraphRAG provider integration, not a provider SDK call, not
an external provider call, not runtime retrieval, not provider enablement, and
not provider-backed prompt context evidence.

## Provider Evaluation Scenario

A future workflow may package KnowledgeAdapter provider evaluation evidence
only for a disabled-by-default provider candidate. The record must preserve the
candidate provider name, provider family, adapter type, provider version,
adapter version, license name, license URL, license compatibility notes,
license review result, reference intake URLs, documentation snapshot artifact
ids, supported retrieval modes, supported source types, expected
KnowledgeEvidence normalization fields, provider_state, provider_state
recommendation, disabled by default policy, disabled by default decision,
network policy, credential policy, fallback behavior expectations, fallback
behavior summary, metrics to collect, metrics plan, metric set, evidence
normalization completeness, source traceability coverage, redaction safety
status, fallback coverage, safety and redaction requirements, source hash
requirements, source manifest ids, source hashes, ReviewHistory ids,
ReviewHistory links, failure_code, failure code, visible_reason, visible
reason, and failure behavior without enabling a provider or claiming that
knowledge was used.

| Surface | Required boundary |
|---|---|
| KnowledgeAdapter Provider Evaluation Plan | Provider evaluation planning evidence only |
| evaluate_knowledge_adapter_provider_plan | Future scoped evaluation action only |
| knowledge_adapter_provider_evaluation_plan | Artifact and manifest naming only |
| provider evaluation | Candidate review before provider integration |
| provider candidate | Disabled-by-default candidate metadata only |
| Haystack | Candidate provider family, not runtime integration |
| LlamaIndex | Candidate provider family, not runtime integration |
| GraphRAG | Candidate provider family, not runtime integration |
| KnowledgeEvidence | Normalization target, not generated evidence here |
| provider_state | Display/health metadata only |
| fallback behavior | Local/no-knowledge fallback stays visible |
| license review | Required before any future integration |
| reference intake | Documentation/reference intake evidence only |
| disabled by default | Safe candidate outcome |
| metrics | Evaluation metadata only |
| provider suitability status | Evaluation label only |
| ReviewHistory | Human review trace remains visible |
| failure behavior | Invalid input fails without successful provider-ready state |

## Provider Evaluation Inputs

The contract must define:

- knowledge_adapter_provider_evaluation_plan_action.
- evaluate_knowledge_adapter_provider_plan.
- evaluate_provider_candidate.
- record_provider_evaluation.
- block_provider_candidate.
- request_provider_evaluation_revision.
- enforce_disabled_by_default.
- provider_candidate_not_evaluated.
- provider_evaluation_pending.
- provider_evaluation_recorded.
- provider_evaluation_blocked.
- provider_evaluation_needs_revision.
- provider_candidate_disabled_by_default.
- candidate provider name.
- provider family.
- adapter type.
- provider version.
- adapter version.
- license name.
- license URL.
- license compatibility notes.
- license review result.
- reference intake URLs.
- documentation snapshot artifact ids.
- supported retrieval modes.
- supported source types.
- expected KnowledgeEvidence normalization fields.
- KnowledgeEvidence normalization.
- provider_state.
- provider_state recommendation.
- disabled by default policy.
- disabled by default decision.
- network policy.
- credential policy.
- fallback behavior expectations.
- fallback behavior summary.
- metrics to collect.
- metrics plan.
- metric set.
- evidence normalization completeness.
- source traceability coverage.
- redaction safety status.
- fallback coverage.
- safety and redaction requirements.
- source hash requirements.
- source manifest ids.
- source hashes.
- ReviewHistory ids.
- ReviewHistory links.

## Provider Evaluation Outputs

KnowledgeAdapter provider evaluation plan output may include:

- provider evaluation plan id.
- provider evaluation plan artifact id.
- knowledge_adapter_provider_evaluation_plan_artifact_id.
- knowledge_adapter_provider_evaluation_plan.
- knowledge_adapter_provider_evaluation_plan.json.
- artifact_type=knowledge_adapter_provider_evaluation_plan.
- manifest_kind=knowledge_adapter_provider_evaluation_plan.
- provider suitability status.
- not_evaluated.
- suitable.
- suitable_with_constraints.
- blocked.
- needs_revision.
- unsupported.
- KnowledgeEvidence normalization notes.
- normalized KnowledgeEvidence requirements.
- citation traceability requirements.
- redaction and safety requirements.
- blocker reasons.
- unresolved safety questions.
- fallback_required.
- local_no_knowledge_fallback.
- normalization_required.
- citation_traceability_required.
- license_review_required.
- planning evidence only.
- used_knowledge=true.
- failure_code.
- failure code.
- visible_reason.
- visible reason.
- prompt_input.json.

Provider suitability status, provider_state recommendation, disabled by
default decision, fallback behavior summary, metrics plan, blocker reasons,
unresolved safety questions, source hashes, source manifest ids, and
ReviewHistory links are evidence labels. They do not create provider
connectivity, provider-backed prompt context evidence, runtime retrieval, or
automatic used_knowledge=true.

## Failure Behavior

KnowledgeAdapter provider evaluation must fail without a successful provider
evaluation plan when input is missing, stale, unsafe, unlicensed,
license-unknown, version-unknown, reference-missing, reference-mismatched,
normalization-unsupported, redaction-failed, provider-state-unsafe,
fallback-missing, cross-project, unbounded, credential-required,
runtime-required, or provider-evaluation-mismatched input.

Invalid provider evaluation input must produce failure_code, failure code,
visible_reason, and visible reason. It must not append a successful provider
evaluation plan, mark a provider ready, rewrite KnowledgeEvidence, or set
used_knowledge=true.

## Runtime Boundary

The KnowledgeAdapter Provider Evaluation Plan contract is not provider runtime,
prompt runtime, provider-backed prompt context, UI, backend API, or storage
mutation behavior:

- no Haystack provider integration.
- no LlamaIndex provider integration.
- no GraphRAG provider integration.
- no provider SDK.
- no provider SDK call.
- no external provider call.
- no API key handling.
- no credentials.
- no OAuth.
- no remote URL fetch.
- no external call.
- no network retrieval.
- no runtime retrieval.
- no provider-backed prompt context evidence.
- no prompt assembly implementation.
- no prompt runtime execution.
- no automatic used_knowledge=true marking.
- no vector database.
- no vector index.
- no embedding model.
- no embedding service.
- no embedding vectors.
- no embedding.
- no embeddings.
- no semantic index.
- no ANN search.
- no reranking service.
- no reranking.
- no background indexing job.
- no crawler.
- no document chunking pipeline.
- no graph runtime.
- no GraphRAG job.
- no MCP runtime.
- no frontend page.
- no report generation behavior.
- no export/download endpoint.
- no backend feature API.
- no endpoint.
- no router.
- no service.
- no worker.
- no queue.
- no scheduler.
- no migration.
- no package upgrade.
- no broad KnowledgeAdapter CRUD.
- no automatic provider enablement.
- no automatic knowledge ingestion.
- no TestKnowledgeCard CRUD.
- no automatic prompt eligibility.
- no artifact upload.
- no Artifact mutation.
- no artifact delete.
- no KnowledgeAdapterConfig runtime state mutation.
- no KnowledgeEvidence mutation.
- no TestKnowledgeCard mutation.
- no GeneratedCaseCandidate mutation.
- no TestCase auto-promotion.
- no generated-case auto-approval.
- no ToolInvocation rows.
- no execute AITasks.
- no runner behavior change.
- no remote CI provider behavior.
- no RBAC.
- no tenants.
- no permissions.
- no review bypass.

## Forbidden Side Effects

The contract must not create or trigger:

- Haystack provider integration.
- LlamaIndex provider integration.
- GraphRAG provider integration.
- provider SDK.
- provider SDK call.
- external provider call.
- API key handling.
- credentials.
- OAuth.
- remote URL fetch.
- external call.
- network retrieval.
- runtime retrieval.
- provider-backed prompt context evidence.
- prompt assembly implementation.
- prompt runtime execution.
- automatic used_knowledge=true marking.
- vector database.
- vector index.
- embedding model.
- embedding service.
- embedding vectors.
- embedding.
- embeddings.
- semantic index.
- ANN search.
- reranking service.
- reranking.
- background indexing job.
- crawler.
- document chunking pipeline.
- graph runtime.
- GraphRAG job.
- MCP runtime.
- frontend page.
- report generation behavior.
- export/download endpoint.
- backend feature API.
- endpoint.
- router.
- service.
- worker.
- queue.
- scheduler.
- migration.
- package upgrade.
- broad KnowledgeAdapter CRUD.
- automatic provider enablement.
- automatic knowledge ingestion.
- TestKnowledgeCard CRUD.
- automatic prompt eligibility.
- artifact upload.
- Artifact mutation.
- artifact delete.
- KnowledgeAdapterConfig runtime state mutation.
- KnowledgeEvidence mutation.
- TestKnowledgeCard mutation.
- GeneratedCaseCandidate mutation.
- TestCase auto-promotion.
- generated-case auto-approval.
- ToolInvocation rows.
- execute AITasks.
- runner behavior change.
- remote CI provider behavior.
- RBAC.
- tenants.
- permissions.
- review bypass.

KnowledgeAdapter Provider Evaluation Plan remains planning evidence. It
preserves provider evaluation inputs, KnowledgeEvidence normalization
requirements, provider_state recommendation, fallback behavior, license
review, reference intake, disabled by default policy, metrics, ReviewHistory,
failure behavior, failure_code, visible_reason, and visible reason without
installing packages, calling providers, creating vector infrastructure,
assembling prompts, running retrieval, enabling providers, mutating historical
evidence, or bypassing review.
