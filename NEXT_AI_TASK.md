# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 32: Agent Workflow Contract.

## Current Task

Slice 32 Task 3: Add agent workflow contract golden smoke.

## Product Value Answer

After this task, Chtest has a golden smoke proving the agent workflow contract
can be checked without running agents, providers, RAG, MCP, tools, or reports.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/02-api-contract.md`
4. `docs/contracts/03-state-machines.md`
5. `docs/contracts/05-prompt-skill-contract.md`
6. `docs/implementation/slices/slice-32-agent-workflow-contract.md`
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
backend/app/tests/golden/test_agent_workflow_contract_golden.py
docs/fixtures/20-agent-workflow-contract-golden.md
docs/implementation/slices/slice-32-agent-workflow-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden task only. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, external provider integrations, vector database,
embeddings, reranking, background indexing, graph runtime, MCP runtime,
TestKnowledgeCard CRUD, artifact upload/mutation/delete, generated-case
auto-approval, runner behavior changes, report generation behavior changes,
remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_agent_workflow_contract_golden.py -q
git diff --check
```

Expected result: agent workflow contract golden smoke and diff check pass.

## Acceptance

- Golden proves the contract names all requirement-to-reviewed-case agents.
- Golden proves each step has prompt/skill seed, input evidence, output,
  write permission, human gate, failure behavior, and trace requirement.
- Golden proves no TestCase, TestRun, Report, provider call, vector index,
  graph job, MCP runtime, or artifact mutation is created by the contract.
- Fixture documents the evidence-only workflow boundary.

## Commit Message

```text
test(golden): add agent workflow contract smoke
```

## Next Task

Slice 32 Completion Gate.
