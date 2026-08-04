# Current Development Context

Updated: 2026-08-04 (Asia/Shanghai)

Use this file to resume development in a new Codex task. Repository rules still
require reading `AGENTS.md`, `START_HERE_FOR_AI.md`, and `NEXT_AI_TASK.md` first.

## Resume Prompt

```text
Read AGENTS.md, START_HERE_FOR_AI.md, NEXT_AI_TASK.md, and
CURRENT_DEVELOPMENT_CONTEXT.md. Tasks 49.15 through 49.22 are complete. Continue
Task 49.23 from NEXT_AI_TASK.md. Preserve unrelated pytest temp directories and
never use storage/chtest-dev.db for migration or smoke data.
```

## Product Direction

- AI may generate candidates, but cannot advance workflow or create formal
  assets by itself.
- Deterministic code validates facts; human review grants scoped approval;
  Runner output is execution truth.
- Every controlled action uses an immutable snapshot, server lock version, and
  exact approval decision. Changed input invalidates old approval.
- No evidence means `insufficient_evidence`; do not infer missing facts.
- Current scope remains local-first V1. Do not add RBAC, tenants, dashboards,
  cloud CI, broad RAG runtime, marketplace, or unrelated refactors.

## Git State

- Repository: `D:\Desktop\chenyan\Chtest-docs-preflight-vibecoding-fixes`
- Branch: `docs/preflight-vibecoding-fixes`
- Remote tracking: `origin/docs/preflight-vibecoding-fixes`
- Last pushed commit: `42b8383 feat(workflow): resume exact automation plan review`
- Previous backend campaign commit: `78c0ab3 feat(test-campaigns): add controlled campaign scope`
- Task 49.14 is committed and pushed.
- Task 49.15 is committed and pushed.
- Task 49.16 is committed and pushed.
- Task 49.17 is committed and pushed.
- Task 49.18 is committed and pushed.
- Task 49.19 and Task 49.20 are committed and pushed through `24e74b7`.
- Task 49.21 is committed and pushed as `42b8383`.
- Task 49.22 is complete and fully verified for its handoff commit.

Historical untracked `.pytest-tmp-*` directories and `.t49/` are test scratch
data. Do not stage, commit, or delete them.

## Completed Task 49.15

Goal: an AI Workbench Scope queue item must open the exact same-project
TestCampaign. It must never fall back to the newest campaign or browser state.

Implementation:

- `backend/app/modules/workflow_control/service.py`
  - Returns `/campaigns/scope?campaign_id={id}` only for an active Scope run
    whose UUID subject resolves to an active TestCampaign in the same project.
  - Malformed, missing, inactive, cross-project, and non-Scope subjects keep a
    null route.
- `backend/app/tests/workflow_control/test_workflow_queue.py`
  - Covers exact route and every fail-closed case above.
- `frontend/src/stores/testCampaigns.ts`
  - `load(projectId?, campaignId?)` fetches an explicit campaign directly.
  - Failed explicit restore clears campaign state and disables save; refresh
    retries the same id instead of listing/falling back.
- `frontend/src/views/campaigns/TestCampaignScopeView.vue`
  - Reads `campaign_id` from the route and passes it to the store.
  - Shows an explicit restore failure hint and keeps mutations locked.
- `frontend/src/views/campaigns/TestCampaignScopeView.spec.ts`
  - Covers exact-id loading and malformed-id fail-closed behavior; now 5 tests.
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
  - Confirms the queue renders the exact Scope link.
- `docs/contracts/02-api-contract.md`
  - Defines exact Scope route semantics and fail-closed behavior.

The intended commit message is
`feat(workflow): resume exact test campaign scope`.

## Verification Completed

