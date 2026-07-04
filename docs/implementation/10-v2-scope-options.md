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

Status: long-term final-version direction. This section does not authorize a
RAG runtime, vector database, GraphRAG runtime, MCP runtime, external provider
call, or generated-case auto-approval in the current slice.

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
- Improve AI case-generation quality through a three-tier testing-knowledge
  capability: structured test knowledge evidence, optional hybrid retrieval,
  and later test relationship graph reasoning.

Recommended architecture:

```text
ContextArtifact / imported knowledge
  -> TestKnowledgeCard extraction
  -> structured evidence filtering
  -> optional keyword/full-text/vector retrieval
  -> optional offline test relationship graph retrieval
  -> RiskAnalysisAgent
  -> TestDesignAgent
  -> CaseGenerationAgent
  -> CaseReviewAgent / CoverageGapAgent
  -> human review
  -> execution and report evidence
  -> KnowledgeFeedbackAgent
```

AI workflow planning:

- Split the future AI flow across focused agents instead of one broad case
  generation prompt.
- Define Agent, PromptVersion, SkillVersion, input evidence, output artifact,
  write permission, human gate, failure behavior, and metrics before
  implementation.
- Keep Agent orchestration independent from provider schemas. Provider output
  must normalize into Chtest `KnowledgeEvidence`.
- Keep MCP as a ToolDefinition-compatible transport layer. MCP must not bypass
  approval, Artifact persistence, ToolInvocation status, Prompt/Skill version
  tracking, or review gates.

Prompt/Skill work that can be planned early:

- knowledge card extraction.
- requirement understanding.
- risk analysis.
- coverage analysis.
- test design.
- evidence-backed case generation.
- evidence-backed case review.
- case dedup.
- automation readiness.
- knowledge feedback.

Open-source acceleration:

- Use structure-aware document retrieval ideas for traceable professional
  documents.
- Use Haystack or LlamaIndex as the first external KnowledgeAdapter provider
  candidates.
- Use Microsoft GraphRAG later for offline/background relationship extraction
  and graph reasoning after Chtest has enough reviewed requirements, cases,
  failures, and reports.
- Use RAGFlow only as an external provider/service reference, not as Chtest's
  internal product shell.
- Use pgvector first if semantic retrieval is needed; use Qdrant only if scale
  exceeds PostgreSQL.
- Prefer library/API/provider integration over copying large open-source
  application code into Chtest.
- Keep the canonical source list in
  `docs/reference/01-open-source-migration-map.md`.

Optimization rules:

- L1 `TestKnowledgeCard` + `KnowledgeEvidence` is the core product capability.
- L2 hybrid retrieval is optional and must be promoted by eval evidence, not by
  architecture preference.
- L3 graph reasoning is offline/background and must not block case generation.
- Every provider result must normalize into Chtest evidence before use.
- Core workflows must keep working when external retrieval is disabled or
  unavailable.

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

Recommended follow-up documentation slices:

1. Evidence-backed generated case contract.
2. Agent workflow contract for requirement-to-reviewed-case.
3. Prompt/Skill draft contracts for knowledge extraction and evidence-backed
   review.
4. MCP-ready ToolDefinition and KnowledgeAdapter safety boundary review.
5. Provider evaluation plan for Haystack or LlamaIndex after local evidence
   contracts pass golden fixtures.

Risks:

- Full RAG/GraphRAG can become expensive to index, hard to tune, and hard to
  explain if evidence contracts are weak.
- Provider schemas can leak into Chtest if KnowledgeAdapter normalization is
  skipped.
- Case quality will not improve reliably without eval fixtures and human review
  feedback loops.
- Open-source references can expand scope if future AI sessions copy platform
  features instead of migrating only the testing-quality capability.

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
  execution reports, AI tasks, imported CI evidence, and quality gates.
- Slice 29 closed the remaining execution-level readability gap by explaining
  the TestRun itself: command, working directory, runner mode, workspace,
  repository/network policy, snapshots, and output artifacts.
- The slice stayed read-only and evidence-only by deriving the manifest from
  existing TestRun fields and Artifact metadata.

Completed slice name:

```text
Slice 29: Execution Run Manifest
```

Delivered output:

- Slice plan, contract boundary, frontend pytest execution manifest panel,
  golden smoke, and completion gate.
- Local links are limited to persisted local Artifact ids. Missing runtime,
  dependency, and environment snapshots remain visible as unavailable evidence.
- No runner behavior, report generation, FailureAnalysis, QualityGateDecision,
  remote provider, RAG runtime, MCP runtime, RBAC, tenants, or permissions were
  added.

## Recommended Next V2 Slice

Recommended: Test knowledge card contract.

Why:

- Slice 19 added deterministic local ContextArtifact retrieval evidence, but
  generated test cases still need a richer explanation of which testing
  knowledge supports them, which risks they cover, and why they should pass
  agent and human review.
- The final RAG and Agent direction calls for Chtest to become a testing
  knowledge evidence system, not a generic chat knowledge base.
- Starting with contracts keeps the next step small and reviewable before any
  vector database, external provider, graph reasoning, or frontend work.

Next slice name:

```text
Slice 30: Test Knowledge Card Contract
```

Smallest useful boundary:

- Define `TestKnowledgeCard` and `KnowledgeEvidence` contracts.
- Define generated-case evidence fields for source knowledge evidence ids,
  risk coverage, generation reason, automation readiness, quality score,
  review findings, and coverage gap notes.
- Add one fixture and one smoke proof showing requirement text, knowledge
  cards, generated candidates, review findings, and evidence ids.

Explicit non-goals:

- No RAG runtime, external KnowledgeAdapter calls, vector database, embeddings,
  reranking, GraphRAG runtime, graph database, background indexing, provider
  SDK, frontend implementation, generated-case auto-approval, runner behavior,
  artifact mutation, MCP runtime, marketplace, RBAC, tenants, permissions, or
  remote CI provider behavior.

Suggested next task:

