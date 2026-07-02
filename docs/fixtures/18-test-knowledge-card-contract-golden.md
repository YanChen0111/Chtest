# Test Knowledge Card Contract Golden Fixture

This fixture proves Slice 30 TestKnowledgeCard and KnowledgeEvidence contracts
without adding a RAG runtime, provider integration, graph runtime, or generated
case auto-approval.

## Scenario

1. A checkout requirement describes coupon usage rules.
2. A same-project ContextArtifact contains API and business-rule notes.
3. Structured TestKnowledgeCard records are available as local testing
   knowledge evidence.
4. A case generation task creates three GeneratedCaseCandidate examples:
   accepted evidence, needs-review evidence, and rejected evidence.
5. Candidate review still follows the existing GeneratedCaseCandidate state
   machine before any TestCase is created.

## Requirement

```json
{
  "id": "00000000-0000-0000-0000-000000000401",
  "title": "Coupon checkout rules",
  "content": "Users can select one available coupon during checkout. Expired coupons cannot be used. Coupons cannot be combined with points.",
  "source_type": "manual",
  "source_ref": "REQ-COUPON-001"
}
```

## Source Context Artifacts

```json
[
  {
    "id": "00000000-0000-0000-0000-000000000371",
    "artifact_type": "context_markdown",
    "title": "coupon-api-notes.md",
    "source_ref": "manual:coupon-api-notes.md",
    "safe_to_show": true,
    "redaction_applied": false,
    "allowed_for_prompt": true,
    "sha256": "sha256:coupon-notes"
  },
  {
    "id": "00000000-0000-0000-0000-000000000372",
    "artifact_type": "context_json",
    "title": "historical-defects.json",
    "source_ref": "import:defects-2026-06",
    "safe_to_show": true,
    "redaction_applied": true,
    "allowed_for_prompt": true,
    "sha256": "sha256:defect-notes"
  }
]
```

## TestKnowledgeCard Examples

```json
[
  {
    "id": "00000000-0000-0000-0000-000000000821",
    "project_id": "00000000-0000-0000-0000-000000000101",
    "title": "Expired coupon boundary",
    "knowledge_type": "boundary_condition",
    "summary": "Expired coupons must be rejected before order submission.",
    "source_type": "context_artifact",
    "source_artifact_id": "00000000-0000-0000-0000-000000000371",
    "source_section": "coupon validation",
    "source_quote_or_hash": "sha256:expired-coupon-section",
    "related_requirement_ids": ["00000000-0000-0000-0000-000000000401"],
    "related_risk_ids": ["00000000-0000-0000-0000-000000000411"],
    "test_type": "functional",
    "risk_level": "high",
    "case_type_hint": "boundary",
    "confidence": 92,
    "safe_to_show": true,
    "allowed_for_prompt": true,
    "evidence_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
    "status": "active"
  },
  {
    "id": "00000000-0000-0000-0000-000000000822",
    "project_id": "00000000-0000-0000-0000-000000000101",
    "title": "Coupon and points conflict",
    "knowledge_type": "business_rule",
    "summary": "Coupon discount and points deduction cannot be used in the same order.",
    "source_type": "context_artifact",
    "source_artifact_id": "00000000-0000-0000-0000-000000000371",
    "source_section": "discount conflict rules",
    "related_requirement_ids": ["00000000-0000-0000-0000-000000000401"],
    "related_risk_ids": ["00000000-0000-0000-0000-000000000412"],
    "test_type": "functional",
    "risk_level": "high",
    "case_type_hint": "exception",
    "confidence": 88,
    "safe_to_show": true,
    "allowed_for_prompt": true,
    "evidence_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
    "status": "active"
  },
  {
    "id": "00000000-0000-0000-0000-000000000823",
    "project_id": "00000000-0000-0000-0000-000000000101",
    "title": "Historical duplicate coupon defect",
    "knowledge_type": "bug_pattern",
    "summary": "Past checkout failures occurred when duplicate coupon submission was retried.",
    "source_type": "manual",
    "source_artifact_id": "00000000-0000-0000-0000-000000000372",
    "source_section": "defect COUPON-142",
    "related_requirement_ids": ["00000000-0000-0000-0000-000000000401"],
    "related_risk_ids": ["00000000-0000-0000-0000-000000000413"],
    "test_type": "regression",
    "risk_level": "medium",
    "case_type_hint": "regression",
    "confidence": 77,
    "safe_to_show": true,
    "allowed_for_prompt": true,
    "evidence_artifact_ids": ["00000000-0000-0000-0000-000000000372"],
    "status": "active"
  }
]
```

