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
- Plan file:
  `docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md`.
- No product code until the plan defines selection inputs, eligibility
  filters, exclusion behavior, retrieval evidence outputs, failure behavior,
  and non-goals.

## Completed Next V2 Slice

Completed: TestKnowledgeCard retrieval boundary contract.

Why it was selected:

- Slice 39 defined which reviewed cards can become prompt eligible, but Chtest
  still needed a contract for future prompt-context selection.
- Slice 40 defined read-only selection filters so `allowed_for_prompt=true` is
  necessary but not sufficient for prompt-context inclusion.
- The slice preserved source evidence, source manifest, redaction,
  ReviewHistory, prompt eligibility artifacts, exclusion reasons, and retrieval
  evidence outputs without implementing runtime retrieval.

Completed slice name:

```text
Slice 40: TestKnowledgeCard Retrieval Boundary Contract
```

Delivered output:

- Slice plan, data/API/state/artifact contracts, fixture, contract-level golden
  smoke, and completion gate.
- TestKnowledgeCard retrieval boundary is now a read-only contract with
  `select_prompt_eligible_cards`, eligibility filters, selection evidence, and
  `excluded_card_reason`.
- No prompt runtime retrieval implementation, deterministic retrieval behavior
  change, vector database, embeddings, reranking, background indexing, graph
  runtime, GraphRAG job, MCP runtime, provider calls, provider SDK,
  credentials, backend feature API, frontend page, migration, broad
  TestKnowledgeCard CRUD, automatic prompt eligibility, automatic card
  creation, automatic knowledge ingestion, artifact mutation, historical
  evidence mutation, generated-case auto-approval, runner behavior, report
  behavior, RBAC, tenants, permissions, or remote CI provider behavior were
  added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard prompt context evidence contract.

Why:

- Slice 40 decides which prompt-eligible cards can be selected, but a later
  prompt workflow also needs a bounded evidence contract for what is actually
  placed into prompt context.
- The next narrow boundary should define prompt context evidence records:
  selected card ids, safe snippets or hashes, source evidence ids, selection
  reasons, exclusion summaries, and prompt/skill trace links.
- This keeps prompt assembly auditable without adding runtime retrieval,
  provider calls, prompt execution, vector search, embeddings, reranking, graph
  traversal, or frontend behavior.

Next slice name:

```text
Slice 41: TestKnowledgeCard Prompt Context Evidence Contract
```

Smallest useful boundary:

- Define a prompt context evidence artifact shape for future prompt workflows
  that includes selected TestKnowledgeCard ids, bounded safe snippets or source
  hashes, source manifest ids, retrieval boundary artifact ids, ReviewHistory
  ids, prompt/skill version ids, and omission/exclusion summaries.
- Define safety rules for snippet bounds, `safe_to_show`, redaction, source
  traceability, and unsupported claims before any prompt input can cite a card.
- Define failure behavior when selected card evidence is stale, unsafe,
  cross-project, unbounded, missing, or revoked after selection.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No prompt runtime execution, prompt assembly implementation, provider call,
  LLM call, prompt runner, deterministic retrieval behavior change, vector
  database, embeddings, reranking, background indexing, graph runtime,
  GraphRAG job, MCP runtime, provider SDK, credentials, backend feature API,
  frontend page, migration, broad TestKnowledgeCard CRUD, automatic prompt
  eligibility, automatic card creation, automatic knowledge ingestion,
  artifact mutation outside declared prompt-context evidence, historical
  evidence mutation, generated-case auto-approval, runner behavior, report
  behavior, RBAC, tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 41 Task 1: Add TestKnowledgeCard Prompt Context Evidence task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md`.
- No product code until the plan defines prompt context evidence inputs,
  bounded outputs, safety checks, trace links, failure behavior, and non-goals.

## Completed Next V2 Slice

Completed: TestKnowledgeCard prompt context evidence contract.

Why it was selected:

- Slice 40 defined read-only prompt-context selection, but Chtest still needed
  a bounded evidence contract for what selected card evidence can enter future
  prompt context.
- Slice 41 defined prompt context evidence inputs, bounded snippets/source
  hashes, source manifest, retrieval boundary artifacts, PromptVersion/
  SkillVersion trace, context manifest links, omission reasons, and failure
  behavior.
- The slice kept prompt assembly, prompt runtime execution, provider calls,
  retrieval ranking, vector DB/embeddings/reranking/graph/MCP out of scope.

Completed slice name:

```text
Slice 41: TestKnowledgeCard Prompt Context Evidence Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- TestKnowledgeCard prompt context evidence is now a bounded contract with
  `build_prompt_context_evidence`, safe bounded snippet/source hash entries,
  prompt/skill trace, context manifest links, and omission reason.
- No prompt assembly implementation, prompt runtime execution, provider calls,
  retrieval ranking change, vector database, embeddings, reranking, graph
  runtime, MCP runtime, backend feature API, frontend page, migration, broad
  TestKnowledgeCard CRUD, automatic prompt eligibility, automatic card
  creation, automatic knowledge ingestion, artifact mutation outside declared
  prompt-context evidence, historical evidence mutation, generated-case
  auto-approval, runner behavior, report behavior, RBAC, tenants, permissions,
  or remote CI provider behavior were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard prompt context consumption contract.

Why:

- Slice 41 defines prompt context evidence, but future AI workflows still need
  a contract for consuming that evidence in agent inputs without treating it as
  provider/runtime permission.
- The next narrow boundary should define how future agents reference prompt
  context evidence ids, `used_knowledge` flags, prompt/skill trace, and output
  citations while preserving review gates.
- This keeps evidence consumption auditable without adding prompt assembly
  implementation, provider calls, runtime retrieval, model output behavior
  changes, or frontend behavior.

Next slice name:

```text
Slice 42: TestKnowledgeCard Prompt Context Consumption Contract
```

Smallest useful boundary:

- Define future agent input references to prompt context evidence artifact ids,
  context manifest ids, selected TestKnowledgeCard ids, source hashes,
  PromptVersion/SkillVersion ids, and ReviewHistory ids.
- Define allowed output citations and `used_knowledge` semantics when prompt
  context evidence is present.
- Define failure behavior when prompt context evidence is missing, stale,
  unsafe, revoked, or mismatched.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No prompt assembly implementation, prompt runtime execution, provider call,
  LLM call, prompt runner, deterministic retrieval behavior change, vector
  database, embeddings, reranking, background indexing, graph runtime, MCP
  runtime, provider SDK, credentials, backend feature API, frontend page,
  migration, broad TestKnowledgeCard CRUD, automatic prompt eligibility,
  automatic card creation, automatic knowledge ingestion, artifact mutation
  outside declared consumption evidence, historical evidence mutation,
  generated-case auto-approval, runner behavior, report behavior, RBAC,
  tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 42 Task 1: Add TestKnowledgeCard Prompt Context Consumption task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md`.
- No product code until the plan defines prompt context evidence inputs,
  consumption/citation rules, `used_knowledge` semantics, failure behavior,
  and non-goals.

## Completed Next V2 Slice

Completed: TestKnowledgeCard prompt context consumption contract.

Why it was selected:

- Slice 41 defined bounded prompt context evidence, but Chtest still needed a
  contract for how future agents may consume that evidence and cite it.
- Slice 42 defined prompt context consumption inputs, `consume_prompt_context_evidence`,
  `used_knowledge` semantics, output citations, consumed context entry/source
  hash references, skipped evidence, PromptVersion/SkillVersion trace,
  ReviewHistory links, and failure behavior.
- The slice kept prompt assembly, prompt runtime execution, provider calls,
  retrieval ranking, model output behavior changes, frontend/report behavior,
  vector DB/embeddings/reranking/graph/MCP out of scope.

Completed slice name:

```text
Slice 42: TestKnowledgeCard Prompt Context Consumption Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- TestKnowledgeCard prompt context consumption is now a bounded contract with
  `consume_prompt_context_evidence`, `prompt_context_consumption`,
  `used_knowledge` decision rules, consumed evidence citations, source hash and
  context manifest links, skipped evidence, and failure behavior.
- No prompt assembly implementation, prompt runtime execution, provider calls,
  retrieval ranking change, model output behavior implementation, automatic
  citation generation, vector database, embeddings, reranking, graph runtime,
  MCP runtime, backend feature API, frontend page, report behavior change,
  migration, broad TestKnowledgeCard CRUD, automatic prompt eligibility,
  automatic card creation, automatic knowledge ingestion, artifact mutation
  outside declared prompt-context consumption, historical evidence mutation,
  generated-case auto-approval, runner behavior, RBAC, tenants, permissions, or
  remote CI provider behavior were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard prompt context audit summary contract.

Why:

- Slice 42 defines how future agents consume prompt context evidence, but Chtest
  still needs a read-only audit summary contract for explaining what knowledge
  was used, skipped, unsupported, or failed.
