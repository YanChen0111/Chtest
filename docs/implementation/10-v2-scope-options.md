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

- `Slice 20: CI Run Metadata Import`
- Plan and completion evidence:
  `docs/implementation/slices/slice-20-ci-run-metadata-import.md`
- Final focused verification:
  - CI import API + golden tests: `54 passed`.
  - Frontend shell: `15` test files passed, `20` tests passed.
  - `git diff --check`: clean.

Slice 20 moved Candidate Direction D from option to delivered value in a narrow
form. It added import-only CI metadata evidence, imported changed files,
frontend-readable `ci_run_metadata`, and inert artifact references without
adding remote CI provider calls, webhooks, pipeline triggers, reruns, PR
comments, deploy/release controls, credentials, RBAC, tenants, permissions,
marketplace, RAG runtime, or MCP runtime.

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

## Future Candidate Direction E: Test Knowledge RAG And Agent System

Detailed strategy:

- `docs/implementation/11-final-rag-agent-strategy.md`

Problem:

- Slice 19 added deterministic local ContextArtifact retrieval evidence, but
  final Chtest needs knowledge-driven case generation and review, not a generic
  chat knowledge base.
- Test-case quality depends on testing knowledge: requirements, business
  rules, API constraints, boundary conditions, exception paths, historical
  defects, test strategy notes, accepted cases, rejected cases, and execution
  feedback.

Candidate final value:

- Generate test cases that cite exact knowledge evidence, cover explicit risks,
  expose coverage gaps, and pass agent/human review before entering the case
  library.
- Improve AI case-generation quality through a three-layer RAG design:
  structured test knowledge, hybrid retrieval, and later test relationship
  graph reasoning.

Recommended architecture:

```text
ContextArtifact / imported knowledge
  -> TestKnowledgeCard extraction
  -> structured + keyword + vector retrieval
  -> test relationship graph retrieval
  -> RiskAnalysisAgent
  -> TestDesignAgent
  -> CaseGenerationAgent
  -> CaseReviewAgent / CoverageGapAgent
  -> human review
  -> execution and report evidence
  -> KnowledgeFeedbackAgent
```

Open-source acceleration:

- Use PageIndex-style tree and section reasoning for traceable professional
  document retrieval.
- Use Haystack or LlamaIndex as the first external KnowledgeAdapter provider
  candidates.
- Use Microsoft GraphRAG later for offline/background relationship extraction
  and graph reasoning after Chtest has enough reviewed requirements, cases,
  failures, and reports.
- Use Awesome LLM Apps as reference examples only.
- Prefer library/API/provider integration over copying large open-source
  application code into Chtest.

Smallest future slice:

```text
Slice N: Test Knowledge Card Contract
```

Smallest useful boundary:

- Define `TestKnowledgeCard` and `KnowledgeEvidence` contracts.
- Define generated-case fields for evidence ids, risk coverage, generation
  reason, quality score, and review findings.
- Add one fixture showing requirement text, knowledge cards, generated case
  candidates, review findings, and evidence ids.
- Do not add vector database, embeddings, reranking, graph runtime, external
  provider calls, or frontend implementation in the planning task.

Risks:

- Full RAG/GraphRAG can become expensive to index, hard to tune, and hard to
  explain if evidence contracts are weak.
- Provider schemas can leak into Chtest if KnowledgeAdapter normalization is
  skipped.
- Case quality will not improve reliably without eval fixtures and human review
  feedback loops.

Recommended only if:

- The next product priority is materially improving AI-generated test-case
  quality through knowledge evidence, not adding another runner or display
  summary.

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

## Completed Next V2 Slice

Completed: Candidate Direction D, as an import-only CI evidence bridge.

Why it was selected:

- Slice 18 expanded local runner evidence and Slice 19 improved AI context
  evidence. The next practical value was connecting external CI facts into the
  existing evidence workbench without letting Chtest control remote providers.
- Slice 15 and Slice 16 already had CICDRun, CICDChangedFile,
  UnitTestPatch, QualityGateDecision, artifacts, and CI/CD 管理 surfaces that
  could receive imported evidence.
- Import-only CI metadata strengthened the CI/CD Quality Center while preserving
  the product boundary: evidence in, no remote actions out.

Completed slice name:

```text
Slice 20: CI Run Metadata Import
```

Delivered output:

- Slice plan, contract updates, deterministic parser, import API, frontend
  evidence display, golden smoke, and completion gate.
- Imported CI conclusion remains evidence only; it does not automatically pass
  QualityGateDecision.
- Imported artifact references are inert references only.

## Recommended Next V2 Slice

Recommended: Candidate Direction C, but renamed and narrowed to local review
attribution/history.

Why:

- Slice 18, Slice 19, and Slice 20 added more evidence sources. The next
  highest product value is making the human review side of that evidence loop
  more traceable.
- Chtest's core positioning is human-reviewed, evidence-backed testing work.
  Local attribution/history strengthens trust without requiring external tools.
- JMeter local execution evidence remains valuable and should stay a strong
  follow-up candidate, but it depends on another runner/tool path. Review
  attribution improves the existing workflows first and avoids immediate tool
  installation variability.

Next slice name:

```text
Slice 21: Local Review Attribution History
```

Smallest useful boundary:

- Add append-only local review events for existing review-gated workflows.
- Record entity, action, status transition, reviewer, comment, timestamp, and
  evidence artifact references.
- Use deterministic local reviewer attribution, such as `Default User`.
- Show compact review history in existing review surfaces.

Explicit non-goals:

- No RBAC, roles, permissions, tenants, departments, SSO, enterprise audit, or
  login/session redesign.
- No assignment workflow, approval delegation, notifications, team inbox, or
  comment threads.
- No remote CI provider governance, PR comments, deploy/release controls, or
  provider credentials.
- No RAG runtime, MCP runtime, marketplace, cloud sync, or release automation.

Suggested next task:

```text
Slice 21 Task 1: Add Local Review Attribution History task plan
```

Expected output:

- A slice plan under `docs/implementation/slices/`.
- No product code until contracts define review history data, API surface,
  state-machine relationship, and non-goals.

## Next Task

Start Slice 21 Task 1 from
`docs/implementation/slices/slice-21-local-review-attribution-history.md`.

## Completed Next V2 Slice

Completed: Candidate Direction C, as local review attribution/history.

Why it was selected:

- Slice 18, Slice 19, and Slice 20 added more evidence sources. The next highest
  product value was making the human review side of that evidence loop more
  traceable.
