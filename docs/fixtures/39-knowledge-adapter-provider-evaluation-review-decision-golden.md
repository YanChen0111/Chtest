# KnowledgeAdapter Provider Evaluation Review Decision Golden

This fixture proves Slice 51 remains a contract-only KnowledgeAdapter Provider
Evaluation Review Decision definition. It is audit evidence only for future
provider evaluation review, not provider enablement, not a Haystack provider
integration, not a LlamaIndex provider integration, not a GraphRAG provider
integration, not a provider SDK call, not runtime retrieval, and not
provider-backed prompt context evidence.

## Provider Evaluation Review Scenario

A future workflow may package a local review decision for a provider evaluation
plan artifact. The record must preserve provider evaluation plan artifact id,
knowledge_adapter_provider_evaluation_plan_artifact_id, same-project plan
artifact, created_by_component=KnowledgeAdapterProviderEvaluationReviewDecision,
owner_entity_type=AITask, owner_entity_type=Project, candidate provider name,
provider family, adapter type, provider version, adapter version, provider
suitability status, license name, license URL, license compatibility notes,
license review result, reference intake summary, reference intake URLs,
documentation snapshot artifact ids, expected KnowledgeEvidence normalization
fields, KnowledgeEvidence normalization, KnowledgeEvidence normalization
notes, provider_state, provider_state recommendation, disabled by default
policy, disabled by default decision, fallback behavior summary, fallback
labels, metrics plan, metric set, evidence normalization completeness, source
traceability coverage, redaction safety status, fallback coverage, blocker
reasons, unresolved safety questions, source manifest ids, source hashes,
ReviewHistory ids, ReviewHistory links, failure_code, failure code,
visible_reason, visible reason, and failure behavior without enabling a
provider or claiming that knowledge was used.

| Surface | Required boundary |
|---|---|
| KnowledgeAdapter Provider Evaluation Review Decision | Provider review audit evidence only |
| review_knowledge_adapter_provider_evaluation | Future scoped review action only |
| knowledge_adapter_provider_evaluation_review_decision | Artifact and manifest naming only |
| provider evaluation review | Local review decision before provider integration |
| provider evaluation plan artifact | Reviewed evidence source |
| provider candidate | Disabled-by-default candidate metadata only |
| review decision | Audit label only |
| review status | Audit state only |
| accepted_for_planning | Future planning label only |
| accepted_with_constraints | Future planning label with constraints only |
| blocked | Provider candidate remains blocked |
| needs_revision | Requested revision remains visible |
| unsupported | Unsupported reason remains visible |
| provider suitability status | Input status from the evaluation plan |
| KnowledgeEvidence | Normalization target, not generated evidence here |
| provider_state | Display/health metadata only |
| fallback behavior | Local/no-knowledge fallback stays visible |
| license review | Required before any future integration |
| reference intake | Documentation/reference intake evidence only |
| disabled by default policy | Provider remains disabled |
| ReviewHistory | Human review trace remains visible |
| failure behavior | Invalid input fails without successful review decision |

## Provider Evaluation Review Inputs

The contract must define:

- knowledge_adapter_provider_evaluation_review_decision_action.
- knowledge_adapter_provider_evaluation_review_decision_action=review_knowledge_adapter_provider_evaluation.
- review_knowledge_adapter_provider_evaluation.
- provider evaluation plan artifact.
- provider evaluation plan artifact id.
- knowledge_adapter_provider_evaluation_plan_artifact_id.
- created_by_component=KnowledgeAdapterProviderEvaluationReviewDecision.
- owner_entity_type=AITask.
- owner_entity_type=Project.
- same-project plan artifact.
- candidate provider name.
- provider family.
- adapter type.
- provider version.
- adapter version.
- provider suitability status.
- license name.
- license URL.
- license compatibility notes.
- license review result.
- reference intake summary.
- reference intake URLs.
- documentation snapshot artifact ids.
- expected KnowledgeEvidence normalization fields.
- KnowledgeEvidence normalization.
- KnowledgeEvidence normalization notes.
- provider_state.
- provider_state recommendation.
- disabled by default policy.
- disabled by default decision.
- fallback behavior summary.
- fallback labels.
- metrics plan.
- metric set.
- evidence normalization completeness.
- source traceability coverage.
- redaction safety status.
- fallback coverage.
- blocker reasons.
- unresolved safety questions.
- source manifest ids.
- source hashes.
- ReviewHistory ids.
- ReviewHistory links.
- PromptVersion id.
- SkillVersion id.
- PromptVersion name/version.
- SkillVersion name/version.

## Field-Level Keys

The review request and response evidence keeps these explicit payload fields:

- project_id.
- knowledge_adapter_provider_evaluation_plan_artifact_id.
- candidate_provider_name.
- provider_family.
- adapter_type.
- provider_version.
- adapter_version.
- provider_suitability_status.
- provider_state_recommendation.
- disabled_by_default_decision.
- license_review_result.
- reference_intake_summary.
- knowledge_evidence_normalization_notes.
- fallback_behavior_summary.
- metrics_plan.
- blocker_reasons.
- unresolved_safety_questions.
- source_manifest_ids.
- source_hashes.
- review_history_ids.
- review_decision.
- review_status.
- reviewer_label.
- reviewer_note.
- accepted_constraints.
- requested_revision_fields.
- blocked_reasons.
- unsupported_reasons.
- review_history_links.
- failure_code.
- visible_reason.

