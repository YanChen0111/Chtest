# TestKnowledgeCard Handoff Golden

This fixture proves Slice 36 remains a contract-only TestKnowledgeCard handoff
definition. It is not TestKnowledgeCard CRUD, not a backend feature API, not a
frontend review page, and not prompt eligibility automation.

## Handoff Scenario

An approved KnowledgeFeedbackDraft in `approved_by_human` state may prepare a
`create_knowledge_card_candidate` handoff payload. The payload is a
TestKnowledgeCard candidate, not a TestKnowledgeCard row. Human review is
required before future card creation, and a separate prompt eligibility gate is
required before `allowed_for_prompt=true` can ever be granted.

| Surface | Required boundary |
|---|---|
| KnowledgeFeedbackDraft | Source feedback must be approved by human review before handoff |
| ReviewHistory | ReviewHistory id links the approval decision |
| feedback review artifact | Review artifact records reviewer action and source evidence |
| KnowledgeEvidence | used_knowledge_evidence_ids stay citation evidence only |
| source Artifact | same-project source Artifact ids and source_quote_or_hash are required |
| TestKnowledgeCard handoff | handoff payload remains candidate evidence only |

## Handoff Payload

The contract must define a `handoff_payload_json` shape with:

- approved KnowledgeFeedbackDraft.
- approved_by_human.
- create_knowledge_card_candidate.
- handoff payload.
- source_entity_type.
- source_entity_id.
- source_artifact_id.
- source_artifact_ids.
- source_quote_or_hash.
- source_span.
- source_section.
- same-project source Artifact.
- source evidence.
- ReviewHistory id.
- feedback review artifact.
- unsupported claims.

## Candidate Field Mapping

The candidate payload maps draft feedback into future TestKnowledgeCard
candidate fields:

- TestKnowledgeCard candidate.
- knowledge_type.
- title.
- summary.
- body.
- confidence.
- safe_to_show.
- redaction_applied.
- allowed_for_prompt=false.
- evidence_artifact_ids.
- used_knowledge_evidence_ids.
- related_requirement_ids.
- related_risk_ids.
- related_test_case_ids.
- review_required=true.
- test_knowledge_card_handoff.json.
- artifact_type=test_knowledge_card_handoff.

## Duplicate/Merge Hints

Duplicate/merge hints are reviewer evidence only:

- duplicate_knowledge_card_ids.
- duplicate candidates.
- merge_hint.
- merge recommendation.
- duplicate/merge hints.
- duplicate review required.
- merge review required.

They must not merge, archive, replace, relabel, delete, or create
TestKnowledgeCard rows.

## Review Boundary

Human review is required for:

- approving the KnowledgeFeedbackDraft before handoff.
- accepting source evidence as safe_to_show.
- preserving reviewed source citations.
- resolving duplicate/merge hints.
- creating any future TestKnowledgeCard row.
- granting prompt eligibility after a card exists.

Model confidence, schema validity, absence of unsupported claims, and the
existence of a feedback review artifact must not approve a card, create a card,
or make any card prompt-eligible.

## Forbidden Side Effects

The contract must not create or trigger:

- TestKnowledgeCard CRUD.
- TestKnowledgeCard auto-creation.
- automatic card creation.
- automatic prompt eligibility.
- allowed_for_prompt=true auto-marking.
- automatic knowledge ingestion.
- KnowledgeIngestionAgent runtime.
- backend feature API.
- frontend review page.
- historical ReviewHistory mutation.
- FailureAnalysis mutation.
- Report mutation.
- TestRun mutation.
- TestResult mutation.
- TestCase mutation.
- GeneratedCaseCandidate mutation.
- Artifact mutation.
- provider call.
- vector index.
- embedding.
- reranking.
- graph job.
- MCP runtime.
- review bypass.
- generated-case auto-approval.
- TestCase auto-promotion.
- runner behavior change.
- report generation behavior change.
- remote CI provider behavior.
- RBAC.
- tenants.
- permissions.

TestKnowledgeCard handoff remains auditable candidate evidence. It preserves
source evidence, ReviewHistory, feedback review artifact, unsupported claims,
safe_to_show checks, `allowed_for_prompt=false`, and duplicate/merge hints
until a later scoped workflow owns card creation.
