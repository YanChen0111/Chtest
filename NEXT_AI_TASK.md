# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. Docker runtime work remains intentionally skipped because the local
Docker Desktop/WSL engine is unavailable.

## Current Slice

Slice 47: Final Test Knowledge RAG System.

## Current Task

Slice 47 Task 47.6: add optional Qdrant and Haystack/LlamaIndex provider
contracts behind the provider-neutral KnowledgeAdapter boundary using fake
clients only.

Required output:

1. Define optional `qdrant`, `haystack`, and `llamaindex` provider configuration
   and capability contracts without adding a required runtime dependency.
2. Normalize fake provider matches into the existing KnowledgeRetrievalRun,
   KnowledgeEvidence, Artifact, score, safety, lifecycle, and fallback shapes.
3. Keep provider documents, payloads, node ids, collection schemas, and raw
   scores out of public API, ORM, prompt, case, report, and evidence contracts.
4. Add deterministic degraded/failed behavior and stable diagnostic snapshots
   for unavailable or failing optional providers.
5. Add focused provider contract tests with fake clients only. Do not start or
   install Qdrant, Haystack, LlamaIndex, online embeddings, or cloud services.

## Previous Task Verified

- Added optional Alembic `20260714_0013`: PostgreSQL full-text GIN is always
  emitted; pgvector extension/native column/HNSW setup is capability-gated and
  does not block SQLite or PostgreSQL without extension privileges.
- Added safe `postgres_hybrid` configuration, capability snapshots, native
  embedding synchronization, full-text/vector candidate SQL, provider-neutral
  score normalization, dimension/freshness checks, and deterministic keyword
  fallback with `vector_score=null`.
- Added PostgreSQL dialect/offline DDL tests, fake capability/native-result
  tests, SQLite no-op migration/fallback tests, and existing consumer regressions.
- Post-implementation review split full-text and vector candidate CTEs, applies
  dimension-matched casts/filters, keeps the similarity threshold outside the
  HNSW-ordered pool, and prevents vector-only mode from admitting text-only
  candidates. Focused Task 47.4/47.5 verification is now `76 passed`.
- Online acceptance completed on isolated PostgreSQL 16.14 databases at
  `127.0.0.1:55432`: the plain database upgraded to head with GIN full-text
  only, while the pgvector database upgraded to head with native vector storage
  and the HNSW index. The application adapter returned a real hybrid match with
  `vector_score=1.0`; the limited database correctly reported no vector
  capability and never fabricated a vector score.

## Task 47.5 Acceptance Evidence

The temporary PostgreSQL acceptance environment is outside the repository and
uses empty test databases only:

- `chtest_plain_test` is owned by a limited role and has no pgvector extension;
- `chtest_vector_test` has pgvector `0.8.3`, native `embedding_vector`, and
  `ix_test_knowledge_embedding_vector_hnsw_64`;
- online migration, extension privilege behavior, native `<=>`, HNSW index
  planning, and native/fallback capability behavior were verified;
- the blocked `storage/chtest-dev.db` was not used for migration or smoke data.

Docker Desktop/WSL remains unavailable, but it no longer blocks this task.

## Product Value Answer

Test engineers can choose a scale or orchestration provider without changing
the evidence, trace, safety, and review contracts used by the rest of Chtest.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/slices/slice-47-final-test-knowledge-rag-system.md`
9. `memory/08-session-handoff.md`
10. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Docker Desktop/WSL repair, provider runtime installation/deployment guides,
  graph/feedback, enterprise collaboration, marketplace, cloud CI, RBAC,
  tenants, permissions, unrelated frontend pages, or broad roadmap documents.

## Expected Files

Default write boundary:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
backend/pyproject.toml
backend/app/modules/knowledge/**
backend/app/modules/extension/** only for KnowledgeAdapter capability wiring
backend/app/tests/**knowledge**
backend/app/tests/db/**
backend/alembic/versions/**
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-47-final-test-knowledge-rag-system.md
```

Explain any write outside this set before editing it.

## Verification Commands

Run focused optional-provider fake-client contract tests and provider-neutral
retrieval API tests, then:

```powershell
git diff --check
```

The source `storage/chtest-dev.db` remains blocked and read-only. Do not run
upgrade, stamp, bootstrap, or registry mutation against it.

## Acceptance

- Optional provider payloads never leak into public/core contracts.
- Fake Qdrant/Haystack/LlamaIndex matches persist the same provider-neutral
  run/evidence and Artifact shapes as PostgreSQL and deterministic fallback.
- Unavailable/failing optional providers record actual degraded/failed state,
  stable reasons, and no fabricated scores.
- Prompt eligibility and freshness still exclude stale, unsafe, duplicate,
  archived, missing, or cross-project cards.
- `git diff --check` passes.

## Commit Message

```text
feat(knowledge): add optional provider contracts
```

## Next Task

After Task 47.6 is verified and committed, continue Task 47.7 with
evidence-backed CaseGeneration fields.
