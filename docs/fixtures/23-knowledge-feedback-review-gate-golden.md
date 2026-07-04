# Knowledge Feedback Review Gate Golden

This fixture proves Slice 35 remains a contract-only human review gate for
KnowledgeFeedbackDraft outputs. It is not a review runtime API, not a frontend
review page, and not TestKnowledgeCard CRUD.

## Review Actions

| Action | Actor | Source state | Target state | Evidence | Prompt eligibility |
|---|---|---|---|---|---|
| approve_feedback | human reviewer | needs_review | approved_by_human | ReviewHistory plus feedback review artifact | remains false unless separately marked |
| reject_feedback | human reviewer | needs_review | rejected | ReviewHistory plus rejection reason | false; rejected feedback is not positive knowledge |
| request_revision | human reviewer | needs_review | draft | ReviewHistory plus reviewer comment and unsupported claims | false |
| mark_prompt_eligible | human reviewer | approved_by_human | prompt_eligible | ReviewHistory, feedback review artifact, safe_to_show evidence, reviewed source citations, prompt eligibility reason | true only after explicit human approval |
| create_knowledge_card_candidate | human reviewer | approved_by_human | handoff payload only | source Artifact ids and source quote/hash | does not create TestKnowledgeCard rows in this contract |

## Required Terms

The contract must define:

- KnowledgeFeedbackDraft.
- approve_feedback.
- reject_feedback.
- request_revision.
- mark_prompt_eligible.
- create_knowledge_card_candidate.
- human review.
- ReviewHistory.
- feedback review artifact.
- prompt eligibility.
- prompt eligibility reason.
- TestKnowledgeCard handoff.
- unsupported claims.
- safe_to_show evidence.
- reviewed source citations.
- ReviewHistory id.
- evidence artifact ids.

## Review Boundary

Model confidence, schema validity, absence of unsupported claims, and the
existence of a draft feedback artifact must not approve feedback or mark it
prompt-eligible. Rejected feedback remains auditable and cannot be reused as
positive knowledge. A future TestKnowledgeCard handoff payload is not CRUD and
does not create, approve, archive, delete, or mutate TestKnowledgeCard rows.

## Forbidden Side Effects

The contract must not create or trigger:

- feedback review runtime API.
- frontend review page.
- TestKnowledgeCard CRUD.
- TestKnowledgeCard auto-creation.
- prompt-eligible auto-marking.
- automatic prompt eligibility.
- automatic knowledge ingestion.
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
- RBAC.
- tenants.
- permissions.

KnowledgeFeedbackDraft review remains a human gate. Prompt eligibility is a
separate human decision with source evidence and a recorded reason.
