# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 36: TestKnowledgeCard Handoff Contract.

## Current Task

Slice 36 Task 3: Add TestKnowledgeCard handoff golden smoke.

## Product Value Answer

After this task, Chtest has a contract-level fixture and golden smoke proving
approved KnowledgeFeedbackDraft handoff remains a reviewed TestKnowledgeCard
candidate payload and cannot bypass card review or prompt eligibility.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md`
8. `docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md`
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
docs/implementation/slices/slice-36-test-knowledge-card-handoff-contract.md
docs/fixtures/24-test-knowledge-card-handoff-golden.md
backend/app/tests/golden/test_test_knowledge_card_handoff_contract_golden.py
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden-smoke task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, TestKnowledgeCard CRUD implementation, backend
feature API, frontend page, automatic card creation, automatic card approval,
automatic prompt eligibility, automatic knowledge ingestion, external provider
integrations, vector database, embeddings, reranking, graph runtime, MCP
runtime, provider SDK, credentials, artifact upload/mutation/delete,
historical evidence mutation, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior,
RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_handoff_contract_golden.py -q
git diff --check
```

Expected result: TestKnowledgeCard handoff golden smoke passes and diff check
passes.

## Acceptance

- Golden names approved KnowledgeFeedbackDraft handoff, ReviewHistory,
  feedback review artifact, TestKnowledgeCard candidate fields, source
  evidence, safe_to_show, `allowed_for_prompt=false`, duplicate/merge hints,
  unsupported claims, and human review.
- Golden proves no TestKnowledgeCard CRUD, automatic row creation, automatic
  prompt eligibility, historical evidence mutation, provider call, vector
  index, graph job, MCP runtime, artifact mutation, review bypass,
  auto-promotion, RBAC, tenants, or permissions is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 36 Completion Gate.

## Commit Message

```text
test(golden): add test knowledge card handoff smoke
```

## Next Task

Slice 36 Completion Gate.