- The next narrow boundary should define audit summary inputs and outputs from
  prompt context consumption artifacts, output citations, source hashes,
  context manifest links, PromptVersion/SkillVersion trace, and ReviewHistory.
- This keeps knowledge usage reviewable without adding a frontend page, report
  generator behavior change, prompt assembly implementation, provider calls,
  runtime retrieval, model output behavior changes, or database migration.

Next slice name:

```text
Slice 43: TestKnowledgeCard Prompt Context Audit Summary Contract
```

Smallest useful boundary:

- Define read-only audit summary inputs from prompt context consumption artifact
  ids, prompt context evidence artifact ids, `used_knowledge` decision,
  consumed citations, skipped evidence, unsupported claims, source hashes,
  context manifest ids, PromptVersion/SkillVersion ids, and ReviewHistory ids.
- Define audit summary outputs such as knowledge usage status, cited entries,
  skipped entries, unsupported claim summaries, failure reasons, and review
  flags.
- Define failure behavior when consumption evidence is missing, stale,
  mismatched, unsafe, revoked, or citation-incomplete.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No frontend page, report generation behavior change, backend feature API,
  prompt assembly implementation, prompt runtime execution, provider call, LLM
  call, prompt runner, deterministic retrieval behavior change, vector
  database, embeddings, reranking, background indexing, graph runtime, MCP
  runtime, provider SDK, credentials, migration, broad TestKnowledgeCard CRUD,
  automatic prompt eligibility, automatic card creation, automatic knowledge
  ingestion, artifact mutation outside declared audit summary evidence,
  historical evidence mutation, generated-case auto-approval, runner behavior,
  RBAC, tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 43 Task 1: Add TestKnowledgeCard Prompt Context Audit Summary task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md`.
- No product code until the plan defines audit summary inputs, cited/skipped
  evidence summary outputs, unsupported claim handling, failure behavior, and
  non-goals.

## Completed Next V2 Slice

Completed: TestKnowledgeCard prompt context audit summary contract.

Why it was selected:

- Slice 42 defined prompt context consumption evidence, but Chtest still needed
  a read-only audit summary contract for explaining what knowledge was used,
  skipped, unsupported, or failed.
- Slice 43 defined audit summary inputs and outputs from prompt context
  consumption artifacts, prompt context evidence artifacts, output citations,
  skipped evidence, unsupported claims, source hashes, context manifest links,
  PromptVersion/SkillVersion trace, ReviewHistory, usage status, review flags,
  and failure behavior.
- The slice kept frontend pages, report generation behavior, prompt assembly,
  prompt runtime execution, provider calls, retrieval ranking, model output
  behavior changes, vector DB/embeddings/reranking/graph/MCP out of scope.

Completed slice name:

```text
Slice 43: TestKnowledgeCard Prompt Context Audit Summary Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- TestKnowledgeCard prompt context audit summary is now a read-only contract
  with `summarize_prompt_context_consumption`, `prompt_context_audit_summary`,
  usage status, cited/skipped entries, unsupported claim summaries, source hash
  and context manifest links, PromptVersion/SkillVersion trace, ReviewHistory,
  review flags, and failure behavior.
- No frontend page, report generation behavior, prompt assembly
  implementation, prompt runtime execution, provider calls, retrieval ranking
  change, model output behavior implementation, automatic citation generation,
  vector database, embeddings, reranking, graph runtime, MCP runtime, backend
  feature API, migration, broad TestKnowledgeCard CRUD, automatic prompt
  eligibility, automatic card creation, automatic knowledge ingestion, artifact
  mutation outside declared prompt-context audit summary, historical evidence
  mutation, generated-case auto-approval, runner behavior, RBAC, tenants,
  permissions, or remote CI provider behavior were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard prompt context audit review decision contract.

Why:

- Slice 43 defines read-only audit summaries, but Chtest still needs a contract
  for how a future human review decision may accept, question, or reject the
  audit summary without changing knowledge evidence or report behavior.
- The next narrow boundary should define review-decision inputs and outputs
  from audit summary artifacts, cited/skipped evidence, unsupported claims,
  source hashes, PromptVersion/SkillVersion trace, and ReviewHistory.
- This keeps knowledge usage review-gated without adding a frontend page,
  report generator behavior change, prompt assembly implementation, provider
  calls, runtime retrieval, model output behavior changes, or database
  migration.

Next slice name:

```text
Slice 44: TestKnowledgeCard Prompt Context Audit Review Decision Contract
```

Smallest useful boundary:

- Define human review decision inputs from audit summary artifact ids, prompt
  context consumption artifact ids, cited/skipped evidence, unsupported claims,
  source hashes, context manifest ids, PromptVersion/SkillVersion ids, and
  ReviewHistory ids.
- Define review decisions such as accepted, needs_clarification,
  rejected_for_missing_evidence, rejected_for_unsupported_claim, and
  rejected_for_citation_mismatch.
- Define review output evidence, reviewer comments, follow-up flags, and
  failure behavior without mutating the underlying audit summary or knowledge
  artifacts.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No frontend page, report generation behavior change, backend feature API,
  prompt assembly implementation, prompt runtime execution, provider call, LLM
  call, prompt runner, deterministic retrieval behavior change, vector
  database, embeddings, reranking, background indexing, graph runtime, MCP
  runtime, provider SDK, credentials, migration, broad TestKnowledgeCard CRUD,
  automatic prompt eligibility, automatic card creation, automatic knowledge
  ingestion, artifact mutation outside declared review decision evidence,
  historical evidence mutation, generated-case auto-approval, runner behavior,
  RBAC, tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 44 Task 1: Add TestKnowledgeCard Prompt Context Audit Review Decision task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md`.
- No product code until the plan defines review decision inputs, reviewer
  action outputs, follow-up flags, failure behavior, and non-goals.

## Completed Next V2 Slice

Completed: TestKnowledgeCard prompt context audit review decision contract.

Why it was selected:

- Slice 43 defined read-only audit summaries, but Chtest still needed a human
  review decision boundary for accepting, questioning, or rejecting those audit
  summaries without changing knowledge evidence or report behavior.
- Slice 44 defined review decision inputs and outputs from audit summary
  artifacts, prompt context consumption artifacts, prompt context evidence
  artifacts, cited/skipped evidence, unsupported claims, source hashes, context
  manifest links, PromptVersion/SkillVersion trace, and ReviewHistory.
- The slice kept knowledge usage review-gated without adding frontend pages,
  report generation behavior, prompt assembly, prompt runtime execution,
  provider calls, retrieval ranking changes, model output behavior changes,
  vector DB/embeddings/reranking/graph/MCP, backend feature APIs, or database
  migrations.

Completed slice name:

```text
Slice 44: TestKnowledgeCard Prompt Context Audit Review Decision Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- TestKnowledgeCard prompt context audit review decision is now a contract with
  `review_prompt_context_audit_summary`,
  `prompt_context_audit_review_decision`, reviewer action, `accepted`,
  `needs_clarification`, rejected decision states, accepted/questioned/rejected
  citations, follow-up flags, ReviewHistory, source hashes, context manifest
  references, PromptVersion/SkillVersion trace, and failure behavior.
- No frontend page, report generation behavior, prompt assembly
  implementation, prompt runtime execution, provider calls, retrieval ranking
  change, model output behavior implementation, automatic citation generation,
  vector database, embeddings, reranking, graph runtime, MCP runtime, backend
  feature API, migration, broad TestKnowledgeCard CRUD, automatic prompt
  eligibility, automatic card creation, automatic knowledge ingestion, artifact
  mutation outside declared prompt-context audit review decision, historical
  evidence mutation, generated-case auto-approval, runner behavior, RBAC,
  tenants, permissions, or remote CI provider behavior were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard prompt context audit review summary export
contract.

Why:

- Slice 44 defines human review decisions, but Chtest still needs a contract
  for how a future exportable summary may package accepted, questioned, and
  rejected prompt context audit review decision evidence without changing
  frontend pages, report generation behavior, or runtime prompt behavior.
- The next narrow boundary should define export-summary inputs and outputs from
  review decision artifacts, audit summary artifacts, accepted/questioned/
  rejected citations, follow-up flags, unsupported claims, source hashes,
  context manifest links, PromptVersion/SkillVersion trace, and ReviewHistory.
- This keeps review decision handoff auditable before any UI renderer, report
  generator, download endpoint, provider, or prompt runtime consumes the
  summary.

Next slice name:

```text
Slice 45: TestKnowledgeCard Prompt Context Audit Review Summary Export Contract
```

Smallest useful boundary:

- Define export summary inputs from prompt context audit review decision
  artifact ids, audit summary artifact ids, prompt context consumption artifact
  ids, accepted/questioned/rejected citations, follow-up flags, unsupported
  claims, source hashes, context manifest ids, PromptVersion/SkillVersion ids,
  and ReviewHistory ids.