## KnowledgeEvidence Examples

```json
[
  {
    "evidence_id": "ke-expired-coupon-boundary",
    "project_id": "00000000-0000-0000-0000-000000000101",
    "provider_name": "chtest_local",
    "retrieval_mode": "structured_card",
    "source_artifact_id": "00000000-0000-0000-0000-000000000371",
    "knowledge_card_id": "00000000-0000-0000-0000-000000000821",
    "source_section": "coupon validation",
    "snippet": "Expired coupons must be rejected before order submission.",
    "score": 0.92,
    "matched_terms": ["expired", "coupon", "checkout"],
    "query_terms": ["coupon", "expired"],
    "retrieval_reason": "Supports the expired-coupon rejection path.",
    "safe_to_show": true,
    "allowed_for_prompt": true,
    "created_by_component": "TestKnowledgeContract"
  },
  {
    "evidence_id": "ke-coupon-points-conflict",
    "project_id": "00000000-0000-0000-0000-000000000101",
    "provider_name": "chtest_local",
    "retrieval_mode": "structured_card",
    "source_artifact_id": "00000000-0000-0000-0000-000000000371",
    "knowledge_card_id": "00000000-0000-0000-0000-000000000822",
    "source_section": "discount conflict rules",
    "snippet": "Coupon discount and points deduction cannot be used in the same order.",
    "score": 0.88,
    "matched_terms": ["coupon", "points", "conflict"],
    "query_terms": ["coupon", "points"],
    "retrieval_reason": "Supports the coupon and points conflict exception path.",
    "safe_to_show": true,
    "allowed_for_prompt": true,
    "created_by_component": "TestKnowledgeContract"
  }
]
```

Provider note:

- Future Haystack, LlamaIndex, GraphRAG, or other provider payloads must be
  normalized into the KnowledgeEvidence shape above before generated cases cite
  them.
- Raw provider fields are not source truth and must not be stored directly in
  GeneratedCaseCandidate evidence fields.

## GeneratedCaseCandidate Examples

### Accepted Evidence Condition

```json
{
  "id": "00000000-0000-0000-0000-000000000801",
  "title": "Expired coupon cannot submit order",
  "priority": "P0",
  "test_type": "functional",
  "steps": ["Login", "Open checkout", "Select expired coupon", "Submit order"],
  "expected_results": ["Submission is blocked", "Expired coupon message is shown"],
  "requirement_refs": ["Expired coupons cannot be used"],
  "risk_refs_json": ["coupon expiration boundary"],
  "source_knowledge_evidence_ids": ["ke-expired-coupon-boundary"],
  "knowledge_evidence_refs": [
    {
      "evidence_id": "ke-expired-coupon-boundary",
      "knowledge_card_id": "00000000-0000-0000-0000-000000000821",
      "source_artifact_id": "00000000-0000-0000-0000-000000000371",
      "snippet": "Expired coupons must be rejected before order submission.",
      "score": 0.92
    }
  ],
  "covered_risk_ids": ["00000000-0000-0000-0000-000000000411"],
  "generation_reason": "Boundary case for expired coupon validation.",
  "automation_readiness": "suitable_for_playwright",
  "quality_score": 88,
  "review_findings": [
    {
      "type": "evidence_complete",
      "severity": "info",
      "message": "Candidate cites the required boundary-condition knowledge card."
    }
  ],
  "coverage_gap_notes": "",
  "status": "generated"
}
```

