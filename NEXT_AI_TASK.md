# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 42: TestKnowledgeCard Prompt Context Consumption Contract.

## Current Task

Slice 42 Task 3: Add TestKnowledgeCard prompt context consumption golden smoke.

## Product Value Answer

After this task, Chtest has contract-level golden coverage proving prompt
context consumption cannot set `used_knowledge=true` or cite TestKnowledgeCard
content without valid prompt context evidence, source hashes, context manifest
links, and prompt/skill trace.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/contracts/05-prompt-skill-contract.md`
8. `docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md`
9. `docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md`
10. `docs/fixtures/29-test-knowledge-card-prompt-context-evidence-golden.md`
11. `backend/app/tests/golden/test_test_knowledge_card_prompt_context_evidence_contract_golden.py`
12. `memory/08-session-handoff.md`
13. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/tests/golden/test_test_knowledge_card_prompt_context_consumption_contract_golden.py
docs/fixtures/30-test-knowledge-card-prompt-context-consumption-golden.md
docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden-smoke task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, broad TestKnowledgeCard CRUD implementation,
backend feature API, frontend page, automatic prompt eligibility, prompt
assembly implementation, prompt runtime execution, provider calls,
deterministic retrieval behavior change, automatic card creation from model
output, automatic knowledge ingestion, external provider integrations, vector
database, embeddings, reranking, graph runtime, MCP runtime, provider SDK,
credentials, artifact upload/mutation/delete, historical evidence mutation,
generated-case auto-approval, runner behavior changes, report generation
behavior changes, remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_consumption_contract_golden.py -q
git diff --check
```

Expected result: focused Slice 42 golden verification passes and diff check
passes.

## Acceptance

- Golden names prompt context evidence artifact id, context manifest,
  `used_knowledge`, consumed TestKnowledgeCard ids, source hash, output
  citations, PromptVersion, SkillVersion, ReviewHistory, skipped evidence,
  failure behavior, and forbidden side effects.
- Golden proves no prompt assembly implementation, prompt runtime execution,
  provider call, retrieval ranking change, vector index, embedding, reranking,
  graph job, MCP runtime, broad CRUD, automatic eligibility, historical
  evidence mutation, RBAC, tenants, or permissions is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 42 Completion Gate.

## Commit Message

```text
test(golden): add test knowledge card prompt context consumption smoke
```

## Next Task

Slice 42 Completion Gate.