- Define export summary outputs such as export summary artifact id, review
  outcome summary, accepted/questioned/rejected citation groups, unresolved
  follow-up flags, unsupported claim references, source manifest ids and
  hashes, context manifest references, ReviewHistory links,
  PromptVersion/SkillVersion trace, failure code, and visible reason.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No frontend page, report generation behavior change, actual report renderer,
  export/download endpoint, backend feature API, prompt assembly
  implementation, prompt runtime execution, provider call, LLM call, prompt
  runner, deterministic retrieval behavior change, vector database, embeddings,
  reranking, background indexing, graph runtime, MCP runtime, provider SDK,
  credentials, migration, broad TestKnowledgeCard CRUD, automatic prompt
  eligibility, automatic card creation, automatic knowledge ingestion, artifact
  mutation outside declared review summary export evidence, historical evidence
  mutation, generated-case auto-approval, runner behavior, RBAC, tenants,
  permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 45 Task 1: Add TestKnowledgeCard Prompt Context Audit Review Summary Export task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md`.
- No product code until the plan defines export summary inputs, review outcome
  outputs, unresolved follow-up handling, failure behavior, and non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-45-test-knowledge-card-prompt-context-audit-review-summary-export-contract.md`.

## Completed Next V2 Slice

Completed: TestKnowledgeCard prompt context audit review summary export
contract.

Why it was selected:

- Slice 44 defined human audit review decisions, but Chtest still needed a
  contract for packaging accepted, questioned, and rejected review decision
  evidence into a future exportable summary without changing frontend pages,
  report generation behavior, export endpoints, or runtime prompt behavior.
- Slice 45 defined export summary inputs and outputs from audit review decision
  artifacts, audit summary artifacts, accepted/questioned/rejected citations,
  unresolved follow-up flags, unsupported claims, source hashes, context
  manifest links, PromptVersion/SkillVersion trace, and ReviewHistory.
- The slice kept review decision handoff auditable before any UI renderer,
  report generator, download endpoint, provider, or prompt runtime consumes
  the summary.

Completed slice name:

```text
Slice 45: TestKnowledgeCard Prompt Context Audit Review Summary Export Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- TestKnowledgeCard prompt context audit review summary export is now a
  contract with `export_prompt_context_audit_review_summary`,
  `prompt_context_audit_review_summary_export`, review outcome summary,
  accepted/questioned/rejected citation groups, unresolved follow-up flags,
  unsupported claim references, ReviewHistory links, source hashes, context
  manifest references, PromptVersion/SkillVersion trace, and failure behavior.
- No frontend page, report generation behavior, export/download endpoint,
  prompt assembly implementation, prompt runtime execution, provider calls,
  retrieval ranking change, model output behavior implementation, automatic
  citation generation, vector database, embeddings, reranking, graph runtime,
  MCP runtime, backend feature API, migration, broad TestKnowledgeCard CRUD,
  automatic prompt eligibility, automatic card creation, automatic knowledge
  ingestion, artifact mutation outside declared prompt-context audit review
  summary export, historical evidence mutation, generated-case auto-approval,
  runner behavior, RBAC, tenants, permissions, or remote CI provider behavior
  were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard prompt context review discrepancy tracking
contract.

Why:

- Slice 45 packages review decisions into exportable summaries, but Chtest
  still needs a contract for tracking discrepancies between consumed prompt
  context, audit summaries, review decisions, and export summaries without
  mutating any underlying evidence.
- The next narrow boundary should define discrepancy inputs and outputs from
  review summary export artifacts, audit review decision artifacts, audit
  summary artifacts, accepted/questioned/rejected citations, skipped evidence,
  unsupported claims, unresolved follow-up flags, source hashes, context
  manifest links, PromptVersion/SkillVersion trace, and ReviewHistory.
- This keeps evidence problems visible as reviewable discrepancy records before
  any UI, report generator, provider, or prompt runtime uses them.

Next slice name:

```text
Slice 46: TestKnowledgeCard Prompt Context Review Discrepancy Tracking Contract
```

Smallest useful boundary:

- Define discrepancy input references from review summary export artifact ids,
  audit review decision artifact ids, audit summary artifact ids, prompt
  context consumption artifact ids, accepted/questioned/rejected citations,
  skipped evidence, unsupported claims, unresolved follow-up flags, source
  hashes, context manifest ids, PromptVersion/SkillVersion ids, and
  ReviewHistory ids.
- Define discrepancy outputs such as discrepancy artifact id, discrepancy type,
  affected citation ids, evidence gap summary, mismatch reason, reviewer note,
  severity, resolution status, ReviewHistory links, failure code, and visible
  reason.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No frontend page, report generation behavior change, actual report renderer,
  export/download endpoint, backend feature API, prompt assembly
  implementation, prompt runtime execution, provider call, LLM call, prompt
  runner, deterministic retrieval behavior change, vector database, embeddings,
  reranking, background indexing, graph runtime, MCP runtime, provider SDK,
  credentials, migration, broad TestKnowledgeCard CRUD, automatic prompt
  eligibility, automatic card creation, automatic knowledge ingestion, artifact
  mutation outside declared discrepancy tracking evidence, historical evidence
  mutation, generated-case auto-approval, runner behavior, RBAC, tenants,
  permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 46 Task 1: Add TestKnowledgeCard Prompt Context Review Discrepancy Tracking task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-46-test-knowledge-card-prompt-context-review-discrepancy-tracking-contract.md`.
- No product code until the plan defines discrepancy inputs, discrepancy
  outputs, severity/status fields, failure behavior, and non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-46-test-knowledge-card-prompt-context-review-discrepancy-tracking-contract.md`.

## Completed Next V2 Slice

Completed: TestKnowledgeCard prompt context review discrepancy tracking
contract.

Why it was selected:

- Slice 45 packaged audit review decisions into exportable summaries, but
  Chtest still needed a contract for tracking discrepancies between consumed
  prompt context, audit summaries, review decisions, and summary exports
  without mutating underlying evidence.
- Slice 46 defined discrepancy inputs and outputs from review summary export
  artifacts, audit review decision artifacts, audit summary artifacts, prompt
  context consumption artifacts, affected citations, skipped evidence,
  unsupported claims, unresolved follow-up flags, source hashes, context
  manifest links, PromptVersion/SkillVersion trace, and ReviewHistory.
- The slice kept evidence problems visible as reviewable discrepancy records
  before any UI, report generator, provider, prompt runtime, or export
  endpoint uses them.

Completed slice name:

```text
Slice 46: TestKnowledgeCard Prompt Context Review Discrepancy Tracking Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- TestKnowledgeCard prompt context review discrepancy tracking is now a
  contract with `track_prompt_context_review_discrepancy`,
  `prompt_context_review_discrepancy`, discrepancy type, affected citation
  ids, evidence gap summary, mismatch reason, reviewer note, severity,
  resolution status, unsupported claim references, unresolved follow-up flags,
  ReviewHistory links, source hashes, context manifest references,
  PromptVersion/SkillVersion trace, and failure behavior.
- No frontend page, report generation behavior, export/download endpoint,
  prompt assembly implementation, prompt runtime execution, provider calls,
  retrieval ranking change, model output behavior implementation, automatic
  citation generation, vector database, embeddings, reranking, graph runtime,
  MCP runtime, backend feature API, migration, broad TestKnowledgeCard CRUD,
  automatic prompt eligibility, automatic card creation, automatic knowledge
  ingestion, artifact mutation outside declared prompt-context review
  discrepancy tracking, historical evidence mutation, generated-case
  auto-approval, runner behavior, RBAC, tenants, permissions, or remote CI
  provider behavior were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard prompt context discrepancy resolution review
contract.

Why:

- Slice 46 tracks prompt context discrepancies, but Chtest still needs a
  contract for reviewing and resolving discrepancy records without mutating
  the underlying review summaries, review decisions, audit summaries, prompt
  context consumption evidence, prompt context evidence, or knowledge evidence.
- The next narrow boundary should define resolution review inputs and outputs
  from discrepancy artifact ids, review summary export artifact ids, affected
  citation ids, discrepancy type, evidence gap summary, mismatch reason,
  severity, resolution status, reviewer notes, unresolved follow-up flags,
  source hashes, context manifest links, PromptVersion/SkillVersion trace, and
  ReviewHistory.
- This keeps discrepancy closure auditable before any UI, report generator,
  provider, prompt runtime, or export endpoint treats a discrepancy as
  acknowledged, rejected, or resolved by later review.

Next slice name:

```text
Slice 47: TestKnowledgeCard Prompt Context Discrepancy Resolution Review Contract
```

Smallest useful boundary:

- Define resolution review inputs from prompt context review discrepancy
  artifact ids, review summary export artifact ids, affected citation ids,
  discrepancy type, evidence gap summary, mismatch reason, severity,
  resolution status, unresolved follow-up flags, source hashes, context
  manifest ids, PromptVersion/SkillVersion ids, and ReviewHistory ids.
