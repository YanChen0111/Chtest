# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

V2 Planning.

## Current Task

Slice 19 Task 2: Define deterministic retrieval contract boundary.

## Product Value Answer

After this task, contracts explicitly define deterministic local
ContextArtifact retrieval before implementation starts.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`
9. `docs/implementation/00-v0.1-walking-skeleton.md`
10. `docs/fixtures/00-v1-demo-path.md`
11. `docs/implementation/10-v2-scope-options.md`
12. `docs/implementation/slices/slice-17-extension-surface.md`
13. `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
```

Contract-only task. Do not add product code, vector database, embeddings,
reranking, background indexing, external RAG provider calls, MCP runtime, RBAC,
tenants, permissions, marketplace, cloud sync, release automation, or remote CI
provider integration.

## Verification Command

```bash
rg -n "Deterministic|KnowledgeAdapter|ContextArtifact|used_knowledge|retrieval|retrieved" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
git diff --check
```

Expected result: deterministic retrieval contract boundaries are visible and
diff check passes.

## Acceptance

- Contract defines deterministic local retrieval as a KnowledgeAdapter stub.
- Contract defines retrieved snippet evidence, scores, matched terms, and
  ContextArtifact ids.
- Contract explains when `used_knowledge=true` is allowed.
- Artifact contract defines retrieval evidence artifact shape.
- Non-goals still exclude vectors, embeddings, reranking, background indexing,
  external providers, MCP runtime, RBAC, tenants, and permissions.

## Commit Message

```text
docs(v2): define deterministic retrieval contract
```

## Next Task

Start Slice 19 Task 3 only after the deterministic retrieval contract boundary
is committed.
