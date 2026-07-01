# V2 Scope Options

Date: 2026-06-30

## Purpose

This document lists candidate V2 directions after V1 acceptance. It is a
planning document, not implementation authorization.

V1 is accepted as a local-first AI testing evidence workbench. V2 should extend
that evidence loop deliberately, one small slice at a time, without turning
previous V1 non-goals into accidental default scope.

## V1 Baseline

Accepted V1 evidence:

- Release package: `docs/release/v1/README.md`
- Acceptance evidence: `docs/release/v1/acceptance-evidence.md`
- Manual walkthrough: `docs/release/v1/manual-walkthrough.md`
- Final handoff: `docs/implementation/08-v1-final-acceptance-handoff.md`

Current V1 automated gate:

- Backend golden release-acceptance suite: `10 passed`.
- Frontend workbench suite: `14` test files passed, `17 tests passed`.
- `git diff --check`: clean.

## V2 Progress

Completed V2 slices:

- `Slice 18: Newman API Execution`
- Plan and completion evidence:
  `docs/implementation/slices/slice-18-newman-api-execution.md`
- Final focused verification:
  - Newman API + golden tests: `5 passed`.
  - Frontend shell: `15` test files passed, `18` tests passed.
  - `git diff --check`: clean.

Slice 18 moved Candidate Direction B from option to delivered value. It added a
single allowlisted runner path without adding arbitrary shell, Postman parity,
remote CI/CD provider control, marketplace, RAG runtime, MCP runtime, RBAC,
tenants, or permissions.

- `Slice 19: Deterministic Knowledge Retrieval Stub`
- Plan and completion evidence:
  `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`
- Final focused verification:
  - Deterministic retrieval + requirement review + extension surface + golden
    smoke: `23 passed`.
  - Frontend shell: `15` test files passed, `19` tests passed.
  - `git diff --check`: clean.

Slice 19 moved Candidate Direction A from option to delivered value in a narrow
form. It added deterministic local ContextArtifact retrieval and evidence
display without adding a vector database, embeddings, reranking, external RAG
provider runtime, MCP runtime, RBAC, tenants, permissions, marketplace, cloud
sync, or remote CI/CD provider integration.

## Candidate Direction A: RAG Knowledge Runtime

Problem:

- V1 exposes RAG 知识库 as a ContextArtifact and KnowledgeAdapter management
  surface, but does not retrieve knowledge from a real index.

Candidate V2 value:

- Improve requirement review, case generation, and failure analysis with
  retrieved project knowledge while preserving evidence traceability.

Smallest slice:

- Add a local-only KnowledgeAdapter stub that can return deterministic matches
  from existing ContextArtifact text.
- Record retrieved artifact ids, snippets, and scores in AITask metadata.
- Keep vector database, external provider calls, reranking, and background
  indexing out until this deterministic slice is accepted.

Risks:

- Easy to overbuild into full search infrastructure.
- Evidence quality can degrade if retrieved snippets are not visible and
  reviewable.

Recommended only if:

- The next product priority is better AI context quality.

## Candidate Direction B: Tool And Runner Expansion

Problem:

- V1 supports pytest and Playwright evidence loops, with Newman/JMeter/Appium
  left as roadmap tools.

Candidate V2 value:

- Expand practical test execution coverage while preserving ToolDefinition
  allowlists and approval gates.

Smallest slice:

- Add one new runner path, preferably Newman API execution, because API tests
  are closer to existing command/artifact contracts than performance or mobile
  automation.
- Record stdout/stderr, report artifacts, command allowlist, and sandbox
  metadata.
- Add one golden smoke and one frontend shell update.

Risks:

- Tool execution can become arbitrary shell execution if allowlists are weak.
- Broad runner support can distract from evidence quality.

Recommended only if:

- The next product priority is broader daily testing workflow coverage.

## Candidate Direction C: Team Review And Governance

Problem:

- V1 is single-user and local-first. It has review states, but not team roles or
  enterprise governance.

Candidate V2 value:

- Add lightweight collaboration around review ownership without becoming a full
  enterprise RBAC platform.

Smallest slice:

- Add reviewer attribution and local review history for TestCase,
  AutomationDraft, UnitTestPatch, and QualityGateDecision.
- Keep tenants, roles, permissions, departments, SSO, and enterprise audit out
  until explicitly approved.

Risks:

- This can quickly become RBAC/tenant design work.
- Collaboration can conflict with the local-first product stance.

Recommended only if:

- The next product priority is team handoff and review accountability.

## Candidate Direction D: CI/CD Integration Bridge

Problem:

- V1 CI/CD Quality Center is local diff based and deliberately not a remote
  CI/CD provider integration.

Candidate V2 value:

- Let users import CI evidence while keeping Chtest as the evidence workbench,
  not a deployment system.

Smallest slice:

- Add import-only CI run metadata from a static JSON fixture or uploaded file.
- Map imported status, changed files, and artifacts into CICDRun evidence.
- Do not trigger remote pipelines, comment on PRs, deploy, or manage releases.

Risks:

- Remote authentication and provider APIs can consume the whole roadmap.
- PR comments and release automation would change the product boundary.

Recommended only if:

- The next product priority is connecting Chtest evidence to existing CI data.

## Recommended First V2 Slice

Recommended: Candidate Direction B, Newman API execution.

Why:

- It extends the existing runner/evidence architecture without requiring
  multi-user governance, vector infrastructure, or remote provider
  authentication.
- It fits the current ToolDefinition, TestCommand, TestRun, Artifact, Report,
  and frontend execution-center patterns.
- It gives visible user value while keeping scope small and testable.

First slice name:

```text
Slice 18: Newman API Execution
```

Suggested first task:

```text
V2 Task 2: Draft Slice 18 Newman API Execution plan
```

Expected output:

- A slice plan under `docs/implementation/slices/`.
- No product code until the plan defines models/APIs/artifacts/state
  boundaries.
- Verification command and non-goals listed before implementation starts.

## Still Out Of Scope Until Explicitly Promoted

- Full RAG platform, vector database, embeddings service, reranking service.
- MCP runtime, remote MCP calls, marketplace, or plugin installation.
- RBAC, tenants, departments, SSO, permissions, enterprise audit.
- Remote CI/CD provider control, PR comment bots, deployment automation,
  release automation.
- Broad dashboards, model leaderboard, or benchmark platform.
- Unapproved AI changes to business source files.

## Completed Next V2 Slice

Completed: Candidate Direction A, as a deterministic local KnowledgeAdapter
retrieval stub.

Why it was selected:

- Slice 18 expanded runner coverage. The next highest product value was
  improving AI context quality while keeping evidence visible and reviewable.
- V1 already had ContextArtifact, RAG 知识库, KnowledgeAdapter empty state, and
  AI task `context_artifact_ids`; the deterministic retrieval slice reused
  those contracts.
- The user-facing RAG 知识库 surface needed evidence-backed behavior, not a full
  RAG platform.

Completed slice name:

```text
Slice 19: Deterministic Knowledge Retrieval Stub
```

Smallest useful boundary:

- Search only existing ContextArtifact text/markdown/json/yaml records already
  allowed for prompt use.
- Use deterministic local matching, such as keyword overlap or exact term
  scoring.
- Record retrieved ContextArtifact ids, snippets, scores, and query terms in
  AITask metadata/artifacts.
- Show retrieved local context as evidence in the RAG 知识库 / AI task surfaces.
- Keep `used_knowledge=true` only for this deterministic local
  KnowledgeAdapter stub.

Explicit non-goals:

- No vector database.
- No embeddings service.
- No reranking service.
- No background indexing pipeline.
- No external RAG provider.
- No MCP runtime or remote MCP calls.
- No RBAC, tenants, permissions, marketplace, cloud sync, or remote CI/CD
  provider integration.

Completed first task:

```text
V2 Task 4: Draft Slice 19 Deterministic Knowledge Retrieval Stub plan
```

Delivered output:

- Slice plan, contract updates, backend deterministic retrieval service,
  requirement review evidence attachment, frontend evidence display, golden
  smoke, and completion gate.

## Recommended Next V2 Slice

Recommended: Candidate Direction D, but only as an import-only CI evidence
bridge.

Why:

- Slice 18 expanded local runner evidence and Slice 19 improved AI context
  evidence. The next practical value is connecting external CI facts into the
  existing evidence workbench without letting Chtest control remote providers.
- Slice 15 and Slice 16 already have CICDRun, CICDChangedFile,
  UnitTestPatch, QualityGateDecision, artifacts, and CI/CD 管理 surfaces that can
  receive imported evidence.
- Import-only CI metadata strengthens the CI/CD Quality Center while preserving
  the product boundary: evidence in, no remote actions out.

Next slice name:

```text
Slice 20: CI Run Metadata Import
```

Smallest useful boundary:

- Import static CI run JSON or an uploaded JSON payload handled locally.
- Map imported CI conclusion, changed files, refs, duration, and artifact
  references into CICDRun evidence.
- Store external artifact URLs as inert references only; do not fetch,
  authenticate, execute, mutate, or comment on remote systems.
- Treat imported CI status as evidence, not authority. It must not
  automatically pass QualityGateDecision.

Explicit non-goals:

- No remote CI provider API calls.
- No webhooks, pipeline triggers, reruns, PR comments, commit status updates,
  deploy, release, merge, push, tag, or scheduling.
- No provider credentials, OAuth, secrets, token storage, organization
  permissions, or broad provider parity.
- No RBAC, tenants, permissions, marketplace, RAG runtime, MCP runtime, cloud
  sync, or release automation.

Suggested next task:

```text
Slice 20 Task 1: Add CI Run Metadata Import task plan
```

Expected output:

- A slice plan under `docs/implementation/slices/`.
- No product code until contracts define the import payload, evidence artifacts,
  API boundary, state behavior, and non-goals.

## Next Task

Start Slice 20 Task 1 from
`docs/implementation/slices/slice-20-ci-run-metadata-import.md`.
