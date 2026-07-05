# KnowledgeAdapter Provider Evaluation Review Summary Export Golden

This fixture proves Slice 52 remains a contract-only KnowledgeAdapter Provider
Evaluation Review Summary Export definition. It is audit evidence only for
future provider planning, not provider enablement, not a Haystack provider
integration, not a LlamaIndex provider integration, not a GraphRAG provider
integration, not a provider SDK call, not runtime retrieval, not a report
generator, and not an export/download endpoint.

## Provider Evaluation Review Summary Export Scenario

A future workflow may package a local provider evaluation review decision into
a summary export artifact. The record must preserve provider evaluation review
decision artifact id,
knowledge_adapter_provider_evaluation_review_decision_artifact_id, same-project
provider evaluation review decision artifact, provider evaluation plan artifact
id, knowledge_adapter_provider_evaluation_plan_artifact_id, same-project
provider evaluation plan artifact,
created_by_component=KnowledgeAdapterProviderEvaluationReviewSummaryExport,
owner_entity_type=AITask, owner_entity_type=Project, candidate provider name,
provider family, adapter type, provider version, adapter version, provider
suitability status, review decision, review status, review summary status,
exported decision groups, reviewer label, local reviewer id, reviewer notes,
accepted constraints, blocked reasons, unsupported reasons, requested revision
fields, unresolved safety questions, decision rationale, license name, license
URL, license compatibility notes, license review result, license/reference
summary, reference intake summary, reference intake URLs, documentation
snapshot artifact ids, expected KnowledgeEvidence normalization fields,
KnowledgeEvidence normalization, KnowledgeEvidence normalization notes,
KnowledgeEvidence normalization summary, provider_state, provider_state
recommendation, provider_state summary, disabled by default policy, disabled
by default decision, disabled by default summary, fallback behavior summary,
fallback labels, fallback summary, metrics plan, metric set, metrics summary,
evidence normalization completeness, source traceability coverage, redaction
safety status, fallback coverage, source traceability summary, source manifest
ids, source hashes, ReviewHistory ids, ReviewHistory links, ReviewHistory
summary, failure_code, failure code, visible_reason, visible reason, and
failure behavior without enabling a provider or claiming that knowledge was
used.

| Surface | Required boundary |
|---|---|
| KnowledgeAdapter Provider Evaluation Review Summary Export | Provider review summary audit evidence only |
| export_knowledge_adapter_provider_evaluation_review_summary | Future scoped summary export action only |
| knowledge_adapter_provider_evaluation_review_summary_export | Artifact and manifest naming only |
| provider evaluation review summary export | Local review summary evidence before provider integration |
| provider evaluation review decision artifact | Reviewed decision evidence source |
| provider evaluation plan artifact | Reviewed plan evidence source |
| review summary status | Summary export state only |
| exported decision groups | Audit grouping labels only |
| accepted_for_planning | Future planning label only |
| accepted_with_constraints | Future planning label with constraints only |
| blocked | Provider candidate remains blocked |
| needs_revision | Requested revision remains visible |
| unsupported | Unsupported reason remains visible |
| provider suitability status | Input status from the review decision |
| KnowledgeEvidence | Normalization target, not generated evidence here |
| provider_state | Display/health metadata only |
| fallback behavior | Local/no-knowledge fallback stays visible |
| license review | Required before any future integration |
| reference intake | Documentation/reference intake evidence only |
| disabled by default policy | Provider remains disabled |
| ReviewHistory | Human review trace remains visible |
| failure behavior | Invalid input fails without successful summary export |

## Provider Evaluation Review Summary Export Inputs

The contract must define:

- knowledge_adapter_provider_evaluation_review_summary_export_action.
- knowledge_adapter_provider_evaluation_review_summary_export_action=export_knowledge_adapter_provider_evaluation_review_summary.
- export_knowledge_adapter_provider_evaluation_review_summary.
- provider evaluation review decision artifact.
- provider evaluation review decision artifact id.
- knowledge_adapter_provider_evaluation_review_decision_artifact_id.
- provider evaluation plan artifact.
- provider evaluation plan artifact id.
- knowledge_adapter_provider_evaluation_plan_artifact_id.
- created_by_component=KnowledgeAdapterProviderEvaluationReviewSummaryExport.
- owner_entity_type=AITask.
- owner_entity_type=Project.
- same-project provider evaluation review decision artifact.
- same-project provider evaluation plan artifact.
- candidate provider name.
- provider family.
- adapter type.
- provider version.
- adapter version.
- provider suitability status.
- review decision.
- review status.
- review summary status.
- exported decision groups.
- reviewer label.
- local reviewer id.
- reviewer notes.
- accepted constraints.
- blocked reasons.
- unsupported reasons.
- requested revision fields.
- unresolved safety questions.
- decision rationale.
- license name.
- license URL.
- license compatibility notes.
- license review result.
- license/reference summary.
- reference intake summary.
- reference intake URLs.
- documentation snapshot artifact ids.
- expected KnowledgeEvidence normalization fields.
- KnowledgeEvidence normalization.
- KnowledgeEvidence normalization notes.
- KnowledgeEvidence normalization summary.
- provider_state.
- provider_state recommendation.
- provider_state summary.
- disabled by default policy.
- disabled by default decision.
- disabled by default summary.
- fallback behavior summary.
- fallback labels.
- fallback summary.
- metrics plan.
- metric set.
- metrics summary.
- evidence normalization completeness.
- source traceability coverage.
- redaction safety status.
- fallback coverage.
- source traceability summary.
- source manifest ids.
- source hashes.
- ReviewHistory ids.
- ReviewHistory links.
- ReviewHistory summary.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.

## Field-Level Keys

The summary export request and response evidence keeps these explicit payload
fields:

- project_id.
- knowledge_adapter_provider_evaluation_review_decision_artifact_id.
- knowledge_adapter_provider_evaluation_plan_artifact_id.
- candidate_provider_name.
- provider_family.
- adapter_type.
- provider_version.
- adapter_version.
- provider_suitability_status.
- review_decision.
- review_status.
- reviewer_notes.
- accepted_constraints.
- requested_revision_fields.
- blocked_reasons.
- unsupported_reasons.
- unresolved_safety_questions.
- license_review_result.
- reference_intake_summary.
- knowledge_evidence_normalization_notes.
- provider_state_recommendation.
- disabled_by_default_decision.
- fallback_behavior_summary.
- metrics_plan.
- source_manifest_ids.
- source_hashes.
- review_history_links.
- knowledge_adapter_provider_evaluation_review_summary_export_artifact_id.
- review_summary_status.
- exported_decision_groups.
- provider_suitability_summary.
- license_reference_summary.
- knowledge_evidence_normalization_summary.
- provider_state_summary.
- disabled_by_default_summary.
- fallback_summary.
- metrics_summary.
- source_traceability_summary.
- review_history_summary.
- failure_code.
- visible_reason.

## Provider Evaluation Review Summary Export Outputs

KnowledgeAdapter provider evaluation review summary export output may include:

- provider evaluation review summary export id.
- provider evaluation review summary export artifact id.
- knowledge_adapter_provider_evaluation_review_summary_export_artifact_id.
- knowledge_adapter_provider_evaluation_review_summary_export.
- knowledge_adapter_provider_evaluation_review_summary_export.json.
- artifact_type=knowledge_adapter_provider_evaluation_review_summary_export.
- manifest_kind=knowledge_adapter_provider_evaluation_review_summary_export.
- provider_evaluation_review_summary_export_pending.
- provider_evaluation_review_summary_exported_for_planning.
- provider_evaluation_review_summary_export_failed_validation.
- review summary status.
- exported decision groups.
- not_exported.
- exported_for_planning.
- failed_validation.
- accepted_for_planning.
- accepted_with_constraints.
- blocked.
- needs_revision.
- unsupported.
- audit evidence only.
- future planning.
- not a report generator.
- used_knowledge=true.
- failure_code.
- failure code.
- visible_reason.
- visible reason.
- prompt_input.json.

Review summary status, exported decision groups, reviewer notes, accepted
constraints, blocked reasons, unsupported reasons, requested revision fields,
unresolved safety questions, source hashes, source manifest ids, and
ReviewHistory links are evidence labels. They do not create provider
connectivity, provider-backed prompt context evidence, runtime retrieval,
provider enablement, report generation behavior, export/download endpoint
behavior, or automatic used_knowledge=true marking.

## Failure Behavior

KnowledgeAdapter provider evaluation review summary export must fail without a
successful summary export when input is missing, stale, unsafe, unlicensed,
license-unknown, version-unknown, reference-missing, reference-mismatched,
normalization-unsupported, provider-state-unsafe, fallback-missing,
review-decision-missing, review-decision-invalid, summary-export-invalid,
evaluation-plan-mismatched, review-decision-mismatched, cross-project,
unbounded, credential-required, or runtime-required.

