# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 51: KnowledgeAdapter Provider Evaluation Review Decision Contract.

## Current Task

Slice 51 Completion Gate.

## Product Value Answer

After this task, Slice 51 is closed with its planning, contract, and golden
smoke commits recorded. The next worker can start the next narrow V2 slice
without reopening provider enablement, provider SDK, external call, vector
database, embedding, reranking, runtime retrieval, provider-backed prompt
context behavior, frontend page, RBAC, tenants, or permissions.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md`
5. `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_decision_contract_golden.py`
6. `backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py`
7. `docs/fixtures/39-knowledge-adapter-provider-evaluation-review-decision-golden.md`
8. `docs/fixtures/38-knowledge-adapter-provider-evaluation-plan-golden.md`
9. `memory/08-session-handoff.md`
10. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  and runtime retrieval docs unless a concrete blocker requires them.

## Expected Files

Update only these files for the current task:

```text
docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Completion gate only. Do not add frontend code, backend runtime feature code,
report generation behavior changes, export/download endpoints, migrations,
package upgrades, broad KnowledgeAdapter CRUD implementation, backend feature
API, frontend page, automatic prompt eligibility, prompt assembly
implementation, prompt runtime execution, provider calls, deterministic
retrieval behavior change, automatic knowledge ingestion, external provider
integrations, vector database, embeddings, reranking, graph runtime, MCP
runtime, provider SDK, credentials, provider enablement, runtime retrieval,
provider-backed prompt context evidence, artifact upload/mutation/delete,
historical evidence mutation, generated-case auto-approval, runner behavior
changes, remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_review_decision_contract_golden.py backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py -q
git diff --check
```

Expected result: focused Slice 50/51 golden smoke passes and diff check passes.

## Acceptance

- Slice 51 task table records Task 1, Task 2, and Task 3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

## Commit Message

```text
docs(v2): complete knowledge adapter provider evaluation review decision slice
```

## Next Task

Select the next narrow V2 slice.