- Local review attribution/history strengthened trust in existing review-gated
  workflows without requiring team management, RBAC, tenants, permissions, or
  remote provider governance.
- JMeter local execution evidence remained a strong follow-up candidate after
  the review loop became traceable.

Completed slice name:

```text
Slice 21: Local Review Attribution History
```

Delivered output:

- Slice plan, contract updates, append-only ReviewHistory persistence, action
  hooks, frontend history panels, golden smoke, and completion gate.
- ReviewHistory remains local evidence only. It does not grant permissions,
  assign work, introduce team inboxes, or change approval authority.

## Recommended Next V2 Slice

Recommended: Candidate Direction B follow-up, narrowed to local JMeter execution
evidence.

Why:

- Slice 18 proved the controlled runner-expansion pattern with Newman. After
  Slice 19 knowledge evidence, Slice 20 CI import evidence, and Slice 21 review
  attribution, the next visible workflow value is another practical local
  runner.
- JMeter is already named in the roadmap as a later runner, and performance/API
  test evidence fits the existing TestCommand, ToolDefinition, TestRun,
  TestResult, Artifact, and frontend execution-center patterns.
- The slice can stay small if it is limited to non-GUI local execution and JTL
  parsing, with deterministic fake-runner tests instead of requiring a local
  JMeter installation.

Next slice name:

```text
Slice 22: JMeter Local Execution Evidence
```

Smallest useful boundary:

- Add `command_type=jmeter`, `runner_mode=jmeter_local`, and a JMeter
  ToolDefinition allowlist boundary.
- Execute only approved local non-GUI JMeter runs.
- Persist stdout/stderr, `jmeter_jtl`, parsed_result, and optional TestResult
  evidence.
- Add compact frontend display for status, sampler/assertion counts, durations,
  failures/errors, and artifact links.

Explicit non-goals:

- No JMX editor, recorder, parameterization UI, performance trend dashboard,
  capacity analysis, distributed JMeter, remote load agents, or cloud load
  testing.
- No arbitrary shell execution, unapproved working directory, shell operators,
  secrets manager, credentials vault, RBAC, tenants, permissions, or enterprise
  audit.
- No remote CI provider control, PR comments, deploy/release controls,
  automatic Report/FailureAnalysis/QualityGateDecision, RAG runtime, MCP
  runtime, marketplace, or cloud sync.

Suggested next task:

```text
Slice 22 Task 1: Add JMeter Local Execution Evidence task plan
```

Expected output:

- A slice plan under `docs/implementation/slices/`.
- No product code until contracts define command type, runner mode, artifact
  evidence, API/state behavior, and non-goals.

## Next Task

Start Slice 22 Task 1 from
`docs/implementation/slices/slice-22-jmeter-local-execution.md`.

## Completed Next V2 Slice

Completed: Candidate Direction B follow-up, as local JMeter execution evidence.

Why it was selected:

- Slice 18 proved controlled runner expansion with Newman. Slice 22 reused that
  evidence pattern for local JMeter non-GUI execution.
- JMeter evidence fits the existing TestCommand, ToolDefinition, TestRun,
  TestResult, Artifact, and frontend execution-center contracts.
- The slice stayed deterministic by using parser fixtures and fake JMeter
  executable tests instead of requiring a local JMeter installation.

Completed slice name:

```text
Slice 22: JMeter Local Execution Evidence
```

Delivered output:

- Slice plan, contract boundary, JTL parser, allowlisted local runner, frontend
  execution shell, golden smoke, and completion gate.
- JMeter remains local, allowlisted, non-GUI execution evidence only. It does
  not add a JMX editor, performance dashboard, distributed/cloud load testing,
  arbitrary shell execution, secrets, remote CI provider controls, RAG runtime,
  MCP runtime, RBAC, tenants, or permissions.

## Recommended Next V2 Slice

Recommended: Engineering quality follow-up, narrowed to restoring the frontend
build gate.

Why:

- Slice 22 frontend verification passed, but an extra `npm --prefix frontend run
  build` exposed existing TypeScript baseline errors outside the JMeter work.
- A passing build is product-enabling evidence: it lets future frontend slices
  rely on type checking instead of only Vitest.
- The work is small and verifiable if it is limited to TypeScript compile
  errors, not frontend redesign or product behavior changes.

Next slice name:

```text
Slice 23: Frontend Build Baseline
```

Smallest useful boundary:

- Fix the current `npm --prefix frontend run build` TypeScript failures.
- Keep existing runtime behavior and test expectations unchanged.
- Prefer narrow type/interface fixes over refactors.
- Verify with frontend build, frontend tests, and `git diff --check`.

Explicit non-goals:

- No product behavior changes.
- No new pages, backend APIs, migrations, runners, RAG runtime, MCP runtime,
  CI provider controls, RBAC, tenants, permissions, or marketplace work.
- No broad frontend redesign, design-system rewrite, package upgrade, or
  unrelated lint/style cleanup.

Suggested next task:

```text
Slice 23 Task 1: Add Frontend Build Baseline task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan captures the exact build failures, allowed
  files, verification command, and non-goals.

## Completed Next V2 Slice

Completed: Engineering quality follow-up, as the frontend build baseline.

Why it was selected:

- Slice 22 surfaced that frontend Vitest passed while the production build gate
  failed on existing TypeScript baseline issues.
- Restoring `npm --prefix frontend run build` made future frontend work safer
  without adding product scope.

Completed slice name:

```text
Slice 23: Frontend Build Baseline
```

Delivered output:

- Slice plan, narrow TypeScript fixes, restored frontend build verification,
  frontend test verification, and completion gate.
- No product behavior, backend API, package upgrade, redesign, RBAC, tenants,
  permissions, RAG runtime, MCP runtime, or CI provider control was added.

## Recommended Next V2 Slice

Recommended: Artifact evidence access links, narrowed to local TestRun artifact
read/download evidence.

Why:

- Recent runner slices now show artifact paths, but the execution surfaces do
  not yet prove that a reviewer can open the local evidence artifact from the
  workbench.
- Artifact access is central to Chtest's evidence-workbench value: stdout,
  stderr, parsed output, JTL, Newman JSON, traces, and screenshots should be
  inspectable through a controlled local API.
- This is a small cross-cutting product value improvement if limited to existing
  Artifact rows owned by TestRun and existing local artifact storage.

Next slice name:

```text
Slice 24: Local Artifact Access Links
```

Smallest useful boundary:

- Add a read-only local artifact content/download endpoint for existing
  Artifact rows.
- Add frontend artifact links in execution evidence tables for existing
  TestRun artifacts.
- Preserve artifact metadata display and existing table layout.
- Verify with one backend API test, one frontend execution-view test, and one
  golden smoke if needed.

Explicit non-goals:

- No cloud storage, signed URLs, sharing, upload UI, artifact mutation, delete,
  external provider fetch, remote CI artifact download, retention policy,
  indexing, search, RBAC, tenants, permissions, RAG runtime, MCP runtime, or
  marketplace work.
- No broad artifact browser or dashboard.
- No changes to runner execution behavior.

Suggested next task:

```text
Slice 24 Task 1: Add Local Artifact Access Links task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines endpoint boundaries, frontend link
  behavior, artifact ownership checks, verification, and non-goals.

