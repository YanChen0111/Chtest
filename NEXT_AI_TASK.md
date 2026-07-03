# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 34: Knowledge Feedback Contract.

## Current Task

Slice 34 Task 3: Add Knowledge Feedback Contract golden smoke.

## Product Value Answer

After this task, Chtest has a golden smoke proving the KnowledgeFeedbackAgent
contract remains draft-only, review-gated, and free of feedback runtime side
effects.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/02-api-contract.md`
4. `docs/contracts/03-state-machines.md`
5. `docs/contracts/05-prompt-skill-contract.md`
6. `prompts/knowledge_feedback/v1.md`
7. `skills/knowledge-feedback-skill/v1.md`
8. `docs/implementation/11-final-rag-agent-strategy.md`
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
backend/app/tests/golden/test_knowledge_feedback_contract_golden.py
docs/fixtures/22-knowledge-feedback-contract-golden.md
docs/implementation/slices/slice-34-knowledge-feedback-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden task only. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, KnowledgeFeedbackAgent runtime,
TestKnowledgeCard CRUD, prompt-eligible auto-marking, automatic knowledge
ingestion, external provider integrations, vector database, embeddings,
reranking, graph runtime, MCP runtime, provider SDK, credentials, artifact
upload/mutation/delete, historical review/failure/report/TestCase mutation,
generated-case auto-approval, runner behavior changes, report generation
behavior changes, remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_knowledge_feedback_contract_golden.py -q
git diff --check
```

Expected result: Knowledge feedback contract golden smoke and diff check pass.

## Acceptance

- Golden names KnowledgeFeedbackAgent, knowledge_feedback prompt,
  knowledge-feedback-skill, input evidence sources, draft feedback fields,
  unsupported claims, human review, prompt eligibility, and failure behavior.
- Golden proves no TestKnowledgeCard auto-creation, prompt-eligible
  auto-marking, historical evidence mutation, provider call, vector index,
  graph job, MCP runtime, artifact mutation, review bypass, or auto-promotion
  is created by the contract.

## Commit Message

```text
test(golden): add knowledge feedback contract smoke
```

## Next Task

Slice 34 Completion Gate.