Expected review outcome:

- Candidate may move from `generated` to `under_review`.
- Human reviewer may approve or approve after edit.
- Approval may create a TestCase only through the existing review transition.

### Needs-Review Evidence Condition

```json
{
  "id": "00000000-0000-0000-0000-000000000802",
  "title": "Coupon and points cannot be combined",
  "priority": "P0",
  "test_type": "functional",
  "steps": ["Login", "Open checkout", "Apply coupon", "Apply points", "Submit order"],
  "expected_results": ["Only one discount method is accepted", "Conflict message is shown"],
  "requirement_refs": ["Coupons cannot be combined with points"],
  "source_knowledge_evidence_ids": ["ke-coupon-points-conflict"],
  "covered_risk_ids": ["00000000-0000-0000-0000-000000000412"],
  "generation_reason": "Exception case for mutually exclusive discounts.",
  "automation_readiness": "suitable_for_playwright",
  "quality_score": 71,
  "review_findings": [
    {
      "type": "expected_result_needs_precision",
      "severity": "warning",
      "message": "Expected result should name whether coupon or points takes precedence."
    }
  ],
  "coverage_gap_notes": "Precedence rule is not explicit in the requirement.",
  "status": "generated"
}
```

Expected review outcome:

- Candidate remains reviewable but should not be auto-approved.
- Reviewer or CaseReviewAgent may request optimization until the precedence rule
  is clarified.
- Missing precision remains visible in `review_findings` and
  `coverage_gap_notes`.

### Rejected Evidence Condition

```json
{
  "id": "00000000-0000-0000-0000-000000000803",
  "title": "VIP coupon can stack with points",
  "priority": "P1",
  "test_type": "functional",
  "steps": ["Login as VIP", "Apply VIP coupon", "Apply points", "Submit order"],
  "expected_results": ["Order is submitted with both discounts"],
  "requirement_refs": [],
  "source_knowledge_evidence_ids": [],
  "covered_risk_ids": [],
  "generation_reason": "Model proposed a VIP stacking path without supporting evidence.",
  "automation_readiness": "not_suitable",
  "quality_score": 22,
  "review_findings": [
    {
      "type": "missing_evidence",
      "severity": "error",
      "message": "No KnowledgeEvidence supports VIP coupon stacking."
    },
    {
      "type": "hallucination_risk",
      "severity": "error",
      "message": "Requirement says coupons cannot be combined with points."
    }
  ],
  "coverage_gap_notes": "No accepted source mentions VIP stacking.",
  "status": "generated"
}
```

Expected review outcome:

- Candidate should be rejected or sent back for optimization.
- Missing KnowledgeEvidence must remain visible.
- Rejection must not remove historical evidence artifacts.

## Expected Evidence

- TestKnowledgeCard records preserve source Artifact ids, safe-to-show,
  allowed-for-prompt, risk/requirement classification, confidence, and status.
- KnowledgeEvidence records cite same-project TestKnowledgeCard or Artifact
  evidence and include bounded safe snippets.
- GeneratedCaseCandidate records can carry evidence ids, risk coverage,
  generation reason, automation readiness, quality score, review findings, and
  coverage gap notes.
- Accepted, needs-review, and rejected evidence conditions are distinguishable
  without executing retrieval or calling external providers.
- Existing GeneratedCaseCandidate review gates remain the only way to create a
  reviewed TestCase.

## Non-Goals

- No vector database, embedding service, semantic search, reranking,
  background indexing, GraphRAG runtime, graph database, external
  KnowledgeAdapter provider, provider SDK, OAuth, API key storage, remote URL
  fetch, MCP runtime, marketplace, RBAC, tenants, permissions, frontend
  implementation, generated-case auto-approval, TestCase auto-promotion,
  runner execution, report generation, artifact upload/mutation/delete, cloud
  storage, or remote CI provider behavior.
