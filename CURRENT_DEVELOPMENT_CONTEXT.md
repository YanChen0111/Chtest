# Current Development Context

Updated: 2026-08-04 (Asia/Shanghai)

Use this file to resume development in a new Codex task. Repository rules still
require reading `AGENTS.md`, `START_HERE_FOR_AI.md`, and `NEXT_AI_TASK.md` first.

## Resume Prompt

```text
Read AGENTS.md, START_HERE_FOR_AI.md, NEXT_AI_TASK.md, and
CURRENT_DEVELOPMENT_CONTEXT.md. Tasks 49.15 through 49.17 are complete. Continue
Task 49.18 from NEXT_AI_TASK.md. Preserve unrelated pytest temp directories and
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
- Last pushed commit: `b31d8d4 feat(workflow): resume exact requirement review`
- Previous backend campaign commit: `78c0ab3 feat(test-campaigns): add controlled campaign scope`
- Task 49.14 is committed and pushed.
- Task 49.15 is committed and pushed.
- Task 49.16 is committed and pushed.
- Task 49.17 is implemented and fully verified for commit and push.

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

## Active Task 49.18

Goal: extend exact queue restoration only to standard TestPlanReview runs using
the existing project-scoped TestPlanReview API. The route and page must verify
the Requirement, RequirementReview, WorkflowRun, and `test_plan_review` stage.
Keep CaseReview and TestCampaign-origin RequirementReview runs null.

## Running Local Services

- Frontend: `http://127.0.0.1:5173` (PID 30088, Vite).
- Backend: `http://127.0.0.1:8000` (PID 336, Uvicorn).
- The in-app browser can reach the frontend through
  `http://192.168.37.84:5173` and is currently on `/requirements/review`.
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

1. Commit and push Task 49.17 with only its expected files plus this context
   file staged.
2. Read the Task 49.18 boundary in `NEXT_AI_TASK.md`.
3. Implement exact standard TestPlanReview route resolution and fail-closed
   frontend restore without broadening to later workflow stages.
4. Run focused verification first, then the required full regressions, build,
   and diff checks.