```text
Slice 30 Task 1: Add Test Knowledge Card Contract task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until contracts define knowledge-card data, evidence,
  artifact, state, and review boundaries.

## Completed Next V2 Slice

Completed: Test knowledge card contract.

Why it was selected:

- Slice 19 added deterministic local ContextArtifact retrieval evidence, but
  generated test cases still needed richer proof of which testing knowledge
  supported them and which gaps reviewers needed to resolve.
- Slice 30 established `TestKnowledgeCard`, `KnowledgeEvidence`, generated-case
  evidence fields, artifact rules, state rules, fixture examples, and a
  schema-level golden smoke without adding a RAG runtime.
- The slice kept the final RAG/Agent direction evidence-first and review-first
  before any provider, vector, graph, or frontend implementation.

Completed slice name:

```text
Slice 30: Test Knowledge Card Contract
```

Delivered output:

- Slice plan, data/API/state/artifact contract boundary, fixture, schema-level
  golden smoke, and completion gate.
- GeneratedCaseCandidate can express knowledge evidence fields at schema level.
- No TestKnowledgeCard table, knowledge-card CRUD, RAG runtime, external
  provider, vector database, embedding, reranking, graph runtime, MCP runtime,
  frontend implementation, generated-case auto-approval, runner behavior,
  reports, RBAC, tenants, or permissions were added.

## Recommended Next V2 Slice

Recommended: Generated case knowledge evidence persistence.

Why:

- Slice 30 proved the evidence contract and response schema, but the real case
  generation flow does not yet persist those fields on GeneratedCaseCandidate.
- Persisting the fields is the smallest useful implementation bridge from
  contract to product behavior: generated candidates can carry evidence ids,
  knowledge evidence refs, review findings, and coverage gap notes through the
  existing API.
- This improves the requirement-to-case review loop without implementing
  TestKnowledgeCard CRUD, RAG runtime, external providers, frontend work, or
  review bypasses.

Next slice name:

```text
Slice 31: Generated Case Knowledge Evidence Persistence
```

Smallest useful boundary:

- Persist Slice 30 generated-case evidence fields on GeneratedCaseCandidate.
- Copy normalized fields from AI task output when present.
- Return fields from the candidate list API with safe defaults when absent.
- Add focused database/API/golden coverage proving evidence remains review-only.

Explicit non-goals:

- No TestKnowledgeCard table implementation, knowledge-card CRUD API,
  knowledge ingestion agent, RAG runtime, external KnowledgeAdapter provider,
  vector database, embeddings, reranking, graph runtime, GraphRAG job, MCP
  runtime, frontend implementation, generated-case auto-approval, TestCase
  auto-promotion, runner behavior, reports, artifact mutation, RBAC, tenants,
  permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 31 Task 1: Add Generated Case Knowledge Evidence Persistence task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines persistence behavior, contracts,
  verification, and non-goals.

## Completed Next V2 Slice

Completed: Generated case knowledge evidence persistence.

Why it was selected:

- Slice 30 proved the evidence contract and response schema, but the real case
  generation flow did not persist those fields on GeneratedCaseCandidate.
- Slice 31 bridged that gap by persisting normalized knowledge evidence ids,
  evidence refs, covered risk ids, generation reason, automation readiness,
  quality score, review findings, and coverage gap notes in the existing case
  generation flow.
- The slice improved the requirement-to-case review loop without implementing
  TestKnowledgeCard CRUD, RAG runtime, external providers, frontend work, or
  review bypass.

Completed slice name:

```text
Slice 31: Generated Case Knowledge Evidence Persistence
```

Delivered output:

- Slice plan, contract boundary, model/migration/API persistence, golden smoke,
  and completion gate.
- GeneratedCaseCandidate now exposes knowledge evidence fields through the
  candidate list API with safe defaults.
- No TestCase auto-promotion, TestRun, Report, retrieval job, vector index,
  graph job, provider call, artifact mutation, RAG runtime, MCP runtime, RBAC,
  tenants, or permissions were added.

## Completed Supplemental V2 Slice

Completed: Knowledge prompt/skill seed set.

Why it was integrated:

- The final RAG and agent strategy needs versioned PromptVersion and
  SkillVersion seed files before runtime orchestration can be designed safely.
- The prompt/skill seed branch added knowledge-card extraction, requirement
  understanding, risk analysis, coverage analysis, test design,
  evidence-backed case generation/review, dedup, automation readiness, and
  knowledge feedback seeds.
- The slice remained seed-only and did not enable RAG runtime, provider calls,
  vector search, graph runtime, MCP runtime, frontend, API, migration, runner,
  or report behavior.

Completed slice name:

```text
Slice 31: Knowledge Prompt/Skill Seeds
```

Delivered output:

- Prompt seed files, skill seed files, fixture documentation, contract updates,
  registry count updates, and prompt/skill seed smoke tests.

## Recommended Next V2 Slice

Recommended: Agent workflow contract for requirement-to-reviewed-case.

Why:

- Slice 30 defined knowledge evidence. Slice 31 persisted evidence fields and
  added prompt/skill seeds. The next missing contract is the workflow that ties
  those agent steps together without adding runtime orchestration.
- Chtest needs explicit per-agent input evidence, write permission, human gate,
  failure behavior, and trace rules before a future orchestrator can safely
  run RequirementUnderstandingAgent, RiskAnalysisAgent, CoverageAnalysisAgent,
  TestDesignAgent, CaseGenerationAgent, CaseReviewAgent, DedupAgent, and
  AutomationReadinessAgent.
- Planning this contract first prevents hidden auto-approval, provider schema
  leakage, and accidental RAG/MCP runtime expansion.

Next slice name:

```text
Slice 32: Agent Workflow Contract
```

Smallest useful boundary:

- Define the requirement-to-reviewed-case agent sequence.
- Define per-agent inputs, outputs, prompt/skill seed, write permission, human
  gate, failure behavior, and trace requirements.
- Keep generated candidates review-gated and do not promote TestCase records.
- Add one contract-level golden smoke after the contract is defined.

Explicit non-goals:

- No agent orchestration runtime, workflow engine, queue graph, scheduler,
  frontend workflow page, backend feature API, migrations, provider calls,
  vector database, embeddings, reranking, graph runtime, MCP runtime,
  generated-case auto-approval, runner behavior, report behavior, RBAC,
  tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 32 Task 1: Add Agent Workflow Contract task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines workflow behavior, contracts,
  verification, and non-goals.

## Completed Next V2 Slice

Completed: Agent workflow contract for requirement-to-reviewed-case.

Why it was selected:

- Slice 30 defined knowledge evidence, Slice 31 persisted generated-case
  evidence fields, and the integrated prompt/skill seed work added the
  versioned agent prompts and skills.
- Slice 32 tied those pieces together as a contract-only
  requirement-to-reviewed-case workflow without adding runtime orchestration.
- The contract made per-agent input evidence, output, write permission, human
  gate, failure behavior, and trace requirements explicit before any
  orchestrator can run the flow.

Completed slice name:

```text
Slice 32: Agent Workflow Contract
```

Delivered output:

- Slice plan, API/state/prompt-skill contract boundary, fixture, contract-level
  golden smoke, and completion gate.
- RequirementUnderstandingAgent, RiskAnalysisAgent, CoverageAnalysisAgent,
  TestDesignAgent, CaseGenerationAgent, CaseReviewAgent, DedupAgent, and
  AutomationReadinessAgent all remain review-gated and evidence-only.
- No agent orchestration runtime, workflow engine, queue graph, scheduler,
  frontend workflow page, backend feature API, migrations, provider calls,
  vector database, embeddings, reranking, graph runtime, MCP runtime,
  generated-case auto-approval, runner behavior, report behavior, RBAC,
  tenants, permissions, or remote CI provider behavior were added.

## Recommended Next V2 Slice

Recommended: MCP-ready ToolDefinition and KnowledgeAdapter safety contract
review.

Why:

- Slice 32 defined the agent workflow boundary. The next unsafe gap is future
  tool and retrieval integration: ToolDefinition, ToolInvocation, MCP-ready
  metadata, and KnowledgeAdapter providers must share one safety contract
  before any runtime or provider is added.
- `docs/implementation/11-final-rag-agent-strategy.md` already states that MCP
  is a tool access layer, not an orchestrator or RAG product. Turning that into
  a focused contract reduces the chance that future MCP/provider work bypasses
  approval, artifacts, prompt/skill tracing, or human review.
- This remains a small documentation slice because it can define schema, risk,
  approval, timeout, artifact policy, provider-state, and fallback behavior
  without changing code.

Next slice name:

```text
Slice 33: MCP-Ready ToolDefinition And KnowledgeAdapter Safety Contract
```

Smallest useful boundary:

- Define strict ToolDefinition schema, risk level, approval requirement,
  timeout, artifact policy, and MCP-readiness metadata.
- Define ToolInvocation approval, status, failure, and artifact-retention
  expectations for future local or MCP tools.
- Define KnowledgeAdapter provider-state and fallback behavior, including
  disabled/configured/unhealthy states and normalization to `KnowledgeEvidence`.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No MCP runtime, MCP server/client transport, remote MCP calls, marketplace,
  plugin install, provider SDK, provider credentials, OAuth, API keys, remote
  URL fetch, vector database, embeddings, reranking, background indexing, graph
  runtime, GraphRAG job, backend feature API, migrations, frontend page,
  package upgrade, runner behavior change, report behavior change,
  ToolInvocation execution behavior change, artifact mutation, generated-case
  auto-approval, RBAC, tenants, permissions, or remote CI/CD provider behavior.

Suggested next task:

```text
Slice 33 Task 1: Add MCP-ready ToolDefinition and KnowledgeAdapter safety contract task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines ToolDefinition, ToolInvocation,
  KnowledgeAdapter, artifact, provider-state, and review boundaries.

