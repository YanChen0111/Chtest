# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 33: MCP-Ready ToolDefinition And KnowledgeAdapter Safety Contract.

## Current Task

Slice 33 Task 2: Define MCP-ready ToolDefinition and KnowledgeAdapter safety
contracts.

## Product Value Answer

After this task, Chtest has explicit data, API, state-machine, and artifact
contracts for MCP-ready ToolDefinition and KnowledgeAdapter safety before any
MCP runtime or external provider implementation exists.

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
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract-only task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, external provider integrations, vector database,
embeddings, reranking, background indexing, graph runtime, MCP runtime, MCP
server/client transport, provider SDK, credentials, TestKnowledgeCard CRUD,
artifact upload/mutation/delete, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior, RBAC,
tenants, or permissions.

## Verification Command

```bash
rg -n "ToolDefinition safety|KnowledgeAdapter safety|approval_required|artifact_policy|provider_state|disabled|unhealthy|MCP runtime" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md
git diff --check
```

Expected result: safety contract terms are present across contracts and diff
check passes.

## Acceptance

- Contracts define ToolDefinition strict schema, risk, approval, timeout, and
  artifact policy fields.
- Contracts define ToolInvocation approval/status/failure/artifact behavior.
- Contracts define KnowledgeAdapter provider-state and fallback behavior.
- Contracts forbid MCP runtime, provider SDK, credentials, external calls,
  provider schema leakage, review bypass, and auto-promotion.

## Commit Message

```text
docs(v2): define mcp-ready tool knowledge safety contracts
```

## Next Task

Slice 33 Task 3: Add MCP-ready tool/knowledge safety golden smoke.
