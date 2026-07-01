# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 30: Test Knowledge Card Contract.

## Current Task

Slice 30 Task 3: Add Test Knowledge Card Golden Fixture.

## Product Value Answer

After this task, Chtest has an AI-readable fixture showing how structured
testing knowledge evidence supports generated cases, review findings, and
coverage gap notes without enabling a RAG runtime.

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
docs/fixtures/18-test-knowledge-card-contract-golden.md
docs/implementation/slices/slice-30-test-knowledge-card-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Fixture task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, external provider integrations, vector database,
embeddings, reranking, background indexing, graph runtime, MCP runtime,
artifact upload/mutation/delete, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior, RBAC,
tenants, or permissions.

## Verification Command

```bash
test -f docs/fixtures/18-test-knowledge-card-contract-golden.md
rg -n "TestKnowledgeCard|KnowledgeEvidence|GeneratedCaseCandidate|review_findings|coverage_gap_notes" docs/fixtures/18-test-knowledge-card-contract-golden.md docs/implementation/slices/slice-30-test-knowledge-card-contract.md
git diff --check
```

Expected result: fixture defines requirement text, source artifacts,
TestKnowledgeCard examples, KnowledgeEvidence examples, generated candidates,
review findings, coverage gap notes, and explicit runtime non-goals; diff check
passes.

## Acceptance

- Fixture includes a compact requirement, source ContextArtifact references,
  TestKnowledgeCard examples, KnowledgeEvidence examples, generated case
  candidates, review findings, coverage gap notes, and evidence ids.
- Fixture shows accepted, needs-review, and rejected evidence conditions.
- Fixture explains provider schemas are normalized into Chtest evidence.
- Fixture does not imply vector database, external provider, graph runtime,
  auto-approval, frontend behavior, or execution behavior exists.

## Commit Message

```text
docs(fixtures): add test knowledge card contract golden
```

## Next Task

Slice 30 Task 4: Add Contract Smoke For Generated-Case Evidence Fields.