- Focused backend queue: `2 passed`.
- Focused frontend Scope + AI Workbench: `2 files / 10 tests passed`.
- Full backend after Task 49.15 changes: `525 passed`.
- Full frontend: `26 files / 66 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Completed Task 49.16

Goal: an AI Workbench RequirementReview queue item may open the review page
only when the run's UUID subject resolves to an exact same-project
RequirementReview. The route must carry exact Requirement and
RequirementReview ids; explicit restore failure must not use local storage,
the newest Requirement, or prior browser state.

TestCampaign-origin RequirementReview runs currently retain their campaign id
as `subject_ref` and have no RequirementReview domain row. They must retain a
null route until that adjacent-stage contract is defined; Task 49.16 must not
guess or create one.

Implementation:

- The queue resolves only active same-project RequirementReview subjects at
  the `requirement_review` stage.
- The route includes exact Requirement, RequirementReview, and WorkflowRun ids.
- The frontend loads and verifies all three, clears state on any mismatch, and
  disables new review creation while explicit restore mode is active.
- Explicit failure never reads stale local-storage context.

Verification:

- Focused backend queue: `3 passed`.
- Focused RequirementReview + AI Workbench frontend: `2 files / 10 tests`.
- Full backend: `526 passed`.
- Full frontend: `26 files / 69 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Completed Task 49.17

Goal: extend exact queue restoration only to standard RiskReview runs using the
existing project-scoped RiskReview API. The route and page must verify the
Requirement, RequirementReview, WorkflowRun, and `risk_review` stage. Keep
TestCampaign-origin RequirementReview runs and later stages null.

Implementation:

- RiskReview queue routes require an active same-project RequirementReview
  subject and include exact Requirement, Review, WorkflowRun, and stage values.
- The frontend calls the project-scoped RiskReview API and rejects a generic
  RequirementReview response, mismatched run, or unsupported stage.
- RequirementReview routes remain backward compatible without a stage query.

Verification:

- Focused backend queue: `4 passed`.
- Focused RequirementReview + AI Workbench frontend: `2 files / 12 tests`.
- Full backend: `527 passed`.
- Full frontend: `26 files / 71 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Completed Task 49.18

Goal: extend exact queue restoration only to standard TestPlanReview runs using
the existing project-scoped TestPlanReview API. The route and page must verify
the Requirement, RequirementReview, WorkflowRun, and `test_plan_review` stage.
Keep CaseReview and TestCampaign-origin RequirementReview runs null.

Implementation:

- TestPlanReview route resolution requires an active same-project
  RequirementReview subject and emits exact Requirement, review, run, and stage
  identifiers.
- The frontend selects the TestPlanReview API for the explicit stage and fails
  closed on unsupported stages or any authoritative response mismatch.
- RequirementReview and RiskReview restore behavior remains backward
  compatible; CaseReview and campaign-origin subjects remain unrouted.

Verification:

- Focused backend queue: `5 passed`.
- Focused RequirementReview + AI Workbench frontend: `2 files / 14 tests`.
- Full backend: `528 passed`.
- Full frontend: `26 files / 73 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Completed Task 49.19

Goal: improve the existing Requirement Review workbench's layout, visual
hierarchy, and responsive behavior without changing workflow, route, store, or
API semantics. Verify desktop and `390x844` mobile views in a real browser.

Implementation:

- Added stage/state/version context, icon-backed commands, responsive score and
  action layouts, and a complete two-by-two mobile workflow track.
- Stopped the evidence panel from stretching to the input panel's height and
  added a compact evidence empty state.
- Corrected page-local Arco Alert content so errors and blockers are readable.
- Preserved the existing APIs, store behavior, exact restore paths, workflow
  actions, and test selectors.

Verification:

- Focused RequirementReview: `1 file / 9 tests passed`.
- Full frontend: `26 files / 73 tests passed`.
- Production build passed with the existing large-chunk warning.
- Desktop `1440x900` and mobile `390x844` browser checks found no horizontal
  overflow; all four mobile workflow steps are visible.
- The isolated QA backend returned its existing missing Prompt/Skill 404 when
  asked to generate a live review, and the page displayed the full error text.
- `git diff --check` passed.

## Completed Task 49.20

Goal: extend exact queue restoration only to standard CaseReview runs through
the existing Case Generation Review page. Verify the exact RequirementReview
and WorkflowRun and fail closed without recent candidate/browser fallback.

Implementation:

- The workflow queue resolves `case_review` only for an active same-project
  RequirementReview owner and emits exact Requirement, RequirementReview,
  WorkflowRun, and stage values.