## Completed Next V2 Slice

Completed: Artifact evidence access links, as read-only local TestRun artifact
links.

Why it was selected:

- Recent runner slices showed artifact paths, but reviewers could not yet open
  the local evidence artifact from the workbench.
- Slice 24 added the read-only local artifact access endpoint and execution
  table links while keeping external imported artifact references inert.
- The work strengthened stdout, stderr, parsed output, JTL, Newman JSON, traces,
  screenshots, and future runner evidence without adding cloud storage,
  sharing, upload, delete, RBAC, tenants, permissions, RAG runtime, MCP runtime,
  or runner behavior changes.

Completed slice name:

```text
Slice 24: Local Artifact Access Links
```

Delivered output:

- Slice plan, contract boundary, backend local artifact download API, frontend
  execution artifact links, golden smoke, and completion gate.
- Local artifact access remains read-only and local-first. It does not fetch
  external URLs, mutate artifacts, create reports, compute quality gates, or add
  broad artifact browsing.

## Recommended Next V2 Slice

Recommended: Execution evidence summary, narrowed to existing TestRun and
Report evidence.

Why:

- Slice 24 made artifacts openable. The next product value is explaining what
  those artifacts prove: which claim they support, whether evidence is required,
  whether it is missing, and whether the local artifact can be opened.
- Chtest's positioning is evidence-backed testing work, so a compact evidence
  summary strengthens the report/review loop without expanding into dashboards
  or analytics.
- Existing Report APIs already return `evidence_manifest` and report artifacts,
  so the slice can stay small and mostly frontend/contract driven.

Next slice name:

```text
Slice 25: Execution Evidence Summary
```

Smallest useful boundary:

- Define a read-only evidence summary shape from existing
  `ReportRead.evidence_manifest`, TestRun evidence, and Artifact metadata.
- Add a compact report-page evidence summary with local artifact links.
- Keep missing evidence visible and not downloadable.
- Add one golden smoke proving summary evidence cites persisted artifacts and
  artifact downloads preserve metadata.

Explicit non-goals:

- No report generation redesign, new report types, report editor, report
  dashboard, analytics, trend charts, or export workflow.
- No automatic Report, FailureAnalysis, QualityGateDecision, repair task, or
  runner behavior changes.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  retention, indexing, search, broad artifact browser, external provider fetch,
  credentials, RBAC, tenants, permissions, RAG runtime, MCP runtime,
  marketplace, or model benchmark.

Suggested next task:

```text
Slice 25 Task 1: Add Execution Evidence Summary task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines evidence summary behavior, contracts,
  verification, and non-goals.

## Completed Next V2 Slice

Completed: Execution evidence summary, narrowed to existing TestRun and Report
evidence.

Why it was selected:

- Slice 24 made artifacts openable. Slice 25 explained what those artifacts
  prove by aligning report evidence manifest rows, required flags, missing
  evidence, and local artifact links.
- The slice strengthened the evidence review loop without changing report
  generation, runner behavior, FailureAnalysis, QualityGateDecision, or artifact
  storage.

Completed slice name:

```text
Slice 25: Execution Evidence Summary
```

Delivered output:

- Slice plan, contract boundary, frontend report evidence summary rows, golden
  smoke, and completion gate.
- Evidence summary remains read-only and local-first. It does not auto-create
  reports, mutate artifacts, compute quality gates, add dashboard analytics, or
  fetch external provider data.

## Recommended Next V2 Slice

Recommended: CI imported artifact reference clarity.

Why:

- Slice 20 imported CI metadata and artifact references as inert evidence.
  Slice 24 and Slice 25 clarified local artifact access and evidence summary.
  The remaining readability gap is imported external artifact references: users
  should see that they are useful metadata but not locally downloaded evidence.
- The CI/CD Quality Center already renders imported references, so the smallest
  improvement is display clarity plus one inert-reference proof.
- This avoids remote provider integration while strengthening trust in the
  evidence boundary.

Next slice name:

```text
Slice 26: CI Imported Artifact Reference Clarity
```

Smallest useful boundary:

- Clarify contract language for imported artifact reference display.
- Show imported reference name, kind, external URL, inert status,
  `remote_fetch_performed=false`, and not-locally-openable status.
- Do not render local download links for external references.
- Add a golden smoke proving imported external references remain inert.

Explicit non-goals:

- No remote CI provider API calls, external artifact download, proxying,
  authentication, OAuth, credentials, webhooks, reruns, PR comments, commit
  statuses, deploy/release controls, or scheduling.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  broad artifact browser, QualityGateDecision behavior changes, TestRun,
  Report, FailureAnalysis, runner, RAG runtime, MCP runtime, marketplace, RBAC,
  tenants, or permissions work.

Suggested next task:

```text
Slice 26 Task 1: Add CI Imported Artifact Reference Clarity task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines display behavior, contracts,
  verification, and non-goals.

## Completed Next V2 Slice

Completed: CI imported artifact reference clarity.

Why it was selected:

- Slice 20 imported CI metadata and artifact references as inert evidence.
  Slice 24 and Slice 25 clarified local artifact access and evidence summary.
  Slice 26 closed the remaining readability gap by making external references
  clearly display-only, not locally openable, and not remotely fetched.

Completed slice name:

```text
Slice 26: CI Imported Artifact Reference Clarity
```

Delivered output:

- Slice plan, contract boundary, frontend imported reference clarity, golden
  smoke, and completion gate.
- Imported artifact references remain inert external metadata. They do not
  create local download links, remote fetches, TestRun, Report,
  FailureAnalysis, QualityGateDecision, runner behavior, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions.

## Recommended Next V2 Slice

Recommended: AI task evidence artifact links.