## Completed Next V2 Slice

Completed: MCP-ready ToolDefinition and KnowledgeAdapter safety contract
review.

Why it was selected:

- Slice 32 defined the agent workflow boundary, but future tool and retrieval
  integration still needed one safety contract before any runtime or provider
  work.
- Slice 33 defined strict ToolDefinition schema, risk, approval, timeout,
  artifact policy, ToolInvocation approval/failure/artifact behavior, and
  KnowledgeAdapter provider-state fallback behavior.
- The slice kept MCP and provider work contract-only and evidence-only before
  any MCP runtime, provider SDK, vector, graph, or external retrieval path.

Completed slice name:

```text
Slice 33: MCP-Ready ToolDefinition And KnowledgeAdapter Safety Contract
```

Delivered output:

- Slice plan, data/API/state/artifact safety contracts, fixture,
  contract-level golden smoke, and completion gate.
- ToolDefinition readiness and KnowledgeAdapter provider_state are metadata
  only. ToolInvocation output and KnowledgeEvidence remain evidence only.
- No MCP runtime, MCP server/client transport, provider SDK, credentials,
  external provider calls, vector database, embeddings, reranking, graph
  runtime, artifact mutation, generated-case auto-approval, report behavior,
  runner behavior, RBAC, tenants, permissions, or remote CI provider behavior
  were added.

## Recommended Next V2 Slice

Recommended: Knowledge feedback contract.

Why:

- The integrated prompt/skill seed work already includes
  `KnowledgeFeedbackAgent`, `knowledge_feedback:v1`, and
  `knowledge-feedback-skill:v1`, but Chtest does not yet have a contract that
  defines how accepted cases, rejected cases, review comments, failures, and
  reports become draft knowledge feedback.
- Knowledge feedback is the next feedback-loop boundary after generated-case
  evidence, agent workflow, and tool/provider safety. Without a contract,
  future automation could accidentally make feedback prompt-eligible,
  mutate historical evidence, or create TestKnowledgeCard rows without human
  review.
- The slice can remain small by defining draft-only feedback inputs, outputs,
  artifact evidence, review gates, failure behavior, and a golden smoke without
  adding TestKnowledgeCard CRUD or runtime agents.

Next slice name:

```text
Slice 34: Knowledge Feedback Contract
```

Smallest useful boundary:

- Define KnowledgeFeedbackAgent input evidence from accepted/rejected cases,
  ReviewHistory, FailureAnalysis, Report, execution evidence, and normalized
  KnowledgeEvidence.
- Define draft feedback output with source entity, source quote/hash,
  recommendation, confidence, unsupported claims, and review findings.
- Keep feedback draft-only until human review approves it for TestKnowledgeCard
  or prompt eligibility.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No KnowledgeFeedbackAgent runtime, TestKnowledgeCard CRUD, prompt-eligible
  auto-marking, automatic knowledge ingestion, vector database, embeddings,
  reranking, graph runtime, MCP runtime, provider SDK, external provider calls,
  artifact mutation, historical review/failure/report/TestCase mutation,
  generated-case auto-approval, runner behavior, report behavior, RBAC,
  tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 34 Task 1: Add Knowledge Feedback Contract task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines feedback sources, draft outputs,
  artifact evidence, human review, prompt eligibility, and non-goals.

