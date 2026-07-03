# Knowledge Feedback Contract Golden

This fixture proves Slice 34 remains a contract-only KnowledgeFeedbackAgent
draft feedback definition. It is not a feedback runtime, not TestKnowledgeCard
CRUD, and not prompt-eligibility automation.

## Feedback Contract

| Contract | Input evidence | Draft output | Human gate | Failure behavior |
|---|---|---|---|---|
| KnowledgeFeedbackAgent | accepted GeneratedCaseCandidate, rejected GeneratedCaseCandidate, reviewed TestCase, ReviewHistory, FailureAnalysis, Report, TestRun/TestResult summary, KnowledgeEvidence, existing TestKnowledgeCard | KnowledgeFeedbackDraft entries with feedback_type, draft_knowledge_type, source_entity_type, source_entity_id, source_quote_or_hash, source_span, recommendation, confidence, used_knowledge_evidence_ids, unsupported_claims, review_findings, prompt_eligible=false | Human review is required before TestKnowledgeCard creation or prompt eligibility | UNABLE_TO_CREATE_KNOWLEDGE_FEEDBACK with empty feedback and visible unsupported_claims |

## Required Terms

The contract must define:

- KnowledgeFeedbackAgent.
- knowledge_feedback:v1.
- knowledge-feedback-skill:v1.
- KnowledgeFeedbackDraft.
- draft feedback.
- accepted GeneratedCaseCandidate.
- rejected GeneratedCaseCandidate.
- reviewed TestCase.
- ReviewHistory.
- FailureAnalysis.
- Report.
- TestRun/TestResult summary.
- KnowledgeEvidence.
- existing TestKnowledgeCard.
- feedback_type.
- draft_knowledge_type.
- source_entity_type.
- source_entity_id.
- source_quote_or_hash.
- source_span.
- recommendation.
- confidence.
- used_knowledge_evidence_ids.
- unsupported_claims.
- review_findings.
- prompt_eligible=false.
- human review.
- prompt eligibility.
- UNABLE_TO_CREATE_KNOWLEDGE_FEEDBACK.

## Forbidden Side Effects

The contract must not create or trigger:

- KnowledgeFeedbackAgent runtime.
- TestKnowledgeCard CRUD.
- TestKnowledgeCard auto-creation.
- prompt-eligible auto-marking.
- automatic knowledge ingestion.
- historical ReviewHistory mutation.
- FailureAnalysis mutation.
- Report mutation.
- TestRun mutation.
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

Knowledge feedback remains draft feedback. Model confidence is advisory only,
unsupported claims remain visible, and human review is the only authority that
may later approve knowledge-card creation or prompt eligibility.
