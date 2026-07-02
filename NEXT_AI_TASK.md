# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 31: Generated Case Knowledge Evidence Persistence.

## Current Task

Slice 31 Completion Gate.

## Product Value Answer

After this task, Slice 31 is verified end to end and the next narrow V2 task is
selected for AI coding.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md`
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
docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Use TDD. Do not add frontend code, package upgrades, external provider
integrations, vector database, embeddings, reranking, background indexing,
graph runtime, MCP runtime, TestKnowledgeCard CRUD, artifact upload/mutation/
delete, generated-case auto-approval, runner behavior changes, report
generation behavior changes, remote CI provider behavior, RBAC, tenants, or
permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py backend/app/tests/api/test_case_generation.py backend/app/tests/golden/test_generated_case_knowledge_evidence_persistence_golden.py -q
git diff --check
```

Expected result: DB/API/golden Slice 31 tests pass and diff check passes.

## Acceptance

- Slice 31 task table records current commit ids.
- DB/API/golden tests pass together.
- `NEXT_AI_TASK.md` points to the next narrow V2 task.
- Memory handoff records Slice 31 completion and residual risks.

## Commit Message

```text
docs(v2): complete generated case knowledge evidence persistence slice
```

## Next Task

Select and plan the next narrow V2 task after Slice 31 completion.
