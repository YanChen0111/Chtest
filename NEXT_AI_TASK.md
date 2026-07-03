# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 33: MCP-Ready ToolDefinition And KnowledgeAdapter Safety Contract.

## Current Task

Slice 33 Completion Gate.

## Product Value Answer

After this task, Slice 33 is validated end to end and the next narrow V2 task
is selected without adding MCP runtime, provider calls, or tool execution.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/02-api-contract.md`
4. `docs/contracts/03-state-machines.md`
5. `docs/contracts/05-prompt-skill-contract.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md`
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
docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Completion gate only. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, external provider integrations, vector database,
embeddings, reranking, background indexing, graph runtime, MCP runtime, MCP
server/client transport, provider SDK, credentials, TestKnowledgeCard CRUD,
artifact upload/mutation/delete, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior, RBAC,
tenants, or permissions.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py backend/app/tests/golden/test_agent_workflow_contract_golden.py -q
git diff --check
```

Expected result: Slice 33 focused golden verification and diff check pass.

## Acceptance

- Slice 33 task table records completed task commits.
- Focused golden verification passes.
- `NEXT_AI_TASK.md` points to the next narrow V2 task.

## Commit Message

```text
docs(v2): complete mcp-ready tool knowledge safety slice
```

## Next Task

Select the next narrow V2 task after Slice 33 completion.