Why:

- Slice 24 made local TestRun artifacts openable. Slice 25 explained report
  evidence. Slice 26 clarified external CI artifact references. The remaining
  core evidence surface is AI Workbench: users can see AI task artifact
  metadata, but safe local artifacts are not yet directly openable from the
  task detail.
- Chtest's positioning requires every AI task to record prompt, skill, model,
  input/output artifacts, context artifacts, schema validation, and review or
  execution outcome. Making those safe evidence artifacts openable strengthens
  the AI review loop.
- The slice can stay small because AI task detail APIs already return Artifact
  metadata and Slice 24 already provides the local artifact access endpoint.

Next slice name:

```text
Slice 27: AI Task Evidence Artifact Links
```

Smallest useful boundary:

- Define read-only AI task evidence artifact links from existing Artifact
  metadata.
- Add AI Workbench "打开" links only for persisted local Artifact ids that are
  safe to open from the UI.
- Keep unsafe artifacts such as raw LLM output visible as metadata but not
  directly openable.
- Add one focused frontend test and one golden smoke proving the safe local
  evidence boundary.

Explicit non-goals:

- No inline raw LLM output display, prompt editor, prompt replay, AI task rerun,
  model/provider integration, streaming logs, schema editor, RAG runtime,
  vector database, embeddings, reranking, MCP runtime, marketplace, remote CI
  provider integration, RBAC, tenants, or permissions.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  broad artifact browser, indexing, search, dashboard, report generation,
  FailureAnalysis, QualityGateDecision, runner behavior, or package upgrades.

Suggested next task:

```text
Slice 27 Task 1: Add AI Task Evidence Artifact Links task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines safe artifact link behavior,
  contracts, verification, and non-goals.

## Completed Next V2 Slice

Completed: AI task evidence artifact links.

Why it was selected:

- Slice 24 made local TestRun artifacts openable, Slice 25 explained report
  evidence, and Slice 26 clarified external CI artifact references. Slice 27
  applied the same safe local evidence access pattern to AI Workbench.
- The slice strengthened the AI review loop by making safe AI task artifacts
  openable while keeping unsafe raw LLM output metadata-only.

Completed slice name:

```text
Slice 27: AI Task Evidence Artifact Links
```

Delivered output:

- Slice plan, contract boundary, frontend AI Workbench artifact links, golden
  smoke, and completion gate.
- Safe AI task artifacts can use local open links. Unsafe raw LLM artifacts
  remain metadata-only and no rerun, provider call, artifact mutation, RAG
  runtime, MCP runtime, RBAC, tenants, or permissions were added.

## Recommended Next V2 Slice

Recommended: CI/CD quality gate evidence summary.

Why:

- Slice 16 computes QualityGateDecision, but the CI/CD Quality Center mostly
  shows a gate status, summary, and ids. Users need to see which required
  evidence made the gate pass, fail, or need review.
- Slice 24 made local artifacts openable, and Slice 25 established the evidence
  summary pattern. Applying that pattern to quality gates improves the existing
  CI/CD support workflow without changing gate computation.
- The slice can stay small because QualityGateDecision already stores
  `blocking_reasons`, `status_detail`, and `evidence_artifact_ids`.

Next slice name:

```text
Slice 28: CI/CD Quality Gate Evidence Summary
```

Smallest useful boundary:

- Define a read-only quality gate evidence summary from existing
  QualityGateDecision fields and Artifact metadata.
- Show required evidence for UnitTestPatch, new-test, and regression in the
  CI/CD Quality Center quality gate panel.
- Keep missing evidence visible and not downloadable.
- Add local Artifact links only for persisted local Artifact ids.
- Add one focused frontend test and one golden smoke proving the summary is
  evidence-only.

Explicit non-goals:

- No QualityGateDecision computation changes, scoring model, risk analytics,
  dashboards, trends, automatic reports, FailureAnalysis behavior, runner
  behavior, or report generation behavior changes.
- No remote CI provider API calls, external artifact fetch, PR comments, commit
  statuses, reruns, deploy/release controls, credentials, OAuth, webhooks, or
  scheduling.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  broad artifact browser, indexing, search, RBAC, tenants, permissions, RAG
  runtime, MCP runtime, marketplace, or package upgrades.

Suggested next task:

```text
Slice 28 Task 1: Add CI/CD Quality Gate Evidence Summary task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines summary behavior, contracts,
  verification, and non-goals.

## Completed Next V2 Slice

Completed: CI/CD quality gate evidence summary.

Why it was selected:

- Slice 16 computed QualityGateDecision, but the CI/CD Quality Center needed
  clearer evidence readability for required evidence and blockers.
- Slice 28 applied the read-only evidence summary pattern from local artifact
  access and report evidence summaries to the quality gate panel.
- The slice improved CI/CD support workflow clarity without changing gate
  computation, runner behavior, report generation, or remote CI provider
  behavior.

Completed slice name:

```text
Slice 28: CI/CD Quality Gate Evidence Summary
```

Delivered output:

- Slice plan, contract boundary, frontend quality gate evidence summary, golden
  smoke, and completion gate.
- Missing UnitTestPatch, new-test, or regression evidence remains visible and
  returns `needs_review`, not `passed`.
- Local links are limited to persisted local Artifact ids; no remote provider,
  report, runner, RAG runtime, MCP runtime, RBAC, tenants, or permissions were
  added.

## Recommended Next V2 Slice

Recommended: Execution run manifest.

Why:

- Slices 24-28 made artifacts openable and evidence summaries readable across
  execution reports, AI tasks, imported CI evidence, and quality gates. The
  remaining execution-level readability gap is the TestRun itself: reviewers
  need to see what command ran, where it ran, which runner mode and safety
  policy applied, and which runtime/snapshot/output artifacts prove the run.
- `TestRunRead` already exposes command, working directory, runner mode,
  workspace, repository/network policy, snapshot ids, parsed result, and
  artifacts, so the next slice can stay presentation/contract driven.
- This strengthens the evidence workbench without adding new runners, runner
  behavior, remote providers, dashboards, or artifact storage scope.

Next slice name:

```text
Slice 29: Execution Run Manifest
```

Smallest useful boundary:

- Define a read-only execution run manifest from existing TestRun fields and
  Artifact metadata.
- Show command, working directory, runner mode, run workspace, repository
  read-only flag, network policy, runtime/dependency/environment snapshots, and
  output artifact availability.
