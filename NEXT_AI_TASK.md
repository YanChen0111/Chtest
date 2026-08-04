# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. Docker runtime work remains intentionally skipped because the local
Docker Desktop/WSL engine is unavailable.

## Current Slice

Slice 49: Human-Controlled AI Workflow.

## Current Task

Task 49.16 is complete. Task 49.17 makes an AI Workbench RiskReview queue link
restore the exact same-project Requirement, RequirementReview, and workflow run
named by the server instead of falling back to recent browser context.

Verified behavior:

1. AI output creates only a candidate snapshot and enters `waiting_review`.
2. Human complete, edit, reject, approve, and continue actions are project
   scoped and use server-owned state plus optimistic compare-and-swap.
3. Edit or selected regeneration creates a new snapshot and invalidates old
   approval; continue consumes one exact approval decision.
4. Atomic approve-and-continue rolls back decision, events, snapshot, and run
   changes together on conflict.
5. The frontend cannot navigate or create a formal document before the
   authoritative gate permits it.
6. TestPlanReview backend actions preserve the exact approved RiskReview
   snapshot, invalidate approval after edits, require explicit strategy for
   high/critical risks, and consume one exact approval before creating the
   adjacent CaseReview draft.
7. The RequirementReview page is stage-aware for RiskReview and TestPlanReview
   submit, complete, edit, approve, reject, and continue actions.
8. CaseReview backend actions preserve the exact approved TestPlanReview
   snapshot, require existing GeneratedCaseCandidate human review before
   approval/advance, invalidate approval after edits, and consume one exact
   approval before creating the adjacent AutomationPlanReview draft.
9. The CaseGenerationReview page loads the authoritative CaseReview gate and
   drives submit, complete, edit, approve, reject, continue, and
   approve-and-continue actions with server-owned lock versions.
10. AutomationPlanReview backend actions preserve the exact approved CaseReview
    snapshot, require at least one approved AutomationPlan before
    approval/advance, invalidate approval after edits, and consume one exact
    approval before creating the adjacent AutomationDraftReview draft.
11. The AutomationDraftReview page loads the authoritative AutomationPlanReview
    gate after plan generation and drives submit, complete, edit, approve,
    reject, continue, and approve-and-continue actions with server-owned lock
    versions.
12. AutomationDraftReview backend actions preserve the exact approved
    AutomationPlanReview snapshot, require at least one approved AutomationDraft
    before approval/advance, invalidate approval after edits, and consume one
    exact approval before creating the adjacent ExecutionApproval draft.
13. The AutomationDraftReview page loads the authoritative AutomationDraftReview
    gate after draft creation and drives submit, complete, edit, approve,
    reject, continue, and approve-and-continue actions with server-owned lock
    versions.
14. ExecutionApproval backend actions preserve the exact approved
    AutomationDraftReview snapshot, require a current ExecutionApproval approval
    decision before workflow-backed AutomationDraft execution, invalidate
    approval after edits, and consume one exact approval before creating the
    adjacent ExecutionResultReview draft.
15. The pytest execution page loads the authoritative ExecutionApproval gate
    for workflow-backed drafts and sends the server approval decision id when
    starting an approved run.
16. ExecutionResultReview backend actions preserve the exact approved
    ExecutionApproval snapshot, require generated TestRun and Artifact evidence,
    invalidate approval after edits, consume one exact approval before creating
    the adjacent ReportReview draft, and require the current
    ExecutionResultReview approval decision before workflow-backed failure
    analysis or report generation.
17. ReportReview backend actions preserve the exact approved
    ExecutionResultReview snapshot, require generated report and report
    Artifact evidence in the current snapshot, invalidate approval after edits,
    consume one exact terminal approval before publishing workflow-backed report
    candidates, and reject approval replay.
18. AI Workbench exposes a project-scoped, read-only WorkflowRun queue grouped
    by pending review, pending approval, and approved/can-continue state. Queue
    reads do not mutate workflow, domain, snapshot, approval, report, or
    artifact records.
19. TestCampaign persists explicit environment/version scope, exit conditions,
    selected requirement/risk/test-plan/case evidence, and deterministic
    covered/gap rows. Its Scope WorkflowRun requires exact human approval,
    invalidates approval after edits, consumes approval once on continue, and
    creates no execution or report records.
20. The TestCampaign Scope page exposes the server-owned campaign candidate,
    coverage rows, immutable snapshot hash, lock version, and exact approval id
    through one editable three-region review surface.
