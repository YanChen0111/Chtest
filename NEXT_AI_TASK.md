# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 48: TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export Contract.

## Current Task

Slice 48 Task 1: Add TestKnowledgeCard prompt context discrepancy resolution summary export task plan.

## Product Value Answer

After this task, Chtest has a narrow plan for packaging prompt context
discrepancy resolution review evidence into a future summary handoff without
mutating discrepancy records, review evidence, frontend pages, report
generation, export endpoints, or prompt runtime behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/slices/slice-47-test-knowledge-card-prompt-context-discrepancy-resolution-review-contract.md`
4. `docs/implementation/10-v2-scope-options.md`
5. `docs/contracts/01-data-model-contract.md`
6. `docs/contracts/02-api-contract.md`
7. `docs/contracts/03-state-machines.md`
8. `docs/contracts/04-artifact-contract.md`
9. `docs/contracts/05-prompt-skill-contract.md`
10. `memory/08-session-handoff.md`
11. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Planning-only task. Do not add frontend code, backend runtime feature code,
contract edits,
report generation behavior changes, export/download endpoints,
migrations, package upgrades, broad TestKnowledgeCard CRUD implementation,
backend feature API, frontend page, automatic prompt eligibility, prompt
assembly implementation, prompt runtime execution, provider calls,
deterministic retrieval behavior change, automatic card creation from model
output, automatic knowledge ingestion, external provider integrations, vector
database, embeddings, reranking, graph runtime, MCP runtime, provider SDK,
credentials, artifact upload/mutation/delete, historical evidence mutation,
generated-case auto-approval, runner behavior changes, remote CI provider
behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
test -f docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md
rg -n "TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export|resolution summary export|resolution outcome summary|accepted discrepancy group|rejected discrepancy group|acknowledged discrepancy group|clarification requested fields|resolution status|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md NEXT_AI_TASK.md
git diff --check
```

Expected result: plan file exists, required terms are present, and diff check
passes.

## Acceptance

- Slice 48 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names resolution summary export inputs, resolution outcome summary,
  accepted/rejected/acknowledged discrepancy groups, clarification requested
  fields, resolution status, ReviewHistory, failure behavior, and non-goals.
- The plan excludes frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  calls, retrieval ranking changes, vector indexes, embeddings, reranking,
  graph jobs, MCP runtime, broad CRUD, automatic eligibility, and historical
  evidence mutation.
- `NEXT_AI_TASK.md` points to Task 2.

## Commit Message

```text
docs(v2): add test knowledge card prompt context discrepancy resolution summary export plan
```

## Next Task

Slice 48 Task 2: Define TestKnowledgeCard prompt context discrepancy resolution summary export contracts.
