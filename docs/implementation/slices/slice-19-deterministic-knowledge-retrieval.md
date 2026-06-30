# Slice 19: Deterministic Knowledge Retrieval Stub Task Plan

## Goal

Add the first V2 knowledge-quality improvement without adding a full RAG
platform.

This slice adds a deterministic local KnowledgeAdapter stub that can retrieve
small, safe snippets from existing ContextArtifact records and attach the
retrieval evidence to AI tasks. It must reuse the current ContextArtifact,
AITask, Artifact, RAG 知识库, and KnowledgeAdapter surfaces. It must not add a
vector database, embeddings, reranking, background indexing, external RAG
provider calls, MCP runtime dependencies, RBAC, tenants, permissions, or
marketplace behavior.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `docs/implementation/slices/slice-18-newman-api-execution.md`

## Preconditions

- ContextArtifact is backed by Artifact rows.
- RAG 知识库 already lists ContextArtifact inventory and KnowledgeAdapter state.
- KnowledgeAdapterConfig exists as an empty/configuration surface.
- AI tasks can record `context_artifact_ids` and `used_context_artifact_ids`.
- Slice 18 is complete, so V2 can move from runner expansion to knowledge
  quality while preserving the local-first evidence boundary.

## Product Value Answer

After this slice, a test engineer can enable a deterministic local
KnowledgeAdapter stub and see which existing ContextArtifacts were matched,
which snippets were injected into an AI task, and why those snippets were
eligible. AI context becomes more useful and auditable without hidden vector
infrastructure, external providers, or opaque RAG behavior.

## Non-goals

- No vector database, embedding model, embedding service, semantic index, or
  ANN search.
- No reranking service, background indexing job, crawler, or document chunking
  pipeline.
- No external RAG provider, remote KnowledgeAdapter, cloud sync, or network
  retrieval.
- No MCP runtime dependency, remote MCP calls, plugin marketplace, or tool
  installation flow.
- No RBAC, tenants, organization permissions, SSO, or enterprise audit.
- No broad dashboard, benchmark platform, model leaderboard, or retrieval
  quality laboratory.
- No automatic trust in retrieved text; snippets remain evidence to display and
  review.

## Slice Boundary

- Retrieval reads only existing ContextArtifact records for the same project.
- Eligible ContextArtifacts must be safe to show and allowed for prompt use.
- Matching is deterministic and local, based on exact or normalized keyword
  overlap.
- Retrieval returns bounded snippets, scores, and matched terms.
- Retrieval evidence is recorded in AI task metadata and/or artifacts.
- `used_knowledge=true` is allowed only when the deterministic local
  KnowledgeAdapter stub contributes retrieved snippets.
- `used_context_artifact_ids` must list the exact ContextArtifacts used.
- The RAG 知识库 page should display retrieval status and latest usage evidence,
  not a vector-search UI.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Deterministic Knowledge Retrieval task plan | done | `test -f docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md` | `6bd7a76` | planning-only scope |
| Define deterministic retrieval contract boundary | done | `rg -n "Deterministic|KnowledgeAdapter|ContextArtifact|used_knowledge|retrieval" docs/contracts docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md` | pending commit | contract-only before code |
| Add local KnowledgeAdapter retrieval service | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py -q` | pending | deterministic matcher only |
| Attach retrieval evidence to AI task flows | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py -q` | pending | requirement review first |
| Add retrieval evidence frontend display | planned | `npm --prefix frontend run test -- --run` | pending | RAG 知识库 / AI task evidence |
| Add deterministic retrieval golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q` | pending | context -> retrieval -> AI task |
| Slice 19 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q && npm --prefix frontend run test -- --run` | pending | docs and handoff |

## Task 1: Add Deterministic Knowledge Retrieval Task Plan

Goal: Define the smallest useful local retrieval slice before implementation.

Expected files:

- `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
rg -n "Product Value Answer|Non-goals|Task Table|Deterministic|ContextArtifact|KnowledgeAdapter" docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
git diff --check
```

Acceptance:

- Creates the Slice 19 plan.
- Defines product value, non-goals, slice boundary, task table, expected files,
  and verification commands.
- Keeps the slice limited to deterministic local ContextArtifact retrieval.
- Does not add implementation code.

Commit message:

```text
docs(v2): add deterministic knowledge retrieval slice plan
```

## Task 2: Define Deterministic Retrieval Contract Boundary

