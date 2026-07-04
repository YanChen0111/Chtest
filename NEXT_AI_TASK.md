# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 38: Reviewed TestKnowledgeCard Creation Contract.

## Current Task

Slice 38 Task 3: Add reviewed TestKnowledgeCard creation golden smoke.

## Product Value Answer

After this task, Chtest has a contract-level fixture and golden smoke proving
reviewed TestKnowledgeCard creation cannot bypass source evidence,
duplicate/merge, or prompt eligibility gates.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md`
8. `docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md`
9. `docs/fixtures/25-test-knowledge-card-candidate-review-golden.md`
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
docs/fixtures/26-reviewed-test-knowledge-card-creation-golden.md
backend/app/tests/golden/test_reviewed_test_knowledge_card_creation_contract_golden.py
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden-smoke task. Do not add frontend code, backend runtime feature code,
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
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_reviewed_test_knowledge_card_creation_contract_golden.py -q
git diff --check
```

Expected result: reviewed TestKnowledgeCard creation golden smoke passes and
diff check passes.

## Acceptance

- Golden names reviewed TestKnowledgeCard creation, approved candidate review,
  creation action, card field mapping, source evidence, source manifest,
  duplicate/merge preconditions, `allowed_for_prompt=false`, unsupported
  claims, ReviewHistory, and creation artifact evidence.
- Golden proves no broad TestKnowledgeCard CRUD, automatic card creation from
  model output, automatic prompt eligibility, automatic merge/archive/delete,
  historical evidence mutation, provider call, vector index, graph job, MCP
  runtime, artifact mutation, review bypass, auto-promotion, RBAC, tenants, or
  permissions is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 38 Completion Gate.

## Commit Message

```text
test(golden): add reviewed test knowledge card creation smoke
```

## Next Task

Slice 38 Completion Gate.
