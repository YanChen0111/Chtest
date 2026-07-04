# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 40: TestKnowledgeCard Retrieval Boundary Contract.

## Current Task

Slice 40 Task 3: Add TestKnowledgeCard retrieval boundary golden smoke.

## Product Value Answer

After this task, Chtest has a contract-level fixture and golden smoke proving
future prompt-context selection cannot bypass prompt eligibility,
safe-to-show, source evidence, redaction, ReviewHistory, or exclusion gates.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md`
8. `docs/fixtures/27-test-knowledge-card-prompt-eligibility-golden.md`
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
docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md
docs/fixtures/28-test-knowledge-card-retrieval-boundary-golden.md
backend/app/tests/golden/test_test_knowledge_card_retrieval_boundary_contract_golden.py
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden-smoke task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, broad TestKnowledgeCard CRUD implementation,
backend feature API, frontend page, automatic prompt eligibility, prompt
runtime retrieval implementation, deterministic retrieval behavior change,
automatic card creation from model output, automatic knowledge ingestion,
external provider integrations, vector database, embeddings, reranking, graph
runtime, MCP runtime, provider SDK, credentials, artifact upload/mutation/delete,
historical evidence mutation, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior, RBAC,
tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_retrieval_boundary_contract_golden.py -q
git diff --check
```

Expected result: TestKnowledgeCard retrieval boundary golden smoke passes and
diff check passes.

## Acceptance

- Golden names selection inputs, `select_prompt_eligible_cards`,
  `allowed_for_prompt`, `prompt_eligible`, `safe_to_show`, source manifest,
  ReviewHistory, prompt eligibility artifact evidence, retrieval evidence
  outputs, exclusion reasons, failure behavior, and forbidden side effects.
- Golden proves no prompt runtime retrieval implementation, deterministic
  ranking change, vector index, embedding, reranking, graph job, provider call,
  MCP runtime, broad CRUD, automatic eligibility, historical evidence mutation,
  RBAC, tenants, or permissions is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 40 Completion Gate.

## Commit Message

```text
test(golden): add test knowledge card retrieval boundary smoke
```

## Next Task

Slice 40 Completion Gate.