- Add local links only for persisted local Artifact ids.
- Keep missing snapshots visible and not downloadable.
- Add one focused frontend test and one golden smoke proving the manifest is
  evidence-only.

Explicit non-goals:

- No runner behavior changes, command execution changes, ToolDefinition changes,
  allowlist expansion, new runner types, Docker runner enablement, live log
  streaming, scheduling, retries, or cancellation workflow.
- No report generation, FailureAnalysis, QualityGateDecision, AutomationRepair,
  artifact mutation, broad artifact browser, remote provider calls, PR comments,
  deploy/release controls, credentials, RBAC, tenants, permissions, RAG runtime,
  MCP runtime, marketplace, package upgrades, or frontend redesign.

Suggested next task:

```text
Slice 29 Task 1: Add Execution Run Manifest task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines run manifest behavior, contracts,
  verification, and non-goals.

## Completed Next V2 Slice

Completed: Execution run manifest.

Why it was selected:

- Slices 24-28 made artifacts openable and evidence summaries readable across
  reports, AI tasks, imported CI evidence, and quality gates. Slice 29 filled
  the remaining TestRun-level readability gap: command, working directory,
  runner mode, workspace, safety policy, snapshots, and output artifacts.
- The slice stayed evidence-only by using existing `TestRunRead` fields and
  existing Artifact metadata.

Completed slice name:

```text
Slice 29: Execution Run Manifest
```

Delivered output:

- Read-only execution run manifest contract and golden smoke.
- Pytest execution page run manifest panel.
- Local links remain limited to persisted local Artifact ids.
- Missing runtime/dependency/environment snapshots remain visible as
  unavailable evidence.
- No runner behavior changes, report generation, FailureAnalysis,
  QualityGateDecision, AutomationRepairTask, AutomationDraft behavior, artifact
  mutation, remote provider behavior, RAG runtime, MCP runtime, RBAC, tenants,
  or permissions were added.

## Recommended Next V2 Slice

Recommended: Execution run manifest parity.

Why:

- Slice 29 proved the run manifest behavior and added the first page-level
  implementation on the pytest execution page.
- Playwright, Newman, and JMeter pages already use `TestRunRead`, runner-specific
  evidence panels, and local artifact patterns, so the next smallest product
  improvement is parity rather than a new backend feature.
- This keeps the evidence workbench consistent across local runners without
  adding runner behavior, API changes, report behavior, remote provider scope,
  RAG runtime, MCP runtime, RBAC, tenants, or permissions.

Next slice name:

```text
Slice 30: Execution Run Manifest Parity
```

Smallest useful boundary:

- Add the compact execution run manifest panel to Playwright, Newman, and JMeter
  execution pages.
- Reuse Slice 29 rules for persisted local Artifact links and missing snapshot
  visibility.
- Keep runner-specific metrics as separate evidence, not a replacement for the
  manifest.
- Reuse the Slice 29 backend golden smoke as the evidence-only guard.

Explicit non-goals:

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No new runner types, Docker runner enablement, live log streaming,
  scheduling, retries, cancellation workflow, report generation,
  FailureAnalysis, QualityGateDecision, AutomationRepairTask, AutomationDraft
  behavior, artifact mutation, cloud storage, remote provider fetch, PR
  comments, RBAC, tenants, permissions, RAG runtime, MCP runtime, marketplace,
  package upgrades, or frontend redesign.

Suggested next task:

```text
Slice 30 Task 1: Add Execution Run Manifest Parity task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the parity plan defines expected files, verification,
  and non-goals.

## Completed Next V2 Slice

Completed: Execution run manifest parity.

Why it was selected:

- Slice 29 proved the run manifest behavior and added the pytest page panel.
- Slice 30 made Playwright, Newman, and JMeter execution pages show the same
  compact run context and artifact availability cues.
- The slice improved local runner evidence consistency without backend/API
  changes, runner behavior changes, remote provider behavior, RAG runtime, MCP
  runtime, RBAC, tenants, permissions, or frontend redesign.

Completed slice name:

```text
Slice 30: Execution Run Manifest Parity
```

Delivered output:

- Playwright, Newman, and JMeter execution run manifest panels.
- Focused frontend coverage for all three pages.
- Reuse of the Slice 29 backend run manifest golden smoke.
- Local links remain limited to persisted local Artifact ids.
- Missing runtime/snapshot/output evidence remains visible and not openable.

## Recommended Next V2 Slice

Recommended: Execution evidence availability labels.

Why:

- Slices 24-30 now expose evidence availability in several places, but the
  labels are still page-local strings and duplicated row-building logic.
- A tiny frontend-only label slice improves scanability and reduces drift
  without touching backend contracts, runner behavior, artifacts, fixtures,
  prompts, skills, or the currently dirty knowledge-card scope.
- The first implementation task can be a helper only, which is safer in the
  current worktree than reviving deleted contract/fixture chains.

Next slice name:

```text
Slice 31: Execution Evidence Availability Labels
```

Smallest useful boundary:

- Define frontend labels for local-openable, unavailable, external-reference,
  and metadata-only evidence states.
- Apply those labels to execution run manifest rows after the helper is proven.
- Preserve runner-specific metrics and artifact tables.
- Keep local open links derived only from persisted local Artifact ids.

Explicit non-goals:

- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, or knowledge-provider work.
- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No artifact upload, mutation, delete, cloud storage, remote provider fetch,
  report generation, FailureAnalysis, QualityGateDecision, RAG runtime, MCP
  runtime, marketplace, RBAC, tenants, permissions, package upgrades, or
  frontend redesign.

Suggested next task:

```text
Slice 31 Task 1: Add Execution Evidence Availability Labels task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines expected files, verification, and
  non-goals.

## Completed Next V2 Slice

Completed: Execution run manifest panel.

Why it was selected:

- Slice 32 centralized run manifest row semantics, but four execution pages
  still repeated the same panel template, table columns, slots, and scoped
  styles.
- Slice 33 extracted that display block into one shared frontend component.
- The slice stayed inside the safe execution frontend surface and avoided
  backend, contracts, fixtures, prompts, skills, and deleted knowledge-card
  scope.

Completed slice name:

```text
Slice 33: Execution Run Manifest Panel
```

Delivered output:

- `ExecutionRunManifestPanel.vue` and focused component coverage.
- Pytest, Playwright, Newman, and JMeter pages reuse the shared run manifest
  panel.
- Local links remain limited to persisted local Artifact ids.
- Missing runtime/snapshot/output evidence remains visible and not openable.

## Recommended Next V2 Slice

Recommended: Execution artifact table panel.

Why:

- Slice 33 removed the duplicated run manifest panel, leaving artifact table
  markup as the next obvious duplication in the same low-risk execution
  frontend surface.
- The artifact tables repeat local-open link slots and column definitions while
  pages still need to own runner-specific artifact filters.
- A small component extraction improves consistency without touching backend
  behavior, artifact storage, runner behavior, contracts, fixtures, prompts,
  skills, or deleted knowledge-card scope.

Next slice name:

```text
Slice 34: Execution Artifact Table Panel
```

Smallest useful boundary:

- Add a shared `ExecutionArtifactTable.vue` component.
- Pass each page's existing filtered artifact rows into the component.
- Keep runner-specific artifact filters, metrics, and result tables on the
  pages.
- Preserve local open links through the existing Artifact id download endpoint.

Explicit non-goals:

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  external artifact fetch, remote provider integration, broad artifact browser,
  indexing, search, dashboards, report generation, FailureAnalysis, or
  QualityGateDecision changes.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, RAG runtime, MCP runtime, marketplace, RBAC, tenants,
  permissions, package upgrades, or frontend redesign.

Suggested next task:

```text
Slice 34 Task 2: Add shared execution artifact table component
```

Expected output:

- A shared execution artifact table component and focused test.
- No execution page refactor until the component test passes.

## Completed Next V2 Slice

Completed: Execution run manifest helper.

Why it was selected:

- Slice 30 intentionally duplicated manifest panels to ship parity safely.
- Slice 31 standardized availability labels, but row construction still lived
  in four pages.
- Slice 32 centralized runtime, snapshot, and output artifact row construction
  while keeping runner-specific output definitions on each page.

Completed slice name:

```text
Slice 32: Execution Run Manifest Helper
```

Delivered output:

- `executionRunManifest` frontend helper and focused tests.
- Pytest, Playwright, Newman, and JMeter pages reuse shared row construction.
- Local links remain limited to persisted local Artifact ids.
- Missing runtime/snapshot/output evidence remains visible and not openable.

## Recommended Next V2 Slice

Recommended: Execution run manifest panel.

Why:

- Slice 32 centralized row semantics, but four execution pages still repeat the
  same panel template, table columns, slots, and scoped styles.
- A small component extraction removes display drift without changing page
  layout or runner-specific evidence.
- This stays within the safe frontend execution surface and avoids backend,
  contracts, fixtures, prompts, skills, and deleted knowledge-card scope.

Next slice name:

```text
Slice 33: Execution Run Manifest Panel
```

Smallest useful boundary:

- Add a shared `ExecutionRunManifestPanel.vue` component.
- Pass each page's existing `TestRunRead` and manifest rows into the component.
- Keep runner-specific output artifact definitions and metrics on the pages.
- Preserve local link and missing evidence behavior.

Explicit non-goals:

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, or knowledge-provider work.
- No artifact upload, mutation, delete, cloud storage, remote provider fetch,
  report generation, FailureAnalysis, QualityGateDecision, RAG runtime, MCP
  runtime, marketplace, RBAC, tenants, permissions, package upgrades, or
  frontend redesign.

Suggested next task:

```text
Slice 33 Task 1: Add Execution Run Manifest Panel task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines expected files, verification, and
  non-goals.

## Completed Next V2 Slice

Completed: Execution evidence availability labels.

Why it was selected:

- Slices 24-30 exposed evidence availability across multiple surfaces, but the
  labels were page-local strings and could drift.
- Slice 31 added a small frontend helper for local-openable, unavailable,
  external-reference, and metadata-only states.
- The slice improved evidence scanability without touching backend contracts,
  runner behavior, artifacts, fixtures, prompts, skills, or deleted
  knowledge-card scope.

Completed slice name:

```text
Slice 31: Execution Evidence Availability Labels
```

Delivered output:

- `evidenceAvailability` frontend helper and focused tests.
- Pytest, Playwright, Newman, and JMeter run manifest rows use the helper.
- Local links remain limited to persisted local Artifact ids.
- Missing runtime/snapshot/output evidence remains visible and not openable.

## Recommended Next V2 Slice

Recommended: Execution run manifest helper.

Why:

- Slice 30 intentionally duplicated manifest panels to ship parity safely.
- Slice 31 standardized availability labels, but four execution pages still
  duplicate manifest row construction, snapshot handling, runner mode labels,
  and output artifact lookup semantics.
- A small frontend helper removes real duplication while keeping page layouts
  and runner-specific evidence intact.

Next slice name:

```text
Slice 32: Execution Run Manifest Helper
```

Smallest useful boundary:

- Add a frontend helper that builds runtime, snapshot, and output artifact rows
  from existing `TestRunRead` data.
- Let each page pass its runner-specific output artifact definitions.
- Keep open links limited to persisted local Artifact ids.
- Keep missing evidence visible and not openable.

Explicit non-goals:

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, or knowledge-provider work.
- No artifact upload, mutation, delete, cloud storage, remote provider fetch,
  report generation, FailureAnalysis, QualityGateDecision, RAG runtime, MCP
  runtime, marketplace, RBAC, tenants, permissions, package upgrades, or
  frontend redesign.

Suggested next task:

```text
Slice 32 Task 1: Add Execution Run Manifest Helper task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines expected files, verification, and
  non-goals.

## Completed Next V2 Slice

Completed: Execution artifact table panel.

Why it was selected:

- Slice 33 extracted the run manifest panel, but four execution pages still
  repeated artifact table columns, local-open slots, and section styling.
- Slice 34 kept runner-specific artifact filters on each page while moving the
  read-only artifact display into one component.
- The slice stayed inside the frontend execution surface and avoided backend,
  contracts, fixtures, prompts, skills, and deleted knowledge-card scope.

Completed slice name:

```text
Slice 34: Execution Artifact Table Panel
```

Delivered output:

- `ExecutionArtifactTable` frontend component and focused tests.
- Pytest, Playwright, Newman, and JMeter pages reuse the shared artifact table.
- Local links remain limited to persisted local Artifact ids returned in
  `TestRunRead.artifacts`.
- No artifact upload, mutation, delete, remote fetch, cloud storage, broad
  artifact browser, backend/API behavior, RAG runtime, MCP runtime, RBAC,
  tenants, or permissions were added.

## Recommended Next V2 Slice

Recommended: Execution metrics panel.

Why:

- Slices 33 and 34 extracted the shared run manifest and artifact table display.
  The remaining smallest duplicated display block in the same pages is the
  metric tile template and scoped CSS.
- Each execution page already computes its own runner-specific metric items, so
  this slice can move only the display component without changing metric
  semantics.
- This keeps the work in the frontend execution safe area and avoids backend,
  contracts, fixtures, prompts, skills, and deleted knowledge-card scope.

Next slice name:

```text
Slice 35: Execution Metrics Panel
```

Smallest useful boundary:

- Add a shared `ExecutionMetricsPanel.vue` component.
- Pass each page's existing `metricItems` into the component.
- Keep runner-specific metric calculations on the pages.
- Preserve current labels, values, result tables, artifact filters, and
  execution start/refresh behavior.

Explicit non-goals:

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No metric calculation changes, parsed_result semantics changes, report
  generation, FailureAnalysis, QualityGateDecision, artifact behavior, RAG
  runtime, MCP runtime, marketplace, RBAC, tenants, permissions, package
  upgrades, or frontend redesign.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, or knowledge-provider work.

Suggested next task:

```text
Slice 35 Task 1: Add Execution Metrics Panel task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines expected files, verification, and
  non-goals.

