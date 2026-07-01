# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 30: Test Knowledge Card Contract.

## Current Task

Slice 30 Completion Gate.

## Product Value Answer

After this task, Slice 30 is validated and handed off with contracts, fixture,
and golden smoke evidence for generated-case knowledge evidence fields.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
8. `docs/fixtures/18-test-knowledge-card-contract-golden.md`
9. `memory/08-session-handoff.md`
10. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-30-test-knowledge-card-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Completion task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, external provider integrations, vector database,
embeddings, reranking, background indexing, graph runtime, MCP runtime,
artifact upload/mutation/delete, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior, RBAC,
tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_contract_golden.py -q
git diff --check
```

Expected result: golden smoke passes, diff check passes, and Slice 30 task table
records completed task commits.

## Acceptance

- Slice 30 task table records completed task commits.
- Contract and fixture documents agree on field names and non-goals.
- Golden smoke passes.
- `NEXT_AI_TASK.md` points to the next narrow V2 task.

## Commit Message

```text
docs(v2): complete test knowledge card contract slice
```

## Next Task

Select and plan the next narrow V2 slice after Slice 30 completion.