- Define resolution review outputs such as resolution review artifact id,
  resolution action, accepted/rejected/acknowledged discrepancy ids, reviewer
  note, follow-up flags, ReviewHistory links, failure code, and visible reason.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No frontend page, report generation behavior change, actual report renderer,
  export/download endpoint, backend feature API, prompt assembly
  implementation, prompt runtime execution, provider call, LLM call, prompt
  runner, deterministic retrieval behavior change, vector database, embeddings,
  reranking, background indexing, graph runtime, MCP runtime, provider SDK,
  credentials, migration, broad TestKnowledgeCard CRUD, automatic prompt
  eligibility, automatic card creation, automatic knowledge ingestion, artifact
  mutation outside declared discrepancy resolution review evidence, historical
  evidence mutation, generated-case auto-approval, runner behavior, RBAC,
  tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 47 Task 1: Add TestKnowledgeCard Prompt Context Discrepancy Resolution Review task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-47-test-knowledge-card-prompt-context-discrepancy-resolution-review-contract.md`.
- No product code until the plan defines resolution review inputs, resolution
  actions, discrepancy status handling, failure behavior, and non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-47-test-knowledge-card-prompt-context-discrepancy-resolution-review-contract.md`.

## Completed Next V2 Slice

Completed: TestKnowledgeCard prompt context discrepancy resolution review
contract.

Why it was selected:

- Slice 46 tracked prompt context discrepancies, but Chtest still needed a
  contract for reviewing and resolving discrepancy records without mutating
  review summaries, review decisions, audit summaries, prompt context
  consumption evidence, prompt context evidence, or knowledge evidence.
- Slice 47 defined resolution review inputs and outputs from discrepancy
  artifact ids, review summary export artifact ids, affected citation ids,
  discrepancy type, evidence gap summary, mismatch reason, severity, current
  resolution status, resolution action, accepted/rejected/acknowledged
  discrepancy ids, follow-up flags, source hashes, context manifest links,
  PromptVersion/SkillVersion trace, and ReviewHistory.
- The slice kept discrepancy closure auditable before any UI, report
  generator, provider, prompt runtime, or export endpoint treats a discrepancy
  as acknowledged, rejected, or resolved by later review.

Completed slice name:

```text
Slice 47: TestKnowledgeCard Prompt Context Discrepancy Resolution Review Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- TestKnowledgeCard prompt context discrepancy resolution review is now a
  contract with `review_prompt_context_discrepancy_resolution`,
  `prompt_context_discrepancy_resolution_review`, resolution action, accepted
  discrepancy ids, rejected discrepancy ids, acknowledged discrepancy ids,
  clarification requested fields, resulting resolution status, ReviewHistory
  links, source hashes, context manifest references, PromptVersion/SkillVersion
  trace, failure code, and visible reason.
- No frontend page, report generation behavior, export/download endpoint,
  prompt assembly implementation, prompt runtime execution, provider calls,
  retrieval ranking change, model output behavior implementation, automatic
  citation generation, vector database, embeddings, reranking, graph runtime,
  MCP runtime, backend feature API, migration, broad TestKnowledgeCard CRUD,
  automatic prompt eligibility, automatic card creation, automatic knowledge
  ingestion, artifact mutation outside declared prompt-context discrepancy
  resolution review, historical evidence mutation, generated-case
  auto-approval, runner behavior, RBAC, tenants, permissions, or remote CI
  provider behavior were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard prompt context discrepancy resolution summary
export contract.

Why:

- Slice 47 defines human resolution reviews, but Chtest still needs a contract
  for packaging accepted, rejected, acknowledged, clarification-needed, and
  later-review-resolved discrepancy resolution evidence into a future summary
  handoff without changing frontend pages, report generation behavior, export
  endpoints, or prompt runtime behavior.
- The next narrow boundary should define summary export inputs and outputs from
  resolution review artifacts, discrepancy artifact ids, accepted/rejected/
  acknowledged discrepancy ids, affected citation ids, resulting resolution
  status, reviewer notes, follow-up flags, source hashes, context manifest
  links, PromptVersion/SkillVersion trace, and ReviewHistory.
- This keeps discrepancy resolution handoff auditable before any UI renderer,
  report generator, download endpoint, provider, or prompt runtime consumes
  the summary.

Next slice name:

```text
Slice 48: TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export Contract
```

Smallest useful boundary:

- Define summary export inputs from discrepancy resolution review artifact ids,
  prompt context review discrepancy artifact ids, review summary export
  artifact ids, accepted/rejected/acknowledged discrepancy ids, clarification
  requested fields, affected citation ids, resulting resolution status,
  follow-up flags, source hashes, context manifest ids, PromptVersion/
  SkillVersion ids, and ReviewHistory ids.
- Define summary export outputs such as resolution summary export artifact id,
  resolution outcome summary, accepted/rejected/acknowledged discrepancy
  groups, unresolved clarification fields, follow-up flags, ReviewHistory
  links, failure code, and visible reason.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No frontend page, report generation behavior change, actual report renderer,
  export/download endpoint, backend feature API, prompt assembly
  implementation, prompt runtime execution, provider call, LLM call, prompt
  runner, deterministic retrieval behavior change, vector database, embeddings,
  reranking, background indexing, graph runtime, MCP runtime, provider SDK,
  credentials, migration, broad TestKnowledgeCard CRUD, automatic prompt
  eligibility, automatic card creation, automatic knowledge ingestion, artifact
  mutation outside declared discrepancy resolution summary export evidence,
  historical evidence mutation, generated-case auto-approval, runner behavior,
  RBAC, tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 48 Task 1: Add TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md`.
- No product code until the plan defines resolution summary export inputs,
  outcome groups, unresolved clarification handling, failure behavior, and
  non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-48-test-knowledge-card-prompt-context-discrepancy-resolution-summary-export-contract.md`.

## Completed Next V2 Slice

Completed: TestKnowledgeCard prompt context discrepancy resolution summary
export contract.

Why it was selected:

- Slice 47 defined human discrepancy resolution reviews, but Chtest still
  needed a contract for packaging accepted, rejected, acknowledged,
  clarification-needed, and later-review-resolved discrepancy resolution
  evidence into a future summary handoff without changing frontend pages,
  report generation behavior, export endpoints, or prompt runtime behavior.
- Slice 48 defined resolution summary export inputs and outputs from resolution
  review artifacts, discrepancy artifact ids, accepted/rejected/acknowledged
  discrepancy ids, affected citation ids, resulting resolution status,
  reviewer notes, follow-up flags, source hashes, context manifest links,
  PromptVersion/SkillVersion trace, and ReviewHistory.
- The slice kept discrepancy resolution handoff auditable before any UI
  renderer, report generator, download endpoint, provider, or prompt runtime
  consumes the summary.

Completed slice name:

```text
Slice 48: TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- TestKnowledgeCard prompt context discrepancy resolution summary export is now
  a contract with `export_prompt_context_discrepancy_resolution_summary`,
  `prompt_context_discrepancy_resolution_summary_export`, resolution outcome
  summary, accepted discrepancy group, rejected discrepancy group,
  acknowledged discrepancy group, clarification requested field group,
  unresolved follow-up flag group, reviewer comment summary, resulting
  resolution status group, ReviewHistory links, source hashes, context
  manifest references, PromptVersion/SkillVersion trace, failure code, and
  visible reason.
- No frontend page, report generation behavior, export/download endpoint,
  prompt assembly implementation, prompt runtime execution, provider calls,
  retrieval ranking change, model output behavior implementation, automatic
  citation generation, vector database, embeddings, reranking, graph runtime,
  MCP runtime, backend feature API, migration, broad TestKnowledgeCard CRUD,
  automatic prompt eligibility, automatic card creation, automatic knowledge
  ingestion, artifact mutation outside declared prompt-context discrepancy
  resolution summary export, historical evidence mutation, generated-case
  auto-approval, runner behavior, RBAC, tenants, permissions, or remote CI
  provider behavior were added.

## Recommended Next V2 Slice

Recommended: TestKnowledgeCard prompt context discrepancy resolution audit
handoff contract.

Why:

- Slice 48 packages resolution reviews into summary export evidence, but Chtest
  still needs a contract for a final audit handoff bundle that links the
  resolution summary export back to discrepancy, review, audit, consumption,
  prompt evidence, source hashes, context manifest, PromptVersion/SkillVersion,
  and ReviewHistory without becoming a download endpoint or report renderer.
- The next narrow boundary should define audit handoff inputs and outputs from
  resolution summary export artifacts, resolution review artifacts,
  discrepancy artifacts, resolution outcome groups, affected citation ids,
  unresolved follow-up flags, source hashes, context manifest links,
  PromptVersion/SkillVersion trace, and ReviewHistory.
- This keeps the discrepancy resolution chain auditable as a handoff contract
  before any UI, report generator, provider, prompt runtime, or external
  archive consumes it.

Next slice name:

```text
Slice 49: TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff Contract
```

Smallest useful boundary:

- Define audit handoff inputs from prompt context discrepancy resolution
  summary export artifact ids, resolution review artifact ids, discrepancy
  artifact ids, review summary export artifact ids, resolution outcome summary,
  accepted/rejected/acknowledged discrepancy groups, clarification requested
  fields, affected citation ids, follow-up flags, source hashes, context
  manifest ids, PromptVersion/SkillVersion ids, and ReviewHistory ids.
- Define audit handoff outputs such as audit handoff artifact id, handoff
  summary, evidence chain status, included artifact ids, excluded artifact
  reasons, unresolved follow-up flags, ReviewHistory links, failure code, and
  visible reason.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No frontend page, report generation behavior change, actual report renderer,
  export/download endpoint, backend feature API, prompt assembly
  implementation, prompt runtime execution, provider call, LLM call, prompt
  runner, deterministic retrieval behavior change, vector database, embeddings,
  reranking, background indexing, graph runtime, MCP runtime, provider SDK,
  credentials, migration, broad TestKnowledgeCard CRUD, automatic prompt
  eligibility, automatic card creation, automatic knowledge ingestion, artifact
  mutation outside declared discrepancy resolution audit handoff evidence,
  historical evidence mutation, generated-case auto-approval, runner behavior,
  RBAC, tenants, permissions, or remote CI provider behavior.

Suggested next task:

```text
Slice 49 Task 1: Add TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md`.
- No product code until the plan defines audit handoff inputs, evidence chain
  status, included/excluded artifact handling, failure behavior, and non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-49-test-knowledge-card-prompt-context-discrepancy-resolution-audit-handoff-contract.md`.

## Completed Next V2 Slice

Completed: TestKnowledgeCard prompt context discrepancy resolution audit
handoff contract.

Why it was selected:

- Slice 48 packaged discrepancy resolution reviews into summary export
  evidence, but Chtest still needed a final audit handoff contract that linked
  the resolution summary export back to discrepancy, review, audit,
  consumption, prompt evidence, source hashes, context manifest,
  PromptVersion/SkillVersion, and ReviewHistory without becoming a download
  endpoint, report renderer, runtime prompt input, or external archive
  integration.
- Slice 49 defined audit handoff inputs and outputs from resolution summary
  export artifacts, resolution review artifacts, discrepancy artifacts, audit
  evidence, resolution outcome groups, affected citation ids, unresolved
  follow-up flags, source hashes, context manifest links,
  PromptVersion/SkillVersion trace, and ReviewHistory.
- The slice kept the full discrepancy resolution evidence chain auditable as a
  handoff contract before any UI, report generator, provider, prompt runtime,
  or external archive consumes it.

Completed slice name:

```text
Slice 49: TestKnowledgeCard Prompt Context Discrepancy Resolution Audit Handoff Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- TestKnowledgeCard prompt context discrepancy resolution audit handoff is now
  a contract with
  `build_prompt_context_discrepancy_resolution_audit_handoff`,
  `prompt_context_discrepancy_resolution_audit_handoff`, handoff summary,
  evidence chain status, included artifact ids, excluded artifact reasons,
  unresolved follow-up flags, unresolved evidence gaps, unsupported claim
  references, source manifest ids, source hashes, context manifest references,
  PromptVersion/SkillVersion trace, ReviewHistory links, failure code, and
  visible reason.
- No frontend page, report generation behavior, export/download endpoint,
  external archive integration, prompt assembly implementation, prompt runtime
  execution, provider calls, retrieval ranking change, model output behavior
  implementation, automatic citation generation, vector database, embeddings,
  reranking, graph runtime, MCP runtime, backend feature API, migration, broad
  TestKnowledgeCard CRUD, automatic prompt eligibility, automatic card
  creation, automatic knowledge ingestion, artifact upload/mutation/delete,
  artifact mutation outside declared prompt-context discrepancy resolution
  audit handoff, historical evidence mutation, generated-case auto-approval,
  runner behavior, RBAC, tenants, permissions, or remote CI provider behavior
  were added.

## Recommended Next V2 Slice

Recommended: KnowledgeAdapter provider evaluation plan contract.

Why:

- Slice 49 closes the prompt-context discrepancy audit-handoff contract chain.
  Before adding Haystack, LlamaIndex, or any external provider integration,
  Chtest needs a contract for evaluating providers as inert candidate
  KnowledgeAdapter options.
- The next narrow boundary should define provider evaluation inputs and outputs
  from provider names, versions, licenses, reference intake, provider_state,
  KnowledgeEvidence normalization expectations, fallback behavior, metrics,
  and disabled-by-default policy.
- This keeps external retrieval providers evaluable as evidence and policy
  records before any SDK, credential, external call, vector database,
  embedding, reranking, runtime retrieval, UI, RBAC, tenant, or permission
  behavior exists.

Next slice name:

```text
Slice 50: KnowledgeAdapter Provider Evaluation Plan Contract
```

Smallest useful boundary:

- Define evaluation inputs for candidate provider name, adapter type,
  provider version, license, supported modes, reference URLs or documentation
  snapshots, disabled-by-default policy, provider_state, and local fallback
  expectations.
- Define evaluation outputs such as evaluation artifact id, provider
  suitability status, KnowledgeEvidence normalization notes, citation
  traceability requirements, required redaction and safety checks, metrics,
  blocker reasons, fallback behavior, ReviewHistory links, failure code, and
  visible reason.
- Add one contract-level fixture and golden smoke after the contract is
  defined.

Explicit non-goals:

- No Haystack or LlamaIndex provider integration, provider SDK, external call,
  remote URL fetch, credential handling, OAuth, vector database, embeddings,
  reranking, background indexing, graph runtime, MCP runtime, runtime
  retrieval, prompt runtime execution, provider-backed prompt context
  evidence, frontend page, report generation behavior, migration, broad
  KnowledgeAdapter CRUD, automatic provider enablement, automatic knowledge
  ingestion, RBAC, tenants, permissions, runner behavior changes, remote CI
  behavior, or package upgrades.

Suggested next task:

```text
Slice 50 Task 1: Add KnowledgeAdapter Provider Evaluation Plan task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md`.
- No product code until the plan defines evaluation inputs, provider
  evaluation outputs, KnowledgeEvidence normalization, provider_state,
  fallback behavior, license/reference intake, disabled-by-default policy, and
  non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md`.

## Completed Next V2 Slice

Completed: KnowledgeAdapter provider evaluation plan contract.

Why it was selected:

- Slice 49 closed the prompt-context discrepancy audit-handoff chain, and
  Chtest needed a provider-facing contract before any Haystack, LlamaIndex, or
  external retrieval provider could be considered.
- Slice 50 defined provider evaluation inputs and outputs from provider names,
  versions, licenses, reference intake, provider_state, KnowledgeEvidence
  normalization expectations, fallback behavior, metrics, disabled-by-default
  policy, ReviewHistory, and visible failure reasons.
- The slice kept external retrieval providers evaluable as evidence and policy
  records before any provider SDK, credential, external call, vector database,
  embedding, reranking, runtime retrieval, UI, RBAC, tenant, or permission
  behavior exists.

Completed slice name:

```text
Slice 50: KnowledgeAdapter Provider Evaluation Plan Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- KnowledgeAdapter Provider Evaluation Plan is now a contract with
  `evaluate_knowledge_adapter_provider_plan`,
  `knowledge_adapter_provider_evaluation_plan`, candidate provider metadata,
  provider suitability status, KnowledgeEvidence normalization requirements,
  provider_state recommendation, disabled by default decision, fallback
  behavior, license review result, reference intake summary, metrics plan,
  blocker reasons, source hashes, ReviewHistory links, failure code, and
  visible reason.
- No Haystack or LlamaIndex provider integration, GraphRAG provider
  integration, provider SDK, external call, remote URL fetch, credential
  handling, OAuth, vector database, embeddings, reranking, background
  indexing, graph runtime, MCP runtime, runtime retrieval, prompt runtime
  execution, provider-backed prompt context evidence, frontend page, report
  generation behavior, migration, broad KnowledgeAdapter CRUD, automatic
  provider enablement, automatic knowledge ingestion, RBAC, tenants,
  permissions, runner behavior changes, remote CI behavior, or package
  upgrades were added.

## Recommended Next V2 Slice

Recommended: KnowledgeAdapter provider evaluation review decision contract.

Why:

- Slice 50 defines inert provider evaluation plan evidence, but Chtest still
  needs a human review decision contract for accepting, accepting with
  constraints, blocking, marking unsupported, or requesting revision on those
  provider evaluation records before any future integration work can rely on
  them.
- The next narrow boundary should define review inputs and outputs from the
  provider evaluation plan artifact, provider suitability status, license
  review result, reference intake summary, KnowledgeEvidence normalization
  notes, provider_state recommendation, fallback behavior, metrics, blocker
  reasons, source hashes, and ReviewHistory links.
- This keeps provider evaluation review auditable as a decision record without
  enabling providers, installing SDKs, fetching remote URLs, creating vector
  infrastructure, running retrieval, or changing prompt context behavior.

