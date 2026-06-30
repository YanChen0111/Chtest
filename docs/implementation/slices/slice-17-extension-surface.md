# Slice 17: Extension Surface Task Plan

## Goal

Add the V1 extension surface without adding runtime-heavy extension
infrastructure.

This slice covers the RAG 知识库 page surface, ContextArtifact usage display,
KnowledgeAdapter empty interface/state, ToolDefinition schema boundaries, and
MCP-ready design metadata. It must not add built-in RAG indexing, vector
storage, embeddings, reranking, MCP runtime dependencies, RBAC, tenants,
permissions, plugin marketplace, cloud sync, or broad dashboards.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/product/03-user-journey-and-page-prd.md`
- `docs/product/05-non-goals-and-version-boundaries.md`
- `docs/product/06-frontend-ui-guidelines.md`
- `docs/product/08-frontend-design-spec.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`

## Preconditions

- ContextArtifact is backed by the Artifact table.
- AITask records can reference `context_artifact_ids`.
- ToolDefinition and ToolInvocation contracts already exist.
- V1 remains single-user and local-first.

## Product Value Answer

After this slice, Chtest can show where project knowledge comes from, whether it
is safe to use, how it was attached to AI tasks, and which future extension
points exist. Users get a visible RAG 知识库 surface and MCP-ready tool schema
without the cost or risk of a real RAG/MCP runtime in V1.

## Non-goals

- No built-in vector database, chunking, embeddings, indexing, retrieval, or
  reranking.
- No external KnowledgeAdapter runtime dependency.
- No MCP server/client runtime dependency.
- No plugin marketplace, remote tool catalog, or cloud sync.
- No RBAC, tenants, organization permissions, or enterprise audit.
- No broad dashboard or roadmap-only integration UI.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Extension Surface task plan | done | `test -f docs/implementation/slices/slice-17-extension-surface.md && rg -n "KnowledgeAdapter|RAG 知识库|MCP-ready|Non-goals" docs/implementation/slices/slice-17-extension-surface.md` | `73a1885` | planning-only scope |
| Add Extension Surface contract boundary | done | `rg -n "KnowledgeAdapter|RAG 知识库|ToolDefinition|MCP-ready|Non-goals" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-17-extension-surface.md` | `f2812cf` | contract-only boundary |
| Add KnowledgeAdapter empty interface/schema | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q` | `afffbc9` | no retrieval runtime |
| Add RAG 知识库 ContextArtifact API shell | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q` | pending commit | project context management surface |
| Add MCP-ready ToolDefinition schema metadata | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q` | pending commit | schema only, no MCP runtime |
| Add RAG 知识库 frontend shell | done | `npm --prefix frontend run test -- --run` | pending commit | light workbench UI |
| Add Extension Surface golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_extension_surface_golden.py -q` | - | context -> AI task -> evidence |
| Slice 17 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_extension_surface_golden.py -q && npm --prefix frontend run test -- --run` | - | docs and handoff only |

## Task 2: Add Extension Surface Contract Boundary