## Completed Next V2 Slice

Completed: Execution metrics panel.

Why it was selected:

- Slices 33 and 34 extracted the shared run manifest and artifact table display,
  leaving metric tile markup and scoped styles repeated in four execution pages.
- Slice 35 kept runner-specific metric calculations on each page while moving
  only the display into one component.
- The slice stayed inside the frontend execution surface and avoided backend,
  contracts, fixtures, prompts, skills, and deleted knowledge-card scope.

Completed slice name:

```text
Slice 35: Execution Metrics Panel
```

Delivered output:

- `ExecutionMetricsPanel` frontend component and focused tests.
- Pytest, Playwright, Newman, and JMeter pages reuse the shared metrics panel.
- Runner-specific metric item computation remains page-owned.
- No metric calculation, parsed_result, backend/API behavior, runner behavior,
  report, quality gate, artifact behavior, RAG runtime, MCP runtime, RBAC,
  tenants, or permissions were changed.

## Recommended Next V2 Slice

Recommended: Execution result table panel.

Why:

- Slices 33-35 extracted the shared manifest, artifact table, and metric tile
  displays. The remaining smallest repeated display block in execution pages is
  the result section wrapper and table setup.
- Each execution page already owns its result columns and row shaping, so this
  slice can extract only the titled table section without changing runner
  result semantics.
- This continues the safe frontend execution cleanup and avoids backend,
  contracts, fixtures, prompts, skills, and deleted knowledge-card scope.

Next slice name:

```text
Slice 36: Execution Result Table Panel
```

Smallest useful boundary:

- Add a shared `ExecutionResultTable.vue` component.
- Pass each page's existing result title, columns, and rows into the component.
- Keep runner-specific result columns and row shaping on the pages.
- Preserve current result labels, values, row keys, artifact tables, metrics,
  and execution start/refresh behavior.

Explicit non-goals:

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No result data changes, result column changes, parsed_result semantics
  changes, metric calculation changes, report generation, FailureAnalysis,
  QualityGateDecision, artifact behavior, RAG runtime, MCP runtime,
  marketplace, RBAC, tenants, permissions, package upgrades, or frontend
  redesign.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, or knowledge-provider work.

Suggested next task:

```text
Slice 36 Task 1: Add Execution Result Table Panel task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines expected files, verification, and
  non-goals.

## Completed Next V2 Slice

Completed: Execution result table panel.

Why it was selected:

- Slices 33-35 extracted shared manifest, artifact table, and metric tile
  displays, leaving result section wrappers and table setup repeated in four
  execution pages.
- Slice 36 kept runner-specific result columns and row shaping on each page
  while moving only the titled table section into one component.
- The slice stayed inside the frontend execution surface and avoided backend,
  contracts, fixtures, prompts, skills, and deleted knowledge-card scope.

Completed slice name:

```text
Slice 36: Execution Result Table Panel
```

Delivered output:

- `ExecutionResultTable` frontend component and focused tests.
- Pytest, Playwright, Newman, and JMeter pages reuse the shared result table
  section.
- Runner-specific result columns and row shaping remain page-owned.
- No result data, parsed_result, backend/API behavior, runner behavior, report,
  quality gate, artifact behavior, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions were changed.

## Recommended Next V2 Slice

Recommended: Execution display helpers.

Why:

- Slices 33-36 extracted the repeated execution display components. The
  remaining low-risk duplication is pure display logic for run status and run
  duration labels.
- A helper extraction removes drift while avoiding page layout, form, runner,
  backend, contract, fixture, prompt, and skill scope.
- This is safer than extracting the whole page shell, which would have broader
  layout and interaction blast radius.

Next slice name:

```text
Slice 37: Execution Display Helpers
```

Smallest useful boundary:

- Add a shared `executionDisplay.ts` helper.
- Centralize existing run status labels and run duration labels.
- Keep JMeter-specific parsed JTL duration and result-row duration shaping on
  the JMeter page.
- Preserve current page layout, entry forms, result tables, metrics, artifact
  filters, and execution start/refresh behavior.

Explicit non-goals:

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No page layout extraction, entry form extraction, result data changes, result
  column changes, metric calculation changes, parsed_result semantics changes,
  artifact behavior, report generation, FailureAnalysis, QualityGateDecision,
  RAG runtime, MCP runtime, marketplace, RBAC, tenants, permissions, package
  upgrades, or frontend redesign.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, or knowledge-provider work.

Suggested next task:

```text
Slice 37 Task 1: Add Execution Display Helpers task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines expected files, verification, and
  non-goals.

## Completed Next V2 Slice

Completed: Execution display helpers.

Why it was selected:

- Slices 33-36 extracted repeated execution display components. The remaining
  low-risk duplication was pure display logic for run status and duration
  labels.
- Slice 37 centralized that display logic without changing page layout, forms,
  runner behavior, backend, contracts, fixtures, prompts, or skills.

Completed slice name:

```text
Slice 37: Execution Display Helpers
```

Delivered output:

- `executionDisplay` frontend helper and focused tests.
- Pytest, Playwright, Newman, and JMeter pages use shared run status and run
  duration labels.
- JMeter parsed JTL duration and result-row duration shaping remain page-owned.
- No page layout, form, result data, parsed_result, backend/API behavior,
  runner behavior, report, quality gate, artifact behavior, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions were changed.