Next slice name:

```text
Slice 51: KnowledgeAdapter Provider Evaluation Review Decision Contract
```

Smallest useful boundary:

- Define review inputs from KnowledgeAdapter provider evaluation plan artifact
  ids, candidate provider metadata, provider suitability status, license
  review result, reference intake summary, metrics, fallback labels,
  source hashes, source manifest ids, and ReviewHistory ids.
- Define review outputs such as provider evaluation review decision artifact
  id, review decision, reviewer note, accepted-for-planning status, accepted
  with constraints status, blocked status, unsupported status, requested
  revision fields, unresolved safety questions, ReviewHistory link, failure
  code, and visible reason.
- Add one contract-level fixture and golden smoke after the review decision
  contract is defined.

Explicit non-goals:

- No provider enablement, Haystack provider integration, LlamaIndex provider
  integration, GraphRAG provider integration, provider SDK, API key handling,
  credentials, OAuth, remote URL fetch, external call, network retrieval,
  runtime retrieval, provider-backed prompt context evidence, prompt assembly
  implementation, prompt runtime execution, automatic `used_knowledge=true`,
  vector database, vector index, embeddings, reranking, background indexing,
  graph runtime, MCP runtime, frontend page, report generation behavior,
  export/download endpoint, backend feature API, migration, package upgrade,
  broad KnowledgeAdapter CRUD, automatic knowledge ingestion,
  TestKnowledgeCard CRUD, automatic prompt eligibility, artifact upload,
  Artifact mutation outside declared review evidence, historical evidence
  mutation, generated-case auto-approval, runner behavior, remote CI provider
  behavior, RBAC, tenants, or permissions.

Suggested next task:

```text
Slice 51 Task 1: Add KnowledgeAdapter Provider Evaluation Review Decision task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md`.
- No product code until the plan defines provider evaluation review inputs,
  review decision outputs, human review semantics, failure behavior, and
  non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md`.

## Completed Next V2 Slice

Completed: KnowledgeAdapter provider evaluation review decision contract.

Why it was selected:

- Slice 50 defined inert provider evaluation plan evidence, and Chtest needed
  an auditable local review decision before any future provider integration
  planning could rely on that evidence.
- Slice 51 defined review inputs and outputs from the provider evaluation plan
  artifact, provider suitability status, license review result, reference
  intake summary, KnowledgeEvidence normalization notes, provider_state
  recommendation, fallback behavior, metrics, source hashes, source manifest
  ids, and ReviewHistory links.
- The slice kept provider review decisions local and auditable as evidence
  before any provider SDK, credential, external call, vector database,
  embedding, reranking, runtime retrieval, UI, RBAC, tenant, or permission
  behavior exists.

Completed slice name:

```text
Slice 51: KnowledgeAdapter Provider Evaluation Review Decision Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- KnowledgeAdapter Provider Evaluation Review Decision is now a contract with
  `review_knowledge_adapter_provider_evaluation`,
  `knowledge_adapter_provider_evaluation_review_decision`, same-project
  provider evaluation plan artifact linkage, review decision/status labels,
  accepted-for-planning, accepted-with-constraints, blocked, needs-revision,
  unsupported, provider suitability status, KnowledgeEvidence normalization,
  provider_state recommendation, disabled by default decision, fallback
  behavior, license review result, reference intake summary, metrics plan,
  source hashes, ReviewHistory links, failure code, and visible reason.
- No provider enablement, Haystack or LlamaIndex provider integration,
  GraphRAG provider integration, provider SDK, external call, remote URL
  fetch, credential handling, OAuth, vector database, embeddings, reranking,
  background indexing, graph runtime, MCP runtime, runtime retrieval, prompt
  runtime execution, provider-backed prompt context evidence, frontend page,
  report generation behavior, migration, broad KnowledgeAdapter CRUD,
  automatic provider enablement, automatic knowledge ingestion, RBAC, tenants,
  permissions, runner behavior changes, remote CI behavior, or package
  upgrades were added.

## Recommended Next V2 Slice

Recommended: KnowledgeAdapter provider evaluation review summary export
contract.

Why:

- Slice 51 defines local review decisions, but Chtest still needs a narrow
  contract for exporting a review summary artifact that future integration
  planning can read without mutating provider state.
- The next boundary should summarize accepted_for_planning,
  accepted_with_constraints, blocked, needs_revision, unsupported, license
  review, reference intake, KnowledgeEvidence normalization, provider_state,
  fallback behavior, metrics, source hashes, and ReviewHistory while
  preserving failure visibility.
- This keeps provider review decisions portable as audit evidence without
  enabling providers, installing SDKs, fetching remote URLs, creating vector
  infrastructure, running retrieval, or changing prompt context behavior.

Next slice name:

```text
Slice 52: KnowledgeAdapter Provider Evaluation Review Summary Export Contract
```

Smallest useful boundary:

- Define summary export inputs from KnowledgeAdapter provider evaluation review
  decision artifact ids, provider evaluation plan artifact ids, review
  decision/status labels, reviewer notes, accepted constraints, blocked
  reasons, unsupported reasons, requested revision fields, unresolved safety
  questions, source hashes, source manifest ids, and ReviewHistory links.
- Define summary export outputs such as
  `knowledge_adapter_provider_evaluation_review_summary_export`, export
  artifact id, review summary status, exported decision groups, provider
  suitability summary, license/reference summary, KnowledgeEvidence
  normalization summary, fallback summary, failure code, and visible reason.
- Add one contract-level fixture and golden smoke after the summary export
  contract is defined.

Explicit non-goals:

- No provider enablement, Haystack provider integration, LlamaIndex provider
  integration, GraphRAG provider integration, provider SDK, API key handling,
  credentials, OAuth, remote URL fetch, external call, network retrieval,
  runtime retrieval, provider-backed prompt context evidence, prompt assembly
  implementation, prompt runtime execution, automatic `used_knowledge=true`,
  vector database, vector index, embeddings, reranking, background indexing,
  graph runtime, MCP runtime, frontend page, report generation behavior,
  export/download endpoint, backend feature API, migration, package upgrade,
  broad KnowledgeAdapter CRUD, automatic knowledge ingestion,
  TestKnowledgeCard CRUD, automatic prompt eligibility, artifact upload,
  Artifact mutation outside declared summary export evidence, historical
  evidence mutation, generated-case auto-approval, runner behavior, remote CI
  provider behavior, RBAC, tenants, or permissions.

Suggested next task:

```text
Slice 52 Task 1: Add KnowledgeAdapter Provider Evaluation Review Summary Export task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md`.
- No product code until the plan defines provider evaluation review summary
  export inputs, outputs, failure behavior, artifact boundaries, and
  non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-52-knowledge-adapter-provider-evaluation-review-summary-export-contract.md`.

## Completed Next V2 Slice

Completed: KnowledgeAdapter provider evaluation review summary export
contract.

Why it was selected:

- Slice 51 defined local provider evaluation review decisions, and Chtest
  needed a compact summary export contract that future provider integration
  planning can read without mutating provider state.
- Slice 52 defined summary export inputs and outputs from provider evaluation
  review decision artifact ids, provider evaluation plan artifact ids, review
  decision/status labels, reviewer notes, constraints, blocker reasons,
  unsupported reasons, requested revisions, unresolved safety questions,
  source hashes, source manifest ids, and ReviewHistory links.
- The slice kept provider review summaries portable as audit evidence before
  any provider SDK, credential, external call, vector database, embedding,
  reranking, runtime retrieval, frontend, report, export endpoint, RBAC,
  tenant, or permission behavior exists.

Completed slice name:

```text
Slice 52: KnowledgeAdapter Provider Evaluation Review Summary Export Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- KnowledgeAdapter Provider Evaluation Review Summary Export is now a
  contract with
  `export_knowledge_adapter_provider_evaluation_review_summary`,
  `knowledge_adapter_provider_evaluation_review_summary_export`, provider
  evaluation review decision artifact linkage, provider evaluation plan
  artifact linkage, review summary status, exported decision groups, provider
  suitability summary, license/reference summary, KnowledgeEvidence
  normalization summary, provider_state summary, disabled by default summary,
  fallback summary, metrics summary, source traceability summary,
  ReviewHistory summary, failure code, and visible reason.
- No provider enablement, Haystack or LlamaIndex provider integration,
  GraphRAG provider integration, provider SDK, external call, remote URL
  fetch, credential handling, OAuth, vector database, embeddings, reranking,
  background indexing, graph runtime, MCP runtime, runtime retrieval, prompt
  runtime execution, provider-backed prompt context evidence, frontend page,
  report generation behavior, export/download endpoint, migration, broad
  KnowledgeAdapter CRUD, automatic provider enablement, automatic knowledge
  ingestion, RBAC, tenants, permissions, runner behavior changes, remote CI
  behavior, or package upgrades were added.

## Recommended Next V2 Slice

Recommended: KnowledgeAdapter provider evaluation review audit handoff
contract.

