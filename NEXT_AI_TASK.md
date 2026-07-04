# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 46: TestKnowledgeCard Prompt Context Review Discrepancy Tracking Contract.

## Current Task

Slice 46 Task 3: Add TestKnowledgeCard prompt context review discrepancy tracking golden smoke.

## Product Value Answer

After this task, Chtest has a focused golden fixture and smoke test proving the
TestKnowledgeCard prompt context review discrepancy tracking contract preserves
review summary exports, review decisions, audit summaries, `used_knowledge`,
ReviewHistory, and forbidden side effects.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/slices/slice-46-test-knowledge-card-prompt-context-review-discrepancy-tracking-contract.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/contracts/05-prompt-skill-contract.md`
9. `docs/fixtures/33-test-knowledge-card-prompt-context-audit-review-summary-export-golden.md`
10. `backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_summary_export_contract_golden.py`
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
backend/app/tests/golden/test_test_knowledge_card_prompt_context_review_discrepancy_tracking_contract_golden.py
docs/fixtures/34-test-knowledge-card-prompt-context-review-discrepancy-tracking-golden.md
docs/implementation/slices/slice-46-test-knowledge-card-prompt-context-review-discrepancy-tracking-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden-only task. Do not add frontend code, backend runtime feature code,
report generation behavior changes, export/download endpoints, migrations,
package upgrades, broad TestKnowledgeCard CRUD implementation, backend feature
API, frontend page, automatic prompt eligibility, prompt assembly
implementation, prompt runtime execution, provider calls, deterministic
retrieval behavior change, automatic card creation from model output,
automatic knowledge ingestion, external provider integrations, vector database,
embeddings, reranking, graph runtime, MCP runtime, provider SDK, credentials,
artifact upload/mutation/delete, historical evidence mutation, generated-case
auto-approval, runner behavior changes, remote CI provider behavior, RBAC,
tenants, or permissions.

## Verification Command

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_review_discrepancy_tracking_contract_golden.py -q
git diff --check
```

Expected result: golden smoke passes and diff check passes.

## Acceptance

- Golden names review summary export artifact id, discrepancy type, affected
  citation ids, evidence gap summary, mismatch reason, reviewer note, severity,
  resolution status, ReviewHistory, failure behavior, and forbidden side
  effects.
- Golden proves no frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  call, retrieval ranking change, vector index, embedding, reranking, graph
  job, MCP runtime, broad CRUD, automatic eligibility, historical evidence
  mutation, RBAC, tenants, or permissions is created by the contract.
- `NEXT_AI_TASK.md` points to the Slice 46 Completion Gate.

## Commit Message

```text
test(golden): add test knowledge card prompt context review discrepancy tracking smoke
```

## Next Task

Slice 46 Completion Gate.