## Recommended Next V2 Slice

Recommended: Execution output artifact definitions.

Why:

- Slice 32 centralized manifest row building, but pages still repeat output
  artifact definition arrays before calling the helper.
- A tiny constants module can remove label drift while preserving page-owned
  manifest calls, artifact filters, and runner-specific evidence behavior.
- This remains in the frontend execution safe area and avoids backend,
  contracts, fixtures, prompts, skills, and deleted knowledge-card scope.

Next slice name:

```text
Slice 38: Execution Output Artifact Definitions
```

Smallest useful boundary:

- Add shared output artifact definition constants.
- Keep existing output artifact ordering and labels for pytest, Playwright,
  Newman, and JMeter.
- Replace page-local output artifact arrays with shared constants.
- Preserve artifact lookup, artifact filtering, manifest row-building semantics,
  result tables, metrics, and execution start/refresh behavior.

Explicit non-goals:

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No artifact lookup changes, artifact filtering changes, artifact link
  behavior changes, run manifest row-building semantics changes, result data
  changes, metric calculation changes, report generation, FailureAnalysis,
  QualityGateDecision, RAG runtime, MCP runtime, marketplace, RBAC, tenants,
  permissions, package upgrades, or frontend redesign.
- No TestKnowledgeCard, generated case knowledge evidence, prompt, skill,
  contract, fixture, or knowledge-provider work.

Suggested next task:

```text
Slice 38 Task 1: Add Execution Output Artifact Definitions task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines expected files, verification, and
  non-goals.

## Completed Next V2 Slice

Completed: Execution output artifact definitions.

Why it was selected:

- Slice 32 centralized manifest row building, but pages still repeated output
  artifact definition arrays before calling the helper.
- Slice 38 removed that label drift while preserving page-owned manifest calls,
  artifact filters, and runner-specific evidence behavior.

Completed slice name:

```text
Slice 38: Execution Output Artifact Definitions
```

Delivered output:

- `executionOutputArtifacts` frontend constants and focused tests.
- Pytest, Playwright, Newman, and JMeter pages use shared manifest output
  artifact definitions.
- Existing output ordering and labels are preserved.
- No artifact lookup, artifact filtering, manifest row-building semantics,
  backend/API behavior, runner behavior, report, quality gate, artifact
  behavior, RAG runtime, MCP runtime, RBAC, tenants, or permissions were
  changed.

## Recommended Next V2 Slice

Recommended: Execution evidence link accessibility.

Why:

- Slice 34 added accessible labels to artifact table open links, but the shared
  run manifest panel still renders multiple identical `打开` links without
  row-specific labels.
- Adding `aria-label` and `title` to existing links improves evidence review
  accessibility without changing URLs, row availability rules, runner behavior,
  or page layout.

Next slice name:

```text
Slice 39: Execution Evidence Link Accessibility
```

Smallest useful boundary:

- Add row-specific accessible labels to run manifest open links.
- Keep visible link text, href generation, row availability rules, and table
  layout unchanged.
- Add focused component assertions.

Explicit non-goals:

- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No artifact lookup changes, artifact filtering changes, artifact URL changes,
  run manifest row-building semantics changes, result data changes, report
  generation, FailureAnalysis, QualityGateDecision, page shell/form refactor,
  RAG runtime, MCP runtime, marketplace, RBAC, tenants, permissions, package
  upgrades, or frontend redesign.

Suggested next task:

```text
Slice 39 Task 1: Add Execution Evidence Link Accessibility task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines expected files, verification, and
  non-goals.

## Completed Next V2 Slice

Completed: Execution evidence link accessibility.

Why it was selected:

- Slice 34 added accessible labels to artifact table open links, but the shared
  run manifest panel still rendered multiple identical compact open links
  without row-specific labels.
- Slice 39 improved evidence review accessibility while preserving visible link
  text, local artifact URLs, row availability rules, runner behavior, and page
  layout.

Completed slice name:

```text
Slice 39: Execution Evidence Link Accessibility
```

Delivered output:

- `ExecutionRunManifestPanel.vue` now adds row-specific `aria-label` and
  `title` attributes to local evidence open links.
- `ExecutionRunManifestPanel.spec.ts` covers the accessible link labels while
  preserving compact visible text.
- No artifact lookup, artifact URL, manifest row-building, backend/API
  behavior, runner behavior, report, quality gate, RAG runtime, MCP runtime,
  RBAC, tenants, or permissions were changed.

## Recommended Next V2 Slice

Recommended: select a new narrow V2 task deliberately, or explicitly promote
execution page shell/form refactor scope.

Why:

- Slices 30-39 exhausted the small, low-risk execution-page cleanup tasks around
  run manifest parity, evidence labels, shared display components, display
  helpers, output artifact definitions, and link accessibility.
- The remaining execution-page duplication is mostly page shell, layout, and
  entry-form structure, which has a broader interaction and regression surface
  than the completed component/helper slices.
- Continuing automatically would blur the V2 scope boundary and risk mixing a
  broad frontend refactor with the unrelated dirty knowledge-card/prompt/skill
  deletion chain currently present in the worktree.

Next slice name:

```text
TBD: deliberate V2 scope selection
```

Smallest useful boundary:

- Before selecting the next product-code task, path-limit review/stage/commit
  the Slice 39 implementation and handoff files, or explicitly document why
  Slice 39 remains uncommitted.
- Pick one product-value task before editing product code.
- If the next task is execution page shell/form cleanup, first add a dedicated
  slice plan with expected files, verification, non-goals, and page-level
  regression coverage.
- Otherwise choose a new narrow V2 task outside the automatic execution cleanup
  thread.

Explicit non-goals:

- No automatic page shell/form refactor.
- No broad staging or commit across the unrelated dirty worktree.
- No backend feature code, migrations, API shape changes, runner behavior
  changes, command assembly changes, ToolDefinition changes, or allowlist
  expansion.
- No artifact upload, mutation, delete, sharing, signed URLs, cloud storage,
  external provider integration, broad artifact browser, report generation,
  FailureAnalysis, QualityGateDecision, RAG runtime, MCP runtime, marketplace,
  RBAC, tenants, permissions, package upgrades, or frontend redesign unless
  explicitly selected as a new task.

Suggested next task:

```text
Scope selection: choose the next narrow V2 task or explicitly promote execution page shell/form refactor.
```

Expected output:

- A deliberate next task in `NEXT_AI_TASK.md`.
- No product code until the next task defines expected files, verification, and
  non-goals.