Invalid provider evaluation review summary export input must produce
failure_code, failure code, visible_reason, and visible reason. It must not
append a successful summary export, mark a provider ready, mutate the reviewed
provider evaluation review decision artifact, mutate the provider evaluation
plan artifact, rewrite KnowledgeEvidence, generate reports, expose
export/download endpoints, or set used_knowledge=true.

## Runtime Boundary

The KnowledgeAdapter Provider Evaluation Review Summary Export contract is not
provider runtime, prompt runtime, provider-backed prompt context, UI, backend
API, report generation behavior, export/download endpoint, or storage mutation
behavior:

- no provider enablement.
- no automatic provider enablement.
- no Haystack provider integration.
- no LlamaIndex provider integration.
- no GraphRAG provider integration.
- no provider SDK.
- no provider SDK call.
- no external provider call.
- no API key handling.
- no API keys.
- no credentials.
- no tokens.
- no OAuth.
- no OAuth state.
- no OAuth material.
- no remote URL fetch.
- no remote fetch payloads.
- no external call.
- no network retrieval.
- no provider runtime.
- no runtime retrieval.
- no provider-backed prompt context evidence.
- no raw provider payloads.
- no provider request payloads.
- no provider-specific payloads.
- no prompt assembly implementation.
- no prompt runtime execution.
- no runtime prompt_input.json.
- no automatic used_knowledge=true marking.
- no deterministic retrieval behavior change.
- no prompt eligibility change.
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
- no report generator.
- no export/download endpoint.
- no download endpoint.
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
- no KnowledgeAdapterConfig runtime state mutation.
- no KnowledgeAdapterConfig.status mutation.
- no automatic knowledge ingestion.
- no TestKnowledgeCard CRUD.
- no automatic prompt eligibility.
- no artifact upload.
- no Artifact mutation.
- no artifact mutation outside declared summary export evidence.
- no artifact delete.
- no provider evaluation review decision artifact mutation.
- no provider evaluation plan artifact mutation.
- no historical evidence mutation.
- no KnowledgeEvidence mutation.
- no TestKnowledgeCard mutation.
- no GeneratedCaseCandidate mutation.
- no TestCase auto-promotion.
- no generated-case auto-approval.
- no ToolInvocation creation.
- no execute AITasks.
- no runner behavior change.
- no remote CI provider behavior.
- no retrieval evidence.
- no reports.
- no secrets.
- no vector store payloads.
- no reranker traces.
- no graph payloads.
- no executable prompt assembly payloads.
- no frontend-rendered markup.
- no report-rendered payloads.
- no export-rendered payloads.
- no downloadable provider payloads.
- no generated replacement evidence.
- no RBAC.
- no tenants.
- no permissions.
- no review bypass.

## Forbidden Side Effects

The contract must not create or trigger provider enablement, provider runtime,
external provider calls, prompt runtime execution, vector infrastructure,
frontend pages, backend feature APIs, report generator behavior,
export/download endpoints, artifact upload, artifact mutation outside declared
summary export evidence, provider evaluation review decision artifact
mutation, provider evaluation plan artifact mutation,
KnowledgeAdapterConfig.status mutation, historical evidence mutation,
retrieval evidence, reports, secrets, vector store payloads, reranker traces,
graph payloads, raw provider payloads, API keys, tokens, OAuth state, OAuth
material, remote fetch payloads, provider request payloads,
provider-specific payloads, executable prompt assembly payloads,
frontend-rendered markup, report-rendered payloads, export-rendered payloads,
downloadable provider payloads, generated replacement evidence,
generated-case auto-approval, review bypass, RBAC, tenants, or permissions.

KnowledgeAdapter Provider Evaluation Review Summary Export remains audit
evidence. It preserves provider evaluation review decision artifact id,
provider evaluation plan artifact id, review summary status, exported decision
groups, accepted_for_planning, accepted_with_constraints, blocked,
needs_revision, unsupported, KnowledgeEvidence normalization summary,
provider_state summary, fallback summary, license/reference summary,
reference intake, disabled by default policy, ReviewHistory summary, failure
behavior, failure_code, visible_reason, and visible reason without installing
packages, calling providers, creating vector infrastructure, assembling
prompts, running retrieval, enabling providers, mutating historical evidence,
generating reports, exposing export/download endpoints, or bypassing review.
