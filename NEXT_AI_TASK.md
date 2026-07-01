# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 30: Test Knowledge Card Contract.

## Current Task

Slice 30 Task 2: Define TestKnowledgeCard and KnowledgeEvidence contracts.

## Product Value Answer

After this task, Chtest has a contract for reviewable testing knowledge evidence
that generated cases can cite before any RAG runtime or provider integration is
implemented.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/10-v2-scope-options.md`
9. `docs/implementation/11-final-rag-agent-strategy.md`
10. `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
11. `memory/08-session-handoff.md`
12. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-30-test-knowledge-card-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, external provider integrations, vector database,
embeddings, reranking, background indexing, graph runtime, MCP runtime,
artifact upload/mutation/delete, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior, RBAC,
tenants, or permissions.

## Verification Command

```bash
rg -n "TestKnowledgeCard|KnowledgeEvidence|source_knowledge_evidence_ids|coverage_gap_notes|RAG runtime|MCP runtime" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-30-test-knowledge-card-contract.md
git diff --check
```

Expected result: contracts define TestKnowledgeCard, KnowledgeEvidence, generated
case evidence fields, artifact/state/API boundaries, and explicit runtime
non-goals; diff check passes.

## Acceptance

- Data contract defines local `TestKnowledgeCard` and normalized
  `KnowledgeEvidence` fields.
- API contract defines the contract boundary without enabling external
  retrieval, indexing, provider calls, or runtime behavior.
- State-machine contract states knowledge-card status changes do not trigger
  retrieval jobs, indexing, embeddings, graph extraction, or generated-case
  promotion.
- Artifact contract defines knowledge-card and generated-case evidence file
  rules.
- GeneratedCaseCandidate contract defines evidence ids, risk coverage,
  generation reason, automation readiness, quality score, review findings, and
  coverage gap notes.
- Review gates and no RAG runtime, MCP runtime, vector, embedding, reranking,
  external provider, RBAC, tenant, permission, and remote CI provider boundaries
  remain explicit.

## Commit Message

```text
docs(v2): define test knowledge card contract
```

## Next Task

Slice 30 Task 3: Add Test Knowledge Card Golden Fixture.
