# Reviewed TestKnowledgeCard Creation Golden

This fixture proves Slice 38 remains a contract-only Reviewed
TestKnowledgeCard Creation definition. It is not broad TestKnowledgeCard CRUD,
not a backend feature API, not a frontend page, not a migration, and not prompt
eligibility automation.

## Creation Scenario

A reviewed TestKnowledgeCard creation workflow may start only from an approved
candidate review. The approved candidate must preserve the candidate review
artifact, handoff artifact, source evidence, source manifest, ReviewHistory,
and duplicate/merge preconditions. The future creation action is
`create_reviewed_test_knowledge_card`, and the created card must default to
`allowed_for_prompt=false`.

| Surface | Required boundary |
|---|---|
| Reviewed TestKnowledgeCard Creation | Future scoped creation only |
| approved candidate review | Source candidate must be approved by human review |
| create_reviewed_test_knowledge_card | Creation action is not broad CRUD |
| candidate review artifact | Candidate approval evidence is required |
| source manifest | Source artifacts and hashes are preserved |
| ReviewHistory | ReviewHistory ids link feedback, candidate review, and creation |
| duplicate/merge preconditions | Unresolved duplicate or merge conflict blocks creation |
| prompt eligibility | prompt eligibility remains separate from card creation |

## Creation Input

The contract must define:

- approved candidate.
- approved candidate review.
- candidate_approved_for_future_creation.
- candidate review artifact.
- source_handoff_artifact_id.
- test_knowledge_card_handoff.json.
- candidate_card_json.
- source_feedback_id.
- source evidence.
- same-project source Artifact.
- source_artifact_ids.
- source_quote_or_hash.
- source_manifest.
- ReviewHistory.
- ReviewHistory id.
- unsupported claims.

## Card Field Mapping

Reviewed creation maps candidate_card_json into TestKnowledgeCard fields:

- project_id.
- module_id.
- title.
- knowledge_type.
- summary.
- body.
- source_type.
- source_artifact_id.
- source_artifact_ids.
- source_document_version.
- source_section.
- source_quote_or_hash.
- related_requirement_ids.
- related_risk_ids.
- related_test_case_ids.
- tags.
- test_type.
- risk_level.
- module_key.
- api_endpoint.
- applicability.
- confidence.
- safe_to_show.
- redaction_applied.
- evidence_artifact_ids.
- last_verified_at.
- status.
- allowed_for_prompt=false.

## Creation Evidence

Creation evidence must preserve:

- reviewed_test_knowledge_card_creation.json.
- artifact_type=reviewed_test_knowledge_card_creation.
- create_reviewed_test_knowledge_card.
- creation_action.
- creation_artifact_id.
- source_manifest.
- duplicate_merge_preconditions.
- prompt_eligibility_decision=deferred.
- failure_code.

## Duplicate/Merge Preconditions

Duplicate/merge preconditions must be resolved before creation:

- duplicate_knowledge_card_ids.
- duplicate conflict.
- merge_hint.
- merge conflict.
- duplicate/merge preconditions.
- unresolved duplicate blocks creation.
- unresolved merge blocks creation.

They must not automatically merge, archive, replace, relabel, delete, or create
conflicting TestKnowledgeCard rows.

## Prompt Eligibility Boundary

Reviewed creation is not prompt eligibility:

- prompt eligibility remains separate.
- prompt eligibility is deferred.
- allowed_for_prompt=false remains mandatory.
- allowed_for_prompt=true auto-marking is forbidden.

## Failure Boundary

Creation must fail or stay blocked for:

- stale candidate review.
- rejected candidate.
- revision-requested candidate.
- duplicate-conflicted candidate.
- cross-project source evidence.
- unsafe source evidence.
- unbounded source evidence.
- unsupported source evidence.

Failed creation must not create fallback cards or fabricate source evidence.

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
- list/update/delete API.
- historical ReviewHistory mutation.
- FailureAnalysis mutation.
- Report mutation.
- TestRun mutation.
- TestResult mutation.
- TestCase mutation.
- GeneratedCaseCandidate mutation.
- KnowledgeEvidence mutation.
- Artifact mutation.
- provider call.
- vector index.
- embedding.
- reranking.
- graph job.
- MCP runtime.
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

Reviewed TestKnowledgeCard Creation remains auditable creation evidence. It
preserves approved candidate review, source manifest, ReviewHistory, creation
artifact evidence, duplicate/merge preconditions, unsupported claims, and
`allowed_for_prompt=false` until a later scoped prompt-eligibility workflow
grants reuse.