- The Case Generation Review store clears generation, candidate selection, and
  gate state before explicit restore, then verifies project ownership, review
  identity, exact `case_review` stage, and WorkflowRun id.
- Missing or mismatched explicit input fails closed without local storage,
  newest requirement/candidate recovery, or prior browser context.
- The page disables source switching and new candidate generation in explicit
  mode; controlled actions continue to use server lock versions and approval
  ids.

Verification:

- Focused backend queue: `6 passed`.
- Focused Case Generation Review + AI Workbench frontend: `2 files / 19 tests`.
- Frontend typecheck passed.
- Full backend: `529 passed`.
- Full frontend: `26 files / 79 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Completed Task 49.21

Goal: extend exact queue restoration only to standard AutomationPlanReview runs
through the existing Automation Draft Review page. Verify the exact
RequirementReview and WorkflowRun and fail closed without recent plan, draft,
approved-test-case, or browser fallback.

Implementation:

- The queue emits an exact Automation Draft Review route only for active
  same-project RequirementReview subjects at `automation_plan_review`.
- Explicit restore clears TestCase, plan, draft, plan/draft gate, and history
  state before directly loading Requirement, RequirementReview, and the
  project-scoped AutomationPlanReview gate.
- The page can display and act on the authoritative gate without restoring a
  stale AutomationPlan. Actions use the exact lock version; editing remains
  disabled without the plan decision payload.
- Explicit mode skips approved-TestCase, latest-draft, asset-list, and browser
  context recovery.

Verification:

- Focused backend queue: `7 passed`.
- Focused Automation Draft Review + AI Workbench frontend: `2 files / 18 tests`.
- Frontend typecheck passed.
- Full backend: `530 passed`.
- Full frontend: `26 files / 85 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Completed Task 49.22

Goal: extend exact queue restoration only to standard AutomationDraftReview
runs through the existing Automation Draft Review page. Verify the exact
RequirementReview and WorkflowRun and fail closed without recent draft, plan,
approved-test-case, or browser fallback.

Implementation:

- The queue emits the Automation Draft Review page only for exact
  `automation_draft_review` runs with active same-project RequirementReview
  ownership.
- Explicit restore clears plan, draft, both automation gates, TestCase,
  commands, and review history before loading the authoritative gate.
- The page displays AutomationDraftReview without loading a recent draft;
  submit, complete, approve, reject, and continue use the server lock, while
  draft-dependent edit remains disabled.
- Missing or mismatched explicit input never reads local-storage draft or asset
  context.

Verification:

- Focused backend queue: `8 passed`.
- Focused Automation Draft Review + AI Workbench frontend: `2 files / 24 tests`.
- Frontend typecheck passed.
- Full backend: `531 passed`.
- Full frontend: `26 files / 91 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Completed Task 49.23

Goal: extend exact queue restoration only to standard ExecutionApproval runs
through the existing pytest Execution page. Verify the exact RequirementReview
and WorkflowRun and fail closed without recent draft, command, run, or browser
fallback.

Implementation:

- The queue emits the pytest Execution page only for exact
  `execution_approval` runs with active same-project RequirementReview
  ownership.
- Explicit restore clears automation draft, framework, TestCommand, current
  run, recent runs, and approval-gate state before loading Requirement,
  RequirementReview, and the authoritative ExecutionApproval gate.
- The page displays the exact gate without loading a recent draft or command;
  controlled actions use the server lock, while snapshot editing and execution
  remain disabled without an exact executable source.
- Missing or mismatched explicit input never reads local-storage draft/run data
  or prior browser context.

Verification:

- Focused backend queue: `9 passed`.
- Focused pytest Execution + AI Workbench frontend: `2 files / 14 tests`.
- Frontend typecheck passed.
- Full backend: `532 passed`.
- Full frontend: `26 files / 97 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Completed Task 49.24

Goal: extend exact queue restoration only to standard ExecutionResultReview
runs through the existing Report Failure Analysis page. Verify the exact
RequirementReview and WorkflowRun and fail closed without recent TestRun,
report, failure-analysis, default-id, or browser fallback.

