# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. Docker runtime work remains intentionally skipped because the local
Docker Desktop/WSL engine is unavailable.

## Current Slice

Slice 47: Final Test Knowledge RAG System.

## Current Task

Slice 47 Task 47.5: add the default PostgreSQL full-text + pgvector
KnowledgeAdapter behind the provider-neutral retrieval/evidence contracts.

Required output:

1. Add PostgreSQL-native full-text and pgvector storage/query support for
   prompt-eligible TestKnowledgeCard rows while preserving SQLite deterministic
   fallback behavior.
2. Keep KnowledgeRetrievalRun, KnowledgeEvidence, Artifact ownership, scores,
   safety snapshots, current lifecycle fields, and API responses independent of
   PostgreSQL/pgvector operator or payload shape.
3. Add capability detection and deterministic degraded fallback when pgvector
   or PostgreSQL-native vector search is unavailable; never fabricate a vector
   score.
4. Add focused PostgreSQL adapter SQL/DDL tests and provider-neutral retrieval
   tests. Use temporary/empty databases only; do not touch the blocked local
   acceptance database.
5. Do not add Qdrant, Haystack, LlamaIndex, online embedding providers,
   rerankers, graph, feedback, frontend redesign, RBAC, tenants, or cloud
   services in this task.

## Product Value Answer

Local-first PostgreSQL users gain semantic and full-text recall without losing
the stable logs, evidence trace, review gates, or deterministic fallback that
test engineers depend on for diagnosis and audit.

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

- Docker Desktop/WSL repair, Qdrant, Haystack, LlamaIndex, graph/feedback,
  enterprise collaboration, marketplace, cloud CI, RBAC, tenants, permissions,
  unrelated frontend pages, or broad roadmap documents.

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

Run focused PostgreSQL adapter/DDL tests, SQLite deterministic fallback tests,
and provider-neutral retrieval API tests, then:

```powershell
git diff --check
```

The source `storage/chtest-dev.db` remains blocked and read-only. Do not run
upgrade, stamp, bootstrap, or registry mutation against it.

## Acceptance

- PostgreSQL uses native full-text plus pgvector when capability is available.
- SQLite and PostgreSQL-without-pgvector degrade deterministically and record
  the actual mode/fallback reason with `vector_score=null`.
- Native and fallback paths persist the same provider-neutral run/evidence and
  Artifact contracts.
- Index freshness and prompt eligibility exclude stale, unsafe, duplicate,
  archived, missing, or cross-project cards.
- Temporary-database migration/DDL tests pass without changing the local
  acceptance database.
- `git diff --check` passes.

## Commit Message

```text
feat(knowledge): add postgres hybrid adapter
```

## Next Task

After Task 47.5 is verified and committed, continue Task 47.6 with optional
Qdrant and Haystack/LlamaIndex provider contracts using fake clients only.
