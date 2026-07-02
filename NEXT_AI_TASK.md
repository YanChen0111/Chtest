# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 33: MCP-Ready ToolDefinition And KnowledgeAdapter Safety Contract.

## Current Task

Slice 33 Task 1: Add MCP-ready ToolDefinition and KnowledgeAdapter safety
contract task plan.

## Product Value Answer

After this task, Chtest has a narrow plan for MCP-ready ToolDefinition and
KnowledgeAdapter safety boundaries before any MCP runtime or external provider
implementation exists.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/02-api-contract.md`
4. `docs/contracts/03-state-machines.md`
5. `docs/contracts/05-prompt-skill-contract.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/11-final-rag-agent-strategy.md`
8. `docs/implementation/10-v2-scope-options.md`
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
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Planning-only task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, external provider integrations, vector database,
embeddings, reranking, background indexing, graph runtime, MCP runtime, MCP
server/client transport, provider SDK, credentials, TestKnowledgeCard CRUD,
artifact upload/mutation/delete, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior, RBAC,
tenants, or permissions.

## Verification Command

```bash
test -f docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md
rg -n "MCP-Ready ToolDefinition|KnowledgeAdapter|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md NEXT_AI_TASK.md
git diff --check
```

Expected result: Slice 33 plan exists, names the safety boundary, and diff
check passes.

## Acceptance

- Slice 33 plan defines ToolDefinition and KnowledgeAdapter safety review
  scope.
- Product value, non-goals, task table, expected files, verification commands,
  and commit messages are explicit.
- No runtime implementation is added.

## Commit Message

```text
docs(v2): add mcp-ready tool knowledge safety plan
```

## Next Task

Slice 33 Task 2: Define MCP-ready ToolDefinition and KnowledgeAdapter safety
contracts.
