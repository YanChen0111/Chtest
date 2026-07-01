# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 30: Test Knowledge Card Contract.

## Current Task

Slice 30 Task 4: Add Contract Smoke For Generated-Case Evidence Fields.

## Product Value Answer

After this task, a focused golden smoke proves generated-case evidence fields
can be serialized and read back without creating runtime retrieval behavior or
review bypasses.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
9. `docs/fixtures/18-test-knowledge-card-contract-golden.md`
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
backend/app/tests/golden/test_test_knowledge_card_contract_golden.py
backend/app/schemas/*.py
backend/app/models/*.py
backend/app/api/*.py
docs/implementation/slices/slice-30-test-knowledge-card-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Only touch backend schema/model/API files if required by the existing
implementation shape. Do not add frontend code, migrations unless the current
model implementation already requires them, package upgrades, external provider
integrations, vector database, embeddings, reranking, background indexing,
graph runtime, MCP runtime, artifact upload/mutation/delete, generated-case
auto-approval, runner behavior changes, report generation behavior changes,
remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_contract_golden.py -q
git diff --check
```

Expected result: golden smoke passes and proves generated-case evidence fields
are structured evidence only; diff check passes.

## Acceptance

- Golden proves generated-case evidence fields can be serialized and read back
  through the relevant schema or API boundary.
- Golden proves knowledge evidence references are structured data and do not
  create TestCase records, runner executions, reports, external provider calls,
  retrieval jobs, vector indexes, graph jobs, or artifact mutations.
- If database models are not yet implemented, the task stays schema/fixture
  level and documents the missing implementation as the next task instead of
  inventing a runtime.

## Commit Message

```text
test(golden): add test knowledge card contract smoke
```

## Next Task

Slice 30 Completion Gate.