Goal: Tighten the Slice 17 contract before implementation.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "KnowledgeAdapter|RAG 知识库|ToolDefinition|MCP-ready|Non-goals" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-17-extension-surface.md
```

Acceptance:

- Contract names the RAG 知识库 page as a ContextArtifact management and usage
  display surface.
- Contract defines KnowledgeAdapter as an empty interface/configuration state in
  V1, not a retrieval runtime.
- Contract defines MCP-ready ToolDefinition metadata while keeping ToolAdapter
  allowlist safety as the executable boundary.
- Contract keeps RAG runtime, MCP runtime dependency, RBAC, tenants, and
  permissions out of scope.

Commit message:

```text
docs(extension): define extension surface boundary
```

## Task 3: Add KnowledgeAdapter Empty Interface Schema

Goal: Add backend schema and persisted state for future KnowledgeAdapter
configuration without retrieval behavior.

Expected files:

- `backend/app/modules/extension/models.py`
- `backend/app/modules/extension/schemas.py`
- `backend/app/modules/extension/router.py`
- `backend/app/modules/extension/service.py`
- `backend/app/tests/api/test_extension_surface.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
```

Acceptance:

- Provides an empty KnowledgeAdapter read model or configuration state for a
  project.
- Records status such as `not_configured`, `disabled`, or `configured_stub`.
- Returns `used_knowledge=false` unless a future runtime explicitly implements
  retrieval.
- Does not call external RAG providers, create vector indexes, embed content, or
  rank search results.

Commit message:

```text
feat(extension): add knowledge adapter shell
```

## Task 4: Add RAG 知识库 ContextArtifact API Shell

Goal: Expose a focused RAG 知识库 backend surface backed by ContextArtifact
records.

Expected files:

- `backend/app/modules/extension/router.py`
- `backend/app/modules/extension/service.py`
- `backend/app/modules/extension/schemas.py`
- `backend/app/tests/api/test_extension_surface.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
```

Acceptance:

- Lists project ContextArtifacts with title, source, MIME type, redaction, and
  prompt eligibility metadata.
- Shows AI task usage references when available.
- Reuses existing ContextArtifact creation/list contracts.
- Does not create a separate ContextArtifact table.
- Does not perform semantic search or external retrieval.

Commit message:

```text
feat(extension): add knowledge context api
```

## Task 5: Add MCP-ready ToolDefinition Schema Metadata

Goal: Make ToolDefinition records ready for later MCP exposure while retaining
the internal Tool Adapter execution boundary.

Expected files:

- `backend/app/modules/extension/router.py`
- `backend/app/modules/extension/service.py`
- `backend/app/modules/extension/schemas.py`
- `backend/app/tests/api/test_extension_surface.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
```

Acceptance:

- Exposes ToolDefinition input/output schema, risk level, approval requirement,
  artifact policy, and allowlist metadata.
- Allows `tool_type=mcp_proxy` as schema intent only.
- Requires ToolInvocation to keep using allowlisted internal execution rules.
- Does not add MCP server/client packages or runtime calls.

Commit message:

```text
feat(extension): add mcp ready tool schema
```

## Task 6: Add RAG 知识库 Frontend Shell

Goal: Add the visible V1 RAG 知识库 page for context and extension state.

Expected files:

- `frontend/src/api/extension.ts`
- `frontend/src/stores/extension.ts`
- `frontend/src/views/extension/KnowledgeBaseView.vue`
- `frontend/src/views/extension/KnowledgeBaseView.spec.ts`
- navigation files needed to expose the page

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- Uses a light workbench UI aligned with the final Chtest frontend direction.
- Shows ContextArtifact inventory, safety metadata, prompt eligibility, and AI
  usage references.
- Shows KnowledgeAdapter configuration as empty/not configured state.
- Shows MCP-ready ToolDefinition schema/readiness without executable MCP
  controls.
- Does not add RBAC, tenant, marketplace, cloud sync, vector search, or runtime
  provider controls.

Commit message:

```text
feat(frontend): add knowledge base shell
```

## Task 7: Add Extension Surface Golden Smoke

Goal: Prove the extension surface supports the V1 evidence loop without hidden
runtime infrastructure.

Expected files:

- `backend/app/tests/golden/test_extension_surface_golden.py`
- `docs/fixtures/06-extension-surface-golden.md`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_extension_surface_golden.py -q
```

Acceptance:

- Creates or references ContextArtifacts as project knowledge.
- Runs an AI task that records `used_context_artifact_ids`.
- Confirms `used_knowledge=false` while KnowledgeAdapter remains empty.
- Confirms ToolDefinition schema metadata is visible but no MCP runtime executes.
- Confirms no vector/RAG/MCP/RBAC/tenant/permission tables or dependencies are
  introduced.

Commit message:

```text
test(extension): add extension surface golden smoke
```

## Slice 17 Completion Gate

Goal: Validate all Extension Surface work and prepare the next V1 task.

Expected files:

- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_extension_surface_golden.py -q && npm --prefix frontend run test -- --run
```

Acceptance:

- All Slice 17 task rows are marked done with commit ids.
- Completion evidence records backend, golden, and frontend verification.
- Handoff names the next V1 slice or completion task.
- Non-goals remain excluded.

Commit message:

```text
docs(extension): complete extension surface slice
```
