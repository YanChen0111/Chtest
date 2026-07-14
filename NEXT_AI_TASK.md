# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. Docker runtime work remains intentionally skipped by the user because
the local Docker Desktop/WSL engine cannot be repaired in this session.

## Current Slice

Slice 47: Final Test Knowledge RAG System.

## Current Task

Slice 47 Task 47.3: add KnowledgeIngestionRun persistence and the contracted
TestKnowledgeCard provenance/review fields as the first final RAG data/API step.

Required output:

1. Add KnowledgeIngestionRun model/schema/migration fields from the data
   contract, including observable counts, safe errors, timestamps, source refs,
   parser/config snapshots, and evidence artifact ids.
2. Add TestKnowledgeCard provenance/review fields for source locators,
   ingestion-run ownership, review rationale, duplicate links, and verification
   time without weakening prompt eligibility rules.
3. Implement the smallest create/list/read ingestion API path with same-project
   persisted source validation and deterministic/idempotent local behavior.
4. Preserve Artifact evidence and review gates; do not add retrieval, pgvector,
   Qdrant, external parsers, or frontend redesign in this task.
5. Verify on empty/test databases only; do not migrate or stamp the blocked
   local acceptance database.

## Product Value Answer

The user can inspect every knowledge import as a persisted, traceable run and
review exactly which source evidence produced each testing knowledge card.

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

Only edit files directly needed for KnowledgeIngestionRun and enhanced
TestKnowledgeCard persistence/API behavior. Do not add retrieval/vector/provider
runtime or mutate the blocked local acceptance database.

## Verification Commands

Use focused DB/API ingestion tests and an empty-database Alembic upgrade, then:

```bash
git diff --check
```

The existing local preflight must remain blocked until its independently
designed baseline recovery is complete; new migrations run only on test data.

## Acceptance

- Knowledge ingestion runs persist observable source, parser, status, count,
  error, timing, and evidence fields.
- Enhanced cards retain exact source/ingestion/review provenance and preserve
  approved + safe + prompt-eligible generation rules.
- Create/list/read behavior is same-project, deterministic, idempotent, and
  evidence-backed.
- Empty/test database migrations pass without touching the local acceptance DB.
- `git diff --check` passes.

## Commit Message

```text
feat(knowledge): add ingestion run model and api
```

## Next Task

After Task 47.3 is verified and committed, continue Task 47.4 with
KnowledgeRetrievalRun and normalized KnowledgeEvidence persistence/API behavior.