Goal: Update contracts so local retrieval behavior is explicit before code.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "Deterministic|KnowledgeAdapter|ContextArtifact|used_knowledge|retrieval|retrieved" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
git diff --check
```

Acceptance:

- Contract defines deterministic local retrieval as a KnowledgeAdapter stub.
- Contract defines retrieved snippet evidence, scores, matched terms, and
  ContextArtifact ids.
- Contract explains when `used_knowledge=true` is allowed.
- Artifact contract defines retrieval evidence artifact shape.
- Non-goals still exclude vectors, embeddings, reranking, background indexing,
  external providers, MCP runtime, RBAC, tenants, and permissions.

Commit message:

```text
docs(v2): define deterministic retrieval contract
```

## Task 3: Add Local KnowledgeAdapter Retrieval Service

Goal: Implement deterministic matching over eligible ContextArtifacts.

Expected files:

- `backend/app/modules/extension/service.py`
- `backend/app/modules/extension/schemas.py`
- retrieval helper module if needed under `backend/app/modules/extension/`
- `backend/app/tests/api/test_deterministic_knowledge_retrieval.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py -q
```

Acceptance:

- Matches only ContextArtifacts for the same project.
- Requires `safe_to_show=true` and `allowed_for_prompt=true`.
- Uses deterministic local term matching with bounded result count.
- Returns snippet text, score, matched terms, and source ContextArtifact id.
- Does not create vector indexes, embeddings, reranking jobs, background
  workers, external provider calls, MCP calls, RBAC, tenants, or permissions.

Commit message:

```text
feat(extension): add deterministic knowledge retrieval
```

## Task 4: Attach Retrieval Evidence To AI Task Flows

Goal: Use the deterministic retrieval stub in the first AI workflow without
changing the broader AI runtime model.

Expected files:

- requirement review service/router/schema files needed for retrieval evidence
- AI runtime artifact helpers if needed
- `backend/app/tests/api/test_deterministic_knowledge_retrieval.py`
- focused existing requirement review tests when touched

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py -q
```

Acceptance:

- Requirement review can request local deterministic knowledge retrieval.
- AITask records `used_knowledge=true` only when retrieved snippets are used.
- AITask records exact `used_context_artifact_ids`.
- Retrieval evidence artifact includes query terms, matched terms, snippets,
  scores, and ContextArtifact ids.
- Existing explicit `context_artifact_ids` behavior remains unchanged when
  `use_knowledge=false`.
- No external RAG or MCP runtime is introduced.

Commit message:

```text
feat(ai): attach deterministic knowledge evidence
```

## Task 5: Add Retrieval Evidence Frontend Display

Goal: Make local retrieval evidence visible without adding a search product.

Expected files:

- `frontend/src/api/extension.ts`
- `frontend/src/stores/extension.ts`
- `frontend/src/views/extension/KnowledgeBaseView.vue`
- focused frontend tests for retrieval evidence display

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- RAG 知识库 shows deterministic retrieval status.
- ContextArtifact rows can show whether they were retrieved recently.
- The page shows latest matched terms/snippets/scores when available.
- UI remains Chinese-facing while preserving product terms such as
  ContextArtifact, KnowledgeAdapter, Prompt, Skill, and MCP-ready.
- No vector search controls, provider configuration, marketplace controls,
  RBAC, tenants, permissions, or remote sync controls are added.

Commit message:

```text
feat(frontend): show deterministic knowledge evidence
```

## Task 6: Add Deterministic Retrieval Golden Smoke

Goal: Prove local retrieval improves AI context while preserving evidence
traceability.

Expected files:

- `backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py`
- `docs/fixtures/08-deterministic-knowledge-retrieval-golden.md`
- `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
```

Acceptance:

- Creates safe ContextArtifacts with coupon/API knowledge.
- Runs a requirement review or equivalent AI task with deterministic retrieval
  enabled.
- Confirms retrieved ContextArtifact ids, snippets, scores, and matched terms
  are persisted as evidence.
- Confirms `used_knowledge=true` and `used_context_artifact_ids` are accurate.
- Confirms no vector/RAG provider/MCP/RBAC/tenant/permission dependency is
  introduced.

Commit message:

```text
test(v2): add deterministic knowledge retrieval golden
```

## Slice 19 Completion Gate

Goal: Validate all deterministic retrieval work and prepare the next V2 task.

Expected files:

- `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- All Slice 19 task rows are marked done with commit ids.
- Completion evidence records backend, golden, frontend, and diff verification.
- Handoff names the next V2 slice or planning task.
- Non-goals remain excluded.

Commit message:

```text
docs(v2): complete deterministic knowledge retrieval slice
```
