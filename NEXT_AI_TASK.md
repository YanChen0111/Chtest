# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. The current focus is V2 acceptance stabilization through the local
dev/browser workflow. Docker runtime work remains intentionally skipped by the
user because the local Docker Desktop/WSL engine cannot be repaired in this
session.

## Current Slice

V2 acceptance stabilization: make the local-first AI testing workbench feel
acceptance-ready for the main reviewer workflow from requirement review to case
generation, knowledge grounding, automation planning, automation draft review,
and local execution evidence surfaces.

## Current Task

Slice 47 Task 47.1: promote the Final Test Knowledge RAG System into product and
contract scope, preserve the complete web-experience review, and define the
implementation/acceptance task sequence with a design reason for each major
capability.

Required output:

1. Product scope explicitly includes ingestion, structured cards, reviewed
   safety flow, hybrid retrieval, evidence-backed cases, coverage agents,
   relationship graph, feedback, and provider isolation.
2. Data/API/state/artifact contracts define observable ingestion and retrieval
   runs, normalized KnowledgeEvidence, relationships, feedback, trace APIs, and
   final CaseGeneration fields.
3. The final strategy validates pgvector, Qdrant, Haystack, and LlamaIndex
   against official documentation while preserving KnowledgeAdapter ownership.
4. A Slice 47 task plan explains why every capability exists and orders code
   work behind the local database preflight blocker.
5. The full web review records page-by-page efficiency, quality, log, trace, and
   visual findings.

## Product Value Answer

The user can evaluate and implement the final RAG system against one stable
Chtest-owned evidence model, understand why each major function exists, and
avoid coupling case generation or review to a specific vector/agent provider.
The web review also makes test-efficiency, quality, log-query, and evidence-trace
gaps explicit before frontend redesign.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `memory/08-session-handoff.md`
8. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Docker Desktop, WSL, container runtime recovery, broad roadmap, migration,
  enterprise collaboration, marketplace, distributed execution, cloud storage,
  cloud CI/provider integration, RBAC, tenants, permissions, or unrelated
  deleted golden-chain files unless a concrete verification failure requires
  them.

## Expected Files

Default write boundary for the next local evidence risk:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/product/01-positioning-and-scope.md
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/implementation/11-final-rag-agent-strategy.md
docs/implementation/slices/slice-47-final-test-knowledge-rag-system.md
docs/reviews/2026-07-14-full-web-test-experience-review.md
```

Only edit files that are directly required to fix a verification blocker. Do
not revert unrelated dirty-worktree changes.

## Verification Commands

Use the documentation scope check:

```bash
rg -n "Final Test Knowledge RAG|KnowledgeIngestionRun|KnowledgeRetrievalRun|KnowledgeEvidence|postgres_hybrid|KnowledgeFeedback|evidence-trace|why|Why" docs/product/01-positioning-and-scope.md docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/11-final-rag-agent-strategy.md docs/implementation/slices/slice-47-final-test-knowledge-rag-system.md docs/reviews/2026-07-14-full-web-test-experience-review.md NEXT_AI_TASK.md
git diff --check
```

Docker/compose runtime verification is intentionally skipped until the machine's
Docker Desktop Linux Engine is repaired outside this repo.

## Acceptance

- Product/contracts no longer classify final RAG as an unpromoted future-only
  runtime.
- Every major final RAG capability has an explicit design reason, stable Chtest
  owner, evidence boundary, state, API, and planned verification.
- The review covers every current route and prioritizes efficiency, quality,
  logs, traceability, and visual hierarchy.
- Provider schemas remain behind KnowledgeAdapter.
- `git diff --check` passes.

## Commit Message

```text
docs(rag): promote final test knowledge system
```

## Next Task

After Task 47.1 is committed, continue Task 47.2: repair the local acceptance
database baseline on a copy of the current database and add a safe preflight.
The database has no Alembic version record, is missing current candidate columns,
and contains PromptVersion content drift. Do not add final RAG tables or mutate
the only local database copy until the preflight is verified. Docker/compose
runtime repair remains out of scope until the local engine is fixed outside this
repo.