Why:

- Slice 52 packages provider evaluation review decisions into summary export
  evidence, but Chtest still needs a final audit handoff contract that links
  the summary export back to the review decision, provider evaluation plan,
  candidate provider metadata, license/reference evidence, KnowledgeEvidence
  normalization expectations, provider_state recommendation, fallback
  behavior, disabled-by-default decision, source hashes, and ReviewHistory.
- The next narrow boundary should define what a future integration planning
  worker can consume as one evidence-chain bundle without approving or
  enabling a provider.
- This keeps provider evaluation review evidence traceable as a handoff
  contract before any SDK, credential, external call, vector infrastructure,
  runtime retrieval, prompt-context behavior, UI, RBAC, tenant, or permission
  behavior exists.

Next slice name:

```text
Slice 53: KnowledgeAdapter Provider Evaluation Review Audit Handoff Contract
```

Smallest useful boundary:

- Define audit handoff inputs from provider evaluation review summary export
  artifact ids, provider evaluation review decision artifact ids, provider
  evaluation plan artifact ids, candidate provider metadata, review
  decision/status labels, accepted constraints, blocked reasons, unsupported
  reasons, requested revision fields, unresolved safety questions,
  license/reference summaries, KnowledgeEvidence normalization summary,
  provider_state summary, fallback summary, metrics, source manifest ids,
  source hashes, and ReviewHistory ids.
- Define audit handoff outputs such as
  `knowledge_adapter_provider_evaluation_review_audit_handoff`, audit handoff
  artifact id, handoff summary, evidence chain status, included artifact ids,
  excluded artifact reasons, provider review decision group summary,
  unresolved blocker summary, unresolved safety question summary, disabled by
  default summary, source traceability summary, ReviewHistory links, failure
  code, and visible reason.
- Add one contract-level fixture and golden smoke after the audit handoff
  contract is defined.

Explicit non-goals:

- No provider enablement, Haystack provider integration, LlamaIndex provider
  integration, GraphRAG provider integration, provider SDK, API key handling,
  credentials, OAuth, remote URL fetch, external call, network retrieval,
  runtime retrieval, provider-backed prompt context evidence, prompt assembly
  implementation, prompt runtime execution, automatic `used_knowledge=true`,
  vector database, vector index, embeddings, reranking, background indexing,
  graph runtime, MCP runtime, frontend page, report generation behavior,
  export/download endpoint, backend feature API, migration, package upgrade,
  broad KnowledgeAdapter CRUD, automatic knowledge ingestion,
  automatic provider enablement, TestKnowledgeCard CRUD, artifact upload,
  artifact mutation outside declared audit handoff evidence, historical
  evidence mutation, provider evaluation review summary export mutation,
  provider evaluation review decision mutation, provider evaluation plan
  mutation, generated-case auto-approval, runner behavior, remote CI provider
  behavior, RBAC, tenants, or permissions.

Suggested next task:

```text
Slice 53 Task 1: Add KnowledgeAdapter Provider Evaluation Review Audit Handoff task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md`.
- No product code until the plan defines audit handoff inputs, evidence-chain
  outputs, included/excluded artifact handling, failure behavior, and
  non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-53-knowledge-adapter-provider-evaluation-review-audit-handoff-contract.md`.

## Completed Next V2 Slice

Completed: KnowledgeAdapter provider evaluation review audit handoff contract.

Why it was selected:

- Slice 52 packaged provider evaluation review decisions into summary export
  evidence, and Chtest needed a final audit handoff contract that links the
  summary export back to the review decision, provider evaluation plan,
  candidate provider metadata, license/reference evidence, KnowledgeEvidence
  normalization expectations, provider_state recommendation, fallback
  behavior, disabled-by-default decision, source hashes, and ReviewHistory.
- Slice 53 defined that evidence-chain bundle while keeping provider
  evaluation review evidence traceable before any SDK, credential, external
  call, vector infrastructure, runtime retrieval, prompt-context behavior, UI,
  RBAC, tenant, or permission behavior exists.

Completed slice name:

```text
Slice 53: KnowledgeAdapter Provider Evaluation Review Audit Handoff Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- KnowledgeAdapter Provider Evaluation Review Audit Handoff is now a contract
  with
  `build_knowledge_adapter_provider_evaluation_review_audit_handoff`,
  `knowledge_adapter_provider_evaluation_review_audit_handoff`, provider
  evaluation review summary export artifact linkage, provider evaluation
  review decision artifact linkage, provider evaluation plan artifact
  linkage, evidence chain status, included artifact ids, excluded artifact
  reasons, provider review decision group summary, unresolved blocker
  summary, unresolved safety question summary, unresolved follow-up flags,
  source traceability summary, ReviewHistory links, failure code, and visible
  reason.
- No provider enablement, Haystack or LlamaIndex provider integration,
  GraphRAG provider integration, provider SDK, external call, remote URL
  fetch, credential handling, OAuth, vector database, embeddings, reranking,
  background indexing, graph runtime, MCP runtime, runtime retrieval, prompt
  runtime execution, provider-backed prompt context evidence, frontend page,
  report generation behavior, export/download endpoint, migration, broad
  KnowledgeAdapter CRUD, automatic provider enablement, automatic knowledge
  ingestion, RBAC, tenants, permissions, runner behavior changes, remote CI
  behavior, or package upgrades were added.

## Recommended Next V2 Slice

Recommended: Generated Case Human Review Evidence Package contract.

Why:

- Slice 50-53 closed the KnowledgeAdapter provider evaluation review evidence
  chain through an audit handoff. Continuing provider-related work now risks
  drifting into provider enablement, SDK integration, or runtime retrieval.
- Chtest already has GeneratedCaseCandidate evidence fields, prompt-context
  evidence contracts, CaseReviewAgent findings, dedup signals, automation
  readiness signals, and ReviewHistory. The next narrow contract should
  package those into one human-review evidence bundle without approving or
  rejecting candidates.
- This keeps the core human review workflow evidence-driven before any UI,
  runtime API, automation drafting, provider integration, RBAC, tenant, or
  permission work exists.

Next slice name:

```text
Slice 54: Generated Case Human Review Evidence Package Contract
```

Smallest useful boundary:

- Define evidence package inputs from GeneratedCaseCandidate ids,
  `source_knowledge_evidence_ids`, `knowledge_evidence_refs_json`,
  `quality_score`, `review_findings_json`, `coverage_gap_notes`,
  `automation_readiness`, dedup findings, prompt context evidence artifact
  ids, prompt context consumption artifact ids, audit/discrepancy handoff
  artifact ids, and ReviewHistory ids.
- Define evidence package outputs such as
  `generated_case_human_review_evidence_package`, evidence package artifact
  id, candidate summary, evidence chain completeness, missing evidence
  summary, conflicting evidence summary, review blocker summary,
  dedup/readiness summary, human review checklist, failure code, and visible
  reason.
- Add one contract-level fixture and golden smoke after the evidence package
  contract is defined.

Explicit non-goals:

- No backend runtime API, endpoint, router, service, worker, queue, scheduler,
  migration, or package upgrade.
- No frontend page, store, component, report generation behavior, or
  export/download endpoint.
- No provider integration, provider SDK, external call, credential handling,
  OAuth, vector database, embeddings, reranking, background indexing, graph
  runtime, MCP runtime, runtime retrieval, provider-backed prompt context
  evidence, prompt execution, or AITask orchestration.
- No automatic `used_knowledge=true`, TestCase promotion,
  GeneratedCaseCandidate approve/reject mutation, automation draft creation,
  runner behavior changes, artifact upload, artifact mutation outside
  declared package evidence, RBAC, tenants, or permissions.

Suggested next task:

```text
Slice 54 Task 1: Add Generated Case Human Review Evidence Package task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md`.
- No contract edits or product code until the plan defines evidence package
  inputs, outputs, failure behavior, artifact boundaries, golden smoke plan,
  and non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md`.

## Completed Next V2 Slice

Completed: Generated Case Human Review Evidence Package contract.

Why it was selected:

- Slice 50-53 closed the KnowledgeAdapter provider evaluation review evidence
  chain. Chtest then needed a core generated-case human review evidence bundle
  that packages candidate content, knowledge evidence, review findings,
  dedup/readiness signals, prompt-context lineage, and ReviewHistory without
  approving or rejecting candidates.
- Slice 54 defined that bundle as contract-only evidence and kept it separate
  from GeneratedCaseCandidate state changes, TestCase promotion, automation
  draft creation, runtime APIs, UI, provider integrations, vector
  infrastructure, prompt execution, RBAC, tenants, and permissions.

Completed slice name:

```text
Slice 54: Generated Case Human Review Evidence Package Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- Generated Case Human Review Evidence Package is now a contract with
  `build_generated_case_human_review_evidence_package`,
  `generated_case_human_review_evidence_package`, GeneratedCaseCandidate
  linkage, candidate summary, knowledge evidence refs, review findings,
  quality score, coverage gap notes, automation readiness, dedup findings,
  prompt-context artifact lineage, evidence chain completeness,
  missing/conflicting evidence summaries, review blocker summary,
  dedup/readiness summary, human review checklist, ReviewHistory links,
  failure code, and visible reason.