## Completed Next V2 Slice

Completed: Knowledge feedback contract.

Why it was selected:

- The prompt/skill seed set already included KnowledgeFeedbackAgent, but Chtest
  did not have a contract for converting reviewed outcomes into draft
  knowledge feedback.
- Slice 34 defined draft-only KnowledgeFeedbackDraft input evidence, output
  fields, prompt/skill trace rules, artifact evidence, unsupported claims,
  human review gates, and failure behavior.
- The slice kept feedback from automatically creating TestKnowledgeCard rows,
  becoming prompt-eligible, or mutating historical review/failure/report/case
  evidence.

Completed slice name:

```text
Slice 34: Knowledge Feedback Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- Knowledge feedback remains draft-only and review-gated.
- No KnowledgeFeedbackAgent runtime, TestKnowledgeCard CRUD, prompt-eligible
  auto-marking, automatic knowledge ingestion, provider calls, vector database,
  embeddings, reranking, graph runtime, MCP runtime, artifact mutation,
  historical evidence mutation, generated-case auto-approval, runner behavior,
  report behavior, RBAC, tenants, permissions, or remote CI provider behavior
  were added.

## Recommended Next V2 Slice

Recommended: Knowledge feedback review gate contract.

Why:

- Slice 34 defines draft feedback, but the next boundary is how a human review
  gate may accept, reject, or request revision on that draft without creating a
  broad TestKnowledgeCard CRUD surface.
- This keeps the knowledge feedback loop auditable: draft feedback can become a
  reviewed knowledge-card candidate only through explicit human action, with
  prompt eligibility still separated from model confidence.
- The slice can stay contract-only by defining review actions, source evidence,
  ReviewHistory entries, prompt eligibility rules, and a golden smoke before
  any runtime or UI implementation.

Next slice name:

```text
Slice 35: Knowledge Feedback Review Gate Contract
```

Smallest useful boundary:

- Define review actions for KnowledgeFeedbackDraft: approve, reject,
  request_revision, and mark_prompt_eligible only through human review.
- Define how approved feedback may later feed a TestKnowledgeCard creation
  workflow without creating CRUD in this slice.
- Define ReviewHistory and artifact evidence rules for feedback review.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No runtime review API, frontend page, TestKnowledgeCard CRUD,
  KnowledgeFeedbackAgent runtime, automatic prompt eligibility, automatic
  knowledge ingestion, vector database, embeddings, reranking, graph runtime,
  MCP runtime, provider SDK, external provider calls, artifact mutation,
  historical evidence mutation, generated-case auto-approval, runner behavior,
  report behavior, RBAC, tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 35 Task 1: Add Knowledge Feedback Review Gate Contract task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines feedback review actions,
  ReviewHistory, artifact evidence, prompt eligibility, and non-goals.

## Completed Next V2 Slice

Completed: Knowledge feedback review gate contract.

Why it was selected:

- Slice 34 defined KnowledgeFeedbackDraft as draft-only output, but Chtest still
  needed the human gate that accepts, rejects, requests revision, or marks
  prompt eligibility without creating broad TestKnowledgeCard CRUD.
- Slice 35 defined review actions, ReviewHistory linkage, feedback review
  artifact evidence, prompt eligibility reason, and future TestKnowledgeCard
  handoff payloads.
- The slice kept prompt eligibility separate from model confidence and blocked
  rejected feedback from becoming positive prompt knowledge.

Completed slice name:

```text
Slice 35: Knowledge Feedback Review Gate Contract
```

Delivered output:

- Slice plan, data/API/state/artifact contracts, fixture, contract-level golden
  smoke, and completion gate.
- KnowledgeFeedbackDraft review remains human-gated and auditable.
- No feedback review runtime API, frontend review page, TestKnowledgeCard CRUD,
  automatic prompt eligibility, automatic knowledge ingestion, provider calls,
  vector database, embeddings, reranking, graph runtime, MCP runtime, artifact
  mutation, historical evidence mutation, generated-case auto-approval, runner
  behavior, report behavior, RBAC, tenants, permissions, or remote CI provider
  behavior were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard handoff contract.

Why:

- Slice 35 intentionally stops at a handoff payload. The next narrow contract
  is to define how an approved KnowledgeFeedbackDraft can become a reviewed
  TestKnowledgeCard candidate without introducing a broad CRUD surface or
  prompt-eligibility automation.
- This keeps the knowledge loop closed but controlled: human-reviewed feedback
  can be mapped into card fields, source evidence, safe-to-show checks, and
  prompt eligibility gates before any implementation writes card rows.
- The slice can stay contract-only by defining handoff payload shape,
  duplicate/merge rules, source evidence requirements, card review states, and
  a golden smoke.

Next slice name:

```text
Slice 36: TestKnowledgeCard Handoff Contract
```

Smallest useful boundary:

- Define handoff payload from approved KnowledgeFeedbackDraft to a future
  TestKnowledgeCard candidate.
- Define source evidence, source quote/hash, knowledge_type mapping,
  duplicate/merge hints, safe_to_show checks, and allowed_for_prompt default.
- Keep card creation and prompt eligibility review-gated and separate.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No TestKnowledgeCard CRUD implementation, backend feature API, frontend page,
  migration, automatic card creation, automatic prompt eligibility, automatic
  knowledge ingestion, provider calls, vector database, embeddings, reranking,
  graph runtime, MCP runtime, artifact mutation, historical evidence mutation,
  generated-case auto-approval, runner behavior, report behavior, RBAC,
  tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 36 Task 1: Add TestKnowledgeCard Handoff Contract task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines handoff payload, source evidence,
  card review boundaries, prompt eligibility, and non-goals.

## Completed Next V2 Slice

Completed: TestKnowledgeCard handoff contract.

Why it was selected:

- Slice 35 intentionally stopped at a feedback review handoff payload. Chtest
  needed a precise contract for how approved KnowledgeFeedbackDraft output can
  become a future TestKnowledgeCard candidate without creating card rows.
- Slice 36 defined handoff input, mapped candidate fields, source evidence,
  duplicate/merge hints, safe-to-show checks, `allowed_for_prompt=false`,
  ReviewHistory/review artifact trace, failure behavior, and forbidden side
  effects.
- The slice kept card creation and prompt eligibility behind later human review
  workflows and blocked model confidence from approving reusable knowledge.

Completed slice name:

```text
Slice 36: TestKnowledgeCard Handoff Contract
```

Delivered output:

- Slice plan, data/API/state/artifact contracts, fixture, contract-level golden
  smoke, and completion gate.
- Approved KnowledgeFeedbackDraft handoff remains a candidate payload with
  source evidence, duplicate/merge hints, safe_to_show checks, and
  `allowed_for_prompt=false`.
- No TestKnowledgeCard CRUD implementation, backend feature API, frontend page,
  migration, automatic card creation, automatic card approval, automatic prompt
  eligibility, automatic knowledge ingestion, provider calls, vector database,
  embeddings, reranking, graph runtime, MCP runtime, artifact mutation,
  historical evidence mutation, generated-case auto-approval, runner behavior,
  report behavior, RBAC, tenants, permissions, or remote CI provider behavior
  were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard candidate review contract.

Why:

- Slice 36 creates a clean handoff payload boundary, but a future card still
  needs a human review decision before Chtest can safely create or merge a
  TestKnowledgeCard.
- The next narrow contract should define how reviewers accept, reject, request
  revision, or route duplicate/merge decisions for handoff candidates without
  opening a broad CRUD surface.
- This keeps prompt eligibility separate from card candidate approval:
  `allowed_for_prompt=false` remains the default until a later explicit card
  review decision grants eligibility.

Next slice name:

```text
Slice 37: TestKnowledgeCard Candidate Review Contract
```

Smallest useful boundary:

- Define review actions for TestKnowledgeCard handoff candidates:
  approve_candidate_for_creation, reject_candidate, request_candidate_revision,
  flag_duplicate, request_merge_review, and defer_prompt_eligibility.
- Define ReviewHistory and artifact evidence rules for candidate review.
- Define how duplicate/merge hints are reviewed without automatically merging,
  archiving, replacing, deleting, or creating card rows.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No TestKnowledgeCard CRUD implementation, backend feature API, frontend page,
  migration, automatic card creation, automatic card approval, automatic prompt
  eligibility, automatic knowledge ingestion, provider calls, vector database,
  embeddings, reranking, graph runtime, MCP runtime, artifact mutation,
  historical evidence mutation, generated-case auto-approval, runner behavior,
  report behavior, RBAC, tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 37 Task 1: Add TestKnowledgeCard Candidate Review Contract task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines candidate review actions,
  ReviewHistory, artifact evidence, duplicate/merge handling, prompt
  eligibility, and non-goals.

## Completed Next V2 Slice

Completed: TestKnowledgeCard candidate review contract.

Why it was selected:

- Slice 36 created a clean handoff payload boundary, but the candidate still
  needed human review before it could safely feed any future card creation
  workflow.
- Slice 37 defined candidate review actions, ReviewHistory linkage, candidate
  review artifact evidence, duplicate/merge routing, prompt eligibility
  deferral, failure behavior, and forbidden side effects.
- The slice kept candidate approval separate from TestKnowledgeCard row
  creation, duplicate merge/archive/delete, and prompt eligibility.

Completed slice name:

```text
Slice 37: TestKnowledgeCard Candidate Review Contract
```

Delivered output:

- Slice plan, data/API/state/artifact contracts, fixture, contract-level golden
  smoke, and completion gate.
- TestKnowledgeCard handoff candidates can be reviewed, rejected, revised, or
  routed for duplicate/merge review without creating card rows.
- No TestKnowledgeCard CRUD implementation, backend feature API, frontend page,
  migration, automatic card creation, automatic card approval, automatic prompt
  eligibility, automatic merge/archive/delete/relabel, provider calls, vector
  database, embeddings, reranking, graph runtime, MCP runtime, artifact
  mutation, historical evidence mutation, generated-case auto-approval, runner
  behavior, report behavior, RBAC, tenants, permissions, or remote CI provider
  behavior were added.

## Recommended Next V2 Slice

Recommended: Reviewed TestKnowledgeCard creation contract.

Why:

- Slice 37 ends at `approve_candidate_for_creation`, which intentionally does
  not create a TestKnowledgeCard row.
- The next narrow contract should define the reviewed creation boundary from an
  approved candidate into a future TestKnowledgeCard record without opening a
  broad CRUD surface.
- This keeps card creation, duplicate decisions, source evidence, and prompt
  eligibility explicit: a created card can remain `allowed_for_prompt=false`
  until a later prompt-eligibility workflow grants reuse.

Next slice name:

```text
Slice 38: Reviewed TestKnowledgeCard Creation Contract
```

Smallest useful boundary:

- Define creation input from an approved candidate review artifact, handoff
  artifact, source evidence, ReviewHistory, and candidate_card_json.
- Define the created TestKnowledgeCard field mapping, source manifest,
  evidence artifacts, duplicate/merge preconditions, `safe_to_show`, and
  `allowed_for_prompt=false` default.
- Define failure behavior for stale, rejected, duplicate-conflicted,
  cross-project, unsafe, or unsupported source evidence.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No broad TestKnowledgeCard CRUD implementation, list/update/delete API,
  frontend page, migration, automatic card creation from model output,
  automatic prompt eligibility, automatic knowledge ingestion, provider calls,
  vector database, embeddings, reranking, graph runtime, MCP runtime, artifact
  mutation outside declared creation evidence, historical evidence mutation,
  generated-case auto-approval, runner behavior, report behavior, RBAC,
  tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 38 Task 1: Add Reviewed TestKnowledgeCard Creation Contract task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines reviewed creation input, card field
  mapping, source evidence, duplicate/merge preconditions, prompt eligibility,
  failure behavior, and non-goals.

## Completed Next V2 Slice

Completed: Reviewed TestKnowledgeCard creation contract.

Why it was selected:

- Slice 37 ended at `approve_candidate_for_creation`, which intentionally did
  not create a TestKnowledgeCard row.
- Slice 38 defined the reviewed creation boundary from an approved candidate
  into a future TestKnowledgeCard record, including source manifest,
  duplicate/merge preconditions, failure behavior, ReviewHistory linkage, and
  `allowed_for_prompt=false`.
- The slice kept broad CRUD, prompt eligibility, automatic creation from model
  output, and duplicate merge/archive/delete out of scope.

Completed slice name:

```text
Slice 38: Reviewed TestKnowledgeCard Creation Contract
```

Delivered output:

- Slice plan, data/API/state/artifact contracts, fixture, contract-level golden
  smoke, and completion gate.
- Reviewed creation is now a future scoped contract with explicit input,
  card-field mapping, source manifest, and creation evidence.
- No broad TestKnowledgeCard CRUD implementation, backend feature API, frontend
  page, migration, automatic card creation from model output, automatic prompt
  eligibility, automatic knowledge ingestion, provider calls, vector database,
  embeddings, reranking, graph runtime, MCP runtime, artifact mutation outside
  declared creation evidence, historical evidence mutation, generated-case
  auto-approval, runner behavior, report behavior, RBAC, tenants, permissions,
  or remote CI provider behavior were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard prompt eligibility contract.

Why:

- Slice 38 intentionally defaults created cards to `allowed_for_prompt=false`.
  Chtest still needs an explicit human-reviewed contract before any card can be
  used as prompt context.
- Prompt eligibility should require safe_to_show evidence, redaction status,
  reviewed source citations, ReviewHistory, and a prompt eligibility reason.
- This keeps card creation separate from retrieval/runtime behavior and blocks
  model confidence or schema validity from making knowledge reusable.

Next slice name:

```text
Slice 39: TestKnowledgeCard Prompt Eligibility Contract
```

Smallest useful boundary:

- Define prompt eligibility review actions for TestKnowledgeCard records:
  mark_card_prompt_eligible, deny_card_prompt_eligibility,
  request_prompt_eligibility_revision, and revoke_card_prompt_eligibility.
- Define safe_to_show, redaction, source evidence, ReviewHistory, prompt
  eligibility reason, and artifact evidence requirements.
- Define revocation/failure behavior without retrieval, indexing, or prompt
  runtime changes.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No broad TestKnowledgeCard CRUD implementation, frontend page, migration,
  automatic prompt eligibility, prompt runtime retrieval change, vector
  database, embeddings, reranking, graph runtime, MCP runtime, provider calls,
  artifact mutation outside declared prompt-eligibility evidence, historical
  evidence mutation, automatic card creation, automatic knowledge ingestion,
  generated-case auto-approval, runner behavior, report behavior, RBAC,
  tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 39 Task 1: Add TestKnowledgeCard Prompt Eligibility Contract task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines prompt eligibility review actions,
  safe_to_show/redaction/source evidence requirements, ReviewHistory, artifact
  evidence, revocation/failure behavior, and non-goals.

## Completed Next V2 Slice

Completed: TestKnowledgeCard prompt eligibility contract.

Why it was selected:

- Slice 38 intentionally defaulted created cards to `allowed_for_prompt=false`;
  Slice 39 defined the explicit human review gate before any reviewed card can
  enter prompt context.
- Slice 39 required safe_to_show evidence, redaction status, reviewed source
  citations, ReviewHistory, prompt eligibility reason, and prompt eligibility
  artifact evidence before `allowed_for_prompt=true`.
- The slice kept prompt eligibility separate from card creation, retrieval
  runtime, model confidence, schema validity, and source presence.

Completed slice name:

```text
Slice 39: TestKnowledgeCard Prompt Eligibility Contract
```

Delivered output:

- Slice plan, data/API/state/artifact contracts, fixture, contract-level golden
  smoke, and completion gate.
- TestKnowledgeCard prompt eligibility is now a human-reviewed contract with
  mark, deny, revision-request, and revoke actions.
- No broad TestKnowledgeCard CRUD implementation, backend feature API,
  frontend page, migration, automatic prompt eligibility, prompt runtime
  retrieval change, vector database, embeddings, reranking, graph runtime, MCP
  runtime, provider calls, artifact mutation outside declared
  prompt-eligibility evidence, historical evidence mutation, automatic card
  creation, automatic knowledge ingestion, generated-case auto-approval,
  runner behavior, report behavior, RBAC, tenants, permissions, or remote CI
  provider behavior were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard retrieval boundary contract.

Why:

- Slice 39 says which reviewed cards may be allowed for prompt use, but Chtest
  still needs a contract for how prompt-eligible cards may be considered by a
  later retrieval or prompt-context workflow.
- The next narrow boundary should define read-only eligibility filters,
  source evidence checks, exclusion rules, and retrieval evidence outputs
  without implementing retrieval runtime behavior.
- This keeps `allowed_for_prompt=true` necessary but not sufficient for future
  prompt inclusion: stale, unsafe, cross-project, revoked, or unsupported
  evidence must remain excluded.

Next slice name:

```text
Slice 40: TestKnowledgeCard Retrieval Boundary Contract
```

Smallest useful boundary:

- Define a read-only selection contract for future TestKnowledgeCard prompt
  context using `allowed_for_prompt=true`, `safe_to_show=true`, non-revoked
  prompt eligibility evidence, same-project source artifacts, and current
  source manifest checks.
- Define exclusion behavior for denied, revoked, revision-requested, stale,
  cross-project, unsafe, unsupported, missing, or unbounded evidence.
- Define retrieval evidence shape for a later workflow without adding runtime
  retrieval, deterministic ranking changes, vector indexes, embeddings,
  reranking, graph jobs, provider calls, or MCP runtime.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No prompt runtime retrieval implementation, deterministic retrieval behavior
  change, vector database, embeddings, reranking, background indexing, graph
  runtime, GraphRAG job, MCP runtime, provider calls, provider SDK,
  credentials, backend feature API, frontend page, migration, broad
  TestKnowledgeCard CRUD, automatic prompt eligibility, automatic card
  creation, automatic knowledge ingestion, artifact mutation, historical
  evidence mutation, generated-case auto-approval, runner behavior, report
  behavior, RBAC, tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 40 Task 1: Add TestKnowledgeCard Retrieval Boundary task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- No product code until the plan defines selection inputs, eligibility
  filters, exclusion behavior, retrieval evidence outputs, failure behavior,
  and non-goals.