21. Scope submit, review, approve, reject, and continue actions stop on stale
    versions; successful continue navigates only after the backend returns the
    adjacent `requirement_review` stage.
22. AI Workbench Scope queue routes resolve only active same-project
    TestCampaign subjects. The Scope page restores the exact campaign id and
    fails closed without listing or selecting a different campaign.
23. Standard RequirementReview queue routes include exact Requirement,
    RequirementReview, and WorkflowRun ids. The page verifies all three and
    fails closed without local-storage or recent-record fallback.

## Previous Tasks Verified

- Added optional Alembic `20260714_0013`: PostgreSQL full-text GIN is always
  emitted; pgvector extension/native column/HNSW setup is capability-gated and
  does not block SQLite or PostgreSQL without extension privileges.
- Added safe `postgres_hybrid` configuration, capability snapshots, native
  embedding synchronization, full-text/vector candidate SQL, provider-neutral
  score normalization, dimension/freshness checks, and deterministic keyword
  fallback with `vector_score=null`.
- Added PostgreSQL dialect/offline DDL tests, fake capability/native-result
  tests, SQLite no-op migration/fallback tests, and existing consumer regressions.
- Post-implementation review split full-text and vector candidate CTEs, applies
  dimension-matched casts/filters, keeps the similarity threshold outside the
  HNSW-ordered pool, and prevents vector-only mode from admitting text-only
  candidates. Focused Task 47.4/47.5 verification is now `76 passed`.
- Online acceptance completed on isolated PostgreSQL 16.14 databases at
  `127.0.0.1:55432`: the plain database upgraded to head with GIN full-text
  only, while the pgvector database upgraded to head with native vector storage
  and the HNSW index. The application adapter returned a real hybrid match with
  `vector_score=1.0`; the limited database correctly reported no vector
  capability and never fabricated a vector score.
- Added dependency-free optional Qdrant/Haystack/LlamaIndex fake-client
  contracts, safe configuration validation, provider-visible routing, and
  deterministic no-client/failure/invalid-candidate fallback. Focused suite is
  `46 passed`.
- Added Alembic `20260715_0014` and evidence-backed GeneratedCaseCandidate
  fields for covered requirement/risk ids, case type, generation reason, gap
  notes, automation readiness, and quality assessment. Existing model output
  remains backward compatible through deterministic defaults. CaseGeneration
  and migration verification is `13 passed`.
- Added deterministic `CaseReviewAgent` and `CoverageGapAgent` quality
  functions plus automation readiness assessment. Candidate persistence now
  writes provider-neutral findings and blockers. Focused quality/CaseGeneration
  verification is `12 passed`.
- Added Alembic `20260715_0015`, typed same-project knowledge relationships,
  creation API validation, and persisted relationship edges in the graph
  response. Migration/API verification is `28 passed`.
- Added Alembic `20260715_0016` and reviewed feedback APIs. Approval creates an
  extracted card only; card approval remains separate. Migration/API
  verification is `29 passed`.
- Built the final RAG workbench at `/extension/knowledge-workbench` with KPI
  cards, next-action links, provider health/degraded state, retrieval log
  filters, evidence/trace columns, coverage summary, and responsive layouts.
- Added focused `RagWorkbenchView` coverage and preserved HTTP status codes in
  API errors so tester-facing diagnostics retain failures such as `502`.
- Frontend verification: `25 test files / 50 tests passed`; production build
  passed with the existing chunk-size warning; desktop and 390px mobile browser
  smoke confirmed reachable controls and no visible overlap.
- Added the contract-backed `GET /api/projects/{project_id}/evidence-trace`
  endpoint with bounded `q` search, project isolation, safe artifact refs, and
  retrieval diagnostics. The focused knowledge API suite is `27 passed`.
- Added global evidence trace search and a details drawer to the workbench,
  preserving source locators, evidence ids, provider/mode, fallback, latency,
  and safe artifact links. Full frontend verification remains `25 files / 50
  tests` after the trace integration; desktop and 390px mobile smoke passed.
- Added consistent recent-run resume actions, named `data-test` selectors,
  loading/empty/error/stale states, and safe downstream-state clearing across
  knowledge, case review/library, pytest/Playwright/Newman/JMeter execution,
  reporting, automation, and CI/CD pages.