## Provider Evaluation Review Outputs

KnowledgeAdapter provider evaluation review decision output may include:

- provider evaluation review decision id.
- provider evaluation review decision artifact id.
- knowledge_adapter_provider_evaluation_review_decision_artifact_id.
- knowledge_adapter_provider_evaluation_review_decision.
- knowledge_adapter_provider_evaluation_review_decision.json.
- artifact_type=knowledge_adapter_provider_evaluation_review_decision.
- manifest_kind=knowledge_adapter_provider_evaluation_review_decision.
- provider_candidate_disabled_by_default.
- provider_evaluation_review_pending.
- provider_evaluation_review_accepted_for_planning.
- provider_evaluation_review_accepted_with_constraints.
- provider_evaluation_review_blocked.
- provider_evaluation_review_needs_revision.
- provider_evaluation_review_unsupported.
- provider_evaluation_review_failed_validation.
- review decision.
- review status.
- reviewer label.
- local reviewer id.
- reviewer note.
- accepted constraints.
- blocked reasons.
- unsupported reasons.
- requested revision fields.
- decision rationale.
- reviewer_label.
- local_reviewer_id.
- reviewer_note.
- accepted_constraints.
- blocked_reasons.
- unsupported_reasons.
- requested_revision_fields.
- unresolved_safety_questions.
- decision_rationale.
- review_history_links.
- provider_state_recommendation.
- disabled_by_default_decision.
- license_review_result.
- reference_intake_summary.
- knowledge_evidence_normalization_notes.
- fallback_behavior_summary.
- fallback_labels.
- metrics_plan.
- source_manifest_ids.
- source_hashes.
- not_reviewed.
- accepted_for_planning.
- accepted_with_constraints.
- blocked.
- needs_revision.
- unsupported.
- failed_validation.
- audit evidence only.
- future planning.
- used_knowledge=true.
- failure_code.
- failure code.
- visible_reason.
- visible reason.
- prompt_input.json.

Review decision, review status, reviewer note, accepted constraints, blocked
reasons, unsupported reasons, requested revision fields, unresolved safety
questions, source hashes, source manifest ids, and ReviewHistory links are
evidence labels. They do not create provider connectivity,
provider-backed prompt context evidence, runtime retrieval, provider
enablement, or automatic used_knowledge=true marking.

## Failure Behavior

KnowledgeAdapter provider evaluation review decision must fail without a
successful review decision when input is missing, stale, unsafe, unlicensed,
license-unknown, version-unknown, reference-missing, reference-mismatched,
normalization-unsupported, provider-state-unsafe, fallback-missing,
review-decision-invalid, evaluation-plan-mismatched, cross-project, unbounded,
credential-required, or runtime-required.

Invalid provider evaluation review input must produce failure_code, failure
code, visible_reason, and visible reason. It must not append a successful
review decision, mark a provider ready, mutate the provider evaluation plan
artifact, mutate/rewrite the reviewed provider evaluation plan artifact,
rewrite KnowledgeEvidence, or set used_knowledge=true.

## Runtime Boundary

The KnowledgeAdapter Provider Evaluation Review Decision contract is not
provider runtime, prompt runtime, provider-backed prompt context, UI, backend
API, or storage mutation behavior:

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
- no KnowledgeAdapterConfig runtime state mutation.
- no automatic knowledge ingestion.
- no TestKnowledgeCard CRUD.
- no automatic prompt eligibility.
- no artifact upload.
- no Artifact mutation.
- no artifact mutation outside declared review decision evidence.
- no artifact delete.
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
- no generated replacement evidence.
- no KnowledgeAdapterConfig.status mutation.
- no RBAC.
- no tenants.
- no permissions.
- no review bypass.

## Forbidden Side Effects

The contract must not create or trigger provider enablement, provider runtime,
external provider calls, prompt runtime execution, vector infrastructure,
frontend pages, backend feature APIs, artifact mutation outside declared review
decision evidence, provider evaluation plan artifact mutation,
KnowledgeAdapterConfig.status mutation, historical evidence mutation,
retrieval evidence, reports, secrets, vector store payloads, reranker traces,
graph payloads, raw provider payloads, API keys, tokens, OAuth state, OAuth
material, remote fetch payloads, provider request payloads,
provider-specific payloads, executable prompt assembly payloads,
frontend-rendered markup, report-rendered payloads, generated replacement
evidence, generated-case auto-approval, review bypass, RBAC, tenants, or
permissions.

KnowledgeAdapter Provider Evaluation Review Decision remains audit evidence.
It preserves provider evaluation plan artifact id, review decision, review
status, accepted_for_planning, accepted_with_constraints, blocked,
needs_revision, unsupported, KnowledgeEvidence normalization requirements,
provider_state recommendation, fallback behavior, license review, reference
intake, disabled by default policy, ReviewHistory, failure behavior,
failure_code, visible_reason, and visible reason without installing packages,
calling providers, creating vector infrastructure, assembling prompts, running
retrieval, enabling providers, mutating historical evidence, or bypassing
review.
