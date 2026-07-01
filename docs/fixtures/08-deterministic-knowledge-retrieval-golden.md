# Golden Path: Deterministic Knowledge Retrieval

## 1. Purpose

This fixture proves the smallest V2 knowledge-quality loop:

```text
ContextArtifact
  -> deterministic local retrieval
  -> requirement review
  -> knowledge_retrieval evidence artifact
  -> RAG 知识库 latest retrieval surface
```

The goal is to prove that existing safe project context can improve an AI task
while staying auditable. This is a local deterministic fixture, not a full RAG
runtime.

## 2. Seed Data

Required seed data:

- Project: `Checkout System`.
- Requirement: `Coupon checkout API rejects expired coupons`.
- ContextArtifact: `coupon-api-notes.md`, stored as `context_markdown`, owner
  `Project`.
- ContextArtifact content includes `coupon`, `checkout`, `API`, and `expired`
  terms.
- ContextArtifact metadata:
  - `safe_to_show=true`
  - `allowed_for_prompt=true`
  - `redaction_applied=false`
- KnowledgeAdapterConfig:
  - `adapter_name=default`
  - `status=configured_stub`
  - `provider_type=deterministic_local`
  - `match_mode=keyword_overlap`
- Built-in PromptVersion: `requirement_review:v1`.
- Built-in SkillVersion: `requirement-review-skill:v1`.
- Mock provider: `mock-requirement-review`.

## 3. Minimum Flow

1. Create Project.
2. Create Requirement with coupon checkout API wording.
3. Create safe ContextArtifact `coupon-api-notes.md`.
4. Configure the deterministic local KnowledgeAdapter stub.
5. Start Requirement Review with `use_knowledge=true` and no explicit
   `context_artifact_ids`.
6. Confirm deterministic retrieval contributes `coupon-api-notes.md` to the AI
   task context.
7. Confirm Requirement Review records `used_knowledge=true` and exact
   `used_context_artifact_ids`.
8. Confirm the AITask owns a `knowledge_retrieval` Artifact.
9. Read `knowledge_retrieval.json` and confirm query terms, matched terms,
   snippets, scores, SHA256, ContextArtifact ids, prompt eligibility, and
   redaction status.
10. Read `/api/projects/{project_id}/knowledge-base` and confirm the RAG
    知识库 surface can display the latest retrieval evidence.

## 4. Success Criteria

- Requirement Review start response has `used_knowledge=true`.
- Requirement Review start response and review detail both report
  `used_context_artifact_ids=[coupon-api-notes.md id]`.
- AITask status is `succeeded`.
- AITask `context_artifact_ids` contains the retrieved ContextArtifact id.
- AITask `output_json` includes `retrieval_evidence_artifact_id`.
- Retrieval evidence Artifact:
  - has `artifact_type=knowledge_retrieval`;
  - is owned by the Requirement Review AITask;
  - has `mime_type=application/json`;
  - records `created_by_component=DeterministicKnowledgeAdapter`;
  - records `retrieval_mode=deterministic_local`;
  - records exact retrieved ContextArtifact ids.
- Persisted `knowledge_retrieval.json` includes:
  - `query_text`;
  - `query_terms`;
  - `used_knowledge=true`;
  - exact `used_context_artifact_ids`;
  - result `title`, `source_ref`, `score`, `matched_terms`, `snippet`,
    `sha256`, `allowed_for_prompt`, and `redaction_applied`.
- RAG 知识库 surface includes:
  - `knowledge_adapter.used_knowledge=true`;
  - `knowledge_adapter.retrieval_mode=deterministic_local`;
  - ContextArtifact `retrieved_count=1`;
  - ContextArtifact `latest_retrieved_at`;
  - one latest retrieval summary with the same AITask id, evidence Artifact id,
    matched terms, score, and snippet.

## 5. Minimum Evidence

The golden smoke must show:

- ContextArtifact list with `coupon-api-notes.md`, `safe_to_show=true`, and
  `allowed_for_prompt=true`.
- RequirementReview result with `used_knowledge=true`.
- AITask output with exact retrieved ContextArtifact ids.
- `knowledge_retrieval` Artifact metadata.
- Persisted `knowledge_retrieval.json` content.
- RAG 知识库 latest retrieval summary derived from the evidence artifact.

## 6. Out Of Scope

- Vector database.
- Embedding model or embedding service.
- Semantic index or ANN search.
- Reranking.
- Background indexing workers.
- External RAG provider calls.
- MCP runtime dependency or remote MCP calls.
- RBAC, tenants, permissions, SSO, or organization audit features.
- Marketplace, plugin installation, cloud sync, release automation, or remote
  CI provider integration.
