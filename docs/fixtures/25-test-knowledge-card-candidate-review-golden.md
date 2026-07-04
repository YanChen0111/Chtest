# TestKnowledgeCard Candidate Review Golden

This fixture proves Slice 37 remains a contract-only TestKnowledgeCard
Candidate Review definition. It is not TestKnowledgeCard CRUD, not a backend
feature API, not a frontend review page, not a migration, and not prompt
eligibility automation.

## Candidate Review Scenario

A TestKnowledgeCard handoff candidate may enter candidate review only after the
handoff payload preserves source evidence, ReviewHistory, and a feedback review
artifact. Candidate review is a human review gate. It can route a candidate
toward future card creation, rejection, revision, duplicate review, or merge
review, but it does not create TestKnowledgeCard rows and does not grant prompt
eligibility.

| Surface | Required boundary |
|---|---|
| TestKnowledgeCard Candidate Review | Human review of handoff candidates only |
| TestKnowledgeCard handoff | Source handoff remains candidate evidence |
| TestKnowledgeCard handoff candidate | Candidate must preserve source evidence |
| TestKnowledgeCard candidate | Candidate is not a TestKnowledgeCard row |
| candidate review | Candidate review actions are human reviewer actions |
| ReviewHistory | ReviewHistory id records the candidate review decision |
| artifact evidence | candidate review artifact stores bounded review evidence |
| duplicate/merge handling | Duplicate and merge routing does not mutate cards |
| prompt eligibility | prompt eligibility remains separate from candidate review |

## Review Actions

The contract must define:

- approve_candidate_for_creation.
- reject_candidate.
- request_candidate_revision.
- flag_duplicate.
- request_merge_review.
- defer_prompt_eligibility.
- human review.
- ReviewHistory id.
- candidate review artifact.
- evidence_artifact_ids.
- source evidence.
- same-project source Artifact.
- reviewed source citations.
- source_quote_or_hash.
- unsupported claims.
- safe_to_show.
- allowed_for_prompt=false.
- review_required=true.

## Candidate Review Evidence

Candidate review evidence must preserve:

- test_knowledge_card_handoff.json.
- test_knowledge_card_candidate_review.json.
- artifact_type=test_knowledge_card_candidate_review.
- source_handoff_artifact_id.
- source_feedback_id.
- candidate_card_json.
- source_artifact_ids.
- source_span.
- reviewer_label.
- reviewer_comment.
- candidate_review_action.
- candidate_review_decision.
- failure_code.

## Duplicate/Merge Handling

Duplicate/merge handling must remain review routing only:

- duplicate_knowledge_card_ids.
- duplicate candidates.
- merge_hint.
- merge recommendation.
- duplicate review required.
- merge review required.
- duplicate_review_required.
- merge_review_required.

It must not automatically merge, archive, replace, relabel, delete, or create
TestKnowledgeCard rows.

## Prompt Eligibility Boundary

Candidate approval is not prompt eligibility:

- prompt eligibility remains separate.
- defer_prompt_eligibility is the default.
- prompt_eligibility_deferred records the state boundary.
- prompt_eligibility_decision=deferred records the artifact boundary.
- allowed_for_prompt=false remains mandatory.
- allowed_for_prompt=true auto-marking is forbidden.

## Review Boundary

Model confidence, schema validity, safe_to_show, duplicate similarity, absence
of unsupported claims, and existence of a candidate review artifact must not
approve a card, create a card, merge cards, archive cards, delete cards,
replace cards, relabel cards, or make any card prompt-eligible.

## Forbidden Side Effects

The contract must not create or trigger:

- TestKnowledgeCard CRUD.
- TestKnowledgeCard auto-creation.
- automatic card creation.
- automatic card approval.
- automatic prompt eligibility.
- allowed_for_prompt=true auto-marking.
- automatic knowledge ingestion.
- KnowledgeIngestionAgent runtime.
- backend feature API.
- frontend review page.
- migration.
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

TestKnowledgeCard Candidate Review remains auditable candidate evidence. It
preserves handoff source evidence, candidate review artifact evidence,
ReviewHistory, unsupported claims, duplicate/merge routing, and
`allowed_for_prompt=false` until a later scoped workflow owns card creation and
prompt eligibility.
