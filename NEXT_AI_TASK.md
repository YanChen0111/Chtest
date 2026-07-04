# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 38: Reviewed TestKnowledgeCard Creation Contract.

## Current Task

Slice 38 Completion Gate.

## Product Value Answer

After this task, Slice 38 is closed with focused golden verification and the
next narrow V2 task is selected.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md`
8. `docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md`
9. `docs/fixtures/26-reviewed-test-knowledge-card-creation-golden.md`
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
docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Completion-only task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, broad TestKnowledgeCard CRUD implementation,
backend feature API, frontend page, automatic card creation from model output,
automatic prompt eligibility, automatic knowledge ingestion, external provider
integrations, vector database, embeddings, reranking, graph runtime, MCP
runtime, provider SDK, credentials, artifact upload/mutation/delete,
historical evidence mutation, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior,
RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_reviewed_test_knowledge_card_creation_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_candidate_review_contract_golden.py -q
git diff --check
```

Expected result: Slice 38 and Slice 37 focused golden verification passes and
diff check passes.

## Acceptance

- Slice 38 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

## Commit Message

```text
docs(v2): complete reviewed test knowledge card creation slice
```

## Next Task

Select the next narrow V2 slice from `docs/implementation/10-v2-scope-options.md`.
