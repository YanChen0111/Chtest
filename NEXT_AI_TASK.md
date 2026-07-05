# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 47: TestKnowledgeCard Prompt Context Discrepancy Resolution Review Contract.

## Current Task

Slice 47 Completion Gate.

## Product Value Answer

After this task, Slice 47 is closed with task commits recorded, focused golden
verification passing, and the next narrow V2 task handed off.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/slices/slice-47-test-knowledge-card-prompt-context-discrepancy-resolution-review-contract.md`
4. `docs/implementation/10-v2-scope-options.md`
5. `backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_review_contract_golden.py`
6. `backend/app/tests/golden/test_test_knowledge_card_prompt_context_review_discrepancy_tracking_contract_golden.py`
7. `memory/08-session-handoff.md`
8. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-47-test-knowledge-card-prompt-context-discrepancy-resolution-review-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Completion-only task. Do not add frontend code, backend runtime feature code,
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
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_discrepancy_resolution_review_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_review_discrepancy_tracking_contract_golden.py -q
git diff --check
```

Expected result: focused golden verification passes and diff check passes.

## Acceptance

- Slice 47 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.

## Commit Message

```text
docs(v2): complete test knowledge card prompt context discrepancy resolution review slice
```

## Next Task

Slice 48 Task 1: Add next narrow V2 task plan.
