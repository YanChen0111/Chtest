# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. Docker runtime work remains intentionally skipped by the user because
the local Docker Desktop/WSL engine cannot be repaired in this session.

## Current Slice

Slice 47: Final Test Knowledge RAG System.

## Current Task

Slice 47 Task 47.4: persist KnowledgeRetrievalRun and normalized
KnowledgeEvidence as the provider-neutral retrieval log and evidence boundary.

Required output:

1. Add KnowledgeRetrievalRun and KnowledgeEvidence model/schema/migration fields
   from the data contract, including provider/mode snapshots, safe query/filter
   evidence, scores, latency, counts, errors, and exact source locators.
2. Route the existing deterministic TestKnowledgeCard retrieval through a
   persisted run and normalized evidence rows without changing provider-neutral
   response ownership.
3. Implement the smallest create/list/read retrieval-log API with project,
   status, provider, consumer, limit, and cursor filters.
4. Persist a `knowledge_retrieval` Artifact for successful empty and non-empty
   results; never fabricate semantic scores when vector capability is absent.
5. Do not add pgvector, Qdrant, Haystack, LlamaIndex, online embeddings, graph,
   feedback, or frontend redesign in this task. Test migrations only on
   empty/temporary databases.

## Product Value Answer

The user can query retrieval history, diagnose provider/filter/latency behavior,
and trace every returned snippet to stable Chtest evidence independent of the
retrieval provider.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `memory/08-session-handoff.md`
9. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Docker Desktop, WSL, container runtime recovery, broad roadmap, migration,
  enterprise collaboration, marketplace, distributed execution, cloud storage,
  cloud CI/provider integration, RBAC, tenants, permissions, or unrelated
  deleted golden-chain files unless a concrete verification failure requires
  them.

## Expected Files

Default write boundary:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
backend/app/**
backend/app/tests/**
backend/alembic/versions/**
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-47-final-test-knowledge-rag-system.md
```

Only edit files directly needed for KnowledgeRetrievalRun and normalized
KnowledgeEvidence persistence/API behavior. Do not add vector/provider runtime
or mutate the blocked local acceptance database.

## Verification Commands

Use focused DB/API retrieval-log tests and an empty-database Alembic upgrade,
then:

```bash
git diff --check
```

The existing local preflight must remain blocked until its independently
designed baseline recovery is complete; new migrations run only on test data.

## Acceptance

- Retrieval runs persist query/filter/provider/mode/status/count/latency/error
  fields and one normalized result Artifact.
- KnowledgeEvidence rows preserve card/source ids, exact locators, bounded safe
  snippets, component scores, matched terms, and retrieval reasons.
- Create/list/read behavior is same-project, deterministic, paged, and exposes
  useful retrieval logs for both empty and non-empty results.
- Empty/test database migrations pass without touching the local acceptance DB.
- `git diff --check` passes.

## Commit Message

```text
feat(knowledge): persist retrieval evidence
```

## Next Task

After Task 47.4 is verified and committed, continue Task 47.5 with the default
PostgreSQL full-text + pgvector KnowledgeAdapter behind the stable evidence
contracts.