- Frontend verification after the multi-page refactor: `26 test files / 53
  tests passed`; production build passed with the existing chunk-size warning;
  desktop and `390x844` multi-page smoke found no horizontal overflow.
- Added the final provider-neutral RAG eval fixture with two required cards, a
  distractor, an unsafe same-project card, and a cross-project card. Fixture
  metrics are recall `1.0`, precision `1.0`, and exclusion `1.0`; optional
  provider unavailability remains visible as degraded fallback.
- Final focused backend acceptance is `69 passed`; frontend remains `26 files /
  53 tests`; source DB SHA256 remains unchanged.

## Task 47.5 Acceptance Evidence

The temporary PostgreSQL acceptance environment is outside the repository and
uses empty test databases only:

- `chtest_plain_test` is owned by a limited role and has no pgvector extension;
- `chtest_vector_test` has pgvector `0.8.3`, native `embedding_vector`, and
  `ix_test_knowledge_embedding_vector_hnsw_64`;
- online migration, extension privilege behavior, native `<=>`, HNSW index
  planning, and native/fallback capability behavior were verified;
- the blocked `storage/chtest-dev.db` was not used for migration or smoke data.

Docker Desktop/WSL remains unavailable, but it no longer blocks this task.

## Product Value Answer

Test engineers can resume an actionable RiskReview directly from the read-only
workflow queue without acting on a stale RequirementReview or unrelated
browser selection.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/slices/slice-47-final-test-knowledge-rag-system.md`
9. `memory/08-session-handoff.md`
10. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Docker Desktop/WSL repair, provider runtime installation/deployment guides,
  graph/feedback, enterprise collaboration, marketplace, cloud CI, RBAC,
  tenants, permissions, unrelated frontend pages, or broad roadmap documents.

## Expected Files

Default write boundary for Task 49.17:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/contracts/02-api-contract.md
backend/app/modules/workflow_control/service.py
backend/app/tests/workflow_control/test_workflow_queue.py
frontend/src/stores/requirements.ts
frontend/src/views/requirements/RequirementReviewView.vue
frontend/src/views/requirements/RequirementReviewView.spec.ts
frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts
```

Explain any write outside this set before editing it.

## Verification Commands

Run backend and frontend regression plus the production build:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend/app/tests -q
npm --prefix frontend test -- --run
npm --prefix frontend run build
git diff --check
```

Latest Task 49.16 evidence:

- Focused backend queue verification => `3 passed`.
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests -q --basetemp .t49/task4916-full` => `526 passed`.
- Focused RequirementReview + AI Workbench frontend verification => `2 files / 10 tests passed`.
- `npm.cmd --prefix frontend test -- --run` with Node `v24.18.0` from `D:\Downloads\Chtest-env\node-v24.18.0-win-x64` => `26 files / 69 tests passed`.
- `npm.cmd --prefix frontend run build` with Node `v24.18.0` from `D:\Downloads\Chtest-env\node-v24.18.0-win-x64` => passed with the existing large-chunk warning
- `git diff --check` => passed

The source `storage/chtest-dev.db` remains blocked and read-only. Do not run
upgrade, stamp, bootstrap, or registry mutation against it.

## Acceptance

- A RiskReview queue item returns a route only when its UUID
  `subject_ref` resolves to a RequirementReview whose Requirement belongs to
  the same project and the current stage is `risk_review`.
- The route includes the exact Requirement, RequirementReview, WorkflowRun, and
  `risk_review` stage. Opening it uses the project-scoped RiskReview API and
  verifies all identifiers against the authoritative response.
- Missing, malformed, cross-project, mismatched-review, and non-RequirementReview
  subjects retain a null route or fail closed in the page.
- An explicit restore failure clears review state, disables controlled actions,
  and never falls back to local storage, the newest Requirement, or prior
  browser state.
- The AI Workbench remains read-only; the route is only a navigation hint and
  all mutations still require the RequirementReview API's server lock version.
- `git diff --check` passes.

## Commit Message

```text
feat(workflow): resume exact risk review
```

## Next Task

Task 49.17 connects only standard RiskReview WorkflowRuns to the existing exact
Requirement review page. Keep TestCampaign-origin RequirementReview runs null
until their adjacent-stage domain contract is defined. Do not add
TestPlanReview, CaseReview, generic route guesses, dashboards, RBAC, tenants,
cross-user collaboration, execution/report orchestration, or repair workflows.