- No backend runtime API, frontend page, provider integration, provider SDK,
  external call, credential handling, OAuth, vector database, embeddings,
  reranking, graph runtime, MCP runtime, runtime retrieval, prompt execution,
  AITask orchestration, automatic `used_knowledge=true`,
  GeneratedCaseCandidate approve/reject mutation, TestCase promotion,
  automation draft creation, artifact upload, RBAC, tenants, permissions,
  runner behavior changes, remote CI behavior, or package upgrades were added.

## Recommended Next V2 Slice

Recommended: Generated Case Human Review Decision contract.

Why:

- Slice 54 deliberately packages evidence for human review but does not produce
  a review decision and does not trigger actual candidate approval/rejection.
- The next narrow boundary is a decision evidence contract that consumes the
  Slice 54 evidence package and records reviewer intent as audit evidence
  before any real status mutation, TestCase promotion, automation drafting,
  runtime API, UI, provider integration, or RBAC work exists.
- A summary export or audit handoff would be premature until a generated case
  human review decision artifact exists.

Next slice name:

```text
Slice 55: Generated Case Human Review Decision Contract
```

Smallest useful boundary:

- Define decision inputs from
  `generated_case_human_review_evidence_package_artifact_id`,
  GeneratedCaseCandidate id/status, candidate summary, evidence chain
  completeness, missing/conflicting evidence summaries, review blocker
  summary, dedup/readiness summary, human review checklist, `quality_score`,
  `review_findings_json`, `coverage_gap_notes`, `automation_readiness`, dedup
  findings, duplicate ids, duplicate-of case id, prompt-context lineage
  artifact ids, source hashes, source manifest ids, and ReviewHistory links.
- Define decision outputs such as `generated_case_human_review_decision`,
  `review_generated_case_human_review_evidence_package`, decision artifact id,
  decision labels including `accepted_for_future_promotion`,
  `accepted_with_required_edits`, `needs_optimization`,
  `rejected_for_insufficient_evidence`, `blocked`, `duplicate`,
  `needs_more_evidence`, and `failed_validation`, reviewer label/comment,
  accepted constraints, requested edit fields, optimization request summary,
  rejection/blocker reasons, duplicate resolution notes, ReviewHistory links,
  failure code, and visible reason.
- Add one contract-level fixture and golden smoke after the decision contract
  is defined.

Explicit non-goals:

- No backend runtime API, endpoint, router, service, worker, queue, scheduler,
  migration, or package upgrade.
- No frontend page, store, component, report generation behavior, or
  export/download endpoint.
- No actual GeneratedCaseCandidate approve/reject mutation, status mutation,
  request optimization mutation, TestCase promotion, AutomationDraft creation,
  ToolInvocation creation, TestRun/TestResult creation, runner behavior
  change, or remote CI provider behavior.
- No prompt execution, AITask orchestration, automatic `used_knowledge=true`,
  provider integration, provider SDK, external call, credential handling,
  OAuth, remote URL fetch, vector database, embeddings, reranking, graph
  runtime, MCP runtime, runtime retrieval, RBAC, tenants, or permissions.
- No mutation of the evidence package, GeneratedCaseCandidate content,
  KnowledgeEvidence, prompt-context artifacts, ReviewHistory, historical
  evidence, or source artifacts.

Suggested next task:

```text
Slice 55 Task 1: Add Generated Case Human Review Decision task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md`.
- No contract edits or product code until the plan defines decision inputs,
  outputs, failure behavior, artifact boundaries, golden smoke plan, and
  non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md`.

## Completed Next V2 Slice

Completed: Generated Case Human Review Decision contract.

Why it was selected:

- Slice 54 deliberately packaged GeneratedCaseCandidate review evidence but
  did not record a human review decision or trigger candidate
  approval/rejection.
- Slice 55 added the narrow decision evidence boundary that consumes
  `generated_case_human_review_evidence_package_artifact_id` and records
  reviewer intent without changing GeneratedCaseCandidate status, promoting
  TestCase rows, creating AutomationDraft rows, or adding runtime/UI/provider
  behavior.

Completed slice name:

```text
Slice 55: Generated Case Human Review Decision Contract
```

Delivered output:

- Slice plan, data/API/state/artifact/prompt-skill contracts, fixture,
  contract-level golden smoke, and completion gate.
- Generated Case Human Review Decision is now a contract with
  `review_generated_case_human_review_evidence_package`,
  `generated_case_human_review_decision`,
  `generated_case_human_review_evidence_package_artifact_id`,
  GeneratedCaseCandidate linkage, candidate summary, evidence chain
  completeness, missing/conflicting evidence summaries, review blocker
  summary, dedup/readiness summary, human review checklist, `quality_score`,
  `review_findings_json`, `coverage_gap_notes`, `automation_readiness`, dedup
  findings, duplicate notes, prompt-context lineage, source hashes, source
  manifest ids, ReviewHistory links, decision labels, reviewer label/comment,
  accepted constraints, requested edit fields, optimization request summary,
  rejection/blocker reasons, duplicate resolution notes, failure code, and
  visible reason.
- No backend runtime API, frontend page, provider integration, provider SDK,
  external call, credential handling, OAuth, vector database, embeddings,
  reranking, graph runtime, MCP runtime, runtime retrieval, prompt execution,
  AITask orchestration, automatic `used_knowledge=true`,
  GeneratedCaseCandidate approve/reject mutation, request optimization
  mutation, TestCase promotion, automation draft creation, artifact upload,
  RBAC, tenants, permissions, runner behavior changes, remote CI behavior, or
  package upgrades were added.

## Recommended Next V2 Slice

Recommended: Generated Case Human Review Decision Summary Export contract.

Why:

- Slice 55 records per-candidate human review decision evidence but does not
  provide a bounded export that groups decision outcomes for later audit,
  reporting, or handoff work.
- The next narrow boundary is a summary export contract over one or more
  generated case human review decision artifacts. It can group
  `accepted_for_future_promotion`, `accepted_with_required_edits`,
  `needs_optimization`, `rejected_for_insufficient_evidence`, `blocked`,
  `duplicate`, `needs_more_evidence`, and `failed_validation` without
  mutating candidates or promoting TestCases.
- A final audit handoff would be premature until this summary export artifact
  exists.

Next slice name:

```text
Slice 56: Generated Case Human Review Decision Summary Export Contract
```

Smallest useful boundary:

- Define export inputs from `generated_case_human_review_decision_artifact_id`,
  `generated_case_human_review_evidence_package_artifact_id`,
  GeneratedCaseCandidate id/status, candidate summary, decision label,
  decision status, reviewer label/comment, accepted constraints, requested
  edit fields, optimization request summary, rejection/blocker reasons,
  duplicate resolution notes, ReviewHistory links, source hashes, and source
  manifest ids.
- Define export outputs such as
  `generated_case_human_review_decision_summary_export`,
  `build_generated_case_human_review_decision_summary_export`, summary export
  artifact id, exported decision groups, accepted-for-future-promotion
  summary, accepted-with-required-edits summary, needs-optimization summary,
  rejected-for-insufficient-evidence summary, blocked summary, duplicate
  summary, needs-more-evidence summary, failed-validation summary,
  included/excluded decision artifact ids, source traceability summary,
  failure code, and visible reason.
- Add one contract-level fixture and golden smoke after the summary export
  contract is defined.

Explicit non-goals:

- No backend runtime API, endpoint, router, service, worker, queue, scheduler,
  migration, or package upgrade.
- No frontend page, store, component, report generation behavior, report
  renderer, or export/download endpoint.
- No actual GeneratedCaseCandidate approve/reject mutation, status mutation,
  request optimization mutation, TestCase promotion, AutomationDraft creation,
  ToolInvocation creation, TestRun/TestResult creation, runner behavior
  change, or remote CI provider behavior.
- No prompt execution, AITask orchestration, automatic `used_knowledge=true`,
  provider integration, provider SDK, external call, credential handling,
  OAuth, remote URL fetch, vector database, embeddings, reranking, graph
  runtime, MCP runtime, runtime retrieval, RBAC, tenants, or permissions.
- No mutation of decision artifacts, evidence packages,
  GeneratedCaseCandidate content, KnowledgeEvidence, prompt-context artifacts,
  ReviewHistory, historical evidence, or source artifacts.

Suggested next task:

```text
Slice 56 Task 1: Add Generated Case Human Review Decision Summary Export task plan
```

Expected output:

- A small slice plan under `docs/implementation/slices/`.
- Plan file:
  `docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md`.
- No contract edits or product code until the plan defines summary export
  inputs, outputs, failure behavior, artifact boundaries, golden smoke plan,
  and non-goals.
- Slice plan added:
  `docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md`.