Implementation:

- The queue emits the Report Failure Analysis page only for exact
  `execution_result_review` runs with active same-project RequirementReview
  ownership.
- Explicit restore clears both reporting gates, the default/recent TestRun,
  failure analysis, and report before loading Requirement, RequirementReview,
  and the authoritative ExecutionResultReview gate.
- TestRun identity comes only from the gate's generated evidence; analysis and
  report generation remain locked until the exact gate is approved.
- Missing or mismatched explicit input never hydrates recent runs, loads
  ReportReview, or uses prior browser context.

Verification:

- Focused backend queue: `10 passed`.
- Focused Report Failure Analysis + AI Workbench frontend: `2 files / 14 tests`.
- Frontend typecheck passed.
- Full backend: `533 passed`.
- Full frontend: `26 files / 103 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Completed Task 49.25

Goal: extend exact queue restoration only to standard ReportReview runs through
the existing Report Failure Analysis page. Verify the exact RequirementReview
and WorkflowRun and fail closed without recent TestRun, report,
failure-analysis, default-id, or browser fallback.

Implementation:

- The queue emits the reporting page only for exact `report_review` runs with
  active same-project RequirementReview ownership.
- Explicit restore clears both reporting gates, TestRun, failure analysis, and
  report before loading Requirement, RequirementReview, ReportReview, and the
  exact server-listed Report.
- Report project and TestRun ownership are verified before the gate or report is
  exposed. Analysis/report generation stays disabled in terminal review mode.
- Approval and publish actions use the current server lock version and exact
  approval decision id.

Verification:

- Focused backend queue: `11 passed`.
- Focused Report Failure Analysis + AI Workbench frontend: `2 files / 21 tests`.
- Frontend typecheck passed.
- Full backend: `534 passed`.
- Full frontend: `26 files / 110 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Completed Task 49.26

Goal: polish the shared workbench shell, AI queue, pytest execution, and
reporting layouts for dense desktop work and readable mobile use without
changing workflow, route, API, approval, or persistence behavior.

Implementation:

- Reduced shared shell/header/content spacing while preserving the existing
  navigation structure and controls.
- Converted empty AI workflow queue buckets into compact three-column desktop
  panels with one-column responsive stacking; populated buckets retain full
  width for evidence scanning.
- Rebalanced pytest execution and reporting columns, removed forced equal panel
  heights, and made reporting evidence span the full detail width above paired
  analysis/report panels on wide desktops.
- Added explicit mobile heading/action stacking and kept exact workflow restore
  context readable without changing any route, store, API, or approval action.

Verification:

- Browser inspection passed at `1440x900` and `390x844` for the shared shell,
  AI Workbench, pytest execution, reporting, and mobile navigation drawer.
- No inspected page had horizontal overflow, overlapping controls, or clipped
  workflow identifiers.
- Frontend typecheck passed.
- Full backend: `534 passed`.
- Full frontend: `26 files / 110 tests passed`.
- Production build passed with the existing large-chunk warning.
- `git diff --check` passed.

## Running Local Services

- Frontend: `http://127.0.0.1:5173` (PID 30088, Vite).
- Backend: `http://127.0.0.1:8000` (PID 336, Uvicorn).
- The in-app browser can reach the frontend through
  `http://192.168.1.86:5173` and was verified on `/requirements/review`.
- The QA backend was started with isolated `.t49/campaign-ui.db`; never migrate,
  stamp, bootstrap, or write smoke data to `storage/chtest-dev.db`.

## Task 49.14 Browser Evidence

- Created a real TestCampaign with environment/version/scope/exit conditions.
- Server persisted requirement/risk coverage gaps.
- Completed submit -> human review -> approval -> continue using exact lock
  versions and approval id.
- Navigation occurred only after the server returned `requirement_review`.
- Desktop and `390x844` mobile had no horizontal overflow or overlapping
  action controls.

## Immediate Next Steps

1. Keep historical scratch directories and the protected source database
   untouched.
2. Retry pushing the local Slice 49 commits when GitHub connectivity is
   available.
3. Wait for the next product-owner priority; no Task 49.27 is currently queued.
