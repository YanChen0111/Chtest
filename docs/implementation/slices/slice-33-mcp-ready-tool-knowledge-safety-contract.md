# Slice 33: MCP-Ready ToolDefinition And KnowledgeAdapter Safety Contract Task Plan

## Goal

Define the MCP-ready ToolDefinition and KnowledgeAdapter safety contract before
any MCP runtime, external retrieval provider, or provider SDK exists.

This slice is contract-first. It documents the schema, risk, approval, timeout,
artifact, provider-state, fallback, and review boundaries that future tool and
knowledge integrations must obey.

## Product Value Answer

After this slice, Chtest can evaluate future local tools, MCP tools, and
KnowledgeAdapter providers against one visible safety contract. Users get a
clear guarantee that tool access and knowledge retrieval cannot bypass approval,
artifact persistence, review gates, or provider-output normalization.

## Current Evidence Baseline

- `ToolDefinition`, `ToolInvocation`, `Artifact`, and
  `KnowledgeAdapterConfig` are already named in data/API contracts.
- V2 Slice 19 added deterministic local KnowledgeAdapter retrieval evidence.
- V2 Slice 30 and Slice 31 established `KnowledgeEvidence` and generated-case
  evidence persistence.
- Slice 32 defined the requirement-to-reviewed-case agent workflow contract
  without adding runtime orchestration.
- `docs/implementation/11-final-rag-agent-strategy.md` states that MCP is a
  tool access layer, not an orchestrator or RAG product.

## Non-goals

- No MCP runtime, MCP server/client transport, remote MCP calls, marketplace,
  plugin install, or external tool execution.
- No external KnowledgeAdapter provider implementation, provider SDK,
  provider credentials, OAuth, API keys, remote URL fetch, vector database,
  embeddings, reranking, background indexing, graph runtime, or GraphRAG job.
- No backend feature API, migration, frontend page, package upgrade, runner
  behavior change, report behavior change, TestRun behavior change, or
  ToolInvocation execution behavior change.
- No TestKnowledgeCard CRUD, artifact upload/mutation/delete, generated-case
  auto-approval, TestCase auto-promotion, RBAC, tenants, permissions, cloud
  sync, or remote CI/CD provider behavior.

## Contract Boundary To Define

The follow-up contract task should define:

- ToolDefinition schema rules:
  - strict JSON input/output schema references;
  - tool name, category, risk level, approval requirement, timeout, and artifact
    policy;
  - local-tool and future MCP-tool compatibility fields;
  - disabled/configured/unhealthy readiness without transport controls.
- ToolInvocation safety rules:
  - approval status and human gate for medium/high-risk tools;
  - status transitions and failure codes;
  - artifact creation and retention expectations;
  - no hidden execution, no report conclusion, and no review bypass.
- KnowledgeAdapter safety rules:
  - allowed provider states such as `none`, `stub`, and
    `deterministic_local`;
  - future disabled/configured/unhealthy provider states;
  - provider output must normalize into `KnowledgeEvidence` before use;
  - unavailable providers degrade to local/no-knowledge flows without blocking
    core review.
- Artifact and evidence rules:
  - every future tool or provider result must create bounded artifacts or
    normalized evidence refs;
  - raw provider payload, credentials, secrets, and transport details must not
    leak into generated cases or review surfaces;
  - high-risk operations require reviewable evidence before any downstream
    workflow consumes their output.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add MCP-ready tool/knowledge safety task plan | done | `test -f docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md && rg -n "MCP-Ready ToolDefinition|KnowledgeAdapter|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md NEXT_AI_TASK.md && git diff --check` | pending | planning-only scope |
| Define MCP-ready ToolDefinition and KnowledgeAdapter safety contracts | planned | `rg -n "ToolDefinition safety|KnowledgeAdapter safety|approval_required|artifact_policy|provider_state|disabled|unhealthy|MCP runtime" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md && git diff --check` | pending | contract-only |
| Add MCP-ready tool/knowledge safety golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py -q && git diff --check` | pending | no runtime/provider behavior |
| Slice 33 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py backend/app/tests/golden/test_agent_workflow_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add MCP-Ready Tool/Knowledge Safety Task Plan

Goal: Create a narrow plan for ToolDefinition and KnowledgeAdapter safety before
contract edits or runtime implementation.

Expected files:

- `docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md
rg -n "MCP-Ready ToolDefinition|KnowledgeAdapter|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 33 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names ToolDefinition, ToolInvocation, KnowledgeAdapterConfig,
  KnowledgeEvidence, Artifact, approval, risk, timeout, artifact policy,
  provider state, fallback, and MCP runtime boundaries.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add mcp-ready tool knowledge safety plan
```

## Task 2: Define MCP-Ready ToolDefinition And KnowledgeAdapter Safety Contracts

Goal: Update data, API, state-machine, and artifact contracts with the exact
safety rules for future local tools, MCP tools, and KnowledgeAdapter providers.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "ToolDefinition safety|KnowledgeAdapter safety|approval_required|artifact_policy|provider_state|disabled|unhealthy|MCP runtime" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md
git diff --check
```

Acceptance:

- Contracts define ToolDefinition strict schema, risk, approval, timeout, and
  artifact policy fields.
- Contracts define ToolInvocation approval/status/failure/artifact behavior.
- Contracts define KnowledgeAdapter provider-state and fallback behavior.
- Contracts forbid MCP runtime, provider SDK, credentials, external calls,
  provider schema leakage, review bypass, and auto-promotion.

Commit message:

```text
docs(v2): define mcp-ready tool knowledge safety contracts
```

## Task 3: Add MCP-Ready Tool/Knowledge Safety Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving the safety contract
can be checked without executing tools, calling providers, or starting MCP.

Expected files:

- `backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py`
- `docs/fixtures/21-mcp-ready-tool-knowledge-safety-golden.md`
- `docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names ToolDefinition, ToolInvocation, KnowledgeAdapterConfig,
  KnowledgeEvidence, Artifact, approval, risk, timeout, artifact policy,
  provider state, fallback, and human gate boundaries.
- Golden proves no MCP runtime, external provider call, credentials, vector
  index, graph job, report conclusion, review bypass, artifact mutation, or
  auto-promotion is created by the contract.

Commit message:

```text
test(golden): add mcp-ready tool knowledge safety smoke
```

## Slice 33 Completion Gate

Goal: Validate Slice 33 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py backend/app/tests/golden/test_agent_workflow_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 33 task table records completed task commits.
- Focused golden verification passes.
- `NEXT_AI_TASK.md` points to the next narrow V2 task.

Commit message:

```text
docs(v2): complete mcp-ready tool knowledge safety slice
```
