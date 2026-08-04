# Session Handoff

## 2026-08-04 Slice 49.21 Exact AutomationPlanReview Resume

Task 49.21 is complete; next is Task 49.22 exact AutomationDraftReview
restoration from the AI Workbench workflow queue.

- The queue now returns `/automation/drafts` only for a standard
  `automation_plan_review` run whose UUID subject resolves to an active
  same-project RequirementReview owner.
- The route carries exact Requirement, RequirementReview, WorkflowRun, and
  stage values. Explicit page restoration verifies all identities through the
  Requirement APIs and project-scoped AutomationPlanReview API.
- Explicit restore clears TestCase, plan, draft, both workflow gates, and
  review-history state before loading. It never reads the latest approved case,
  latest automation draft, asset lists, or prior browser context.
- The authoritative AutomationPlanReview gate is visible without reconstructing
  a stale AutomationPlan. Submit, complete, approve, reject, and continue use
  the server lock version and approval id; snapshot editing stays disabled when
  no exact plan decision payload is available.
- Focused backend queue verification passed with `7 passed`; focused Automation
  Draft Review + AI Workbench verification passed with `2 files / 18 tests`;
  frontend typecheck passed.
- Full backend passed with `530 passed`; full frontend passed with `26 files /
  85 tests`; production build and `git diff --check` passed.
- The protected `storage/chtest-dev.db` and historical scratch directories were
  not modified.

Next: apply the same exact-subject, exact-run, and exact-stage rule only to
standard AutomationDraftReview runs. Do not add ExecutionApproval routing in
the same task.

## 2026-08-04 Slice 49.20 Exact CaseReview Resume

Task 49.20 is complete; next is Task 49.21 exact AutomationPlanReview
restoration from the AI Workbench workflow queue.

- The queue now returns a Case Generation Review route only for a standard
  `case_review` run whose UUID subject resolves to an active same-project
  RequirementReview owner.
- The route carries exact Requirement, RequirementReview, WorkflowRun, and
  `case_review` values. The page loads the exact Requirement and review plus the
  project-scoped CaseReview gate, then verifies every identity before exposing
  controlled actions.
- Explicit restore clears generation, candidate selection, CaseReview, and
  review-history state before loading. Missing or mismatched input stays
  cleared and never reads recent local-storage or newest-record context.
- The AI Workbench remains read-only; all CaseReview mutations still use the
  server-owned lock version and approval decision id.
- Focused backend queue verification passed with `6 passed`; focused Case
  Generation Review + AI Workbench verification passed with `2 files / 19
  tests`; frontend typecheck passed.
- Full backend passed with `529 passed`; full frontend passed with `26 files /
  79 tests`; production build and `git diff --check` passed.
- Historical `.pytest-tmp-*` and `.t49/` directories were preserved. The
  protected `storage/chtest-dev.db` was not used.

Next: apply the exact-subject, exact-run, and exact-stage rule only to standard
AutomationPlanReview runs through the existing Automation Draft Review page.
Do not add AutomationDraftReview routing in the same task.

## 2026-08-04 Slice 49.19 Requirement Review Workbench Polish

Task 49.19 is complete. The next scoped task is Task 49.20, exact CaseReview
queue restoration through the existing Case Generation Review page.

- Reworked the Requirement Review page into a denser input/evidence workbench
  with stage, state, and lock-version context at the top.
- Replaced the clipped mobile workflow rail with a complete two-by-two track;
  all four steps remain visible at `390x844` without horizontal overflow.
- Prevented the empty evidence panel from stretching to the input-panel height,
  added a compact evidence empty state, and made score/action layouts responsive.
- Added Arco icons to commands, preserved every existing `data-test` workflow
  action, and kept RequirementReview, RiskReview, and TestPlanReview semantics
  unchanged.
- Fixed five page-local Arco Alert usages so API errors, exact-restore failures,
  stale-input warnings, clarification blockers, and test-plan blockers render
  their actual text instead of an empty Alert body.
- Verification: focused RequirementReview `1 file / 9 tests`; full frontend `26
  files / 73 tests`; production build passed with the existing large-chunk
  warning; `git diff --check` passed.
- Browser QA at `1440x900` and `390x844` found no horizontal overflow. The
  isolated QA environment lacks the configured Prompt/Skill version, so a live
  review result could not be generated; the resulting 404 was rendered clearly,
  while populated review behavior remains covered by the focused component test.

## 2026-08-04 Slice 49.18 Exact TestPlanReview Resume

Task 49.18 is complete. The next scoped task is Task 49.19, focused responsive
layout and visual refinement for the existing Requirement Review workbench.

- Extended deterministic queue route resolution to active same-project
  TestPlanReview subjects without admitting CaseReview or campaign-origin
  RequirementReview subjects.
- Added `workflow_stage=test_plan_review` to the exact Requirement,
  RequirementReview, and WorkflowRun navigation hint.
- Explicit restoration uses the project-scoped TestPlanReview API and verifies
  stage, review identity, requirement identity, and workflow run identity before
  enabling controlled actions.
- Unsupported stages, malformed ids, cross-project subjects, missing records,
  and mismatched responses retain a null route or fail closed without using
  recent browser state.
- Verification: focused backend queue `5 passed`; full backend `528 passed`;
  focused RequirementReview + AI Workbench frontend `2 files / 14 tests`;
  full frontend `26 files / 73 tests`; production build passed with the existing
  large-chunk warning; `git diff --check` passed.
- The protected source database and historical pytest scratch directories were
  not modified.

## 2026-08-03 Slice 49.13 Controlled TestCampaign Scope

Task 49.13 is complete. The next scoped task is Task 49.14, a focused frontend
Scope page over the new campaign API.

- Added migration `20260803_0020` and the project-scoped TestCampaign model for
  environment/version scope, explicit exit conditions, selected evidence ids,
  and persisted deterministic coverage rows.
- Creating a campaign creates Scope iteration 1 on a
  `requirement_to_execution` WorkflowRun. Editing creates a new immutable Scope
  snapshot and invalidates earlier approval; no domain boolean controls the
  gate.
- Added create/list/read/edit/submit/complete/approve/reject/continue APIs.
  Continue consumes one exact current approval and advances only to an adjacent
  RequirementReview input snapshot.
- Coverage is computed from same-project Requirement, RiskItem,
  TestPlanReview snapshot approval, and selected active human-approved TestCase
  evidence. Missing links are explicit gaps.
- Campaign actions create no TestRun, TestResult, Artifact, FailureAnalysis, or
  Report records. The source `storage/chtest-dev.db` was not used.
- Verification: focused API/migration `6 passed`; full backend `524 passed`;
  frontend `25 files / 61 tests`; production build passed with the existing
  large-chunk warning; `git diff --check` passed.
- `backend/app/tests/db/test_alembic_upgrade_head.py` was the only necessary
  write outside the default Task 49.13 list because the migration regression
  hard-coded the previous Alembic head.

## 2026-08-03 Slice 49.12 AI Workbench Workflow Queue

Task 49.12 is complete; next is Task 49.13 lightweight TestCampaign and
coverage matrix entry.

- Added read-only `GET /api/projects/{project_id}/workflow-runs` queue over
  persisted WorkflowRun state.
- Queue groups active same-project runs into `waiting_review`,
  `waiting_approval`, and `can_continue`; draft, rejected, inactive,
  cross-project, and already-consumed terminal approvals are excluded.
- Queue items expose workflow kind, subject ref, current stage/state, lock
  version, snapshot id/hash, approval decision id when continuable, and a
  nullable route hint. Route hints remain null until the destination can
  restore the exact run; generic recent-context links are not emitted. The
  endpoint does not mutate workflow, domain records, reports, snapshots, or
  artifacts.
- AI Workbench now loads the queue alongside recent AI tasks and renders
  read-only grouped sections with explicit unavailable-route state; no
  approval, rejection, or continue actions are exposed from the queue.
- Verification: focused workflow queue backend `1 passed`; backend regression
  `521 passed / 1 symlink-capability test deselected`; focused AI Workbench
  frontend `1 file / 5 tests passed`; full frontend `25 files / 61 tests
  passed`; production build passed with the existing large-chunk warning;
  `git diff --check` passed.
- The deselected existing artifact-store test requires Windows symlink
  privilege unavailable to the current process (`WinError 1314`); its product
  assertion was not reached.
- Source `storage/chtest-dev.db` was not used.

## 2026-07-30 Slice 49.11 ReportReview Workflow Integration

Task 49.11 is complete; next is Task 49.12 AI Workbench workflow queue for
pending review, pending approval, and continuable tasks.

- Added project-scoped ReportReview read/submit/complete/edit/approve/reject/
  continue/approve-and-continue actions on the existing RequirementReview-owned
  WorkflowRun.
- ReportReview input preserves the exact approved ExecutionResultReview
  snapshot id/hash, source ExecutionApproval snapshot id/hash, generated
  TestRun ids, execution Artifact ids, generated Report ids, and Report
  Artifact ids.
- Workflow-backed report generation now creates an editable report candidate
  with `status=draft`; it cannot become formal `ready` output until
  ReportReview approval is recorded and consumed.
- ReportReview approval requires current same-project TestRun execution
  artifacts plus generated Report and Report Artifact evidence captured in the
  current immutable ReportReview snapshot. Editing the gate creates a JSON-safe
  report-decision snapshot and invalidates old approval.
- Publishing consumes one exact current ReportReview approval at the terminal
  ReportReview stage, marks generated reports `ready`, returns an authoritative
  lock version, and rejects approval replay.
- The reporting page now loads the authoritative ReportReview gate after report
  generation or ExecutionResultReview continuation, exposes fixed submit,
  complete, edit, approve, reject, and publish actions, and refreshes the
  report after publish.
- Contracts were updated for ReportReview API/state-machine/artifact evidence
  boundaries. `docs/contracts/04-artifact-contract.md` was a necessary write
  outside the prior Expected Files because Task 49.11 acceptance explicitly
  depends on report artifact evidence.
- Verification: focused reporting backend `9 passed`; full backend
  `521 passed`; full frontend `25 files / 60 tests passed`; production build
  passed with the existing large-chunk warning; `git diff --check` passed.
- Node/npm came from `D:\Downloads\Chtest-env\node-v24.18.0-win-x64` for this
  shell; no runtime files were committed. Source `storage/chtest-dev.db` was
  not used.

## 2026-07-29 Slice 49.10 ExecutionResultReview Workflow Integration

Task 49.10 is complete; next is Task 49.11 ReportReview workflow integration
from the exact approved ExecutionResultReview snapshot.

- Added project-scoped ExecutionResultReview read/submit/complete/edit/approve/
  reject/continue/approve-and-continue actions on the existing
  RequirementReview-owned WorkflowRun.
- ExecutionResultReview input preserves the exact approved ExecutionApproval
  snapshot id and hash, generated TestRun ids, execution Artifact ids, upstream
  AutomationDraftReview/AutomationPlanReview/CaseReview snapshot evidence, and
  execution decision evidence.
- ExecutionResultReview approval and advancement require generated TestRun
  evidence plus at least one persisted same-project TestRun Artifact. Edits
  create a JSON-safe immutable result-decision snapshot, re-enter review, and
  invalidate old approval.
- Workflow-backed failure analysis and automation execution report generation
  now require the current ExecutionResultReview approval decision id, or the
  same approval consumed by a recorded successful advance into ReportReview.
  Execution output alone no longer authorizes those reporting actions.
- The reporting page loads the authoritative ExecutionResultReview gate for
  workflow-backed runs, blocks failure-analysis/report actions before approval,
  and sends the approved decision id in both requests.
- Contracts were updated for the ExecutionResultReview API/state-machine
  boundary.
- Necessary writes outside the initial Expected Files: reporting router/schema/
  service and frontend reporting API/store were needed so the gate is enforced
  server-side and in the request contract, not only by page UI; the
  ExecutionArtifactTable spec gained auto-unmount cleanup to prevent Arco/jsdom
  teardown rAF residue during full Vitest.
- Verification: focused backend ExecutionResultReview/reporting/pytest/workflow
  `63 passed`; full backend `521 passed`; focused frontend reporting+pytest
  `2 files / 6 tests passed`; full frontend `25 files / 60 tests passed`;
  production build passed with the existing large-chunk warning;
  `git diff --check` passed.
- Temporary Node/npm remains isolated under `%TEMP%\chtest-task49-node`; it was
  not committed and did not change system PATH.
- No commit was created because the workspace already contains many unrelated
  uncommitted changes from prior tasks; commit only with path-limited staging
  after owner review.

## 2026-07-29 Slice 49.9 ExecutionApproval Workflow Integration

Task 49.9 is complete; next is Task 49.10 ExecutionResultReview workflow
integration from the exact approved ExecutionApproval snapshot.

- Added project-scoped ExecutionApproval read/submit/complete/edit/approve/
  reject/continue/approve-and-continue actions on the existing
  RequirementReview-owned WorkflowRun.
- ExecutionApproval input preserves the exact approved AutomationDraftReview
  snapshot id and hash. Advancing creates the adjacent ExecutionResultReview
  draft from the exact approved ExecutionApproval snapshot and records upstream
  AutomationDraftReview, AutomationPlanReview, and CaseReview snapshot
  evidence, approved AutomationDraft ids, execution decisions, and generated
  TestRun ids.
- Workflow-backed AutomationDraft execution now requires the current
  ExecutionApproval approval decision id. AI execution recommendations or
  approved draft code alone cannot create a TestRun.
- ExecutionApproval edits create a JSON-safe immutable execution-decision
  snapshot, re-enter human review, and invalidate old approval.
- The pytest execution page now loads the authoritative ExecutionApproval gate
  for workflow-backed drafts and sends the approved decision id when starting
  a run.
- Contracts were updated for the ExecutionApproval API/state-machine boundary.
- Verification: focused backend ExecutionApproval/pytest/workflow `55 passed`;
  full backend `521 passed`; focused frontend PytestExecutionView `1 file / 3
  tests passed`; full frontend `25 files / 59 tests passed`; production build
  passed with the existing large-chunk warning; `git diff --check` passed.
- Temporary Node/npm remains isolated under `%TEMP%\chtest-task49-node`; it was
  not committed and did not change system PATH.

## 2026-07-29 Slice 49.8 AutomationDraftReview Workflow Integration

Task 49.8 is complete; next is Task 49.9 ExecutionApproval workflow
integration from the exact approved AutomationDraftReview snapshot.

- Added project-scoped AutomationDraftReview read/submit/complete/edit/approve/
  reject/continue/approve-and-continue actions on the existing
  RequirementReview-owned WorkflowRun.
- AutomationDraftReview input preserves the exact approved AutomationPlanReview
  snapshot id and hash. Advancing creates the adjacent ExecutionApproval draft
  from the exact approved AutomationDraftReview snapshot and records the source
  AutomationDraftReview snapshot id/hash, source AutomationPlanReview snapshot
  id/hash, source CaseReview snapshot id/hash, approved AutomationPlan ids,
  approved TestCase ids, approved AutomationDraft ids, and draft decision
  evidence.
- Existing AutomationDraft creation/approval remains authoritative for draft
  code approval. AI draft output alone cannot approve code or execute tests.
- AutomationDraftReview approval and advancement require at least one approved
  AutomationDraft for an approved AutomationPlan in the AutomationPlanReview
  snapshot.
- AutomationDraftReview edits create a JSON-safe immutable draft-decision
  snapshot, re-enter human review, and invalidate old approval.
- The AutomationDraftReview page now loads the authoritative
  AutomationDraftReview gate after draft creation and drives server-owned
  workflow actions with lock versions.
- Contracts were updated for the AutomationDraftReview API/state-machine
  boundary.
- Verification: focused backend AutomationDraftReview/workflow `44 passed`;
  full backend `520 passed`; focused frontend AutomationDraftReview `1 file / 7
  tests passed`; full frontend `25 files / 58 tests passed`; production build
  passed with the existing large-chunk warning; `git diff --check` passed.
- Temporary Node/npm remains isolated under `%TEMP%\chtest-task49-node`; it was
  not committed and did not change system PATH.

## 2026-07-29 Slice 49.7 AutomationPlanReview Workflow Integration

Task 49.7 is complete; next is Task 49.8 AutomationDraftReview workflow
integration from the exact approved AutomationPlanReview snapshot.

- Added project-scoped AutomationPlanReview read/submit/complete/edit/approve/
  reject/continue/approve-and-continue actions on the existing
  RequirementReview-owned WorkflowRun.
- AutomationPlanReview input preserves the exact approved CaseReview snapshot
  id and hash. Advancing creates the adjacent AutomationDraftReview draft from
  the exact approved AutomationPlanReview snapshot and records the source
  AutomationPlanReview snapshot id/hash, source CaseReview snapshot id/hash,
  source TestPlanReview snapshot id/hash, approved candidate ids, approved
  TestCase ids, approved AutomationPlan ids, and plan decision evidence.
- Existing AutomationPlan creation/approval remains authoritative for
  individual plan approval. AI plan output alone cannot generate draft code,
  approve draft code, or execute tests.
- AutomationPlanReview approval and advancement require at least one approved
  AutomationPlan for an approved TestCase in the CaseReview snapshot.
- AutomationPlanReview edits create a JSON-safe immutable plan-decision
  snapshot, re-enter human review, and invalidate old approval.
- The AutomationDraftReview page now loads the authoritative
  AutomationPlanReview gate after plan generation and drives server-owned
  workflow actions with lock versions.
- Contracts were updated for the AutomationPlanReview API/state-machine
  boundary.
- Verification: focused backend AutomationPlanReview/CaseReview/workflow
  `49 passed`; full backend `519 passed`; focused frontend AutomationDraftReview
  `1 file / 6 tests passed`; full frontend `25 files / 57 tests passed`;
  production build passed with the existing large-chunk warning;
  `git diff --check` passed.
- Temporary Node/npm remains isolated under `%TEMP%\chtest-task49-node`; it was
  not committed and did not change system PATH.

## 2026-07-29 Slice 49.6 CaseReview Workflow Integration

Task 49.6 is complete; next is Task 49.7 AutomationPlanReview workflow
integration from the exact approved CaseReview snapshot.

- Added project-scoped CaseReview read/submit/complete/edit/approve/reject/
  continue/approve-and-continue actions on the existing RequirementReview-owned
  WorkflowRun.
- CaseReview input preserves the exact approved TestPlanReview snapshot id and
  hash. Advancing creates the adjacent AutomationPlanReview draft from the exact
  approved CaseReview snapshot and records the source CaseReview snapshot
  id/hash, source TestPlanReview snapshot id/hash, approved candidate ids,
  approved TestCase ids, and candidate decision evidence.
- Existing GeneratedCaseCandidate review remains authoritative for individual
  candidate approval/rejection and formal TestCase creation. CaseReview approval
  and advancement require final human-reviewed candidate states and at least one
  approved candidate with a TestCase.
- CaseReview edits create a JSON-safe immutable candidate-decision snapshot,
  re-enter human review, and invalidate old approval.
- The CaseGenerationReview page now loads the authoritative CaseReview gate and
  drives server-owned workflow actions with lock versions; the view no longer
  relies on browser state to decide advancement.
- Contracts were updated for the CaseReview API/state-machine boundary.
- Verification: focused backend CaseReview/workflow `46 passed`; full backend
  `518 passed`; focused frontend CaseGenerationReview `1 file / 8 tests
  passed`; full frontend `25 files / 56 tests passed`; production build passed
  with the existing large-chunk warning; `git diff --check` passed.
- Temporary Node/npm remains isolated under `%TEMP%\chtest-task49-node`; it was
  not committed and did not change system PATH.

## 2026-07-24 Slice 48.2 Immutable Case Grounding

Task 48.2 is complete; next is Task 48.3 fixed grounding evaluation.

- Added deterministic, hashed requirement claim snapshots to v2 case-generation
  AITask input without adding a database migration.
- Added Prompt/Skill v2 and multi-version registry discovery; published v1
  content remains unchanged for replay.
- Added per-candidate claim, semantic, risk-id, and knowledge-evidence-id
  validation. Any invalid candidate fails the complete batch before persistence.
- Persisted passing grounding assessments inside candidate quality evidence.
- The case-generation page defaults to v2, rejects stale document binding, and
  recovers the latest reviewed requirement when browser-local workflow ids are
  absent or empty.
- Runtime acceptance produced 5 grounded candidates from an 11-claim snapshot.
- Verification: backend `462 passed`; frontend `25 files / 54 tests`; build
  passed with the existing chunk-size warning; `git diff --check` passed.

## 2026-07-13 Case Generation Decision Gate And Coverage Dimensions

Current Task:
- User-requested P0/P1 completion for the chtest case-generation review flow;
  Docker/runtime repair remains intentionally skipped.

Completed:
- Added a pre-generation decision-table acknowledgement gate to the case
  generation page and API. Missing or false acknowledgement now returns
  `400 CASE_GENERATION_DECISION_TABLE_REQUIRED` without creating AITask or
  CaseGenerationTask rows.
- Added source-change reset for the decision-table gate so switching requirement
  document or advanced requirement/review IDs requires fresh acknowledgement.
- Added `coverage_dimensions_json` to GeneratedCaseCandidate with migration
  `20260713_0010_case_candidate_coverage_dimensions.py`.
- CaseGenerationAgent output must now include legal, non-empty
  `coverage_dimensions` with evidence for every candidate. Missing, empty,
  unknown-key, or evidence-less coverage dimensions fail schema validation and
  do not persist candidates.
- Removed frontend text heuristics for coverage. The case-generation review
  coverage matrix and candidate detail now display persisted backend coverage
  evidence only.
- Updated mock provider and OpenAI provider task instructions to request
  coverage dimensions; synced Prompt/Skill files, fixture seed copies, data/API
  contracts, state-machine rules, error-code contract, and golden fixture.
- Confirmed the AutomationDraft review page already exposes Playwright, API,
  and JMeter as automation-draft execution types; Docker execution remains out
  of scope for this session.

Verification:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_automation_plan.py backend/app/tests/api/test_test_knowledge_cards.py -q`
  - Result: `20 passed in 3.05s`.
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_test_knowledge_cards.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_model_connection_config.py backend/app/tests/api/test_extension_surface.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_automation_plan.py backend/app/tests/db/test_case_generation_models.py -q`
  - Result: `57 passed in 5.19s`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/settings/ProjectSettingsView.spec.ts src/views/extension/KnowledgeBaseView.spec.ts src/views/requirements/RequirementReviewView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts src/views/automation/AutomationDraftReviewView.spec.ts`
  - Result: `5` files passed, `16` tests passed.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run build`
  - Result: passed with existing Vite large chunk warning.
- `git diff --check`
  - Result: no output.

Risks / Remaining:
- Browser-smoke the end-to-end reviewer workflow after this commit/push:
  requirement review -> case generation -> automation plan/draft -> execution
  type selection for Playwright/API/JMeter. Docker/compose runtime verification
  remains skipped until Docker Desktop/WSL is repaired outside the repo.

Next recommended Task:
- Run local browser acceptance over the non-Docker workflow and capture any
  remaining UI/UX blockers for automation-draft execution selection.

## 2026-07-09 Requirement Clarification And Document Flow

Current Task:
- User-requested workflow upgrade for requirement review clarification,
  downloadable requirement documents, and case generation from prior
  requirement documents.

Completed:
- Requirement review requests now accept `supplement_text` and
  `clarification_answers`, persist them into AITask input as
  `clarification_context`, and support follow-up review without mutating the
  original Requirement silently.
- Added requirement document generation as local `requirement_md` Artifact
  records owned by `RequirementReview`.
- Requirement document responses include a generated document number, version,
  status, artifact id, and `/api/artifacts/{id}/download` URL.
- Added project-level requirement document listing.
- Case generation can now accept `requirement_document_artifact_id`; backend
  validates same project and same requirement before reading the Markdown into
  `input_json.requirement_document`.
- Requirement review page now shows a clarification supplement area,
  a re-review action, and a formal requirement document generation/download
  area.
- Case generation page now prefers selectable requirement documents, shows the
  document number/download link, and no longer submits placeholder Requirement
  and RequirementReview UUIDs when no source is available.
- Synced API, Artifact, Prompt/Skill, and error-code contracts for the new
  fields/endpoints.
- Updated the OpenAI Responses provider task instructions so real-model review
  and case generation understand clarification context and requirement document
  inputs.

Verification:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/ai_runtime/test_openai_responses_provider.py -q`
  - Result: `29 passed in 2.29s`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/requirements/RequirementReviewView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts`
  - Result: `2` files passed, `4` tests passed.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run build`
  - Result: passed with existing Vite large chunk warning.
- `D:\Git\cmd\git.exe diff --check`
  - Result: no output.

Changed files in this task:
- `backend/app/modules/requirements/schemas.py`
- `backend/app/modules/requirements/service.py`
- `backend/app/modules/requirements/router.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/router.py`
- `backend/app/modules/ai_runtime/providers/openai_responses_provider.py`
- `backend/app/tests/api/test_requirement_review.py`
- `backend/app/tests/api/test_case_generation.py`
- `frontend/src/api/requirements.ts`
- `frontend/src/api/cases.ts`
- `frontend/src/stores/workflowContext.ts`
- `frontend/src/stores/requirements.ts`
- `frontend/src/stores/cases.ts`
- `frontend/src/views/requirements/RequirementReviewView.vue`
- `frontend/src/views/requirements/RequirementReviewView.spec.ts`
- `frontend/src/views/cases/CaseGenerationReviewView.vue`
- `frontend/src/views/cases/CaseGenerationReviewView.spec.ts`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/contracts/06-error-code-contract.md`
- `memory/08-session-handoff.md`

Risks / Remaining:
- Requirement documents are persisted as Artifacts, not a separate table. This
  keeps the slice small, but future list/detail views that need richer document
  lifecycle may require a dedicated model.
- `CaseGenerationTask` stores the requirement document in AITask input evidence
  today; it does not yet have a first-class `requirement_document_artifact_id`
  DB column.
- RAG knowledge upload/selection remains incomplete. Existing deterministic
  local retrieval is still ContextArtifact-based and should be expanded in a
  separate slice.
- Automation draft generation still needs the later "automation plan -> approve
  plan -> generate code" workflow.
- Repository remains very dirty with unrelated changes; use path-limited
  review/staging only.

Next recommended Task:
- Build the automation generation bridge from reviewed TestCase/Requirement
  Document to an AutomationPlan review step before AutomationDraft code
  generation, or complete the RAG knowledge upload/retrieval-test UI first if
  prioritizing knowledge grounding.

## 2026-07-09 Model Connection Feedback Fix

Current Task:
- User-reported model connection test feedback gap in Project Settings.

Completed:
- Fixed Settings test connection so it sends the current form payload instead
  of always posting `{}`.
- Added detailed test feedback fields to the frontend display: backend
  message, error code, HTTP status, diagnostic, suggestion, and target URL.
- Hardened backend provider-error diagnostic summaries so common API key,
  bearer token, token, and secret patterns are redacted before display.
- Added focused backend and frontend tests for unsaved-form testing,
  HTTP 403 diagnostics, and secret non-echo behavior.
- Restarted the local backend and confirmed current saved model config tests
  successfully through `/api/settings/model-connection/test`.

Verification:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_model_connection_config.py backend/app/tests/ai_runtime/test_openai_responses_provider.py -q`
  - Result: `23 passed in 0.86s`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/settings/ProjectSettingsView.spec.ts`
  - Result: `1` file passed, `2` tests passed.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run build`
  - Result: passed with existing Vite large chunk warning.
- `D:\Git\cmd\git.exe diff --check`
  - Result: no output.
- `Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/settings/model-connection/test`
  - Result: `ok=true` for the saved `OpenAI/gpt-5.5` config.

Acceptance URL:
- Backend: `http://127.0.0.1:8000/health`
- Frontend: `http://127.0.0.1:5173/settings/project`

Risks:
- Repository still has a large unrelated dirty worktree. Use path-limited
  review/staging only.

## 2026-07-09 Other Pages Model Usage Follow-up

Current Task:
- Investigate why other pages looked unavailable after model connection test
  succeeded.

Completed:
- Found the first blocker was not the model: frontend stores used the hard-coded
  project id `00000000-0000-0000-0000-000000000101`, while the local dev DB
  initially only had another project id.
- Added a backend local default project fallback so every request session
  ensures the frontend acceptance project exists.
- Manually confirmed the saved model config works beyond the connection test:
  requirement review created a succeeded `RequirementReviewAgent` task with
  `OpenAI/gpt-5.5`, and case generation created a succeeded
  `CaseGenerationAgent` task with `OpenAI/gpt-5.5`.
- Added frontend workflow context so a successful requirement review records
  the latest requirement/review ids and the case generation page uses them
  instead of stale placeholder ids.

Verification:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_projects.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_model_connection_config.py -q`
  - Result: `35 passed in 2.01s`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/settings/ProjectSettingsView.spec.ts src/views/requirements/RequirementReviewView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts`
  - Result: `3` files passed, `4` tests passed.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run build`
  - Result: passed with existing Vite large chunk warning.
- `D:\Git\cmd\git.exe diff --check`
  - Result: no output.

Current known behavior:
- Requirement review and case generation are real-model capable now.
- Automation draft, reporting failure analysis, CICD analysis, and some
  execution/reporting pages still contain demo placeholder entity ids or
  intentionally deterministic/mock service paths; they need separate workflow
  linkage or seed data before they feel fully connected in the UI.

## 2026-07-08 Codex Config Model Connection Smoke

Current Task:
- User-requested operational model integration check after Slice 46.

Completed:
- Installed Git for Windows because `git` was missing from PATH in this
  PowerShell environment.
- Inspected current Codex config without printing secrets:
  `model_provider=OpenAI`, `model=gpt-5.5`, `review_model=gpt-5.5`,
  `model_reasoning_effort=xhigh`, provider `base_url=https://lucen.cc`,
  `wire_api=responses`, and auth key present in Codex auth state.
- Added an OpenAI Responses-compatible provider adapter selected by
  `AITask.model_provider`.
- Supported provider aliases: `openai`, `OpenAI`, `openai-compatible`,
  `openai_compatible`, `openai_responses`, and `responses`.
- Preserved mock provider behavior as the default and added focused coverage
  for provider selection.
- Hardened `LocalArtifactStore` temporary filenames for Windows long-path
  pytest temp directories.
- Ran a real provider smoke using current Codex config/auth. The request
  reached `https://lucen.cc/v1/responses` but failed with HTTP 403,
  `error code: 1010`.
- Ran a direct official endpoint comparison using the same key. The official
  OpenAI endpoint rejected the key with HTTP 401 invalid API key.
- Wrote one dev-database AI task for Web acceptance:
  `25735582-f388-461f-9ddd-285ffc5fc906`,
  `ConnectionSmokeAgent`, `OpenAI/gpt-5.5`, status `failed`,
  error code `OPENAI_PROVIDER_ERROR`.
- Backend remains available at `http://127.0.0.1:8000/health`; frontend
  remains available at `http://127.0.0.1:5173/`.

Verification:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_openai_responses_provider.py backend/app/tests/ai_runtime/test_ai_task_worker.py backend/app/tests/artifacts/test_artifact_store.py -q`
- Result: `44 passed in 1.16s`.
- Path-limited `git diff --check` for touched model-provider files returned no
  output.

Changed files:
- `backend/app/modules/ai_runtime/artifact_store.py`
- `backend/app/modules/ai_runtime/providers/factory.py`
- `backend/app/modules/ai_runtime/providers/openai_responses_provider.py`
- `backend/app/workers/handlers/ai_task_handler.py`
- `backend/app/tests/artifacts/test_artifact_store.py`
- `backend/app/tests/ai_runtime/test_ai_task_worker.py`
- `backend/app/tests/ai_runtime/test_openai_responses_provider.py`
- `memory/08-session-handoff.md`

Unverified / blocked:
- Real model completion is blocked by credentials/gateway, not by the Chtest
  provider adapter. Current Codex gateway returns HTTP 403 / 1010 from this
  backend process; direct OpenAI returns HTTP 401 invalid API key for the same
  key.
- Docker Desktop daemon is still not usable in this Windows environment from
  the web-start request. Docker Desktop processes run, but
  `docker desktop status` reports `stopped`; `docker version/info/compose up`
  return Docker API HTTP 500 on `dockerDesktopLinuxEngine`.
- Docker diagnostics report `wsl.exe` missing before repair, then WSL package
  install succeeded via winget, but `wsl --install --no-distribution` still
  fails because Windows cannot enable/find `VirtualMachinePlatform`
  (`0x800f080c`, `WSL_E_INSTALL_COMPONENT_FAILED`). Windows optional feature
  queries only show `MSMQ-Container`; WSL/VirtualMachinePlatform/Hyper-V
  features are absent from the component list.
- Docker repository config was still corrected while daemon is blocked:
  backend Dockerfile now starts FastAPI, backend compose build context now uses
  the repo root so `backend.app.main` imports correctly, and compose now passes
  `CHTEST_ARTIFACT_ROOT`.
- Local backend/frontend dev servers remain the active acceptance path.

Next recommended Task:
- Fix or replace the Codex/OpenAI API credential or gateway allowlist, then
  rerun the same provider smoke and the dev-database worker smoke.
- After external auth is corrected, create a successful `OpenAI/gpt-5.5`
  AI task in the dev DB and verify raw-output, parsed-output, schema-validation,
  and token-usage evidence in AI Workbench.
- To run Docker on this machine, repair Windows WSL/VirtualMachinePlatform
  optional features or use a Windows image that includes them, then restart
  Windows and rerun:
  `CHTEST_BACKEND_PORT=18000 CHTEST_FRONTEND_PORT=15173 VITE_API_BASE_URL=http://localhost:18000 docker compose -f deploy/docker-compose.yml up -d --build`.

## 2026-07-08 Slice 46 Completion Gate Complete

Current Slice:
- Slice 46: AI Workbench Evidence Table Empty States.

Current Task:
- Slice 46 Completion Gate.

Completed:
- Selected-task artifact summary now shows an explicit empty state when no
  artifact evidence is recorded.
- Selected-task LLM call log now shows an explicit empty state when no LLM call
  logs are recorded.
- Existing populated artifact and LLM call tables still render as before.
- Updated focused AI Workbench coverage with an empty selected-task fixture.
- Raw prompt, raw request, and raw LLM output remain metadata-only.
- `NEXT_AI_TASK.md` now points to selecting the next narrow V2 task.

Verification:
- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `4` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-46-ai-workbench-evidence-table-empty-states.md`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Commits:
- None in this run. Shared docs/memory files contain large unrelated
  dirty-worktree changes, so any future commit must use path-limited staging or
  partial staging.

Risks:
- The repository still has a large unrelated dirty worktree. Do not use broad
  staging.

Next recommended Task:
- Select another narrow V2 task outside broad refactors, RAG/MCP runtime, RBAC,
  tenants, package upgrades, and unrelated dirty areas.

## 2026-07-08 Slice 46 AI Workbench Evidence Table Empty States Plan

Current Slice:
- Slice 46: AI Workbench Evidence Table Empty States.

Current Task:
- Slice 46 Task 2: Show selected-task evidence table empty states.

Completed:
- Selected a narrow frontend-only AI Workbench empty-state task after Slice 45
  completion.
- Added `docs/implementation/slices/slice-46-ai-workbench-evidence-table-empty-states.md`.
- Updated `NEXT_AI_TASK.md` to Slice 46 Task 2.

Verification:
- Planning verification pending final Slice 46 implementation gate.

Risks:
- Keep this display-only: no backend, API shape, provider, prompt, skill,
  contract, fixture, raw LLM output, execution page, RAG runtime, MCP runtime,
  RBAC, tenants, or package changes.

Next recommended Task:
- Add focused AI Workbench coverage for a selected task with empty artifacts
  and empty LLM call logs, then run focused AI Workbench test, frontend build,
  and `git diff --check`.

## 2026-07-08 Slice 45 Completion Gate Complete

Current Slice:
- Slice 45: AI Workbench Token Usage Empty State.

Current Task:
- Slice 45 Completion Gate.

Completed:
- Empty task-level and LLM-call token usage metadata now renders as not
  recorded instead of a blank AI Workbench value.
- Non-empty token usage metadata still renders formatted token labels.
- Updated focused AI Workbench coverage with LLM-call token usage cell
  assertions for both recorded and empty metadata.
- Raw prompt, raw request, and raw LLM output remain metadata-only.
- `NEXT_AI_TASK.md` now points to selecting the next narrow V2 task.

Verification:
- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-45-ai-workbench-token-usage-empty-state.md`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Commits:
- None in this run. Shared docs/memory files contain large unrelated
  dirty-worktree changes, so any future commit must use path-limited staging or
  partial staging.

Risks:
- The repository still has a large unrelated dirty worktree. Do not use broad
  staging.

Next recommended Task:
- Select another narrow V2 task outside broad refactors, RAG/MCP runtime, RBAC,
  tenants, package upgrades, and unrelated dirty areas.

## 2026-07-08 Slice 45 AI Workbench Token Usage Empty State Plan

Current Slice:
- Slice 45: AI Workbench Token Usage Empty State.

Current Task:
- Slice 45 Task 2: Show not-recorded token usage empty state.

Completed:
- Selected a narrow frontend-only AI Workbench metadata empty-state task after
  Slice 44 completion.
- Added `docs/implementation/slices/slice-45-ai-workbench-token-usage-empty-state.md`.
- Updated `NEXT_AI_TASK.md` to Slice 45 Task 2.

Verification:
- Planning verification pending final Slice 45 implementation gate.

Risks:
- `compactJson` is shared by task-level `token_usage` and call-level
  `token_usage_json`; this slice intentionally applies the same not-recorded
  fallback to both.
- Keep this display-only: no backend, API shape, provider, prompt, skill,
  contract, fixture, raw LLM output, execution page, RAG runtime, MCP runtime,
  RBAC, tenants, or package changes.

Next recommended Task:
- Add focused AI Workbench coverage for empty token usage and update the shared
  display helper, then run focused AI Workbench test, frontend build, and
  `git diff --check`.

## 2026-07-08 Slice 44 Completion Gate Complete

Current Slice:
- Slice 44: AI Workbench Request Evidence Visibility.

Current Task:
- Slice 44 Completion Gate.

Completed:
- AI Workbench LLM call rows now show request evidence as recorded or not
  recorded.
- A local open link appears only when `request_artifact_id` matches an existing
  selected-task Artifact with `safe_to_show=true`.
- Raw prompt, raw request, and raw LLM output remain metadata-only.
- Updated focused AI Workbench coverage with per-call request evidence link
  assertions, including unsafe-artifact and missing-request negative paths.
- `NEXT_AI_TASK.md` now points to selecting the next narrow V2 task.

Verification:
- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-44-ai-workbench-request-evidence-visibility.md`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Commits:
- None in this run. Shared docs/memory files contain large unrelated
  dirty-worktree changes, so any future commit must use path-limited staging or
  partial staging.

Risks:
- The repository still has a large unrelated dirty worktree. Do not use broad
  staging.

Next recommended Task:
- Select another narrow V2 task outside broad refactors, RAG/MCP runtime, RBAC,
  tenants, package upgrades, and unrelated dirty areas.

## 2026-07-08 Slice 43 Completion Gate Complete

Current Slice:
- Slice 43: AI Workbench Parsed Output Evidence Visibility.

Current Task:
- Slice 43 Completion Gate.

Completed:
- AI Workbench LLM call rows now show parsed output evidence as recorded or not
  recorded.
- A local open link appears only when `parsed_artifact_id` matches an existing
  selected-task Artifact with `safe_to_show=true`.
- Raw LLM output remains metadata-only.
- Updated focused AI Workbench coverage with per-call evidence link assertions.
- `NEXT_AI_TASK.md` now points to selecting the next narrow V2 task.

Verification:
- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-43-ai-workbench-parsed-output-evidence-visibility.md`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Commits:
- None in this run. Shared docs/memory files contain large unrelated
  dirty-worktree changes, so any future commit must use path-limited staging or
  partial staging.

Risks:
- The repository still has a large unrelated dirty worktree. Do not use broad
  staging.

Next recommended Task:
- Select another narrow V2 task outside broad refactors, RAG/MCP runtime, RBAC,
  tenants, package upgrades, and unrelated dirty areas.

## 2026-07-08 Slice 43 AI Workbench Parsed Output Evidence Visibility Plan

Current Slice:
- Slice 43: AI Workbench Parsed Output Evidence Visibility.

Current Task:
- Slice 43 Task 2: Show parsed output evidence in AI Workbench.

Completed:
- Selected a narrow frontend-only AI Workbench evidence visibility task after
  Slice 42 completion.
- Added `docs/implementation/slices/slice-43-ai-workbench-parsed-output-evidence-visibility.md`.
- Updated `NEXT_AI_TASK.md` to Slice 43 Task 2.

Verification:
- Planning verification pending final Slice 43 implementation gate.

Risks:
- Keep this evidence visibility only: no backend, API shape, provider, prompt,
  skill, contract, fixture, raw LLM output, execution page, RAG runtime, MCP
  runtime, RBAC, tenants, or package changes.

Next recommended Task:
- Show parsed output evidence in `AiWorkbenchView.vue`, then run focused AI
  Workbench test, frontend build, and `git diff --check`.

## 2026-07-08 Slice 42 Completion Gate Complete

Current Slice:
- Slice 42: AI Workbench Context Manifest Evidence Visibility.

Current Task:
- Slice 42 Completion Gate.

Completed:
- AI Workbench task details now show context manifest evidence as recorded or
  not generated.
- A local open link appears only when `context_manifest_artifact_id` matches an
  existing selected-task Artifact with `safe_to_show=true`.
- Raw LLM output remains metadata-only.
- Updated focused AI Workbench coverage.
- `NEXT_AI_TASK.md` now points to selecting the next narrow V2 task.

Verification:
- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-42-ai-workbench-context-manifest-evidence-visibility.md`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Commits:
- None in this run. Shared docs/memory files contain large unrelated
  dirty-worktree changes, so any future commit must use path-limited staging or
  partial staging.

Risks:
- The repository still has a large unrelated dirty worktree. Do not use broad
  staging.

Next recommended Task:
- Select another narrow V2 task outside broad refactors, RAG/MCP runtime, RBAC,
  tenants, package upgrades, and unrelated dirty areas.

## 2026-07-08 Slice 42 AI Workbench Context Manifest Evidence Visibility Plan

Current Slice:
- Slice 42: AI Workbench Context Manifest Evidence Visibility.

Current Task:
- Slice 42 Task 2: Show context manifest evidence in AI Workbench.

Completed:
- Selected a narrow frontend-only AI Workbench evidence visibility task after
  Slice 41 completion.
- Added `docs/implementation/slices/slice-42-ai-workbench-context-manifest-evidence-visibility.md`.
- Updated `NEXT_AI_TASK.md` to Slice 42 Task 2.

Verification:
- Planning verification pending final Slice 42 implementation gate.

Risks:
- Keep this evidence visibility only: no backend, API shape, provider, prompt,
  skill, contract, fixture, raw LLM output, execution page, RAG runtime, MCP
  runtime, RBAC, tenants, or package changes.

Next recommended Task:
- Show context manifest evidence in `AiWorkbenchView.vue`, then run focused AI
  Workbench test, frontend build, and `git diff --check`.

## 2026-07-08 Slice 41 Completion Gate Complete

Current Slice:
- Slice 41: AI Workbench Artifact Link Accessibility.

Current Task:
- Slice 41 Completion Gate.

Completed:
- AI Workbench artifact summary open links now include row-specific
  `aria-label` and `title` attributes.
- Visible link text remains `打开`.
- Links still render only when an artifact is safe to show.
- Updated focused AI Workbench coverage.
- `NEXT_AI_TASK.md` now points to selecting the next narrow V2 task.

Verification:
- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-41-ai-workbench-artifact-link-accessibility.md`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Commits:
- None in this run. Shared docs/memory files contain large unrelated
  dirty-worktree changes, so any future commit must use path-limited staging or
  partial staging.

Risks:
- The repository still has a large unrelated dirty worktree. Do not use broad
  staging.

Next recommended Task:
- Select another narrow V2 task outside execution shell/form refactor, RAG/MCP
  runtime, RBAC, tenants, package upgrades, and unrelated dirty areas.

## 2026-07-08 Slice 41 AI Workbench Artifact Link Accessibility Plan

Current Slice:
- Slice 41: AI Workbench Artifact Link Accessibility.

Current Task:
- Slice 41 Task 2: Add accessible labels to AI Workbench artifact links.

Completed:
- Selected a narrow frontend-only AI Workbench accessibility task after Slice
  40 completion.
- Added `docs/implementation/slices/slice-41-ai-workbench-artifact-link-accessibility.md`.
- Updated `NEXT_AI_TASK.md` to Slice 41 Task 2.

Verification:
- Planning verification pending final Slice 41 implementation gate.

Risks:
- Keep this link-label only: no artifact URL, artifact lookup, raw LLM output,
  backend, provider, prompt, skill, contract, fixture, execution page, RAG
  runtime, MCP runtime, RBAC, tenants, or package changes.

Next recommended Task:
- Add `aria-label` and `title` to AI Workbench artifact summary open links,
  then run focused AI Workbench test, frontend build, and `git diff --check`.

## 2026-07-08 Slice 40 Completion Gate Complete

Current Slice:
- Slice 40: AI Task Schema Validation Evidence Visibility.

Current Task:
- Slice 40 Completion Gate.

Completed:
- AI Workbench LLM call rows now show schema-validation evidence as recorded or
  not recorded.
- A local open link appears only when `schema_validation_artifact_id` matches an
  existing selected-task Artifact with `safe_to_show=true`.
- Raw LLM output remains metadata-only.
- Updated focused AI Workbench coverage.
- `NEXT_AI_TASK.md` now points to selecting the next narrow V2 task.

Verification:
- `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts`
- Result: `1` file passed, `3` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-40-ai-task-schema-validation-evidence-visibility.md`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Commits:
- None in this run. Shared docs/memory files contain large unrelated
  dirty-worktree changes, so any future commit must use path-limited staging or
  partial staging.

Risks:
- The repository still has a large unrelated dirty worktree, including deleted
  knowledge-card, prompt, skill, fixture, and contract/test files. Do not use
  broad staging.

Next recommended Task:
- Select another narrow V2 task outside execution shell/form refactor, RAG/MCP
  runtime, RBAC, tenants, package upgrades, and unrelated dirty areas.

## 2026-07-08 Slice 40 AI Task Schema Validation Evidence Visibility Plan

Current Slice:
- Slice 40: AI Task Schema Validation Evidence Visibility.

Current Task:
- Slice 40 Task 2: Show schema-validation evidence in AI Workbench.

Completed:
- Selected a new narrow V2 task outside automatic execution-page cleanup.
- Added `docs/implementation/slices/slice-40-ai-task-schema-validation-evidence-visibility.md`.
- Updated `NEXT_AI_TASK.md` to Slice 40 Task 2.
- Explicitly documented that Slice 39 remains uncommitted because shared
  docs/memory files have large unrelated dirty-worktree changes; do not use
  broad staging.

Verification:
- Planning verification pending final Slice 40 implementation gate.

Risks:
- Keep Slice 40 frontend-only in AI Workbench.
- Do not touch backend, API shapes, contracts, fixtures, prompts, skills, RAG
  runtime, MCP runtime, execution pages, or the unrelated deleted
  knowledge-card chain.

Next recommended Task:
- Update `AiWorkbenchView.vue` and `AiWorkbenchView.spec.ts` only, then run the
  focused AI Workbench test, frontend build, and `git diff --check`.

## 2026-07-08 Slice 39 Completion Gate Complete

Current Slice:
- Slice 39: Execution Evidence Link Accessibility.

Current Task:
- Slice 39 Completion Gate.

Completed:
- Completed Slice 39 end to end.
- `ExecutionRunManifestPanel.vue` now adds row-specific `aria-label` and `title`
  attributes to local evidence open links.
- Visible link text remains `打开`, URLs remain unchanged, and links still render
  only when a row has `artifactId` and is available.

Verification:
- `npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionOutputArtifacts.spec.ts src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `12` files passed, `20` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-39-execution-evidence-link-accessibility.md`
- `frontend/src/views/execution/ExecutionRunManifestPanel.vue`
- `frontend/src/views/execution/ExecutionRunManifestPanel.spec.ts`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`
- `NEXT_AI_TASK.md`

Commits:
- None in this run. The working tree contains many unrelated unstaged
  modifications and deletions; any future commit must use path-limited staging.

Risks:
- The repository still has a large unrelated dirty worktree, including deleted
  knowledge-card, prompt, skill, fixture, and contract/test files. Do not use
  broad staging.
- Slice 39 implementation is verified but uncommitted; before new product-code
  work, path-limit review/stage/commit the Slice 39 files or explicitly record
  why they remain uncommitted.
- Remaining execution-page changes should be selected as a fresh product-value
  task or explicitly promoted as a broader shell/form refactor.

Next recommended Task:
- Select a new narrow V2 task outside automatic execution-page cleanup, or ask
  explicitly to promote execution page shell/form refactor scope.

## 2026-07-08 Slice 39 Execution Evidence Link Accessibility Plan

Current Slice:
- Slice 39: Execution Evidence Link Accessibility.

Current Task:
- Slice 39 Task 1: Add Execution Evidence Link Accessibility task plan.

Completed:
- Selected Slice 39 as the next narrow V2 task after Slice 38 completion.
- Added `docs/implementation/slices/slice-39-execution-evidence-link-accessibility.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 38 completion
  and the Slice 39 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 39 planning.

Verification:
- Planning references present.
- `git diff --check`: no output.

Risks:
- Continue to avoid the unrelated dirty knowledge-card/prompt/skill/fixture
  deletion chain.
- Keep this link-label only: no artifact URL, artifact lookup, row-building,
  backend, runner, page shell, report, or quality gate changes.

Next recommended Task:
- Add row-specific `aria-label` and `title` to `ExecutionRunManifestPanel.vue`
  evidence links, then run focused component and completion gates.

## 2026-07-08 Slice 38 Completion Gate Complete

Current Slice:
- Slice 38: Execution Output Artifact Definitions.

Current Task:
- Slice 38 Completion Gate.

Completed:
- Completed Slice 38 end to end.
- `executionOutputArtifacts.ts` now centralizes manifest output artifact
  definitions for pytest, Playwright, Newman, and JMeter execution pages.
- The pages keep manifest row semantics, artifact filters, artifact links,
  metrics, result tables, display helpers, and start/refresh behavior.

Verification:
- `npm --prefix frontend run test -- --run src/views/execution/executionOutputArtifacts.spec.ts src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `12` files passed, `20` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-38-execution-output-artifact-definitions.md`
- `frontend/src/views/execution/executionOutputArtifacts.ts`
- `frontend/src/views/execution/executionOutputArtifacts.spec.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`
- `NEXT_AI_TASK.md`

Commits:
- None in this run. The working tree contains many unrelated unstaged
  modifications and deletions; any future commit must use path-limited staging.

Risks:
- The repository still has a large unrelated dirty worktree, including deleted
  knowledge-card, prompt, skill, fixture, and contract/test files. Do not use
  broad staging.
- Remaining execution-page duplication is mostly shell/layout and entry forms.
  Treat that as a broader refactor and plan it explicitly before editing.

Next recommended Task:
- Stop automatic execution-page cleanup here unless the user explicitly
  promotes a broader execution page shell/form refactor. Otherwise select a new
  product value task outside the current execution cleanup thread.

## 2026-07-08 Slice 38 Execution Output Artifact Definitions Plan

Current Slice:
- Slice 38: Execution Output Artifact Definitions.

Current Task:
- Slice 38 Task 1: Add Execution Output Artifact Definitions task plan.

Completed:
- Selected Slice 38 as the next safe V2 slice after Slice 37 completion.
- Added `docs/implementation/slices/slice-38-execution-output-artifact-definitions.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 37 completion
  and the Slice 38 recommendation.
- `NEXT_AI_TASK.md` already points to Slice 38 planning.

Verification:
- Planning references present.
- `git diff --check`: no output.

Risks:
- Continue to avoid the unrelated dirty knowledge-card/prompt/skill/fixture
  deletion chain.
- Keep output artifact behavior definition-only: no artifact lookup, artifact
  filtering, manifest row-building semantics, backend, runner, report, or
  quality gate changes.

Next recommended Task:
- Add `executionOutputArtifacts.ts` and focused definition coverage, then
  refactor execution pages only after the helper test passes.

## 2026-07-07 Slice 37 Completion Gate Complete

Current Slice:
- Slice 37: Execution Display Helpers.

Current Task:
- Slice 37 Completion Gate.

Completed:
- Completed Slice 37 end to end.
- `executionDisplay.ts` now centralizes run status labels and run duration
  labels for pytest, Playwright, Newman, and JMeter execution pages.
- The pages keep layout, entry forms, JMeter parsed JTL duration formatting,
  result row shaping, run manifest, metrics panel, artifact table, result table,
  and start/refresh behavior.

Verification:
- `npm --prefix frontend run test -- --run src/views/execution/executionDisplay.spec.ts src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `11` files passed, `16` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-37-execution-display-helpers.md`
- `frontend/src/views/execution/executionDisplay.ts`
- `frontend/src/views/execution/executionDisplay.spec.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`
- `NEXT_AI_TASK.md`

Commits:
- None in this run. The working tree contains many unrelated unstaged
  modifications and deletions; any future commit must use path-limited staging.

Risks:
- The repository still has a large unrelated dirty worktree, including deleted
  knowledge-card, prompt, skill, fixture, and contract/test files. Do not use
  broad staging.
- Remaining execution-page duplication is mostly shell/layout and entry forms.
  Treat that as a broader refactor and plan it explicitly before editing.

Next recommended Task:
- Stop automatic frontend extraction here unless the user explicitly promotes a
  broader execution page shell/form refactor. Otherwise select a new product
  value task outside the current execution cleanup thread.

## 2026-07-07 Slice 37 Execution Display Helpers Plan

Current Slice:
- Slice 37: Execution Display Helpers.

Current Task:
- Slice 37 Task 1: Add Execution Display Helpers task plan.

Completed:
- Selected Slice 37 as the next safe V2 slice after Slice 36 completion.
- Added `docs/implementation/slices/slice-37-execution-display-helpers.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 36 completion
  and the Slice 37 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 37 planning.

Verification:
- Planning references present.
- `git diff --check`: no output.

Risks:
- Continue to avoid the unrelated dirty knowledge-card/prompt/skill/fixture
  deletion chain.
- Keep helper behavior display-only: no page layout, form, result data,
  backend, runner, report, or quality gate changes.

Next recommended Task:
- Add `executionDisplay.ts` and focused helper coverage, then refactor execution
  pages only after the helper test passes.

## 2026-07-07 Slice 36 Completion Gate Complete

Current Slice:
- Slice 36: Execution Result Table Panel.

Current Task:
- Slice 36 Completion Gate.

Completed:
- Completed Slice 36 end to end.
- `ExecutionResultTable.vue` now renders titled result table sections for
  pytest, Playwright, Newman, and JMeter execution pages.
- The pages keep runner-specific result columns, row data, JMeter row shaping,
  run manifest, metrics panel, artifact table, and start/refresh behavior.

Verification:
- `npm --prefix frontend run test -- --run src/views/execution/ExecutionResultTable.spec.ts src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `10` files passed, `14` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-36-execution-result-table-panel.md`
- `frontend/src/views/execution/ExecutionResultTable.vue`
- `frontend/src/views/execution/ExecutionResultTable.spec.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`
- `NEXT_AI_TASK.md`

Commits:
- None in this run. The working tree contains many unrelated unstaged
  modifications and deletions; any future commit must use path-limited staging.

Risks:
- The repository still has a large unrelated dirty worktree, including deleted
  knowledge-card, prompt, skill, fixture, and contract/test files. Do not use
  broad staging.

Next recommended Task:
- Select the next narrow V2 task after Slice 36 completion. Prefer staying in
  frontend execution-only cleanup unless a higher-priority blocker appears.

## 2026-07-07 Slice 36 Execution Result Table Panel Plan

Current Slice:
- Slice 36: Execution Result Table Panel.

Current Task:
- Slice 36 Task 1: Add Execution Result Table Panel task plan.

Completed:
- Selected Slice 36 as the next safe V2 slice after Slice 35 completion.
- Added `docs/implementation/slices/slice-36-execution-result-table-panel.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 35 completion
  and the Slice 36 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 36 planning.

Verification:
- Planning references present.
- `git diff --check`: no output.

Risks:
- Continue to avoid the unrelated dirty knowledge-card/prompt/skill/fixture
  deletion chain.
- Keep result behavior display-only: no result data, result column, parsed_result,
  backend, runner, report, or quality gate changes.

Next recommended Task:
- Add `ExecutionResultTable.vue` and focused component coverage, then refactor
  execution pages only after the component test passes.

## 2026-07-07 Slice 35 Completion Gate Complete

Current Slice:
- Slice 35: Execution Metrics Panel.

Current Task:
- Slice 35 Completion Gate.

Completed:
- Completed Slice 35 end to end.
- `ExecutionMetricsPanel.vue` now renders metric label/value tiles for pytest,
  Playwright, Newman, and JMeter execution pages.
- The pages keep runner-specific metric item computation, result tables,
  artifact filters, start/refresh behavior, and evidence links.

Verification:
- `npm --prefix frontend run test -- --run src/views/execution/ExecutionMetricsPanel.spec.ts src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `9` files passed, `13` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-35-execution-metrics-panel.md`
- `frontend/src/views/execution/ExecutionMetricsPanel.vue`
- `frontend/src/views/execution/ExecutionMetricsPanel.spec.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`
- `NEXT_AI_TASK.md`

Commits:
- None in this run. The working tree contains many unrelated unstaged
  modifications and deletions; any future commit must use path-limited staging.

Risks:
- The repository still has a large unrelated dirty worktree, including deleted
  knowledge-card, prompt, skill, fixture, and contract/test files. Do not use
  broad staging.

Next recommended Task:
- Plan Slice 36: Execution Result Table Panel. Keep it frontend execution-only
  and leave runner-specific result columns/row shaping on each page.

## 2026-07-07 Slice 35 Execution Metrics Panel Plan

Current Slice:
- Slice 35: Execution Metrics Panel.

Current Task:
- Slice 35 Task 1: Add Execution Metrics Panel task plan.

Completed:
- Selected Slice 35 as the next safe V2 slice after Slice 34 completion.
- Added `docs/implementation/slices/slice-35-execution-metrics-panel.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 34 completion
  and the Slice 35 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 35 planning.

Verification:
- Planning references present.
- `git diff --check`: no output.

Risks:
- Continue to avoid the unrelated dirty knowledge-card/prompt/skill/fixture
  deletion chain.
- Keep metric behavior display-only: no metric calculation, parsed_result,
  backend, runner, report, or quality gate changes.

Next recommended Task:
- Add `ExecutionMetricsPanel.vue` and focused component coverage, then refactor
  execution pages only after the component test passes.

## 2026-07-07 Slice 34 Completion Gate Complete

Current Slice:
- Slice 34: Execution Artifact Table Panel.

Current Task:
- Slice 34 Completion Gate.

Completed:
- Completed Slice 34 end to end.
- `ExecutionArtifactTable.vue` now renders execution artifact metadata and
  local open links for pytest, Playwright, Newman, and JMeter execution pages.
- The pages keep runner-specific artifact filters, metrics, result tables,
  start/refresh behavior, and existing read-only local artifact rules.
- `NEXT_AI_TASK.md` now points to Slice 35 planning.

Verification:
- `npm --prefix frontend run test -- --run src/views/execution/ExecutionArtifactTable.spec.ts src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `8` files passed, `12` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-34-execution-artifact-table-panel.md`
- `frontend/src/views/execution/ExecutionArtifactTable.vue`
- `frontend/src/views/execution/ExecutionArtifactTable.spec.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`
- `NEXT_AI_TASK.md`

Commits:
- None in this run. The working tree contains many unrelated unstaged
  modifications and deletions; any future commit must use path-limited staging.

Risks:
- The repository still has a large unrelated dirty worktree, including deleted
  knowledge-card, prompt, skill, fixture, and contract/test files. Do not use
  broad staging.

Next recommended Task:
- Plan Slice 35: Execution Metrics Panel. Keep it frontend execution-only and
  leave runner-specific metric computation on each page.

## 2026-07-07 Slice 34 Execution Artifact Table Panel Plan

Current Slice:
- Slice 34: Execution Artifact Table Panel.

Current Task:
- Slice 34 Task 2: Add shared execution artifact table component.

Completed:
- Selected Slice 34 as the next safe V2 slice after Slice 33 completion.
- Added `docs/implementation/slices/slice-34-execution-artifact-table-panel.md`.
- Updated `docs/implementation/10-v2-scope-options.md` with Slice 33 completion
  and the Slice 34 recommendation.
- Updated `NEXT_AI_TASK.md` to Slice 34 Task 2.

Verification:
- Planning references present.
- `git diff --check`: no output.

Risks:
- Continue to avoid the unrelated dirty knowledge-card/prompt/skill/fixture
  deletion chain.
- Keep artifact behavior read-only: no upload, delete, mutation, remote fetch,
  signed URLs, cloud storage, or broad artifact browser.

Next recommended Task:
- Add `ExecutionArtifactTable.vue` and focused component coverage, then refactor
  execution pages only after the component test passes.

## 2026-07-07 Slice 33 Completion Gate Complete

Current Slice:
- Slice 33: Execution Run Manifest Panel.

Current Task:
- Slice 33 Completion Gate.

Completed:
- Completed Slice 33 end to end.
- `ExecutionRunManifestPanel.vue` renders the shared read-only run manifest
  display for pytest, Playwright, Newman, and JMeter execution pages.
- The pages keep runner-specific output artifact definitions, metrics,
  artifact tables, start/refresh behavior, local link rules, and missing
  evidence visibility.

Verification:
- `npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts`
- Result: `7` files passed, `11` tests passed.
- `npm --prefix frontend run build`
- Result: passed with existing Vite large chunk warning.
- `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- Result: `1 passed`.
- `git diff --check`
- Result: no output.

Changed files in this slice:
- `docs/implementation/slices/slice-33-execution-run-manifest-panel.md`
- `frontend/src/views/execution/ExecutionRunManifestPanel.vue`
- `frontend/src/views/execution/ExecutionRunManifestPanel.spec.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/NewmanExecutionView.vue`
- `frontend/src/views/execution/JMeterExecutionView.vue`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`
- `NEXT_AI_TASK.md`

Commits:
- None in this run. The working tree contains many unrelated unstaged
  modifications and deletions; any future commit must use path-limited staging.

Risks:
- The repository still has a large unrelated dirty worktree, including deleted
  knowledge-card, prompt, skill, fixture, and contract/test files. Do not use
  broad staging.

Next recommended Task:
- Select and plan the next narrow V2 slice after Slice 33, staying out of the
  deleted knowledge-card/prompt/skill/fixture chain unless the user explicitly
  promotes that scope.

## 2026-07-07 Slice 33 Execution Run Manifest Panel Implementation 完成

本轮完成：

- 完成 Slice 33 Task 2：Add shared execution run manifest panel component。
- 完成 Slice 33 Task 3：Use shared panel in execution pages。
- 新增 `frontend/src/views/execution/ExecutionRunManifestPanel.vue`。
- 新增 `frontend/src/views/execution/ExecutionRunManifestPanel.spec.ts`。
- Pytest、Playwright、Newman、JMeter 执行页已复用 shared manifest panel。
- 页面保留各自 runner-specific metrics、artifact tables、start/refresh 行为。
- 本地打开链接规则保持不变：只有 id 存在于 `TestRunRead.artifacts` 的持久化
  local Artifact 行时才渲染链接。
- `NEXT_AI_TASK.md` 已切换到 Slice 33 Completion Gate。

本轮验证：

```powershell
npm --prefix frontend run test -- --run src/views/execution/ExecutionRunManifestPanel.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

验证结果：

- Focused frontend specs：`5` files passed，`5` tests passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- `git diff --check`：no output。

风险提醒：

- 当前 working tree 仍有大量与 Slice 33 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- Completion gate 后若要提交，必须 path-limited add，避免混入无关删除。

下一步：

- 执行 Slice 33 Completion Gate。

## 2026-07-07 Slice 33 Execution Run Manifest Panel Plan 完成

本轮完成：

- 选择 Slice 33：Execution Run Manifest Panel。
- 选择原因：
  - Slice 32 已统一 manifest row 构建逻辑；
  - 四个执行页仍重复 manifest panel template、table slots、columns 和 scoped
    styles；
  - component extraction 能减少 display drift，同时继续避开 backend/contracts/
    fixtures/prompts/skills/deleted knowledge-card scope。
- 新增 `docs/implementation/slices/slice-33-execution-run-manifest-panel.md`。
- 更新 `docs/implementation/10-v2-scope-options.md`，记录 Slice 32 completion
  和 Slice 33 推荐。
- `NEXT_AI_TASK.md` 已切换到 Slice 33 Task 2：Add shared execution run manifest
  panel component。

本轮验证：

```powershell
rg -n "Slice 33|Execution Run Manifest Panel|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-33-execution-run-manifest-panel.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

验证结果：

- Planning references present。
- `git diff --check`：no output。

风险提醒：

- 当前 working tree 仍有大量与 Slice 33 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- 继续 Task 2 时只碰 `ExecutionRunManifestPanel.*` 和 handoff docs，避免
  contracts/fixtures/prompts/skills/deleted slice scope。

下一步：

- 继续 Slice 33 Task 2：Add shared execution run manifest panel component。

## 2026-07-07 Slice 32 Completion Gate 完成

本轮完成：

- 完成 Slice 32：Execution Run Manifest Helper。
- 新增 `buildExecutionRunManifestRows`，统一 execution run manifest 的 runtime、
  snapshot、output artifact row 构建逻辑。
- Pytest、Playwright、Newman、JMeter 执行页复用 helper，但保留各自 runner 的
  output artifact definitions。
- 本地打开链接规则保持不变：只有 id 存在于 `TestRunRead.artifacts` 的持久化
  local Artifact 行时才渲染链接。
- 缺失 runtime/snapshot/output evidence 仍显示为不可用且不可打开。
- `NEXT_AI_TASK.md` 已切换到：Select and plan the next narrow V2 task after
  Slice 32 completion。

本轮验证：

```powershell
npm --prefix frontend run test -- --run src/views/execution/executionRunManifest.spec.ts src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

验证结果：

- Focused frontend specs：`6` files passed，`10` tests passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- Backend run manifest golden：`1 passed`。
- `git diff --check`：no output。

Git/风险提醒：

- 当前 working tree 仍有大量与 Slice 32 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- 如要提交，必须 path-limited add，避免混入当前大量无关删除。

下一步：

- 按 `NEXT_AI_TASK.md` 选择并规划 Slice 32 之后的下一条窄 V2 task。

## 2026-07-07 Slice 32 Execution Run Manifest Helper Implementation 完成

本轮完成：

- 完成 Slice 32 Task 2：Add execution run manifest helper。
- 完成 Slice 32 Task 3：Apply run manifest helper to execution pages。
- 新增 `frontend/src/views/execution/executionRunManifest.ts`。
- 新增 `frontend/src/views/execution/executionRunManifest.spec.ts`。
- Pytest、Playwright、Newman、JMeter 执行页已使用 shared helper 构建 run
  manifest rows。
- 保留各 runner 自己的 output artifact list 和现有页面布局。
- 本地打开链接规则保持不变：只有 id 存在于 `TestRunRead.artifacts` 的持久化
  local Artifact 行时才渲染链接。
- 缺失 runtime/snapshot/output evidence 仍显示为不可用且不可打开。
- `NEXT_AI_TASK.md` 已切换到 Slice 32 Completion Gate。

本轮验证：

```powershell
npm --prefix frontend run test -- --run src/views/execution/executionRunManifest.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

验证结果：

- Focused frontend specs：`5` files passed，`8` tests passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- `git diff --check`：no output。

风险提醒：

- 当前 working tree 仍有大量与 Slice 32 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- Completion gate 后若要提交，必须 path-limited add，避免混入无关删除。

下一步：

- 执行 Slice 32 Completion Gate。

## 2026-07-07 Slice 32 Execution Run Manifest Helper Plan 完成

本轮完成：

- 选择 Slice 32：Execution Run Manifest Helper。
- 选择原因：
  - Slice 30 为了安全交付 parity，刻意在四个执行页重复实现 manifest rows；
  - Slice 31 已统一 availability labels，但四个页面仍重复维护 runtime/snapshot/
    output artifact row 构建逻辑；
  - helper extraction 能减少真实重复，同时避开当前 dirty worktree 中 deleted
    knowledge-card/prompt/skill/fixture 链条。
- 新增 `docs/implementation/slices/slice-32-execution-run-manifest-helper.md`。
- 更新 `docs/implementation/10-v2-scope-options.md`，记录 Slice 31 completion
  和 Slice 32 推荐。
- `NEXT_AI_TASK.md` 已切换到 Slice 32 Task 2：Add execution run manifest
  helper。

本轮验证：

```powershell
rg -n "Slice 32|Execution Run Manifest Helper|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-32-execution-run-manifest-helper.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

验证结果：

- Planning references present。
- `git diff --check`：no output。

风险提醒：

- 当前 working tree 仍有大量与 Slice 32 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- 继续 Task 2 时只碰 `frontend/src/views/execution/executionRunManifest.*`
  和 handoff docs，避免 contracts/fixtures/prompts/skills/deleted slice scope。

下一步：

- 继续 Slice 32 Task 2：Add execution run manifest helper。

## 2026-07-07 Slice 31 Completion Gate 完成

本轮完成：

- 完成 Slice 31：Execution Evidence Availability Labels。
- 新增 execution evidence availability helper，统一 local-openable、
  unavailable、external-reference、metadata-only 四类状态文案。
- Pytest、Playwright、Newman、JMeter 执行页 run manifest rows 已使用该 helper。
- 本地打开链接规则保持不变：只有 id 存在于 `TestRunRead.artifacts` 的持久化
  local Artifact 行时才渲染链接。
- 缺失 runtime/snapshot/output evidence 仍显示为不可用且不可打开。
- 保留各 runner 原有 metrics 和 artifact tables。
- `NEXT_AI_TASK.md` 已切换到：Select and plan the next narrow V2 task after
  Slice 31 completion。

本轮验证：

```powershell
npm --prefix frontend run test -- --run src/views/execution/evidenceAvailability.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

验证结果：

- Focused frontend specs：`5` files passed，`6` tests passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- Backend run manifest golden：`1 passed`。
- `git diff --check`：no output。

Git/风险提醒：

- 当前 working tree 仍有大量与 Slice 31 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- 如要提交，必须 path-limited add，避免混入当前大量无关删除。
- 下一步先选择一个不会复活 deleted knowledge-card/prompt/skill/fixture
  链条的小切片。

下一步：

- 按 `NEXT_AI_TASK.md` 选择并规划 Slice 31 之后的下一条窄 V2 task。

## 2026-07-07 Slice 31 Task 3 Execution Manifest Availability Labels 完成

本轮完成：

- 完成 Slice 31 Task 3：Apply availability labels to execution run manifests。
- Pytest、Playwright、Newman、JMeter 执行页的 run manifest rows 已改用
  `evidenceAvailabilityLabels`。
- 本地打开链接规则保持不变：只有 id 存在于 `TestRunRead.artifacts` 的持久化
  local Artifact 行时才渲染链接。
- 缺失 runtime/snapshot/output evidence 仍显示为不可用且不可打开。
- 保留各 runner 原有 metrics 和 artifact tables。
- `NEXT_AI_TASK.md` 已切换到 Slice 31 Completion Gate。

本轮验证：

```powershell
npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

验证结果：

- Focused execution page tests：`4` files passed，`4` tests passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- `git diff --check`：no output。

风险提醒：

- 当前 working tree 仍有大量与 Slice 31 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- Completion gate 后若要提交，必须 path-limited add，避免混入无关删除。

下一步：

- 执行 Slice 31 Completion Gate。

## 2026-07-07 Slice 31 Task 2 Evidence Availability Label Helper 完成

本轮完成：

- 完成 Slice 31 Task 2：Add execution evidence availability label helper。
- 新增 `frontend/src/views/execution/evidenceAvailability.ts`。
- 新增 `frontend/src/views/execution/evidenceAvailability.spec.ts`。
- Helper 只返回 evidence availability 文案和 tag 颜色：
  - local artifact：可打开 / 打开；
  - unavailable：不可用 / 不可打开；
  - external reference：外部引用 / 不可本地打开；
  - metadata only：仅元数据 / 不可直接打开。
- Helper 不创建 URL、不读文件、不 fetch 远端、不突变 Artifact、不依赖后端变化。
- `NEXT_AI_TASK.md` 已切换到 Slice 31 Task 3：Apply availability labels to
  execution run manifests。

本轮验证：

```powershell
npm --prefix frontend run test -- --run src/views/execution/evidenceAvailability.spec.ts
npm --prefix frontend run build
git diff --check
```

验证结果：

- Focused helper test：`1` file passed，`2` tests passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- `git diff --check`：no output。

风险提醒：

- 当前 working tree 仍有大量与 Slice 31 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- 继续 Task 3 时只碰 execution views/specs 和 handoff docs，避免
  contracts/fixtures/prompts/skills/deleted slice scope。

下一步：

- 继续 Slice 31 Task 3：Apply availability labels to execution run manifests。

## 2026-07-07 Slice 31 Execution Evidence Availability Labels Plan 完成

本轮完成：

- 选择 Slice 31：Execution Evidence Availability Labels。
- 选择原因：
  - Slice 24-30 已把本地 Artifact 打开、证据摘要、运行清单等 evidence
    可读性补齐；
  - 当前剩余的小问题是不同页面的 evidence availability 文案和行构建逻辑
    重复，后续容易漂移；
  - 当前 working tree 有大量已删除的 knowledge-card/prompt/skill/fixture
    链条，Slice 31 避开这些范围，只做前端标签一致性。
- 新增
  `docs/implementation/slices/slice-31-execution-evidence-availability-labels.md`。
- 更新 `docs/implementation/10-v2-scope-options.md`，记录 Slice 30 completion
  和 Slice 31 推荐。
- `NEXT_AI_TASK.md` 已切换到 Slice 31 Task 2：Add execution evidence
  availability label helper。

本轮验证：

```powershell
rg -n "Slice 31|Execution Evidence Availability Labels|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-31-execution-evidence-availability-labels.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md memory/08-session-handoff.md memory/07-dev-log.md
git diff --check
```

验证结果：

- Planning references present。
- `git diff --check`：no output。

风险提醒：

- 当前 working tree 仍有大量与 Slice 31 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- 继续 Task 2 时只碰 `frontend/src/views/execution/evidenceAvailability.*`
  和 handoff docs，避免 contracts/fixtures/prompts/skills/deleted slice scope。

下一步：

- 继续 Slice 31 Task 2：Add execution evidence availability label helper。

## 2026-07-07 Slice 30 Completion Gate 完成

本轮完成：

- 完成 Slice 30：Execution Run Manifest Parity。
- Playwright、Newman、JMeter 执行页均已补齐与 pytest 页一致的只读
  `执行运行清单` 面板。
- 三个页面都展示执行命令、工作目录、运行器模式、运行工作区、仓库只读策略、
  网络策略、运行时文件、依赖/环境快照，以及各 runner 的输出工件可用性。
- 本地打开链接只在 Artifact id 能匹配 `TestRunRead.artifacts` 中的持久化
  local Artifact 行时渲染。
- 缺失 runtime/snapshot/output artifact 保持可见且不可打开。
- 保留各 runner 原有证据区：
  - Playwright trace/screenshot；
  - Newman collection/request/assertion metrics；
  - JMeter JTL/Sampler/latency metrics。
- `NEXT_AI_TASK.md` 已切换到：Select and plan the next narrow V2 task after
  Slice 30 completion。

本轮验证：

```powershell
npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts
npm --prefix frontend run build
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

验证结果：

- Focused frontend specs：`3` files passed，`3` tests passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- Backend run manifest golden：`1 passed`。
- `git diff --check`：no output。

Git/风险提醒：

- 当前 working tree 仍有大量与 Slice 30 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- 如要提交，必须 path-limited add，避免混入当前大量无关删除。
- 下一步只做 planning task，先选择一个不会复活大批 deleted docs/contracts/
  fixtures 的小切片。

下一步：

- 按 `NEXT_AI_TASK.md` 选择并规划 Slice 30 之后的下一条窄 V2 task。

## 2026-07-07 Slice 30 Task 4 JMeter Run Manifest Panel 完成

本轮完成：

- 完成 Slice 30 Task 4：Add JMeter run manifest panel。
- 在 `frontend/src/views/execution/JMeterExecutionView.vue` 新增只读
  `执行运行清单` 面板。
- 面板展示 JMeter TestRun 的执行命令、工作目录、运行器模式、运行工作区、
  仓库只读策略、网络策略、运行时文件、依赖/环境快照，以及 stdout、stderr、
  parsed output、JMeter JTL 等输出工件可用性。
- 本地打开链接只在 Artifact id 能匹配 `TestRunRead.artifacts` 中的持久化
  local Artifact 行时渲染。
- 缺失 runtime artifact、环境快照、stderr 仍显示为不可用，不伪装成可下载
  证据。
- 保留原有 JMeter JTL 统计耗时、Sampler/断言/平均延迟 metrics、JMeter 工件表、
  Sampler 结果表和启动/刷新行为。
- `NEXT_AI_TASK.md` 已切换到 Slice 30 Completion Gate。

本轮验证：

```powershell
npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

验证结果：

- Focused JMeter frontend test：`1` file passed，`1` test passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- `git diff --check`：no output。

风险提醒：

- 当前 working tree 仍有大量与 Slice 30 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- 继续任务时仍需 path-limited 审查和提交，避免把无关删除混入。

下一步：

- 执行 Slice 30 Completion Gate。

## 2026-07-07 Slice 30 Task 3 Newman Run Manifest Panel 完成

本轮完成：

- 完成 Slice 30 Task 3：Add Newman run manifest panel。
- 在 `frontend/src/views/execution/NewmanExecutionView.vue` 新增只读
  `执行运行清单` 面板。
- 面板展示 Newman TestRun 的执行命令、工作目录、运行器模式、运行工作区、
  仓库只读策略、网络策略、运行时文件、依赖/环境快照，以及 stdout、stderr、
  newman JSON、parsed output、JUnit 等输出工件可用性。
- 本地打开链接只在 Artifact id 能匹配 `TestRunRead.artifacts` 中的持久化
  local Artifact 行时渲染。
- 缺失 runtime artifact、环境快照、stderr、JUnit 仍显示为不可用，不伪装成
  可下载证据。
- 保留原有 Newman collection/request/assertion metrics、Newman 工件表、
  断言结果表和启动/刷新行为。
- `NEXT_AI_TASK.md` 已切换到 Slice 30 Task 4：Add JMeter run manifest panel。

本轮验证：

```powershell
npm --prefix frontend run test -- --run src/views/execution/NewmanExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

验证结果：

- Focused Newman frontend test：`1` file passed，`1` test passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- `git diff --check`：no output。

风险提醒：

- 当前 working tree 仍有大量与 Slice 30 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- 继续任务时仍需 path-limited 审查和提交，避免把无关删除混入。

下一步：

- 继续 Slice 30 Task 4：Add JMeter run manifest panel。

## 2026-07-07 Slice 30 Task 2 Playwright Run Manifest Panel 完成

本轮完成：

- 完成 Slice 30 Task 2：Add Playwright run manifest panel。
- 在 `frontend/src/views/execution/PlaywrightExecutionView.vue` 新增只读
  `执行运行清单` 面板。
- 面板展示 Playwright TestRun 的执行命令、工作目录、运行器模式、运行工作区、
  仓库只读策略、网络策略、运行时文件、依赖/环境快照，以及 stdout、stderr、
  parsed output、JUnit、trace、screenshot 等输出工件可用性。
- 本地打开链接只在 Artifact id 能匹配 `TestRunRead.artifacts` 中的持久化
  local Artifact 行时渲染。
- 缺失 runtime artifact、环境快照、stderr、parsed output、JUnit 仍显示为
  不可用，不伪装成可下载证据。
- 保留原有 Playwright 追踪/截图证据表、metrics、测试结果表和启动/刷新行为。
- `NEXT_AI_TASK.md` 已切换到 Slice 30 Task 3：Add Newman run manifest panel。

本轮验证：

```powershell
npm --prefix frontend run test -- --run src/views/execution/PlaywrightExecutionView.spec.ts
npm --prefix frontend run build
git diff --check
```

验证结果：

- Focused Playwright frontend test：`1` file passed，`1` test passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- `git diff --check`：no output。

风险提醒：

- 当前 working tree 仍有大量与 Slice 30 无关的 unstaged 修改/删除，本轮没有
  回滚、暂存或提交。
- 继续任务时仍需 path-limited 审查和提交，避免把无关删除混入。

下一步：

- 继续 Slice 30 Task 3：Add Newman run manifest panel。

## 2026-07-07 Slice 30 Execution Run Manifest Parity Plan 完成

本轮完成：

- 按 `NEXT_AI_TASK.md` 启动并发 subagents 选择 Slice 29 之后的下一条窄 V2
  task。
- Gibbs 推荐 `Slice 30: Test Knowledge Card Contract`，价值高但会复活当前
  working tree 中已删除的 `slice-30-test-knowledge-card-contract.md` 和相关
  contracts/fixtures 风险面。
- Aquinas 复核 Git 状态：当前分支 `docs/preflight-vibecoding-fixes`，无 staged
  changes，但有大量 unstaged 修改/删除；规划任务必须避免 `git add -A` 和避免
  碰 backend/frontend/contracts/fixtures/prompts/skills。
- Lagrange 推荐 `Slice 30: Execution Run Manifest Parity`：合同和 golden 已由
  Slice 29 就绪，下一步只需把 Playwright/Newman/JMeter 页面补齐同一只读
  manifest 展示。
- 已选择更安全的小步：`Slice 30: Execution Run Manifest Parity`。
- 新增 `docs/implementation/slices/slice-30-execution-run-manifest-parity.md`。
- 更新 `docs/implementation/10-v2-scope-options.md`，记录 Slice 29 完成和 Slice
  30 推荐。
- Slice 30 Task 1 planning verification 已通过。
- 更新 `NEXT_AI_TASK.md` 到 Slice 30 Task 2：Add Playwright run manifest panel。

风险提醒：

- 当前 working tree 仍包含大量与 Slice 30 planning 无关的修改/删除，本轮没有
  回滚、暂存或提交。
- 下一轮不要碰这些范围，除非任务明确要求且先单独审查：`backend/**`、
  `frontend/**`、`docs/contracts/**`、`docs/fixtures/**`、`prompts/**`、
  `skills/**`、`docs/reference/**`、`docs/architecture/**`。
- 提交前必须 path-limited add，避免把 105 个删除混入 planning commit。

验证：

- Planning verification：
  `rg -n "Execution Run Manifest Parity|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-30-execution-run-manifest-parity.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md`
- `git diff --check`
- Result：planning references present；`git diff --check` no output。

下一步：

- 继续 Slice 30 Task 2：Add Playwright run manifest panel。

## 2026-07-07 Slice 29 Completion Gate 完成

本轮完成：

- 完成 Slice 29：Execution Run Manifest。
- Slice 29 task table 已记录 Task 4 done 和 completion gate done。
- `NEXT_AI_TASK.md` 已切换到：Select and plan the next narrow V2 task after
  Slice 29 completion。

本轮验证：

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Backend golden checks：`2 passed`。
- Frontend build：passed；保留既有 Vite large chunk warning。
- Frontend test suite：`16` files passed，`21` tests passed。
- `git diff --check`：no output。

Git/环境状态：

- portable `uv` 和 MinGit 已放在 `.tmp/tools`，`.tmp/` 被 `.gitignore` 覆盖。
- `.git` 元数据已恢复，当前分支为 `docs/preflight-vibecoding-fixes`。
- 当前 working tree 仍包含大量与 Slice 29 无关的未提交修改/删除，本轮没有
  回滚、暂存或提交这些改动。

下一步建议：

- 按 `NEXT_AI_TASK.md` 做 planning-only 任务：选择并规划下一条窄 V2 slice。
- 在决定提交前，先按任务边界审查当前大量 unstaged changes，避免把无关删除
  混入 Slice 29 或下一条 slice 的提交。


## 2026-07-07 Slice 29 Task 4 Execution Run Manifest Golden Smoke 验证完成

本轮完成：

- 在工作区 `.tmp/tools` 下补齐 portable `uv` 和 portable MinGit。
- 使用 `uv --project backend sync --dev` 创建 `backend/.venv`。
- 恢复 `.git` 元数据到 `origin/docs/preflight-vibecoding-fixes`，未覆盖当前
  working tree 文件。
- 运行并通过 Slice 29 Task 4 golden smoke。
- 运行并通过 `git diff --check`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 29 Completion Gate。

验证结果：

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q
git diff --check
```

- Golden smoke：`1 passed`。
- `git diff --check`：no output。

Git 状态提醒：

- 当前分支：`docs/preflight-vibecoding-fixes`，远端默认 HEAD 也是该分支。
- 当前 working tree 仍包含大量与 Slice 29 Task 4 无关的未提交修改/删除，
  本轮没有回滚、暂存或提交这些改动。
- 便携工具和缓存位于 `.tmp/`，已被 `.gitignore` 覆盖。

下一步建议：

- 按 `NEXT_AI_TASK.md` 执行 Slice 29 Completion Gate。
- Completion Gate 通过后，再决定是否按任务边界分批提交。


## 2026-07-06 Slice 29 Task 4 Execution Run Manifest Golden Smoke 阻塞

本轮完成：

- 按 `NEXT_AI_TASK.md` 继续 Slice 29 Task 4：Add execution run manifest golden
  smoke。
- 新增 `backend/app/tests/golden/test_execution_run_manifest_golden.py`。
- 新增 `docs/fixtures/17-execution-run-manifest-golden.md`。
- Golden seed 覆盖：
  - TestRun command、working_directory、runner_mode、run_workspace；
  - repository_readonly、network_enabled、parsed_result；
  - runtime_artifact_ids、dependency snapshot、missing environment snapshot id；
  - persisted local Artifact rows：runtime_manifest、dependency_snapshot、
    stdout、parsed_output；
  - runtime_artifact_ids 和 environment_snapshot_artifact_id 中包含不存在的
    artifact id，用来证明没有 persisted Artifact metadata 时不能渲染本地打开链接。
- Golden 断言：
  - `GET /api/test-runs/{id}` 返回 run manifest 所需的现有 TestRun/Artifact
    evidence；
  - persisted stdout Artifact metadata 可见，且可通过既有 local artifact
    access endpoint 打开；
  - 缺失 runtime artifact id 返回 `ARTIFACT_NOT_FOUND`；
  - 读取 TestRun/Artifact 不创建或突变 Report、FailureAnalysis、
    QualityGateDecision、AutomationRepairTask、AutomationDraft、AITask、
    TestRun、Artifact。

验证尝试：

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend\app\tests\golden\test_execution_run_manifest_golden.py -q
python -m pytest backend\app\tests\golden\test_execution_run_manifest_golden.py -q
Select-String scoped whitespace and conflict-marker check for Task 4 files
```

验证结果：

- `backend/.venv/Scripts/python.exe` 不存在。
- `python.exe` 是不可用的 WindowsApps stub，返回“指定的登录会话不存在”。
- scoped whitespace/conflict-marker check：no output。

环境/权限阻塞：

- 用户已允许下载/安装缺失环境，但 `winget install Git.Git` 的提升执行被
  auto-review 拒绝。
- 下载 standalone `uv` 到工作区 `.tmp/tools` 的提升执行也被 auto-review
  拒绝。
- 按安全规则，本轮不能继续用其他方式绕过同类下载/安装限制。
- 当前 `.git/` 仍为空目录，无法运行 `git status`、`git diff --check`、
  commit 或确认 GitHub 远端状态。

当前状态：

- Task 4 implementation 已落地，但由于 Python/Git 环境不可用，Task 4 不能
  标记为 verified done。
- `NEXT_AI_TASK.md` 仍保持 Slice 29 Task 4，下一轮应先恢复 backend Python
  `.venv` 和完整 git checkout，再运行验证。

下一步建议：

- 恢复可用 Python 3.12/uv 或项目 `backend/.venv`。
- 恢复完整 git checkout 或可用 `git.exe`。
- 运行：
  `backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_execution_run_manifest_golden.py -q`
- 运行 `git diff --check`，再提交 Task 3/Task 4 对应变更。

## 2026-07-06 Slice 29 Task 3 Frontend Run Manifest Panel 完成

本轮完成：

- 按 `NEXT_AI_TASK.md` 完成 Slice 29 Task 3：Add frontend run manifest panel。
- 在 `frontend/src/views/execution/PytestExecutionView.vue` 新增只读
  `执行运行清单` 面板。
- 面板展示：
  - 执行命令、工作目录、运行器模式、运行工作区；
  - 仓库只读策略和网络策略；
  - 运行时文件、依赖快照、环境快照；
  - 标准输出、标准错误、解析结果、JUnit、覆盖率等输出工件可用性。
- 本地打开链接只在 Artifact id 能匹配 `TestRunRead.artifacts` 中的持久化
  local Artifact 行时渲染。
- 缺失的 runtime/dependency/environment snapshot 和缺失输出仍显示为
  `不可用`/`不可打开`，不伪装成可下载证据。
- `frontend/src/views/execution/PytestExecutionView.spec.ts` 补充了运行清单
  覆盖，断言持久化 Artifact 可打开、缺失环境快照不可打开。
- 使用 subagent 并发：
  - Lorentz 只读梳理 Pytest 执行页数据形状和 artifact link 风险；
  - Hooke 起草 spec 覆盖建议；
  - Aristotle 负责 Vue 草案但未在主线需要其结果前返回。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/execution/PytestExecutionView.spec.ts
npm --prefix frontend run build
Select-String scoped whitespace and conflict-marker check for the two changed frontend files
```

验证结果：

- Focused frontend test：`1` file passed，`1` test passed。
- Frontend build：passed；保留既有 Vite large chunk warning。
- Whitespace/conflict-marker self-check：no output。

Git/GitHub 状态：

- 当前目录存在 `.git/`，但为空目录，没有 `HEAD`、`config` 或 index。
- 当前 PowerShell PATH 中没有 `git` 或 `gh`；本地无法执行
  `git status --short --branch`、`git diff --check` 或 commit。
- GitHub API 普通请求失败；提升联网请求被审批系统拒绝，因此本轮无法确认
  `YanChen0111/Chtest` 远端仓库状态。
- 前端验证使用 bundled Node/npm，并在工作区 `.tmp/npm-cache` 安装依赖；
  `frontend/node_modules/` 和 `.tmp/` 均已被 `.gitignore` 覆盖。

修改文件：

- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `docs/implementation/slices/slice-29-execution-run-manifest.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

未完成/阻塞：

- 未能运行标准 `git diff --check`，因为本地没有可用 git checkout。
- 未能创建提交 `feat(frontend): show execution run manifest`，同样受 git
  checkout 缺失阻塞。
- 未能查看 GitHub 远端当前状态，受网络请求失败和提升审批拒绝阻塞。

下次推荐任务：

- 在恢复完整 git checkout 后先运行 `git status --short --branch`、
  `git diff --check` 并提交 Task 3。
- 继续 `NEXT_AI_TASK.md`：Slice 29 Task 4：Add execution run manifest golden
  smoke。

## 2026-07-01 Slice 29 Task 2 Execution Run Manifest Contract 完成

本轮完成：

- 完成 Slice 29 Task 2：Define execution run manifest contract。
- `docs/contracts/01-data-model-contract.md` 明确 execution run manifest
  使用现有 TestRun 字段和 Artifact metadata，不新增表。
- `docs/contracts/02-api-contract.md` 明确 manifest 是 `TestRunRead` 的只读
  展示，不新增 endpoint。
- `docs/contracts/04-artifact-contract.md` 明确 runtime/dependency/environment
  snapshot 缺失时仍要可见但不可打开。
- 合同保留边界：
  - 不修改 runner 执行；
  - 不修改命令组装或 allowlist；
  - 不生成 Report、FailureAnalysis、QualityGateDecision；
  - 不引入 remote provider、RAG runtime、MCP runtime、RBAC、tenant。
- Slice 29 table 已记录 Task 1 done pending commit，Task 2 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 29 Task 3：Add frontend run manifest panel。

下次推荐任务：

- 提交 Task 2：`docs(v2): define execution run manifest contract`。
- 继续 Slice 29 Task 3：Add frontend run manifest panel。

## 2026-07-01 Slice 29 Task 1 Execution Run Manifest Plan 完成

本轮完成：

- 选择 Slice 29：Execution Run Manifest。
- 选择原因：
  - Slice 24-28 已经补齐 artifact open links、report evidence summary、
    AI task artifact links、CI imported reference clarity、quality gate evidence
    summary；
  - 现在 TestRun 本身仍需要更清楚说明“实际跑了什么、在哪里跑、用什么 runner
    mode、采用什么安全策略、有哪些 snapshot/output artifact”；
  - `TestRunRead` 已经有 command、working_directory、runner_mode、
    run_workspace、repository_readonly、network_enabled、snapshot ids、
    parsed_result 和 artifacts，Slice 29 可以保持 read-only 展示。
- 新增 Slice 29 计划：
  `docs/implementation/slices/slice-29-execution-run-manifest.md`。
- `docs/implementation/10-v2-scope-options.md` 已补充 Slice 28 完成记录和
  Slice 29 推荐。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 29 Task 2：Define execution run manifest contract。

下次推荐任务：

- 提交 Task 1：`docs(v2): add execution run manifest plan`。
- 继续 Slice 29 Task 2：Define execution run manifest contract。

## 2026-07-01 Slice 28 Completion Gate 完成

本轮完成：

- 完成 Slice 28：CI/CD Quality Gate Evidence Summary。
- Slice 28 task table 已记录：
  - Task 1：`3ca3db0`
  - Task 2：`b7ddd13`
  - Task 3：`760f56d`
  - Task 4：`2c0bd91`
  - Completion Gate：done pending commit。
- 验证 CI/CD 质量中心可以展示质量门禁证据摘要：
  - UnitTestPatch/PatchScopeGate；
  - 新增测试证据；
  - 回归证据；
  - blocking reasons；
  - persisted UnitTestPatch Artifact 本地打开链接。
- 验证缺失必需证据返回 `needs_review`，不会被展示或记录成 `passed`。
- 验证没有新增质量门计算逻辑、报告生成行为、runner 行为、远程 CI provider
  行为、PR 评论、部署/发布、RBAC、tenant、RAG runtime 或 MCP runtime。
- `NEXT_AI_TASK.md` 已切换到：
  Select and plan the next narrow V2 task after Slice 28 completion。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_gate_evidence_summary_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Backend golden checks：`2` passed。
- Frontend build：passed，保留 Vite large chunk warning。
- Frontend tests：`16` files passed，`21` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 Completion Gate：`docs(v2): complete quality gate evidence summary slice`。
- 继续 `NEXT_AI_TASK.md`，选择并规划下一个窄 V2 slice。

## 2026-07-01 Slice 28 Task 4 Quality Gate Evidence Summary Golden Smoke 完成

本轮完成：

- 完成 Slice 28 Task 4：Add quality gate evidence summary golden smoke。
- 新增 golden：
  `backend/app/tests/golden/test_cicd_quality_gate_evidence_summary_golden.py`。
- 新增 fixture：
  `docs/fixtures/16-cicd-quality-gate-evidence-summary-golden.md`。
- Golden 覆盖：
  - 完整证据下 QualityGateDecision 为 `passed`；
  - `status_detail` 保留 UnitTestPatch/PatchScopeGate、新增测试、回归证据；
  - `evidence_artifact_ids` 只包含 persisted UnitTestPatch Artifact id；
  - 缺失必需证据时返回 `needs_review`，不是 `passed`；
  - 门禁摘要输入不创建 Report、FailureAnalysis、AutomationDraft、新 Artifact，
    也不修改既有 Artifact。
- Slice 28 table 已记录 Task 3 commit `760f56d`，Task 4 done pending commit。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_gate_evidence_summary_golden.py -q
git diff --check
```

验证结果：

- Golden smoke：`1` passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 4：`test(golden): add quality gate evidence summary smoke`。
- 继续 Slice 28 Completion Gate。

## 2026-07-01 Slice 28 Task 3 CI/CD Quality Gate Frontend Summary 完成

本轮完成：

- 完成 Slice 28 Task 3：Add CI/CD quality gate frontend summary。
- `CicdQualityCenterView.vue`：
  - 质量门禁卡片新增 `门禁证据摘要`；
  - 展示 UnitTestPatch / PatchScopeGate、新增测试证据、回归证据；
  - blocking reasons 显示中文标签；
  - 仅 persisted UnitTestPatch Artifact id 显示本地 `打开` 链接；
  - 新测试/回归保持结构化证据，不伪装成本地 artifact 下载。
- `CicdQualityCenterView.spec.ts` 覆盖：
  - 必需证据行可见；
  - missing new-test 显示 `缺失不可打开`；
  - UnitTestPatch artifact 有 `/api/artifacts/{id}/download` 链接；
  - regression plan/test run id 不被渲染为 artifact 下载链接；
  - 页面不出现 remote provider control 文案。
- Slice 28 table 已记录 Task 2 commit `b7ddd13`，Task 3 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 28 Task 4：Add quality gate evidence summary golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/cicd/CicdQualityCenterView.spec.ts
npm --prefix frontend run build
git diff --check
```

验证结果：

- CI/CD focused frontend test：`1` file passed，`2` tests passed。
- Frontend build：passed，保留 Vite large chunk warning。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 3：`feat(frontend): summarize quality gate evidence`。
- 继续 Slice 28 Task 4：Add quality gate evidence summary golden smoke。

## 2026-07-01 Slice 28 Task 2 Quality Gate Evidence Summary Contract 完成

本轮完成：

- 完成 Slice 28 Task 2：Define quality gate evidence summary contract。
- `docs/contracts/02-api-contract.md` 明确：
  - quality gate evidence summary 是已有 QualityGateDecision 和 Artifact
    metadata 的只读展示；
  - required evidence 包含 UnitTestPatch/PatchScopeGate、new-test、regression；
  - blocking reasons 和 missing evidence 必须可见；
  - 只有 persisted local Artifact ids 才能展示本地打开链接。
- `docs/contracts/04-artifact-contract.md` 新增 Slice 28 quality gate
  evidence summary rules。
- Slice 28 table 已记录 Task 1 commit `3ca3db0`，Task 2 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 28 Task 3：Add CI/CD quality gate frontend summary。

下次推荐任务：

- 提交 Task 2：`docs(v2): define quality gate evidence summary contract`。
- 继续 Slice 28 Task 3：Add CI/CD quality gate frontend summary。

## 2026-07-01 Slice 28 Task 1 CI/CD Quality Gate Evidence Summary Plan 完成

本轮完成：

- 选择 Slice 28：CI/CD Quality Gate Evidence Summary。
- 选择原因：
  - Slice 16 已有 QualityGateDecision；
  - Slice 24/25 已建立本地 artifact access 和 evidence summary 模式；
  - CI/CD 质量中心仍需要更清楚展示质量门禁的必需证据、缺失证据和阻塞原因。
- 新增 Slice 28 计划：
  `docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md`。
- `docs/implementation/10-v2-scope-options.md` 已补充 Slice 27 完成记录和
  Slice 28 推荐。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 28 Task 2：Define quality gate evidence summary contract。

下次推荐任务：

- 提交 Task 1：`docs(v2): add quality gate evidence summary plan`。
- 继续 Slice 28 Task 2：Define quality gate evidence summary contract。

## 2026-07-01 Slice 27 Completion Gate 完成

本轮完成：

- 完成 Slice 27：AI Task Evidence Artifact Links。
- Slice 27 task table 已记录：
  - Task 1：`add4adc`
  - Task 2：`57cf570`
  - Task 3：`c14fa57`
  - Task 4：`f9bebbe`
  - Completion Gate：done pending commit。
- 验证 safe AI task artifacts 可以在 AI Workbench 使用本地打开链接。
- 验证 unsafe raw LLM artifacts 保持 metadata-only，不 inline，不直接打开。
- 验证没有新增 AI task rerun、provider call、Report、FailureAnalysis、
  QualityGateDecision、TestRun、artifact mutation、RAG runtime 或 MCP runtime。
- `NEXT_AI_TASK.md` 已切换到：
  Select and plan the next narrow V2 task after Slice 27 completion。

本轮验证：

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
git diff --check
```

验证结果：

- Frontend build：passed，保留 Vite large chunk warning。
- Full frontend suite：`16` files passed，`21` tests passed。
- Slice 27 + artifact access golden：`2 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 completion gate：`docs(v2): complete ai task artifact link slice`。
- 选择并规划下一条 V2 小切片。

## 2026-07-01 Slice 27 Task 4 AI Task Artifact Link Golden Smoke 完成

本轮完成：

- 完成 Slice 27 Task 4：Add AI task artifact link golden smoke。
- 新增 `backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py`。
- 新增 `docs/fixtures/15-ai-task-evidence-artifact-links-golden.md`。
- Golden 覆盖：
  - safe `parsed_output` AI task artifact 可通过 local artifact access 打开；
  - unsafe `raw_llm_output` 在 AI task detail 中保持 metadata-only；
  - AI task detail 不 inline artifact content，不返回合成 `download_url`；
  - artifact link display 不创建 AI task rerun、provider call、Report、
    FailureAnalysis、QualityGateDecision、TestRun、artifact mutation、RAG
    runtime 或 MCP runtime。
- Slice 27 table 已记录 Task 3 commit `c14fa57`，Task 4 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 27 Completion Gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ai_task_evidence_artifact_links_golden.py -q
git diff --check
```

验证结果：

- AI task artifact link golden：`1 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 4：`test(golden): add ai task artifact link smoke`。
- 继续 Slice 27 Completion Gate。

## 2026-07-01 Slice 27 Task 3 AI Workbench Artifact Links 完成

本轮完成：

- 完成 Slice 27 Task 3：Add AI Workbench artifact links。
- `AiWorkbenchView.vue`：
  - `safe_to_show=true` 的 AI task artifact 显示本地 `打开` 链接；
  - `safe_to_show=false` 的 artifact 显示 `不可直接打开`；
  - raw LLM output 只保留 metadata，不 inline content。
- `AiWorkbenchView.spec.ts` 覆盖：
  - parsed_output 安全 artifact 有 `/api/artifacts/{id}/download` 链接；
  - raw_llm_output 没有下载链接；
  - 页面不出现 rerun / prompt edit / provider control / raw content。
- Slice 27 table 已记录 Task 2 commit `57cf570`，Task 3 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 27 Task 4：Add AI task artifact link golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run build
```

验证结果：

- AI Workbench focused test：`1` file passed，`3` tests passed。
- Frontend build：passed，保留 Vite large chunk warning。

下次推荐任务：

- 提交 Task 3：`feat(frontend): link safe ai task artifacts`。
- 继续 Slice 27 Task 4：Add AI task artifact link golden smoke。

## 2026-07-01 Slice 27 Task 2 AI Task Evidence Artifact Link Contract 完成

本轮完成：

- 完成 Slice 27 Task 2：Define AI task evidence artifact link contract。
- `docs/contracts/02-api-contract.md` 明确：
  - AI task evidence artifact links 是现有 Artifact metadata 的只读展示；
  - 只有 persisted local Artifact 且 `safe_to_show=true` 才能在 AI 工作台展示直接打开链接；
  - `safe_to_show=false` 和 raw LLM output 保持 metadata-only；
  - 不 inline raw LLM output content。
- `docs/contracts/04-artifact-contract.md` 新增 Slice 27 AI task evidence
  artifact link rules。
- Slice 27 table 已记录 Task 1 commit `add4adc`，Task 2 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 27 Task 3：Add AI Workbench artifact links。

下次推荐任务：

- 提交 Task 2：`docs(v2): define ai task artifact link contract`。
- 继续 Slice 27 Task 3：Add AI Workbench artifact links。

## 2026-07-01 Slice 27 Task 1 AI Task Evidence Artifact Links Plan 完成

本轮完成：

- 选择 Slice 27：AI Task Evidence Artifact Links。
- 选择原因：
  - AI 工作台已经展示 AI task artifact metadata 和 safe display flags；
  - Slice 24 已建立本地 artifact access；
  - Slice 25/26 已验证 evidence summary / external reference clarity 模式；
  - 用户此前反馈 AI 工作台可读性需要继续优化。
- 新增 Slice 27 计划：
  `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`。
- `docs/implementation/10-v2-scope-options.md` 已补充 Slice 26 完成记录和
  Slice 27 推荐。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 27 Task 2：Define AI task evidence artifact link contract。

下次推荐任务：

- 提交 Task 1：`docs(v2): add ai task artifact link plan`。
- 继续 Slice 27 Task 2：Define AI task evidence artifact link contract。

## 2026-07-01 Slice 26 Completion Gate 完成

本轮完成：

- 完成 Slice 26：CI Imported Artifact Reference Clarity。
- Slice 26 task table 已记录：
  - Task 1：`82e888d`
  - Task 2：`ae599d2`
  - Task 3：`2fe5088`
  - Task 4：`d67b40e`
  - Completion Gate：done pending commit。
- 验证 imported external artifact references 仍然是：
  - display-only inert metadata；
  - 不可本地打开；
  - 未远程拉取；
  - 不创建 TestRun、Report、FailureAnalysis、QualityGateDecision、
    UnitTestPatch、AutomationDraft 或 remote-provider side effects。
- `NEXT_AI_TASK.md` 已切换到：
  Select and plan the next narrow V2 task after Slice 26 completion。

本轮验证：

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
git diff --check
```

验证结果：

- Frontend build：passed，保留 Vite large chunk warning。
- Full frontend suite：`16` files passed，`21` tests passed。
- Slice 26 + artifact access golden：`2 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 completion gate：`docs(v2): complete ci imported reference clarity slice`。
- 从 `docs/implementation/10-v2-scope-options.md` 选择并规划下一条 V2 小切片。

## 2026-07-01 Slice 26 Task 4 Imported Reference Inert Golden Smoke 完成

本轮完成：

- 完成 Slice 26 Task 4：Add imported reference inert golden smoke。
- 新增 `backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py`。
- 新增 `docs/fixtures/14-ci-imported-artifact-reference-clarity-golden.md`。
- Golden 覆盖：
  - imported external artifact reference 是 inert metadata；
  - 外部引用通过 local artifact access 返回 `ARTIFACT_NOT_LOCAL`；
  - 本地 `ci_run_metadata.json` Artifact 仍可读取；
  - import-only metadata 不创建 TestRun、Report、FailureAnalysis、
    QualityGateDecision、UnitTestPatch 或 AutomationDraft。
- Slice 26 table 已记录：
  - Task 1：`82e888d`
  - Task 2：`ae599d2`
  - Task 3：`2fe5088`
  - Task 4：done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 26 Completion Gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py -q
git diff --check
```

验证结果：

- CI imported artifact reference clarity golden：`1 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 4：`test(golden): add ci imported reference clarity smoke`。
- 继续 Slice 26 Completion Gate。

## 2026-07-01 Slice 26 Task 3 CI Imported Reference Frontend Clarity 完成

本轮完成：

- 完成 Slice 26 Task 3：Add CI imported reference frontend clarity。
- `CicdQualityCenterView.vue` imported reference rows 新增：
  - `不可本地打开`；
  - `未远程拉取`；
  - 保留 external URL 文本；
  - 不新增本地下载链接。
- `CicdQualityCenterView.spec.ts` 覆盖：
  - imported reference 显示 inert/local-openability/remote-fetch 状态；
  - 不渲染 `/api/artifacts/{id}/download` 本地 artifact 链接；
  - 仍不出现 rerun/webhook/token/deploy/release 等远程 provider 控制文案。
- Slice 26 table 已记录 Task 2 commit `ae599d2`，Task 3 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 26 Task 4：Add imported reference inert golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/cicd/CicdQualityCenterView.spec.ts
npm --prefix frontend run build
git diff --check
```

验证结果：

- CI/CD focused frontend test：`2 passed`。
- Frontend build：passed，保留 Vite large chunk warning。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 3：`feat(frontend): clarify ci imported artifact references`。
- 继续 Slice 26 Task 4：Add imported reference inert golden smoke。

## 2026-07-01 Slice 26 Task 2 Imported Reference Display Contract 完成

本轮完成：

- 完成 Slice 26 Task 2：Define imported artifact reference display contract。
- `docs/contracts/02-api-contract.md` 明确：
  - imported artifact reference 是 display-only external metadata；
  - 不是 local Artifact file；
  - 不生成 `/api/artifacts/{id}/download` 本地下载链接；
  - 需要展示 inert status、local-openability status、`remote_fetch_performed=false`。
- `docs/contracts/04-artifact-contract.md` 新增 Slice 26 clarity rules。
- Slice 26 table 已记录 Task 2 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 26 Task 3：Add CI imported reference frontend clarity。

下次推荐任务：

- 提交 Task 2：`docs(v2): define imported reference clarity contract`。
- 继续 Slice 26 Task 3：Add CI imported reference frontend clarity。

## 2026-07-01 Slice 26 Task 1 CI Imported Artifact Reference Clarity Plan 完成

本轮完成：

- 选择 Slice 26：CI Imported Artifact Reference Clarity。
- 选择原因：
  - Slice 20 已导入外部 CI artifact references 为 inert metadata；
  - Slice 24/25 已建立本地 artifact access 和 evidence summary；
  - CI/CD Quality Center 仍需要更清楚展示外部引用不可本地打开、未远程拉取。
- 新增 Slice 26 计划：
  `docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md`。
- `docs/implementation/10-v2-scope-options.md` 已补充 Slice 25 完成记录和
  Slice 26 推荐。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 26 Task 2：Define imported artifact reference display contract。

下次推荐任务：

- 提交 Task 1：`docs(v2): add ci imported reference clarity plan`。
- 继续 Slice 26 Task 2：Define imported artifact reference display contract。

## 2026-07-01 Slice 25 Completion Gate 完成

本轮完成：

- 完成 Slice 25：Execution Evidence Summary。
- Slice 25 task table 已记录：
  - Task 1：`e790ed0`
  - Task 2：`faa3cce`
  - Task 3：`5e64c18`
  - Task 4：`41c8f46`
  - Completion Gate：done pending commit。
- 确认 Slice 25 保持 read-only evidence summary：
  - 不修改 report generation；
  - 不自动创建 Report、FailureAnalysis、QualityGateDecision 或 repair task；
  - 不修改 runner 行为；
  - 不新增 artifact upload/mutation/delete/sharing/cloud storage/signed URL；
  - 不引入 broad artifact browser、RAG runtime、MCP runtime、RBAC、tenants、
    permissions。
- `NEXT_AI_TASK.md` 已切换到：
  Select the next V2 small slice after Slice 25 completion。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_evidence_summary_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Execution evidence summary + artifact access golden：`2 passed`。
- Frontend build：passed，保留 Vite large chunk warning。
- Full frontend suite：`16` files passed，`21` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 completion gate：`docs(v2): complete execution evidence summary slice`。
- 选择并规划下一条 V2 小切片。

## 2026-07-01 Slice 25 Task 4 Execution Evidence Summary Golden Smoke 完成

本轮完成：

- 完成 Slice 25 Task 4：Add execution evidence summary golden smoke。
- 新增 `backend/app/tests/golden/test_execution_evidence_summary_golden.py`。
- 新增 `docs/fixtures/13-execution-evidence-summary-golden.md`。
- Golden 覆盖：
  - summary row 引用 persisted local Artifact；
  - local Artifact 可通过 `GET /api/artifacts/{artifact_id}/download` 读取；
  - 返回 bytes 与持久化 `sha256`、`size_bytes` 匹配；
  - structured metric evidence 不显示为 downloadable；
  - missing evidence 保持显式；
  - external imported artifact reference 返回 `ARTIFACT_NOT_LOCAL`。
- Slice 25 table 已记录 Task 3 commit `5e64c18`，Task 4 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 25 Completion Gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_evidence_summary_golden.py -q
git diff --check
```

验证结果：

- Execution evidence summary golden：`1 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 4：`test(golden): add execution evidence summary smoke`。
- 继续 Slice 25 Completion Gate。

## 2026-07-01 Slice 25 Task 3 Report Evidence Summary Frontend 完成

本轮完成：

- 完成 Slice 25 Task 3：Add report evidence summary frontend。
- `ReportFailureAnalysisView.vue`：
  - evidence manifest rows 有 artifact id 时显示本地 Artifact “打开”链接；
  - metric / TestResult rows 保持为结构化证据；
  - missing evidence 显示为 `缺失不可打开`；
  - report artifacts 表新增本地 Artifact “打开”链接。
- `ReportFailureAnalysisView.spec.ts` 覆盖：
  - stderr evidence 可打开；
  - report artifact 可打开；
  - `environment_snapshot` missing evidence 不可打开。
- Slice 25 table 已记录 Task 2 commit `faa3cce`，Task 3 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 25 Task 4：Add execution evidence summary golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/reporting/ReportFailureAnalysisView.spec.ts
npm --prefix frontend run build
git diff --check
```

验证结果：

- Reporting focused frontend test：`1 passed`。
- Frontend build：passed，保留 Vite large chunk warning。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 3：`feat(frontend): summarize execution evidence`。
- 继续 Slice 25 Task 4：Add execution evidence summary golden smoke。

## 2026-07-01 Slice 25 Task 2 Execution Evidence Summary Contract 完成

本轮完成：

- 完成 Slice 25 Task 2：Define execution evidence summary contract。
- `docs/contracts/02-api-contract.md` 新增 Execution Evidence Summary：
  - 从 `ReportRead.evidence_manifest`、Report/TestRun Artifact metadata 派生；
  - local Artifact row 可使用 `GET /api/artifacts/{artifact_id}/download`；
  - metric / TestResult reference 不显示为可下载；
  - missing evidence 必须保持可见且不可下载；
  - 不修改 Report/TestRun/Artifact/FailureAnalysis/QualityGateDecision。
- `docs/contracts/04-artifact-contract.md` 新增 Slice 25 summary artifact rules。
- Slice 25 table 已记录 Task 2 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 25 Task 3：Add report evidence summary frontend。

下次推荐任务：

- 提交 Task 2：`docs(v2): define execution evidence summary contract`。
- 继续 Slice 25 Task 3：Add report evidence summary frontend。

## 2026-07-01 Slice 25 Task 1 Execution Evidence Summary Plan 完成

本轮完成：

- 选择 Slice 25：Execution Evidence Summary。
- 选择原因：
  - Slice 24 已让 execution artifacts 可打开；
  - 下一步应该解释这些 artifact 支撑什么结论、是否必需、是否缺失、
    是否可本地打开；
  - 该方向承接 report evidence manifest 和本地 artifact access，不需要改
    runner 或 report generation。
- 新增 Slice 25 计划：
  `docs/implementation/slices/slice-25-execution-evidence-summary.md`。
- `docs/implementation/10-v2-scope-options.md` 已补充 Slice 24 完成记录和
  Slice 25 推荐。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 25 Task 2：Define execution evidence summary contract。

下次推荐任务：

- 提交 Task 1：`docs(v2): add execution evidence summary plan`。
- 继续 Slice 25 Task 2：Define execution evidence summary contract。

## 2026-07-01 Slice 24 Completion Gate 完成

本轮完成：

- 完成 Slice 24：Local Artifact Access Links。
- Slice 24 task table 已记录：
  - Task 1：`e06c94b`
  - Task 2：`926cb50`
  - Task 3：`2222cf2`
  - Task 4：`d0f5516`
  - Task 5：`0f27919`
  - Completion Gate：done pending commit。
- 确认 Slice 24 保持 read-only local artifact access：
  - 不新增 artifact upload/mutation/delete/sharing/cloud storage/signed URL；
  - 不 fetch/proxy/download 外部 artifact URL；
  - 不修改 runner 行为；
  - 不生成 Report、FailureAnalysis、QualityGateDecision；
  - 不引入 RAG runtime、MCP runtime、RBAC、tenants、permissions。
- `NEXT_AI_TASK.md` 已切换到：
  Select the next V2 small slice after Slice 24 completion。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Artifact access API + golden：`5 passed`。
- Frontend build：passed，保留 Vite large chunk warning。
- Full frontend suite：`16` files passed，`21` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 completion gate：`docs(v2): complete local artifact access slice`。
- 选择并规划下一条 V2 小切片。

## 2026-07-01 Slice 24 Task 5 Artifact Access Golden Smoke 完成

本轮完成：

- 完成 Slice 24 Task 5：Add artifact access golden smoke。
- 新增 `backend/app/tests/golden/test_artifact_access_golden.py`。
- 新增 `docs/fixtures/12-local-artifact-access-golden.md`。
- Golden 覆盖：
  - 本地 `TestRun` stdout Artifact 可通过
    `GET /api/artifacts/{artifact_id}/download` 读取；
  - 返回 bytes 与持久化 `sha256`、`size_bytes` 匹配；
  - `Content-Type` 使用 Artifact MIME；
  - `Content-Disposition` 只暴露安全 basename；
  - 读取不修改 Artifact / TestRun runtime artifact 引用；
  - 外部 imported artifact reference 返回 `ARTIFACT_NOT_LOCAL`。
- Slice 24 table 已记录 Task 4 commit `d0f5516`，Task 5 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 24 Completion Gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_artifact_access_golden.py -q
git diff --check
```

验证结果：

- Artifact access golden：`1 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 5：`test(golden): add local artifact access smoke`。
- 继续 Slice 24 Completion Gate。

## 2026-07-01 Slice 24 Task 4 Frontend Artifact Links 完成

本轮完成：

- 完成 Slice 24 Task 4：Add frontend artifact links。
- `frontend/src/api/execution.ts` 新增 `artifactDownloadUrl` helper。
- pytest / Playwright / Newman / JMeter execution artifact tables 新增
  `Artifact` 操作列，使用 `GET /api/artifacts/{id}/download` 打开本地证据。
- 保留原有 artifact metadata 表格显示。
- Slice 24 table 已记录 Task 3 commit `2222cf2`，Task 4 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 24 Task 5：Add artifact access golden smoke。

本轮验证：

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Frontend build：passed，保留 Vite large chunk warning。
- Focused execution view tests：`4 passed`。
- Full frontend suite：`16` files passed，`21` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 4：`feat(frontend): link local execution artifacts`。
- 继续 Slice 24 Task 5：Add artifact access golden smoke。

## 2026-07-01 Slice 24 Task 3 Artifact Access Backend API 完成

本轮完成：

- 完成 Slice 24 Task 3：Add backend artifact download API。
- `backend/app/modules/ai_runtime/router.py` 新增：
  - `GET /api/artifacts/{artifact_id}/download`；
  - Artifact id lookup；
  - local artifact store read；
  - MIME type response；
  - safe `Content-Disposition` filename；
  - `ARTIFACT_NOT_FOUND`、`ARTIFACT_FILE_NOT_FOUND`、
    `ARTIFACT_PATH_UNSAFE`、`ARTIFACT_NOT_LOCAL` errors。
- 新增 `backend/app/tests/api/test_artifact_access.py` 覆盖：
  - 成功读取本地 artifact；
  - missing Artifact；
  - unsafe path；
  - external URL / inert reference。
- Slice 24 table 已记录 Task 2 commit `926cb50`，Task 3 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 24 Task 4：Add frontend artifact links。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py backend/app/tests/api/test_context_artifacts.py -q
git diff --check
```

验证结果：

- Artifact access API：`4 passed`。
- Artifact access + ContextArtifact API：`13 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 3：`feat(artifact): add local artifact access api`。
- 继续 Slice 24 Task 4：Add frontend artifact links。

## 2026-07-01 Slice 24 Task 2 Artifact Access Contract 完成

本轮完成：

- 完成 Slice 24 Task 2：Define local artifact access contract。
- `docs/contracts/02-api-contract.md` 新增：
  - `GET /api/artifacts/{artifact_id}/download`；
  - raw bytes response；
  - MIME type / safe filename behavior；
  - missing / unsafe / non-local artifact errors；
  - external imported artifact references remain inert。
- `docs/contracts/04-artifact-contract.md` 新增 Slice 24 local artifact access
  rules：
  - 只能通过 Artifact id 读取；
  - 只能读取 artifact root 内文件；
  - 不接受客户端路径；
  - 不 fetch/proxy/download 外部 URL；
  - 不修改 Artifact/TestRun/Report/Gate 状态。
- Slice 24 table 已记录 Task 1 commit `e06c94b`，Task 2 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 24 Task 3：Add backend artifact download API。

下次推荐任务：

- 提交 Task 2：`docs(v2): define artifact access contract`。
- 继续 Slice 24 Task 3：Add backend artifact download API。

## 2026-07-01 Slice 24 Task 1 Local Artifact Access Plan 完成

本轮完成：

- 完成 Slice 24 Task 1：Add Local Artifact Access Links task plan。
- 选择 Slice 24：Local Artifact Access Links。
- 选择原因：
  - 多个执行页已经展示 artifact path，但用户还不能从 workbench 直接打开本地证据；
  - artifact 可访问性是 evidence workbench 的核心价值；
  - 可以限定为 read-only local Artifact access，不引入云存储、分享、RBAC、
    tenants、permissions 或外部 provider fetch。
- 新增 Slice 24 计划：
  `docs/implementation/slices/slice-24-local-artifact-access-links.md`。
- `docs/implementation/10-v2-scope-options.md` 已补充 Slice 23 完成记录和
  Slice 24 推荐。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 24 Task 2：Define local artifact access contract。

下次推荐任务：

- 提交 Slice 24 Task 1：`docs(v2): add local artifact access plan`。
- 继续 Slice 24 Task 2：Define local artifact access contract。

## 2026-07-01 Slice 23 Completion Gate 完成

本轮完成：

- 完成 Slice 23：Frontend Build Baseline。
- Slice 23 task table 已记录：
  - Task 1：`b35fc8f`
  - Task 2：`07b1442`
  - Completion Gate：done pending commit。
- 确认 `npm --prefix frontend run build` 已恢复通过。
- `NEXT_AI_TASK.md` 已切换到：
  Select the next V2 small slice after Slice 23 completion。

本轮验证：

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Frontend build：passed，保留 Vite large chunk warning。
- Full frontend suite：`16` files passed，`21` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 completion gate：`docs(v2): complete frontend build baseline slice`。
- 选择下一条 V2 小切片。

## 2026-07-01 Slice 23 Task 2 Frontend Build Baseline 修复完成

本轮完成：

- 完成 Slice 23 Task 2：Fix frontend build TypeScript baseline。
- `frontend/src/api/client.ts` 将 JSON body 泛型约束从
  `Record<string, unknown>` 收窄问题改为 `object`，保留对象 payload 约束。
- `AiWorkbenchView.vue` 和 `RequirementReviewView.vue` 将 `replaceAll` 改为
  ES2020 可用的正则 `replace`。
- `CicdQualityCenterView.vue` 对可选 `risk_level` 增加 `low` fallback。
- Slice 23 table 已记录 Task 1 commit `b35fc8f`，Task 2 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 23 Completion Gate。

本轮验证：

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Frontend build：passed，保留 Vite large chunk warning。
- Full frontend suite：`16` files passed，`21` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 2：`fix(frontend): restore build baseline`。
- 继续 Slice 23 Completion Gate。

## 2026-07-01 Next V2 Slice Selected

本轮完成：

- 完成 Slice 22 后选择下一条小切片。
- 选择 Slice 23：Frontend Build Baseline。
- 选择原因：
  - Slice 22 前端测试通过，但额外 `npm --prefix frontend run build` 暴露既有
    TypeScript baseline errors；
  - build gate 是后续 frontend 切片的工程质量基础；
  - 可以限定为小范围 TypeScript 编译修复，不改变产品行为。
- `docs/implementation/10-v2-scope-options.md` 已补充 Slice 22 完成记录和 Slice
  23 推荐。
- 新增 Slice 23 计划：
  `docs/implementation/slices/slice-23-frontend-build-baseline.md`。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 23 Task 2：Fix frontend build TypeScript baseline。

下次推荐任务：

- 提交 Slice 23 Task 1：`docs(v2): add frontend build baseline plan`。
- 继续 Slice 23 Task 2：Fix frontend build TypeScript baseline。

## 2026-07-01 Slice 22 Completion Gate 完成

本轮完成：

- 完成 Slice 22：JMeter Local Execution Evidence。
- Slice 22 task table 已记录：
  - Task 1：`59d3918`
  - Task 2：`10fa27d`
  - Task 3：`0d1a666`
  - Task 4：`b836e65`
  - Task 5：`abcf50d`
  - Task 6：`a2fc879`
  - Completion Gate：done pending commit。
- 确认 JMeter 仍是本地、allowlisted、non-GUI execution evidence：
  - 不新增 JMX 编辑器；
  - 不新增性能 dashboard；
  - 不新增 distributed/cloud JMeter；
  - 不新增 arbitrary shell、secrets、CI provider controls、RAG/MCP runtime、
    RBAC、tenants、permissions。
- `NEXT_AI_TASK.md` 已切换到：
  Select the next V2 small slice after Slice 22 completion。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py backend/app/tests/golden/test_jmeter_local_execution_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- JMeter API + golden：`6 passed`。
- Full frontend suite：`16` files passed，`21` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 completion gate：`docs(v2): complete jmeter execution slice`。
- 选择下一条 V2 小切片。

## 2026-07-01 Slice 22 Task 6 JMeter Golden Smoke 完成

本轮完成：

- 完成 Slice 22 Task 6：Add JMeter local execution golden smoke。
- 新增 `backend/app/tests/golden/test_jmeter_local_execution_golden.py`：
  - 使用 fake JMeter executable，不依赖真实本地 JMeter；
  - 通过 `/api/test-runs` 执行 `runner_mode=jmeter_local`；
  - 验证 approved/configured `TestCommand(command_type=jmeter)` 创建 TestRun；
  - 验证 stdout/stderr、`jmeter_jtl`、`parsed_output` artifacts；
  - 验证 parsed_result、Sampler TestResult rows 和持久化记录；
  - 验证不自动创建 Report、FailureAnalysis、QualityGateDecision。
- 新增 `docs/fixtures/11-jmeter-local-execution-golden.md` 记录 golden command、
  JTL parsed result、artifact/state 期望和非目标。
- Slice 22 table 已记录 Task 5 commit `abcf50d`，Task 6 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 22 Completion Gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_jmeter_local_execution_golden.py -q
```

验证结果：

- JMeter local execution golden：`1 passed`。

下次推荐任务：

- 提交 Task 6：`test(golden): add jmeter local execution smoke`。
- 继续 Slice 22 Completion Gate。

## 2026-07-01 Slice 22 Task 5 JMeter Frontend Shell 完成

本轮完成：

- 完成 Slice 22 Task 5：Add JMeter execution frontend shell。
- 新增 `frontend/src/views/execution/JMeterExecutionView.vue`：
  - TestCommand-only JMeter 启动入口；
  - `runner_mode=jmeter_local`；
  - 展示 TestRun 状态、退出码、耗时、运行器、网络、命令；
  - 展示 total/passed/failed/error、Sampler 数、断言数、平均延迟；
  - 展示 `jmeter_jtl`、`parsed_output`、stdout/stderr 工件；
  - 展示 Sampler TestResult 行。
- 新增 `frontend/src/views/execution/JMeterExecutionView.spec.ts` 覆盖启动、
  刷新、JTL 工件、Sampler 结果和中文指标。
- 路由新增 `/execution/jmeter`，侧边栏新增 `JMeter 执行`。
- `frontend/src/stores/execution.ts` 将刷新错误文案从 pytest 专属改为通用执行文案。
- Slice 22 table 已记录 Task 4 commit `b836e65`，Task 5 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 22 Task 6：Add JMeter local execution golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts src/layouts/WorkbenchLayout.spec.ts
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- JMeter frontend + Workbench navigation tests：`3 passed`。
- Full frontend suite：`16` files passed，`21` tests passed。
- `git diff --check` clean。

额外观察：

- 已启动 frontend dev server，Vite 自动使用 `http://127.0.0.1:5174/`；
  JMeter 页面地址为 `http://127.0.0.1:5174/execution/jmeter`。
- `curl -I http://127.0.0.1:5174/execution/jmeter` 返回 `200 OK`。
- 额外执行 `npm --prefix frontend run build` 时，当前 frontend 仍存在既有
  TypeScript 基线错误，主要在 API `postJson` 泛型约束、`replaceAll` target
  lib、以及 CI/CD 页面可选值收窄；本轮未扩散修复，因为 Task 5 验证命令是
  frontend test + diff check。

下次推荐任务：

- 提交 Task 5：`feat(frontend): show jmeter execution evidence`。
- 继续 Slice 22 Task 6：Add JMeter local execution golden smoke。

## 2026-07-01 Slice 22 Task 4 JMeter Local Runner Backend 完成

本轮完成：

- 完成 Slice 22 Task 4：Add JMeter runner backend。
- `backend/app/modules/execution/jmeter_runner.py` 新增：
  - `JMeterRunner`；
  - JMeter allowlist 校验；
  - non-GUI command 规范：`jmeter -n -t <plan.jmx> -l <result.jtl>`；
  - JTL output path 校验；
  - fake executable 友好的 subprocess 执行。
- `backend/app/modules/projects/service.py` 支持 `command_type=jmeter` allowlist。
- `backend/app/modules/execution/service.py` 支持：
  - `runner_mode=jmeter_local`；
  - active `TestCommand(command_type=jmeter)`；
  - stdout/stderr、`jmeter_jtl`、parsed_output artifacts；
  - JMeter TestResult rows。
- `backend/app/tests/api/test_jmeter_execution.py` 新增：
  - fake JMeter executable 成功路径；
  - forbidden shell operator 拒绝路径。
- Slice 22 table 已记录 Task 3 commit `0d1a666`，Task 4 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 22 Task 5：Add JMeter execution frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py backend/app/tests/api/test_newman_execution.py backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/api/test_playwright_minimal_loop.py -q
git diff --check
```

验证结果：

- JMeter runner/API tests：`5 passed`。
- JMeter + Newman + pytest + Playwright execution tests：`27 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 4：`feat(execution): add jmeter local runner`。
- 继续 Slice 22 Task 5：Add JMeter execution frontend shell。

## 2026-07-01 Slice 22 Task 3 JMeter Parser 完成

本轮完成：

- 完成 Slice 22 Task 3：Add JMeter parser and backend API tests。
- 新增 `backend/app/modules/execution/jmeter_runner.py`：
  - 支持 CSV JTL；
  - 支持 XML `sample` / `httpSample` JTL；
  - 生成 parsed_result 聚合：total / passed / failed / skipped / error /
    sampler_count / assertion_count / duration_ms / average_latency_ms；
  - 生成 JMeter TestResult candidate，保留 response code/message、latency、
    bytes、timestamp 等 metadata；
  - 缺失或空 JTL 抛出 `JMeterRunnerCommandError`。
- 新增 `backend/app/tests/api/test_jmeter_execution.py` 覆盖 parser 行为。
- 当前 Task 3 不执行本地 JMeter，也不要求真实 JMeter 安装。
- Slice 22 table 已记录 Task 2 commit `10fa27d`，Task 3 done pending commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 22 Task 4：Add JMeter runner backend。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_jmeter_execution.py backend/app/tests/api/test_newman_execution.py -q
git diff --check
```

验证结果：

- JMeter parser/API tests：`3 passed`。
- JMeter + Newman execution tests：`7 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 3：`feat(execution): parse jmeter evidence`。
- 继续 Slice 22 Task 4：Add JMeter runner backend。

## 2026-07-01 Slice 22 Task 2 JMeter Execution Contract Boundary 完成

本轮完成：

- 完成 Slice 22 Task 2：Define JMeter execution contract boundary。
- 数据合同已定义：
  - `TestCommand.command_type=jmeter`；
  - `TestRun.runner_mode=jmeter_local`；
  - JMeter TestRun parsed result 字段；
  - JMeter ToolDefinition allowlist 规则。
- API 合同已定义：
  - JMeter 仍走 `POST /api/test-runs`；
  - `runner_mode=jmeter_local`；
  - 不新增 JMX 编辑、性能 dashboard、分布式 runner、云压测 API。
- 状态机合同已定义：
  - sampler/assertion 失败 -> `failed`；
  - 启动失败、timeout、allowlist 拒绝、JTL 缺失/损坏、parser 失败 -> `error`。
- Artifact 合同已定义：
  - `jmeter_jtl`；
  - JMeter `parsed_output` 聚合字段；
  - JMeter artifacts 仅为 evidence，不自动触发 report/failure/gate。
- Slice 22 task table 已记录 Task 1 commit `59d3918`，Task 2 done pending
  commit。
- `NEXT_AI_TASK.md` 已切换到：
  Slice 22 Task 3：Add JMeter parser and backend API tests。

本轮验证：

```bash
rg -n "JMeter|jmeter|jmeter_local|jmeter_jtl|ToolDefinition|command_type" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-22-jmeter-local-execution.md
git diff --check
```

验证结果：

- JMeter contract keywords found across data/API/state/artifact contracts and
  Slice 22 plan。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 2：`docs(v2): define jmeter execution contract`。
- 继续 Slice 22 Task 3：Add JMeter parser and backend API tests。

## 2026-07-01 Slice 22 Task 1 JMeter Local Execution Plan 完成

本轮完成：

- 完成 Slice 21 后下一条 V2 小切片选择。
- 用户确认选择 A：JMeter Local Execution Evidence。
- 只读子代理 `Pascal` 评估后建议选择 JMeter，但先做计划和契约边界，
  不直接进入实现；该建议已吸收。
- 新增 Slice 22 计划：
  `docs/implementation/slices/slice-22-jmeter-local-execution.md`。
- 更新 V2 scope options：
  `docs/implementation/10-v2-scope-options.md`。
- 已将 `NEXT_AI_TASK.md` 切换到：
  Slice 22 Task 2：Define JMeter execution contract boundary。

Slice 22 当前边界：

- 只做本地、allowlisted、non-GUI JMeter 执行证据。
- 后续 contract 需要定义：
  - `TestCommand.command_type=jmeter`
  - `TestRun.runner_mode=jmeter_local`
  - JMeter ToolDefinition allowlist
  - `jmeter_jtl` artifact
  - parsed sampler/assertion evidence
- 不做 JMX 编辑器、参数化 UI、性能趋势 dashboard、分布式 JMeter、云压测、
  任意 shell、secrets manager、CI provider 控制、RAG runtime、MCP runtime、
  RBAC、tenants、permissions。

本轮验证：

```bash
test -f docs/implementation/slices/slice-22-jmeter-local-execution.md
rg -n "JMeter|jmeter|jmeter_local|Product Value Answer|Non-goals|Task Table|Task 2" docs/implementation/slices/slice-22-jmeter-local-execution.md docs/implementation/10-v2-scope-options.md
git diff --check
```

验证结果：

- Slice 22 plan file exists。
- JMeter planning keywords found in Slice 22 plan and V2 scope options。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 1：`docs(v2): add jmeter execution slice plan`。
- 继续 Slice 22 Task 2：Define JMeter execution contract boundary。

## 2026-07-01 Slice 21 Completion Gate 完成

本轮完成：

- 完成 Slice 21：Local Review Attribution History。
- Slice 21 task table 已记录：
  - Task 1：`f121483`
  - Task 2：`b77262b`
  - Task 3：`31bb8cc`
  - Task 4：`53c313a`
  - Task 5：`847c399`
  - Task 6：`0112b89`
  - Completion gate：done pending commit。
- 确认 ReviewHistory 仍是本地 append-only attribution evidence：
  - 不新增通用 public ReviewHistory create/update/delete；
  - 不新增 RBAC、roles、permissions、tenants；
  - 不新增 assignment、notifications、team inbox、远程 provider governance；
  - 不新增 RAG runtime 或 MCP runtime。
- `NEXT_AI_TASK.md` 已切换到：
  Select the next V2 small slice after Slice 21 completion。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/golden/test_review_history_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- ReviewHistory API + golden：`6 passed`。
- Full frontend suite：`15` files passed，`20` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 completion gate：`docs(v2): complete local review history slice`。
- 选择下一条 V2 小切片。

## 2026-07-01 Slice 21 Task 6 Review History Golden Smoke 完成

本轮完成：

- 完成 Slice 21 Task 6：Add review history golden smoke。
- 新增 fixture：
  `docs/fixtures/10-local-review-history-golden.md`。
- 新增 golden smoke：
  `backend/app/tests/golden/test_review_history_golden.py`。
- Golden 走通现有 review-gated evidence 流程：
  - 创建本地 CICDRun；
  - 生成 UnitTestPatch；
  - approve UnitTestPatch；
  - apply approved patch；
  - 记录 new-test 和 regression evidence；
  - compute QualityGateDecision。
- Golden 断言 ReviewHistory：
  - UnitTestPatch approve 事件记录 entity、related CICDRun、action、
    `scope_validated -> approved`、Default User、comment、created_at；
  - QualityGateDecision compute 事件记录 entity、related CICDRun、action、
    `pending -> passed`、Default User、evidence ids、created_at；
  - related CICDRun 查询可关联到两条 history events。
- Guardrail：未新增 roles、permissions、tenants；未新增通用 public
  ReviewHistory 写接口。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_review_history_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/golden/test_review_history_golden.py -q
git diff --check
```

验证结果：

- ReviewHistory golden smoke：`1 passed`。
- ReviewHistory API + golden：`6 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 6：`test(golden): add local review history smoke`。
- 继续 Slice 21 Completion Gate。

## 2026-07-01 Slice 21 Task 5 Frontend Review History Panels 完成

本轮完成：

- 完成 Slice 21 Task 5：Add frontend review history panels。
- 新增 frontend ReviewHistory read helper：
  `frontend/src/api/reviewHistory.ts`。
- 在现有 review stores 中加入本地评审历史读取：
  - `frontend/src/stores/cases.ts`
  - `frontend/src/stores/automation.ts`
  - `frontend/src/stores/cicd.ts`
- 在现有 review 页面加入紧凑的“本地评审历史”二级面板：
  - 用例生成评审：GeneratedCaseCandidate history；
  - AutomationDraft 评审：AutomationDraft history；
  - CI/CD 质量中心：UnitTestPatch history；
  - CI/CD 质量中心：QualityGateDecision history。
- 面板展示：
  - action；
  - reviewer；
  - status transition；
  - created_at 时间；
  - comment；
  - evidence count。
- 页面文案使用中文标签，同时保留 TestCase、AutomationDraft、
  UnitTestPatch、QualityGateDecision 等产品模型术语。
- 未新增用户、角色、权限、租户、任务分配、通知、团队 inbox 或通用
  ReviewHistory 写接口。
- 并发子代理 `Euclid` 只负责测试文件，补充了 review-history fetch mock
  和断言，主线完成源码与最终验证整合。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/cases/CaseGenerationReviewView.spec.ts src/views/automation/AutomationDraftReviewView.spec.ts src/views/cicd/CicdQualityCenterView.spec.ts
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Focused review surface tests：`3` files passed，`4` tests passed。
- Full frontend suite：`15` files passed，`20` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 5：`feat(frontend): show local review history`。
- 继续 Slice 21 Task 6：Add review history golden smoke。

## 2026-07-01 Slice 21 Task 4 Review History Action Hooks 完成

本轮完成：

- 完成 Slice 21 Task 4：Attach history to existing review actions。
- 已在成功动作后写入 ReviewHistory：
  - GeneratedCaseCandidate：approve / approve_after_edit / reject；
  - AutomationDraft：edit / approve；
  - UnitTestPatch：approve / reject；
  - QualityGateDecision：compute / recompute。
- 保持原有状态机校验：
  - 非法动作不会写 ReviewHistory；
  - 不改变审批是否允许；
  - 不新增 public ReviewHistory 写接口。
- QualityGateDecision history：
  - primary entity 为 QualityGateDecision；
  - related entity 为 CICDRun；
  - from/to status 记录 CICDRun `quality_gate_status` 变化。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_unit_test_patch_regression.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_unit_test_patch_regression.py backend/app/tests/api/test_ci_run_metadata_import.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
git diff --check
```

验证结果：

- Task 4 focused tests：`37 passed`。
- Related backend + golden regression：`91 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 4：`feat(review): record review history events`。
- 继续 Slice 21 Task 5：Add frontend review history panels。

## 2026-07-01 Slice 21 Task 3 Review History Model And Service 完成

本轮完成：

- 完成 Slice 21 Task 3：Add review history model and service。
- 新增 backend ReviewHistory 模块：
  - `backend/app/modules/review_history/models.py`
  - `backend/app/modules/review_history/schemas.py`
  - `backend/app/modules/review_history/service.py`
  - `backend/app/modules/review_history/router.py`
  - `backend/app/modules/review_history/__init__.py`
- 在 `backend/app/main.py` 注册 `GET /api/review-history`。
- 新增 Alembic migration：
  `backend/alembic/versions/20260701_0006_review_history.py`。
- 新增测试：
  `backend/app/tests/api/test_review_history.py`。
- 当前实现能力：
  - service 内部 append ReviewHistory；
  - 默认 reviewer 为 `Default User`；
  - 支持 entity 与 related entity 过滤读取；
  - 校验 `evidence_artifact_ids` 必须属于同项目已存在 Artifact；
  - 没有 public `POST /api/review-history`；
  - migration smoke 覆盖表字段。
- 未做且保留给 Task 4：
  - 还未挂接 GeneratedCaseCandidate / AutomationDraft / UnitTestPatch /
    QualityGateDecision 的现有动作。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/api/test_projects.py backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/db/test_case_generation_models.py -q
git diff --check
```

验证结果：

- ReviewHistory focused tests：`5 passed`。
- Related backend regression：`23 passed`。
- `git diff --check` clean。

下次推荐任务：

- Task 3 已提交：`31bb8cc feat(review): add local review history service`。

## 2026-07-01 Slice 21 Task 2 Review History Contract Boundary 完成

本轮完成：

- 完成 Slice 21 Task 2：Define review history contract boundary。
- 数据合同新增 `ReviewHistory`：
  - 本地 append-only review attribution evidence；
  - `entity_type/entity_id`、`related_entity_type/related_entity_id`；
  - `action`、`from_status`、`to_status`；
  - `reviewer=Default User` 默认本地显示标签；
  - `comment`、`evidence_artifact_ids`、`metadata_json`、`created_at`。
- API 合同新增 `GET /api/review-history`：
  - 只读列表；
  - 支持 project、entity、related entity 过滤；
  - 不提供通用 create/update/delete。
- 状态机合同明确 ReviewHistory 只是成功动作后的 side effect：
  - GeneratedCaseCandidate approve / approve_after_edit / reject；
  - AutomationDraft edit / approve / reject；
  - UnitTestPatch approve / reject；
  - QualityGateDecision compute / recompute。
- Artifact 合同明确 Slice 21 不新增 `review_history` artifact type，只引用
  已存在 Artifact id。
- 子代理 `Lorentz` 只读审阅后建议：
  - case approval history 主写 GeneratedCaseCandidate，TestCase 通过
    `source_candidate_id` 展示；
  - QualityGateDecision history 用 related CICDRun 表示
    `quality_gate_status` 变化。
  已吸收到合同。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 21 Task 3：
  Add review history model and service。

本轮验证：

```bash
rg -n "ReviewHistory|review history|review attribution|Default User|RBAC|permissions" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-21-local-review-attribution-history.md
git diff --check
```

验证结果：

- ReviewHistory contract keywords found in data/API/state/artifact contracts
  and Slice 21 plan。
- `git diff --check` clean。

下次推荐任务：

- Task 2 已提交：`b77262b docs(review): define local review history contract`。

## 2026-07-01 V2 Next Slice Selection 完成

本轮完成：

- 选择 Slice 20 后的下一条 V2 小切片。
- 并发启动两个只读子代理：
  - Candidate Direction B follow-up：JMeter local execution evidence；
  - Candidate Direction C：local review attribution/history。
- 两个方向都可行；最终选择 Candidate Direction C，并收窄命名为：
  `Slice 21: Local Review Attribution History`。
- 选择理由：
  - Slice 18/19/20 已分别补强 runner evidence、knowledge evidence、CI
    import evidence。
  - 下一步更应该补强 human-reviewed evidence loop 的可追溯性。
  - 本地 review attribution/history 不依赖外部工具安装，也不需要引入
    RBAC/权限/团队治理。
  - JMeter local execution evidence 保留为后续强候选。
- 新增计划文档：
  `docs/implementation/slices/slice-21-local-review-attribution-history.md`。
- 更新 V2 scope options：
  - 记录 Slice 20 已完成；
  - 推荐 Slice 21；
  - 明确非目标：RBAC、roles、permissions、tenants、SSO、enterprise audit、
    assignment、notifications、team inbox、remote provider governance。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 21 Task 2：
  Define review history contract boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-21-local-review-attribution-history.md
rg -n "Local Review Attribution History|Product Value Answer|Non-goals|Task Table|append-only|RBAC|permissions" docs/implementation/slices/slice-21-local-review-attribution-history.md docs/implementation/10-v2-scope-options.md
git diff --check
```

验证结果：

- Slice 21 plan file exists。
- Scope keywords found in Slice 21 plan and V2 scope options。
- `git diff --check` clean。

下次推荐任务：

- Planning task 已提交：`f121483 docs(v2): add local review history slice plan`。

## 2026-07-01 Slice 20 Completion Gate 完成

本轮完成：

- 完成 Slice 20：CI Run Metadata Import。
- 已运行 completion gate 验证：
  - CI import API tests；
  - CI import golden smoke；
  - frontend suite；
  - `git diff --check`。
- 确认 Slice 20 仍是 import-only / evidence-first：
  - 不调用 remote CI provider；
  - 不接收 webhook；
  - 不触发 pipeline / rerun / cancel / schedule；
  - 不增加 PR comment、deploy、release、credentials、RBAC、tenants、
    permissions、marketplace、RAG runtime 或 MCP runtime。
- Slice 20 task table 已记录 Task 6 commit `499ec1d`，completion gate done
  pending commit。
- 已将 `NEXT_AI_TASK.md` 切换到：
  Select the next V2 small slice after Slice 20 completion。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py backend/app/tests/golden/test_ci_run_metadata_import_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Slice 20 API + golden tests：`54 passed`。
- Frontend suite：`15` files passed，`20` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 completion gate：`docs(v2): complete ci metadata import slice`。
- 选择下一条 V2 小切片。

## 2026-07-01 Slice 20 Task 6 完成

本轮完成：

- 完成 Slice 20 Task 6：Add CI import golden smoke。
- 新增 fixture：
  `docs/fixtures/09-ci-run-metadata-import-golden.md`。
- 新增 golden smoke：
  `backend/app/tests/golden/test_ci_run_metadata_import_golden.py`。
- Golden 证明：
  - static CI metadata JSON 可通过 `POST /api/cicd/runs/import` 导入；
  - 生成 `CICDRun(source_type=ci_import, trigger_type=imported,
    status=imported)`；
  - 生成 imported `CICDChangedFile` rows；
  - 生成 `ci_run_metadata` 和 `changed_files` evidence artifacts；
  - `GET /api/cicd/runs/{id}` 暴露前端可读的 `ci_run_metadata` evidence；
  - imported artifact references 是 inert references；
  - imported CI conclusion 不会自动创建或通过 QualityGateDecision。
- Golden 明确确认没有 `QualityGateDecision`、`UnitTestPatch`、
  `AutomationDraft`、`TestRun` 或 `Report`。
- Slice 20 task table 已记录 Task 5 commit `6aedab0`，Task 6 done pending
  commit。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 20 Completion Gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_run_metadata_import_golden.py -q
```

验证结果：

- CI import golden smoke：`1 passed`。

下次推荐任务：

- 提交 Task 6：`test(golden): add ci metadata import smoke`。
- 继续 Slice 20 Completion Gate。

## 2026-07-01 Slice 20 Task 5 完成

本轮完成：

- 按用户要求继续多子代理并发：
  - 一个只读检查 CI/CD 前端页面和测试模式；
  - 一个只读检查后端 read surface 是否能暴露 `ci_run_metadata`。
- 完成 Slice 20 Task 5：Add CI import frontend evidence display。
- `CI/CD 质量中心` 新增导入 CI 证据展示：
  - Provider inert label；
  - 导入状态；
  - CI 结论；
  - QualityGateDecision 仍为本地门禁状态；
  - Job / external run id；
  - inert artifact references。
- 风险分析证据表继续只显示 `risk_analysis`。
- 进行了一个必要的窄后端 read surface 改动：
  - `GET /api/cicd/runs/{id}` 的 `analysis_artifacts` 现在包含
    `risk_analysis` 和 `ci_run_metadata`；
  - 没有走 RAG/extension surface；
  - 没有新增远程 provider 控件。
- 新增前端 API 类型和页面测试，断言不会出现重新运行、取消流水线、
  Webhook、Token、部署、发布等远程控制文案。
- Slice 20 task table 已记录 Task 4 commit `554e74c`，Task 5 done pending
  commit。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 20 Task 6：Add CI import golden
  smoke。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/api/test_ci_run_metadata_import.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- CI metadata import API tests：`53 passed`。
- Existing CI/CD quality center + import API tests：`60 passed`。
- Frontend suite：`15` files passed，`20` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 5：`feat(frontend): show ci import evidence`。
- 继续 Slice 20 Task 6：Add CI import golden smoke。

## 2026-07-01 Slice 20 Task 4 完成

本轮完成：

- 按用户要求继续多子代理并发：
  - 一个只读检查 router/schema/API 测试模式；
  - 一个只读检查 service/model/artifact 持久化规则。
- 完成 Slice 20 Task 4：Add CI run import API。
- 新增 `POST /api/cicd/runs/import`。
- 新增 import API response schemas。
- 持久化 imported CI metadata 为 evidence-only 记录：
  - `CICDRun(status=imported, source_type=ci_import, trigger_type=imported)`；
  - imported `CICDChangedFile` rows；
  - `ci_run_metadata.json` Artifact；
  - compatible `changed_files.json` Artifact。
- API 错误映射覆盖：
  - invalid payload；
  - remote control fields；
  - credentials；
  - provider operation；
  - external fetch；
  - duplicate external run。
- duplicate 范围按 project/repository/provider/external_run_id。
- import 不创建 `QualityGateDecision`、`UnitTestPatch`、`AutomationDraft`、
  `TestRun` 或 `Report`。
- Slice 20 task table 已记录 Task 3 commit `21ce127`，Task 4 done pending
  commit。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 20 Task 5：Add CI import frontend
  evidence display。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/api/test_ci_run_metadata_import.py -q
git diff --check
```

验证结果：

- CI metadata import API tests：`53 passed`。
- Existing CI/CD quality center + import API tests：`60 passed`。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 4：`feat(cicd): add ci metadata import api`。
- 继续 Slice 20 Task 5：frontend evidence display。

## 2026-07-01 Slice 20 Task 3 完成

本轮完成：

- 启动本地 Web 预览：
  - Vite 服务运行在 `http://127.0.0.1:5173/`。
  - 已在内置浏览器打开，页面标题为 `Chtest AI 测试工作台`。
- 按用户要求启动两个只读子代理并发检查：
  - 一个检查 `cicd` service/schema/test 可复用点；
  - 一个检查 Slice 20 合同、负向字段和文档更新边界。
- 完成 Slice 20 Task 3：Add deterministic CI metadata parser。
- 新增 parser-only CI import schemas。
- 新增 deterministic parser service：
  - 解析静态 CI metadata JSON；
  - 复用现有 changed-file role/risk 分类；
  - 输出 `ci_run_metadata.json` 内容和 metadata；
  - artifact references 仅作为 inert references 保存；
  - 不调用远程 provider，不下载 URL。
- 新增 CI import 专用错误类：
  - `INVALID_CI_IMPORT_PAYLOAD`
  - `CI_IMPORT_CONTROL_FIELD_REJECTED`
  - `CI_IMPORT_CREDENTIAL_REJECTED`
  - `CI_IMPORT_UNSUPPORTED_PROVIDER_OPERATION`
  - `CI_IMPORT_EXTERNAL_FETCH_FORBIDDEN`
- 新增测试覆盖正向解析、changed-file 规范化、控制字段、凭据字段、外部抓取字段、provider operation 和 malformed payload。
- Slice 20 task table 已记录 Task 2 commit `2201b94`，Task 3 done pending
  commit。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 20 Task 4：Add CI run import API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/api/test_ci_run_metadata_import.py -q
```

验证结果：

- CI metadata import parser tests：`46 passed`。
- Existing CI/CD quality center + parser tests：`53 passed`。

下次推荐任务：

- 先运行 `git diff --check` 并提交 Task 3：
  `feat(cicd): add ci metadata import parser`。
- 然后继续 Slice 20 Task 4：Add CI run import API。

## 2026-06-30 Slice 20 Task 2 完成

本轮完成：

- 完成 Slice 20 Task 2：Define CI import contract boundary。
- 数据合同已定义：
  - `source_type=ci_import`。
  - provider 只是 inert source label。
  - imported CI conclusion 只是 evidence，不自动通过 QualityGateDecision。
- API 合同已定义：
  - `POST /api/cicd/runs/import`。
  - static CI metadata import request/response。
  - 拒绝 webhook、trigger、rerun、cancel、schedule、PR comment、commit
    status update、deploy、release、credentials、external fetch 和 provider
    operation。
- 状态机合同已定义：
  - import 是本地 evidence import 状态，不是 remote provider execution。
  - `quality_gate_status` 在显式 quality gate recompute 前保持 `pending`。
- Artifact 合同已定义：
  - `ci_run_metadata.json`。
  - imported artifact references 是 inert references。
  - `remote_fetch_performed=false`。
- Error code 合同已定义：
  - CI import payload/control/credential/provider/fetch/duplicate rejection
    codes。
- 已处理文档评审发现：
  - 数据合同补齐 `imported` / `import_failed` CICDRun statuses。
  - 数据合同补齐 `ci_run_metadata` Artifact type。
  - provider label 清单保持一致。
  - API 合同显式 `trigger_type=imported`。
  - 明确 imported CI run details 存入 `ci_run_metadata.json`，不是 CICDRun
    columns。
- Slice 20 task table 已记录 Task 1 commit `b1acde6`，Task 2 done pending
  commit。
- 用户已在 2026-07-01 明确同意继续开发。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 20 Task 3：Add deterministic CI
  metadata parser。

本轮验证：

```bash
rg -n "ci_import|CI import|imported CI|ci_run_metadata|remote CI provider|QualityGateDecision|CI_IMPORT_" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/06-error-code-contract.md docs/implementation/slices/slice-20-ci-run-metadata-import.md
git diff --check
```

验证结果：

- Contract boundary keywords found across data, API, state-machine, artifact,
  error-code, and Slice 20 docs。
- `git diff --check` clean。

下次推荐任务：

- 提交 Task 2。
- 开始 Slice 20 Task 3：deterministic CI metadata parser。

## 2026-06-30 V2 Next Slice Selection 完成

本轮完成：

- 按用户要求启动多个子代理并发评估下一条 V2 小切片。
- 子代理结论：
  - 方向 B：推荐 JMeter local execution evidence，但不推荐 Appium 或
    traffic capture 先做。
  - 方向 C：推荐 local review attribution/history，但必须排除 RBAC、
    tenants、permissions、SSO、enterprise audit。
  - 方向 D：推荐 import-only CI evidence bridge。
- 最终选择方向 D：
  `Slice 20: CI Run Metadata Import`。
- 选择理由：
  - 直接复用 Slice 15/16 的 CICDRun、CICDChangedFile、Artifact、
    QualityGateDecision 和 CI/CD 管理证据链。
  - 把外部 CI 的事实结果导入 Chtest，而不是让 Chtest 控制远程 CI。
  - imported CI status 是 evidence，不是 QualityGateDecision authority。
- 新增计划：
  `docs/implementation/slices/slice-20-ci-run-metadata-import.md`。
- 更新 V2 scope options：
  - 记录 Slice 19 已完成。
  - 推荐 Slice 20 import-only CI metadata evidence。
- 更新 `NEXT_AI_TASK.md` 到 Slice 20 Task 1。

本轮验证：

```bash
test -f docs/implementation/slices/slice-20-ci-run-metadata-import.md
rg -n "CI Run Metadata Import|Product Value Answer|Non-goals|Task Table|import-only|remote CI provider" docs/implementation/slices/slice-20-ci-run-metadata-import.md docs/implementation/10-v2-scope-options.md
git diff --check
```

验证结果：

- Slice 20 plan file exists。
- Scope keywords found in Slice 20 plan and V2 scope options。
- `git diff --check` clean。

下次推荐任务：

- 提交本 planning task。
- 继续 Slice 20 Task 2：Define CI import contract boundary。

## 2026-06-30 Slice 19 Completion Gate 完成

本轮完成：

- 完成 Slice 19：Deterministic Knowledge Retrieval Stub。
- Slice 19 task table 已记录：
  - Task 5 commit：`b578fac`。
  - Task 6 commit：`ebd67af`。
  - Completion Gate：done，pending commit。
- 确认本 slice 只交付本地 deterministic ContextArtifact retrieval stub：
  - 同项目 ContextArtifact 检索。
  - `safe_to_show=true` 且 `allowed_for_prompt=true` 才能进入 prompt。
  - evidence artifact 记录 query terms、matched terms、scores、snippets、
    ContextArtifact ids。
  - RAG 知识库展示 latest retrieval evidence。
- 未新增 vector database、embedding、reranking、external RAG provider runtime、
  MCP runtime、RBAC、tenants、permissions、marketplace、cloud sync 或 remote CI
  provider integration。
- 已将 `NEXT_AI_TASK.md` 切换到：
  Select the next V2 small slice after Slice 19 completion。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Backend deterministic retrieval + requirement review + extension surface +
  golden smoke：`23 passed`。
- Frontend suite：`15` files passed，`19` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 提交 completion gate。
- 然后按 `NEXT_AI_TASK.md` 做规划任务：选择下一个 V2 小切片。

## 2026-06-30 Slice 19 Task 6 完成

本轮完成：

- 完成 Slice 19 Task 6：Add deterministic retrieval golden smoke。
- 新增 fixture：
  `docs/fixtures/08-deterministic-knowledge-retrieval-golden.md`。
- 新增 golden smoke：
  `backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py`。
- Golden 证明完整证据链：
  - safe `coupon-api-notes.md` ContextArtifact。
  - deterministic local KnowledgeAdapter stub。
  - requirement review `use_knowledge=true`。
  - `used_knowledge=true` 和 exact `used_context_artifact_ids`。
  - AITask owned `knowledge_retrieval` evidence Artifact。
  - persisted `knowledge_retrieval.json` 中的 query terms、matched terms、
    score、snippet、SHA256、prompt eligibility、redaction 状态。
  - RAG 知识库 `/knowledge-base` 可读取 latest retrieval evidence。
- Golden 明确排除 vector database、embedding、reranking、external RAG
  provider、MCP runtime、RBAC、tenants、permissions、marketplace、cloud sync 和
  remote CI provider integration。
- Golden 暴露并修复了一个窄后端 surface 缺口：Requirement Review 现在把
  bounded retrieval result summaries 同步写入 `knowledge_retrieval` Artifact
  metadata，确保 RAG 知识库 `/knowledge-base` 可以稳定读取 snippets、scores
  和 matched terms。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Completion Gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py -q
git diff --check
```

验证结果：

- Golden smoke：`1 passed`。
- Related backend deterministic retrieval + requirement review + extension
  surface + golden tests：`23 passed`。
- `git diff --check` clean。

下次推荐任务：

- 先提交 Task 6。
- 然后按 `NEXT_AI_TASK.md` 运行 Slice 19 Completion Gate：
  backend API + requirement review + extension surface + golden smoke +
  frontend test + diff check。

## 2026-06-30 Slice 19 Task 5 完成

本轮完成：

- 完成 Slice 19 Task 5：Add retrieval evidence frontend display。
- RAG 知识库页面新增 deterministic retrieval evidence 展示：
  - 检索证据计数。
  - KnowledgeAdapter 检索模式。
  - ContextArtifact 行展示检索次数和最近检索时间。
  - 最近检索证据展示 query terms、matched terms、scores、snippets 和来源
    ContextArtifact。
  - 无 evidence 时显示空态，不暴露检索发起控件。
- 前端类型/store 已支持 `latest_retrievals`、`retrieved_count`、
  `latest_retrieved_at`。
- 为了让页面展示真实 evidence，补了很窄的 backend extension surface：
  `/knowledge-base` 从 `knowledge_retrieval` artifacts 派生
  `latest_retrievals`、`retrieved_count`、`latest_retrieved_at`。
- 没有新增 vector search、Embedding、provider runtime config、MCP runtime、
  RBAC、tenants、permissions、marketplace 或 remote sync 控件。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Task 6：Add deterministic
  retrieval golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py backend/app/tests/api/test_deterministic_knowledge_retrieval.py -q
git diff --check
```

验证结果：

- Frontend suite：`15` files passed，`19` tests passed。
- Extension + deterministic retrieval API tests：`12 passed`。
- `git diff --check` clean。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 新增 deterministic retrieval golden smoke。
- Golden 需要证明 ContextArtifact -> deterministic retrieval -> requirement
  review -> knowledge_retrieval evidence -> RAG 知识库 surface。

## 2026-06-30 Slice 19 Task 4 完成

本轮完成：

- 完成 Slice 19 Task 4：Attach retrieval evidence to AI task flows。
- Requirement Review 在 `use_knowledge=true` 时会调用 deterministic local
  retrieval。
- 只有实际检索到 snippets 时才记录：
  - `used_knowledge=true`
  - `used_context_artifact_ids`
  - `retrieval_evidence_artifact_id`
- 新增 `knowledge_retrieval.json` evidence artifact：
  - owner 为 AITask。
  - `artifact_type=knowledge_retrieval`。
  - metadata 包含 `created_by_component=DeterministicKnowledgeAdapter`、
    `retrieval_mode=deterministic_local`、query terms、result count、retrieved
    ContextArtifact ids、redaction 状态。
  - 文件内容包含 query text、query terms、matched terms、scores、snippets、
    SHA256、ContextArtifact ids、allowed_for_prompt 和 redaction 信息。
- 保持旧行为：
  - `use_knowledge=false` 不触发 retrieval。
  - 显式 `context_artifact_ids` 仍进入 AI task context manifest。
  - adapter 未配置或无命中时 `used_knowledge=false`，不写
    `knowledge_retrieval` artifact。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Task 5：Add retrieval evidence
  frontend display。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_requirement_review.py -q
git diff --check
```

验证结果：

- `16 passed`。
- `git diff --check` clean。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 在 RAG 知识库前端展示 deterministic retrieval evidence。
- 前端只展示已有 evidence，不新增 vector search、provider runtime config、
  MCP runtime、RBAC、tenants、permissions、marketplace 或 remote sync 控件。

## 2026-06-30 Slice 19 Task 3 完成

本轮完成：

- 完成 Slice 19 Task 3：Add local KnowledgeAdapter retrieval service。
- 新增 deterministic local retrieval service：
  - 读取同项目 ContextArtifact。
  - 仅匹配 `safe_to_show=true` 且 `allowed_for_prompt=true` 的上下文。
  - 使用确定性关键词重合匹配，支持英文和中文词项。
  - 返回 bounded snippet、score、matched terms、ContextArtifact id、SHA256、
    redaction 和 prompt eligibility 信息。
- 新增
  `POST /api/projects/{project_id}/knowledge-adapter/retrieve`，供后续
  workflow/frontend 使用。
- 允许 KnowledgeAdapterConfig 使用 V2
  `provider_type=deterministic_local`，但更新配置本身仍保持
  `used_knowledge=false`。
- 新增 `backend/app/tests/api/test_deterministic_knowledge_retrieval.py`：
  覆盖 service、API、禁用/未配置 adapter、配置入口和中文 query terms。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Task 4：Attach retrieval evidence
  to AI task flows。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_deterministic_knowledge_retrieval.py -q
git diff --check
```

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 把 deterministic retrieval 接入 requirement review。
- AITask 只有在 retrieved snippets 实际用于 prompt 时才记录
  `used_knowledge=true`。
- 需要写 `knowledge_retrieval` evidence artifact，并记录 query terms、
  matched terms、scores、snippets、ContextArtifact ids。
- 继续排除 frontend、vector database、embeddings、reranking、background
  indexing、external RAG provider、MCP runtime、RBAC、tenants、permissions 或
  marketplace。

## 2026-06-30 Slice 19 Task 2 完成

本轮完成：

- 完成 Slice 19 Task 2：Define deterministic retrieval contract boundary。
- 更新 `docs/contracts/01-data-model-contract.md`：
  - AITask `input_json` / `output_json` 记录 deterministic retrieval 约定。
  - KnowledgeAdapterConfig `provider_type` 增加 V2
    `deterministic_local` 受限模式。
  - Artifact type 增加 `knowledge_retrieval`。
- 更新 `docs/contracts/02-api-contract.md`：
  - `use_knowledge=true` 只在 deterministic local retrieval 有证据时允许。
  - RAG 知识库 surface 可展示 latest retrieval evidence。
  - KnowledgeAdapter config 可配置本地 deterministic matching 参数。
- 更新 `docs/contracts/03-state-machines.md`：
  - retrieval 不新增 AITask 状态，只写 evidence artifact。
  - `disabled` / `not_configured` 强制 `used_knowledge=false`。
- 更新 `docs/contracts/04-artifact-contract.md`：
  - 增加 `knowledge_retrieval.json` 路径和 artifact shape。
  - 记录 query terms、matched terms、scores、snippets、ContextArtifact ids。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Task 3：Add local
  KnowledgeAdapter retrieval service。

本轮验证：

```bash
rg -n "Deterministic|KnowledgeAdapter|ContextArtifact|used_knowledge|retrieval|retrieved" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md
git diff --check
```

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 新增 deterministic retrieval backend service 和 focused
  tests。
- 不要加入 frontend、vector database、embeddings、reranking、background
  indexing、external RAG provider、MCP runtime、RBAC、tenants、permissions 或
  marketplace。

## 2026-06-30 Slice 19 Task 1 完成

本轮完成：

- 完成 Slice 19 Task 1：Add Deterministic Knowledge Retrieval task plan。
- 新增
  `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`。
- 将 Slice 19 收敛为本地 deterministic ContextArtifact retrieval stub：
  - 只读取同项目已有 ContextArtifact。
  - 只匹配 safe_to_show 且 allowed_for_prompt 的上下文。
  - 使用确定性关键词/精确匹配，不使用向量库或外部 provider。
  - 记录 retrieved ContextArtifact ids、snippets、scores、matched terms。
  - `used_knowledge=true` 只允许在 deterministic local stub 实际使用证据时出现。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 19 Task 2：Define deterministic
  retrieval contract boundary。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 更新四份 contracts。
- 先定义 retrieval evidence artifact、`used_knowledge=true` 条件、API/状态边界，
  再写产品代码。
- 继续排除 vector database、embeddings、reranking、background indexing、
  external RAG provider、MCP runtime、RBAC、tenants、permissions、marketplace。

## 2026-06-30 V2 Task 3 完成

本轮完成：

- 完成 V2 Task 3：Select next small V2 slice。
- 更新 `docs/implementation/10-v2-scope-options.md`：
  - 记录 Slice 18 Newman API Execution 已完成。
  - 推荐下一条小切片为
    `Slice 19: Deterministic Knowledge Retrieval Stub`。
  - 明确这是本地确定性 ContextArtifact retrieval stub，不是完整 RAG 平台。
  - 继续排除 vector database、embeddings、reranking、background indexing、
    external RAG provider、MCP runtime、RBAC、tenants、permissions、
    marketplace、remote CI/CD provider integration。
- 已将 `NEXT_AI_TASK.md` 切换到 V2 Task 4：Draft Slice 19 Deterministic
  Knowledge Retrieval Stub plan。

下次推荐任务：

- 起草
  `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`。
- 只做计划，不新增产品代码。
- 先定义 contracts、artifacts、API 行为、frontend evidence display 和
  non-goals，再开始实现。

## 2026-06-30 Slice 18 Completion Gate 完成

本轮完成：

- 完成 Slice 18：Newman API Execution。
- 更新 `docs/implementation/slices/slice-18-newman-api-execution.md`：
  - 所有任务行标记 done。
  - 记录 completion evidence。
  - 记录 Newman API + golden、frontend、diff 验证结果。
- 已将 `NEXT_AI_TASK.md` 切换到 V2 Task 3：Select next small V2 slice。

最终验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py backend/app/tests/golden/test_newman_api_execution_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Newman API + golden tests：`5 passed`。
- Frontend suite：`15` test files passed，`18` tests passed。
- `git diff --check` clean。

Slice 18 结果：

- Newman API execution 已作为 allowlisted local TestCommand 路径接入。
- `command_type=newman`，`runner_mode=newman_local`。
- 证据包含 TestRun、assertion-level TestResult、stdout/stderr、
  `newman_json`、`parsed_output`。
- 前端新增 `API 执行` 页面，只展示 TestCommand-based Newman evidence。
- Golden smoke 覆盖 deterministic Newman collection 和一个可见失败断言。
- 未加入 arbitrary shell、Postman cloud/workspace/editor、remote CI/CD、
  RAG/MCP runtime、RBAC、tenants、permissions、marketplace、release 或
  deployment automation。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 V2 Task 3：Select next small V2 slice。
- 优先从 `docs/implementation/10-v2-scope-options.md` 中选择小切片；如产品优先级
  不清楚，先停在规划评审，不直接加新功能。

## 2026-06-30 Slice 18 Task 5 完成

本轮完成：

- 完成 Slice 18 Task 5：Add Newman API execution golden smoke。
- 新增 `backend/app/tests/golden/test_newman_api_execution_golden.py`。
- 新增 `docs/fixtures/07-newman-api-execution-golden.md`。
- Golden path 覆盖：
  - Project。
  - `TestCommand.command_type=newman`。
  - `TestRun.runner_mode=newman_local`。
  - stdout/stderr、`newman_json`、`parsed_output` artifacts。
  - assertion-level TestResult。
  - failed assertion 作为证据可见。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 18 Completion Gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_newman_api_execution_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py backend/app/tests/golden/test_newman_api_execution_golden.py -q
git diff --check
```

验证结果：

- Newman golden smoke：`1 passed`。
- Newman API + golden：`5 passed`。
- `git diff --check` clean。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 18 completion gate。
- 只记录完成证据和下一步，不新增产品行为。

## 2026-06-30 Slice 18 Task 4 完成

本轮完成：

- 完成 Slice 18 Task 4：Add Newman API execution frontend shell。
- 新增 `frontend/src/views/execution/NewmanExecutionView.vue`：
  - 中文页面标题 `API 执行`。
  - 只接受 TestCommand ID，不展示 AutomationDraft 入口。
  - 使用 `runner_mode=newman_local`。
  - 展示集合名、状态、退出码、耗时、请求数、断言数。
  - 展示 `newman_json`、`parsed_output`、stdout/stderr/JUnit 工件。
  - 展示断言级 TestResult 和失败信息。
- 新增 `frontend/src/views/execution/NewmanExecutionView.spec.ts`。
- 更新 router 和导航，加入 `execution/newman` / `API 执行`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 18 Task 5：Add Newman API execution
  golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Frontend suite：`15` test files passed，`18` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 新增 Newman golden smoke 和 fixture 文档。
- 继续保持 deterministic local fixture，不加入 Postman cloud、collection
  editor、remote CI/CD、RAG/MCP runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 18 Task 3 完成

本轮完成：

- 完成 Slice 18 Task 3：Add Newman runner/parser backend。
- 新增 `backend/app/modules/execution/newman_runner.py`：
  - 校验 `npx newman run ...` allowlist。
  - 禁止 shell chaining、redirection、substitution、pipes 等任意 shell 行为。
  - 解析 Newman JSON reporter 输出。
  - 将 request/assertion 映射为 TestResult candidate。
- 更新 `backend/app/modules/execution/service.py`：
  - `runner_mode=newman_local` 分支。
  - TestRun/TestResult 持久化。
  - stdout/stderr、`newman_json`、`parsed_output` artifacts。
- 更新 `backend/app/modules/projects/service.py`：
  - TestCommand allowlist 支持 `command_type=newman`。
- 新增 `backend/app/tests/api/test_newman_execution.py`：
  - fake `npx` deterministic fixture。
  - runner parse/rejection tests。
  - `/api/test-runs` Newman command execution测试。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 18 Task 4：Add Newman API execution
  frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_newman_execution.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/api/test_playwright_minimal_loop.py backend/app/tests/api/test_test_commands.py -q
git diff --check
```

验证结果：

- Newman focused API tests：`4 passed`。
- 相邻 execution/project tests：`27 passed`。
- `git diff --check` clean。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 增加 Newman API 执行前端页面。
- 页面只展示执行证据和 artifact，不做 collection editor、secret manager、
  remote CI/CD、Postman cloud 或 marketplace。

## 2026-06-30 Slice 18 Task 2 完成

本轮完成：

- 完成 Slice 18 Task 2：Define Newman execution contract boundary。
- 更新 `docs/contracts/01-data-model-contract.md`：
  - `TestCommand.command_type` 增加 `newman`。
  - `TestRun.runner_mode` 增加 `newman_local`。
  - 定义 Newman TestRun/TestResult 解析字段和脱敏规则。
  - 定义 `newman_collection_run` ToolDefinition allowlist 边界。
- 更新 `docs/contracts/02-api-contract.md`：
  - Newman 复用 `/api/test-runs`。
  - 不新增 `POST /api/newman-runs`。
  - 定义 Newman request rules、parsed_result shape 和 artifact response。
- 更新 `docs/contracts/03-state-machines.md`：
  - Newman 仍走 ToolInvocation allowlist。
  - Newman assertion failure 映射为 TestRun `failed`。
  - 启动、超时、allowlist、解析器错误映射为 `error` 或 `timeout`。
- 更新 `docs/contracts/04-artifact-contract.md`：
  - 增加 `newman_json` artifact type。
  - 明确 `parsed_output`、optional `junit`、脱敏和非触发规则。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 18 Task 3：Add Newman
  runner/parser backend。

本轮验证：

```bash
rg -n "Newman|newman|newman_json|command_type|ToolDefinition" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-18-newman-api-execution.md
git diff --check
```

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 新增 Newman backend runner/parser。
- 先写 `backend/app/tests/api/test_newman_execution.py` 的确定性 fixture 测试。
- 不要加入 frontend、Postman cloud、collection editor、remote CI/CD、RAG/MCP
  runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 18 Task 1 完成

本轮完成：

- 完成 Slice 18 Task 1：Add Newman API Execution task plan。
- 新增 `docs/implementation/slices/slice-18-newman-api-execution.md`。
- 将第一个 V2 slice 收敛为 Newman API execution evidence：
  - approved `TestCommand.command_type=newman`。
  - ToolDefinition/TestCommand allowlist。
  - stdout/stderr、Newman JSON、parsed_result、TestResult evidence。
  - API 执行页面只展示执行证据，不做 Postman workspace parity。
- 明确排除 arbitrary shell、Postman cloud/editor、remote CI/CD provider、
  runner marketplace、RAG/MCP runtime、RBAC、tenants、permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 18 Task 2：Define Newman execution
  contract boundary。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 更新四份 contracts。
- 先定义 `command_type=newman`、Newman artifact、parsed result 和
  ToolDefinition allowlist 边界，再写产品代码。

## 2026-06-30 Frontend Chinese Copy Review 完成

本轮按用户反馈完成：

- 保留 `Prompt`、`Skill`、`PromptVersion`、`SkillVersion`、`Agent`、
  `AutomationDraft`、`TestCommand`、`TestRun`、`ContextArtifact`、
  `ToolDefinition` 等产品/模型术语。
- 将页面里的普通英文说明和指标文案中文化，包括：
  - 需求评审、用例生成评审、用例库。
  - 自动化草稿中心。
  - pytest 执行中心与 Playwright 执行。
  - CI/CD 质量中心。
  - 报告中心。
  - RAG 知识库。
  - 项目设置。
  - Prompt / Skill 中心状态和必填契约显示。
- 为后端枚举增加前端显示层中文映射，不改变 API 数据：
  - passed/failed/pending/analyzed 等状态。
  - high/medium/low 等风险。
  - functional/ui/api 等用例类型。
  - approved_after_edit 等评审状态。
  - source/modified/source file changed 等 CI/CD 变更字段。
- 同步更新前端组件测试断言。

本轮验证：

```bash
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Frontend：`14` test files passed，`17` tests passed。
- `git diff --check` clean。

下次推荐任务：

- 回到 `NEXT_AI_TASK.md`：V2 Task 2，起草 Slice 18 Newman API Execution
  plan。

## 2026-06-30 V2 Task 1 完成

本轮完成：

- 完成 V2 Task 1：Draft V2 scope options。
- 新增 `docs/implementation/10-v2-scope-options.md`。
- 规划 4 个候选方向：
  - RAG Knowledge Runtime。
  - Tool And Runner Expansion。
  - Team Review And Governance。
  - CI/CD Integration Bridge。
- 推荐第一条 V2 slice：`Slice 18: Newman API Execution`。
- 保留仍需显式提升的 out-of-scope：full RAG platform、MCP runtime、
  RBAC/tenants、remote CI/CD control、broad dashboards 等。
- 已将 `NEXT_AI_TASK.md` 切换到 V2 Task 2：Draft Slice 18 Newman API
  Execution plan。

下次推荐任务：

- 起草 `docs/implementation/slices/slice-18-newman-api-execution.md`。
- 先定义 slice 计划，不直接新增产品代码。

## 2026-06-30 Post-V1 Task 4 完成

本轮完成：

- 完成 Post-V1 Task 4：Optional frontend screenshot capture or V2 planning。
- 本地 web 已在 `http://localhost:5174/` 可访问。
- 通过内置浏览器捕获 release screenshots：
  - `docs/release/v1/screenshots/ai-workbench.png`
  - `docs/release/v1/screenshots/cicd-quality-center.png`
  - `docs/release/v1/screenshots/report-center.png`
  - `docs/release/v1/screenshots/rag-knowledge-base.png`
- 更新 `docs/release/v1/README.md` 链接截图。
- 已将 `NEXT_AI_TASK.md` 切换到 V2 Task 1：Draft V2 scope options。

下次推荐任务：

- 起草 `docs/implementation/10-v2-scope-options.md`。
- 只做 V2 scope options，不直接加入产品代码或运行时扩张。

## 2026-06-30 Post-V1 Task 3 完成

本轮完成：

- 完成 Post-V1 Task 3：Write V1 manual walkthrough and acceptance evidence
  details。
- 扩展 `docs/release/v1/manual-walkthrough.md` 为 release-ready checklist，
  覆盖项目上下文、需求评审、用例生成、AutomationDraft、pytest execution、
  failure analysis/report、CI/CD Quality Center 和 extension surfaces。
- 扩展 `docs/release/v1/acceptance-evidence.md`，加入 release status、
  blocker status、coverage table、evidence chain 和 non-goals。
- 更新 `docs/release/v1/README.md`，链接 release packaging decision。
- 已将 `NEXT_AI_TASK.md` 切换到 Post-V1 Task 4：Optional frontend
  screenshot capture or V2 planning。

下次推荐任务：

- 决定是否捕获前端截图；如果不需要截图，则将 release package 标记为文档
  complete 并切入 V2 planning。

## 2026-06-30 Post-V1 Task 2 完成

本轮完成：

- 完成 Post-V1 Task 2：Create V1 release package skeleton。
- 新增 `docs/release/v1/README.md`。
- 新增 `docs/release/v1/acceptance-evidence.md`。
- 新增 `docs/release/v1/manual-walkthrough.md`。
- 新增 `docs/release/v1/screenshots/.gitkeep` 作为可选截图目录占位。
- Release package skeleton 链接 V1 acceptance evidence，并保留 V1 non-goals。
- 已将 `NEXT_AI_TASK.md` 切换到 Post-V1 Task 3：Write V1 manual walkthrough
  and acceptance evidence details。

下次推荐任务：

- 扩展 `docs/release/v1/manual-walkthrough.md` 和
  `docs/release/v1/acceptance-evidence.md`，写成 release-ready 文档。

## 2026-06-30 Post-V1 Task 1 完成

本轮完成：

- 完成 Post-V1 Task 1：Decide release packaging and demo artifact strategy。
- 新增 `docs/implementation/09-post-v1-release-packaging-plan.md`。
- 决策：V1 自动化验收采用当前 composable golden suite；不在 V1 packaging 前
  新增大型 narrative E2E 自动化测试。
- 决策：补轻量 release package，包含 release note、manual walkthrough、
  acceptance evidence，截图作为可选材料。
- 更新 `docs/implementation/08-v1-final-acceptance-handoff.md` 的剩余决策。
- 已将 `NEXT_AI_TASK.md` 切换到 Post-V1 Task 2：Create V1 release package
  skeleton。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 创建 `docs/release/v1/` 文档骨架。
- 继续保持 documentation-only，不加入 RAG runtime、MCP runtime、RBAC、
  tenants、permissions 或 remote CI provider integration。

## 2026-06-30 V1 Completion Review Task 4 完成

本轮完成：

- 完成 V1 Completion Review Task 4：Prepare final V1 acceptance handoff。
- 新增 `docs/implementation/08-v1-final-acceptance-handoff.md`。
- 汇总 V1 release recommendation：`GO`。
- 链接 completion audit、release acceptance report、V1 release spine 和产品
  scope。
- 记录 automated evidence：
  - Backend V1 golden release-acceptance suite：`10 passed`。
  - Frontend workbench suite：`14` test files passed，`17` tests passed。
  - `git diff --check` clean。
- 记录剩余非阻塞决策：是否补单一叙事型 E2E demo、是否为 release notes
  增加截图、是否清理旧 slice task table 的 stale pending commit 文字。
- 已将 `NEXT_AI_TASK.md` 切换到 Post-V1 Task 1：Decide release packaging and
  demo artifact strategy。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Post-V1 Task 1。
- 先做 release packaging 决策，不直接加入 RAG runtime、MCP runtime、RBAC、
  tenants、permissions 或 remote CI provider integration。

## 2026-06-30 V1 Completion Review Task 3 完成

本轮完成：

- 完成 V1 Completion Review Task 3：Fix full-suite golden isolation
  assertions。
- 只修改 5 个 historical golden smoke 的断言，不修改产品代码。
- 将旧的 later-slice table absence assertions 改为 row/behavior absence
  assertions：
  - AutomationDraft flow 不创建 `TestRun`、`TestResult`、`Report` rows。
  - Pytest runner flow 不创建 `Report`、`QualityGateDecision` rows。
  - Playwright runner flow 不创建 `Report`、`FailureAnalysis`、
    `QualityGateDecision` rows。
  - Report/FailureAnalysis flow 不创建 `QualityGateDecision` rows。
  - CI/CD Quality Center analysis flow 不创建 `QualityGateDecision` rows。
- 更新 `docs/implementation/07-v1-release-acceptance.md`，release
  recommendation 从 `NO-GO` 更新为 `GO`。
- 已将 `NEXT_AI_TASK.md` 切换到 V1 Completion Review Task 4：Prepare final
  V1 acceptance handoff。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py backend/app/tests/golden/test_extension_surface_golden.py -q
```

验证结果：

- 原失败 golden smokes：`5 passed`。
- V1 full golden release-acceptance suite：`10 passed`。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 V1 Completion Review Task 4。
- 创建最终 V1 acceptance handoff，整理 release evidence 和剩余非阻塞风险。

## 2026-06-30 V1 Completion Review Task 2 完成

本轮完成：

- 完成 V1 Completion Review Task 2：Run V1 release acceptance。
- 新增 `docs/implementation/07-v1-release-acceptance.md`。
- 后端 V1 full golden release-acceptance suite 首次运行结果为 `5 failed,
  5 passed`。
- 前端 Vitest release check 通过：`14` test files passed，`17` tests
  passed。
- `git diff --check` clean。
- 已将 release recommendation 标记为 `NO-GO`。
- 已将 `NEXT_AI_TASK.md` 切换到 V1 Completion Review Task 3：Fix
  full-suite golden isolation assertions。

阻塞原因：

- 5 个历史 slice golden smoke 使用 `test_runs`、`reports`、
  `quality_gate_decisions` 等“表不存在”断言来证明 later-slice behavior 未被
  涉及。
- 完整 V1 应用在 release acceptance 中会先注册全部 SQLAlchemy models，再
  `Base.metadata.create_all`，所以 later-slice tables 会存在。
- 应保留原意，但改为断言没有相关 rows 或 behavior 被当前 flow 创建。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 V1 Completion Review Task 3。
- 只修复 golden isolation assertions，不修改产品代码。
- 修复后重新运行完整 release-acceptance verification command set。

## 2026-06-30 V1 Completion Review Task 1 完成

本轮完成：

- 完成 V1 Completion Review Task 1：Audit V1 completion evidence and remaining
  gaps。
- 新增 `docs/implementation/06-v1-completion-audit.md`。
- 审计已实现闭环：Requirement To Case、Case To Automation Evidence、CI/CD
  Quality Center、Extension Surface、Frontend Shells。
- 记录可用 verification commands 和推荐 V1 release-acceptance command set。
- 记录 remaining gaps：是否需要单一端到端 V1 demo、ToolInvocation 链接、
  runtime artifact 期望、旧 slice 表 pending commit 文档清理、release
  acceptance report。
- 已将 `NEXT_AI_TASK.md` 切换到 V1 Completion Review Task 2：Run V1 release
  acceptance。

本轮验证：

```bash
test -f docs/implementation/06-v1-completion-audit.md && rg -n "Implemented|Remaining gaps|Verification|Next task" docs/implementation/06-v1-completion-audit.md
git diff --check
```

验证结果：

- V1 completion audit exists and names evidence, gaps, verification, and next
  task。
- `git diff --check` clean。

修改文件：

- `docs/implementation/06-v1-completion-audit.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 V1 Completion Review Task 2：Run V1 release
  acceptance。
- 该任务只运行和记录 release acceptance，不新增产品代码。

## 2026-06-30 Slice 17 Completion Gate 完成

本轮完成：

- 完成 Slice 17 completion gate。
- 确认 Slice 17 所有任务均为 `done`，并记录提交号：
  `73a1885`、`f2812cf`、`afffbc9`、`fbbde4f`、`b1d8f5d`、
  `94fbf21`、`2322e42`。
- 完成组合验收：Extension Surface API、golden smoke、frontend shell 均已
  覆盖。
- 已在 `docs/implementation/slices/slice-17-extension-surface.md` 写入
  completion evidence。
- 已在 `memory/07-dev-log.md` 写入 Slice 17 completion log。
- 已将 `NEXT_AI_TASK.md` 切换到 V1 Completion Review Task 1：Audit V1
  completion evidence and remaining gaps。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Extension Surface API + golden smoke：`6 passed`
- Frontend shell：`14 passed`，`17 tests passed`
- `git diff --check` clean

Slice 17 保持的非目标：

- 未加入 vector index、embedding、reranking 或外部 RAG provider。
- 未加入 MCP server/client runtime、remote MCP call 或插件市场。
- 未加入 RBAC、tenants、permissions、marketplace、cloud sync。
- 未触发 release、deployment 或 remote CI provider integration。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 V1 Completion Review Task 1。
- 这是 audit-only 任务，先梳理 V1 completion evidence 和 remaining gaps，
  不直接新增产品代码。

## 2026-06-30 Slice 17 Task 7 Extension Surface Golden Smoke 完成

本轮完成：

- 完成 Slice 17 Task 7：Add Extension Surface golden smoke。
- 新增 `docs/fixtures/06-extension-surface-golden.md`。
- 新增 `backend/app/tests/golden/test_extension_surface_golden.py`。
- Golden smoke 验证 Project -> ContextArtifact -> AITask
  `context_artifact_ids` -> KnowledgeAdapter empty state -> RAG 知识库 surface
  -> MCP-ready ToolDefinition schema。
- 验证 `used_knowledge=false`，同时 `used_context_artifact_ids` 正确记录。
- 验证 ToolDefinition 仅暴露 schema/readiness，不包含 MCP server URL 或
  transport。
- 验证没有 `rag_indexes`、`embeddings`、`mcp_servers`、`mcp_clients`、
  `tenants`、`roles`、`permissions` 表。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_extension_surface_golden.py -q
git diff --check
```

验证结果：

- Extension Surface golden smoke：`1 passed`
- `git diff --check` clean。

修改文件：

- `backend/app/tests/golden/test_extension_surface_golden.py`
- `docs/fixtures/06-extension-surface-golden.md`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 completion gate。
- 组合验证 backend extension API、golden smoke 和 frontend tests，记录
  completion evidence，再选择下一 V1 任务。

## 2026-06-30 Slice 17 Task 6 RAG 知识库 Frontend Shell 完成

本轮完成：

- 完成 Slice 17 Task 6：Add RAG 知识库 frontend shell。
- 新增 `frontend/src/api/extension.ts` 和 `frontend/src/stores/extension.ts`。
- 新增 `frontend/src/views/extension/KnowledgeBaseView.vue` 与组件测试。
- 在导航中加入 `RAG 知识库` 页面。
- 页面展示 ContextArtifact inventory、safe_to_show、allowed_for_prompt、
  usage_count、KnowledgeAdapter 状态、non-goals 和 MCP-ready ToolDefinition
  readiness。
- 按用户验收反馈优化 `AI 工作台`：最近 AI 任务和任务详情改为上下布局，
  避免左右挤压；将主要英文标签中文化。
- 同步中文化全局 `Mock Provider`、`Evidence Loop`、
  `Prompt / Skill 中心` 等可见文案。
- 未加入 vector search、RAG runtime、MCP runtime、marketplace、cloud sync、
  RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 7：Add Extension Surface
  golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Frontend：`14 passed`，`17 tests passed`
- `git diff --check` clean。
- Web 验收：`http://localhost:5174/` 和 `RAG 知识库` 页面均可打开；
  AI 工作台已为上下布局。

修改文件：

- `frontend/src/api/extension.ts`
- `frontend/src/stores/extension.ts`
- `frontend/src/views/extension/KnowledgeBaseView.vue`
- `frontend/src/views/extension/KnowledgeBaseView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `frontend/src/styles/global.css`
- `frontend/src/layouts/WorkbenchLayout.vue`
- `frontend/src/layouts/WorkbenchLayout.spec.ts`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 7：Add Extension Surface golden
  smoke。
- Golden smoke 应证明 ContextArtifact、KnowledgeAdapter empty state、
  MCP-ready ToolDefinition schema 和 AI task context evidence 串联可用，
  同时确认没有 RAG/MCP runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 17 Task 5 MCP-ready Tool Schema 完成

本轮完成：

- 完成 Slice 17 Task 5：Add MCP-ready ToolDefinition schema metadata。
- 新增 `ToolDefinition` model，用于保存 tool schema、risk、approval、
  allowlist、artifact policy、`is_mcp_ready` 和 `mcp_metadata_json`。
- 新增 `GET /api/projects/{project_id}/tool-definitions`。
- API 返回 built-in/project ToolDefinition schema/readiness。
- `tool_type=mcp_proxy` 仅作为 schema intent 展示，不触发 MCP runtime。
- 未加入 MCP server/client 包、远程 MCP 调用、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 6：Add RAG 知识库 frontend
  shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
git diff --check
```

验证结果：

- `5 passed`
- `git diff --check` clean。

修改文件：

- `backend/app/modules/extension/__init__.py`
- `backend/app/modules/extension/models.py`
- `backend/app/modules/extension/router.py`
- `backend/app/modules/extension/schemas.py`
- `backend/app/modules/extension/service.py`
- `backend/app/tests/api/test_extension_surface.py`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 6：Add RAG 知识库 frontend shell。
- 前端使用浅色工作台 UI，展示 ContextArtifact、KnowledgeAdapter 和
  MCP-ready ToolDefinition readiness，不加入 vector search、RAG runtime、MCP
  runtime、marketplace、cloud sync、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 17 Task 4 Knowledge Base Context API 完成

本轮完成：

- 完成 Slice 17 Task 4：Add RAG 知识库 ContextArtifact API shell。
- 新增 `GET /api/projects/{project_id}/knowledge-base`。
- 返回 KnowledgeAdapter 状态、ContextArtifact inventory、source_ref、
  MIME type、redaction、allowed_for_prompt、usage_count、latest_used_at。
- usage 只从 `AITask.context_artifact_ids` 聚合，不新增单独知识库表。
- 返回 non_goals：`no_vector_index`、`no_embedding`、`no_reranking`、
  `no_external_rag_runtime`。
- 未加入 semantic search、embedding、vector index、reranking 或外部 RAG
  provider 调用。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 5：Add MCP-ready
  ToolDefinition schema metadata。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
git diff --check
```

验证结果：

- `4 passed`
- `git diff --check` clean。

修改文件：

- `backend/app/modules/extension/router.py`
- `backend/app/modules/extension/schemas.py`
- `backend/app/modules/extension/service.py`
- `backend/app/tests/api/test_extension_surface.py`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 5：Add MCP-ready ToolDefinition
  schema metadata。
- 该任务只补 ToolDefinition schema/readiness，不加入 MCP runtime、remote MCP
  调用、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 17 Task 3 KnowledgeAdapter Shell 完成

本轮完成：

- 完成 Slice 17 Task 3：Add KnowledgeAdapter empty interface/schema。
- 新增 `backend/app/modules/extension` 模块。
- 新增 `KnowledgeAdapterConfig` model、read/update schema、service 和 router。
- 新增 `GET /api/projects/{project_id}/knowledge-adapter`，未配置时返回
  `not_configured`、`provider_type=none`、`used_knowledge=false`。
- 新增 `PUT /api/projects/{project_id}/knowledge-adapter`，只允许 `none/stub`
  provider 和 `not_configured/disabled/configured_stub` 状态。
- 拒绝 `api_key`、vector DB、embedding、reranker、remote URL、MCP transport
  等运行时配置。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 4：Add RAG 知识库
  ContextArtifact API shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_extension_surface.py -q
git diff --check
```

验证结果：

- `3 passed`
- `git diff --check` clean。

修改文件：

- `backend/app/main.py`
- `backend/app/modules/extension/__init__.py`
- `backend/app/modules/extension/models.py`
- `backend/app/modules/extension/router.py`
- `backend/app/modules/extension/schemas.py`
- `backend/app/modules/extension/service.py`
- `backend/app/tests/api/test_extension_surface.py`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 4：Add RAG 知识库
  ContextArtifact API shell。
- 该任务继续复用 ContextArtifact，不建立单独知识库表，不加入 semantic
  search、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 17 Task 2 Extension Surface Contract Boundary 完成

本轮完成：

- 完成 Slice 17 Task 2：Add Extension Surface contract boundary。
- 在 data model contract 中定义 `KnowledgeAdapterStatus`、
  `KnowledgeAdapterConfig`、ToolDefinition MCP-ready metadata 边界。
- 在 API contract 中定义 RAG 知识库 surface、KnowledgeAdapter config、
  MCP-ready ToolDefinition schema API 边界。
- 在 state machine contract 中定义 KnowledgeAdapterConfig 状态机。
- 在 artifact contract 中明确 Extension Surface artifact rules。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 3：Add KnowledgeAdapter empty
  interface/schema。

本轮验证：

```bash
rg -n "KnowledgeAdapter|RAG 知识库|ToolDefinition|MCP-ready|Non-goals" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-17-extension-surface.md
git diff --check
```

验证结果：

- Slice 17 contracts name extension surface scope and non-goals。
- `git diff --check` clean。

修改文件：

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 3：Add KnowledgeAdapter empty
  interface/schema。
- 该任务只做 backend shell，不加入 RAG runtime、MCP runtime、RBAC、tenants
  或 permissions。

## 2026-06-30 Slice 17 Task 1 Extension Surface Plan 完成

本轮完成：

- 完成 Slice 17 Task 1：Add Extension Surface task plan。
- 新增 `docs/implementation/slices/slice-17-extension-surface.md`。
- 将 Slice 17 拆为 contract boundary、KnowledgeAdapter empty shell、RAG 知识库
  ContextArtifact API shell、MCP-ready ToolDefinition schema、frontend shell、
  golden smoke、completion gate。
- 明确 RAG 知识库是 ContextArtifact 管理和使用展示表面，不是内置 RAG
  runtime。
- 明确 KnowledgeAdapter 在 V1 只保留空接口/配置状态，不做 retrieval。
- 明确 MCP-ready 只落到 ToolDefinition schema metadata，不引入 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 2：Add Extension Surface
  contract boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-17-extension-surface.md && rg -n "KnowledgeAdapter|RAG 知识库|MCP-ready|Non-goals" docs/implementation/slices/slice-17-extension-surface.md
git diff --check
```

验证结果：

- Slice 17 planning document exists and names scope/non-goals。
- `git diff --check` clean。

修改文件：

- `docs/implementation/slices/slice-17-extension-surface.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 2：Add Extension Surface contract
  boundary。
- 该任务只更新 contracts 和 slice task plan，不写运行时代码，不加入 RAG
  runtime、MCP runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 16 Completion Gate 完成

本轮完成：

- 完成 Slice 16 completion gate。
- 确认 Slice 16 所有任务均为 `done`，并记录提交号：
  `c0db91c`、`c164d88`、`ae601ff`、`f8c4156`、`c22f6e5`、
  `824cb4b`、`f4bbc73`、`f6333c5`、`e27cc7b`、`e17ec01`、
  `b0ee6b8`。
- 完成组合验收：UnitTestPatch regression API、golden smoke、frontend shell
  均已覆盖。
- 已在 `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
  写入 completion evidence。
- 已在 `memory/07-dev-log.md` 写入 Slice 16 completion log。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 17 Task 1：Add Extension Surface task
  plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- UnitTestPatch regression API + golden smoke：`23 passed`
- Frontend shell：`13 passed`，`16 tests passed`
- `git diff --check` clean

Slice 16 保持的非目标：

- 未触发 merge、push、release、deployment。
- 未集成 remote CI provider、webhooks、PR comments。
- 未加入 RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- UnitTestPatch 不允许修改业务源码。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 17 Task 1：Add Extension Surface task plan。
- 这是 planning-only 任务，先创建
  `docs/implementation/slices/slice-17-extension-surface.md`，不要直接改产品代码。

## 2026-06-30 Slice 16 Task 11 UnitTestPatch Golden Smoke 完成

本轮完成：

- 完成 Slice 16 Task 11：Add UnitTestPatch golden smoke。
- 新增 `backend/app/tests/golden/test_unit_test_patch_regression_golden.py`。
- Golden smoke 使用 `docs/fixtures/03-golden-cicd-quality.md` 的 local diff
  和 UnitTestPatch 语义。
- 验证 local diff -> CICDRun -> risk analysis -> UnitTestPatch ->
  PatchScopeGate -> approve/apply -> new-test/regression TestRun ->
  QualityGateDecision -> CI/CD quality Report 完整链路。
- 验证 UnitTestPatch 只修改 `tests/test_coupon.py`，PatchScopeGate 通过。
- 验证没有 AutomationDraft，也没有 tenants/roles/permissions/RAG/MCP
  相关表行为。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
```

验证结果：

- `1 passed`

修改文件：

- `backend/app/tests/golden/test_unit_test_patch_regression_golden.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 执行 Slice 16 completion gate：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q`
  和 `npm --prefix frontend run test -- --run`。
- 完成后记录 Slice 16 completion evidence，并寻找 Slice 17 或下一 V1
  优先级。

## 2026-06-30 Slice 16 Task 10 UnitTestPatch Frontend Shell 完成

本轮完成：

- 完成 Slice 16 Task 10：Add UnitTestPatch frontend shell。
- 扩展 `frontend/src/api/cicd.ts`，加入 UnitTestPatch generation/review、
  new-test/regression、QualityGateDecision、CI/CD quality report API 类型和调用。
- 扩展 `frontend/src/stores/cicd.ts`，集中管理 UnitTestPatch、review status、
  new TestRun、regression plan/run、quality gate、quality report 状态。
- 扩展 `CicdQualityCenterView.vue`，展示 UnitTestPatch diff、test intent、
  coverage target、PatchScopeGate result、new-test/regression evidence、
  QualityGateDecision 和 report artifact references。
- 前端支持 approve/reject 操作。
- 未暴露 merge、release、deployment、remote CI provider 或 PR controls。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 11：Add UnitTestPatch golden
  smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
```

验证结果：

- `13 passed`
- `16 tests passed`

修改文件：

- `frontend/src/api/cicd.ts`
- `frontend/src/stores/cicd.ts`
- `frontend/src/views/cicd/CicdQualityCenterView.vue`
- `frontend/src/views/cicd/CicdQualityCenterView.spec.ts`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 11：Add UnitTestPatch golden smoke。
- Golden smoke 需要证明 local diff -> UnitTestPatch -> tests/regression ->
  quality gate -> report evidence 的完整链路。

## 2026-06-30 Slice 16 Task 9 CI/CD Quality Report API 完成

本轮完成：

- 完成 Slice 16 Task 9：Add CI/CD quality report API。
- 新增 `POST /api/cicd/runs/{id}/generate-report`。
- 创建 `report_type=cicd_quality` 的 Report，关联 `related_entity_type=CICDRun`。
- Report conclusion 使用最新 QualityGateDecision status，不重算或覆盖
  `CICDRun.quality_gate_status`。
- 生成 `cicd_quality_evidence_manifest` artifact，引用 QualityGateDecision、
  UnitTestPatch/PatchScopeGate、new-test、regression 和 evidence artifacts。
- 当前任务未触发 merge/push/release/deployment/remote CI/PR comments。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 10：Add UnitTestPatch
  frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `22 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 10：Add UnitTestPatch frontend
  shell。
- 该任务只补前端 CI/CD Quality Center shell，不加入 merge/release/remote CI
  provider/PR controls。

## 2026-06-30 Slice 16 Task 8 QualityGateDecision API 完成

本轮完成：

- 完成 Slice 16 Task 8：Add QualityGateDecision API。
- 新增 `POST /api/cicd/runs/{id}/quality-gate`。
- 每次 compute 都创建新的 QualityGateDecision，并更新
  `CICDRun.quality_gate_status`。
- required evidence 缺失时返回 `needs_review`，不会误判为 `passed`。
- new-test 或 regression evidence 失败时返回 `failed`，并写入具体
  blocking reason。
- patch scope、applied UnitTestPatch、new-test、regression evidence 齐全且无
  failure 时返回 `passed`。
- 当前任务未触发 merge/push/release/deployment/remote CI/PR comments，也未创建
  Report。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 9：Add CI/CD quality report
  API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `21 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 9：Add CI/CD quality report API。
- 该任务只生成本地 evidence-backed Report，不重算/覆盖
  QualityGateDecision，不触发外部 CI 或 PR 行为。

## 2026-06-30 Slice 16 Task 7 New-Test/Regression API 完成

本轮完成：

- 完成 Slice 16 Task 7：Add new-test and regression API。
- 新增 `POST /api/cicd/runs/{id}/run-new-tests`，通过 allowlisted
  TestCommand 创建 `cicd_run_id` 已设置的 TestRun 证据。
- 当请求带 `unit_test_patch_id` 时，要求对应 UnitTestPatch 已为
  `applied` 状态。
- 新增 `POST /api/cicd/runs/{id}/select-regression`，写入
  `artifact_type=regression_plan`、`owner_entity_type=CICDRun` 的
  regression plan artifact metadata。
- 新增 `POST /api/cicd/runs/{id}/run-regression`，基于 regression plan 和
  allowlisted TestCommand 创建 CICD-linked TestRun 记录。
- 当前任务只排队/记录 TestRun evidence，不执行任意 shell 字符串，不计算
  QualityGateDecision，不创建 Report。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 8：Add
  QualityGateDecision API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `18 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 8：Add QualityGateDecision API。
- 该任务只计算本地 evidence-backed gate，不触发 merge/push/release/
  deployment/remote CI/PR comments，也不创建 Report。

## 2026-06-30 Slice 16 Task 6 UnitTestPatch Apply API 完成

本轮完成：

- 完成 Slice 16 Task 6：Add UnitTestPatch apply API。
- 新增 `POST /api/cicd/unit-test-patches/{id}/apply`。
- Apply 只允许 `approved` UnitTestPatch。
- Apply 前重新运行 PatchScopeGate；若 patch 修改非测试路径，返回
  `PATCH_SCOPE_REJECTED`，patch 状态变为 `apply_failed`，不写 artifact。
- 成功 apply 时 patch 状态变为 `applied`，并写入
  `artifact_type=unit_test_patch`、`owner_entity_type=UnitTestPatch` 的
  artifact metadata。
- Artifact metadata 保留原始 `patch_text` 和最新 `scope_gate_result`。
- 当前任务没有将 patch 应用到业务仓库文件，也没有运行测试命令，没有创建
  TestRun、QualityGateDecision 或 Report。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 7：Add new-test and
  regression API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `14 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 7：Add new-test and regression
  API。
- 该任务只创建 CICD-linked TestRun 和 regression_plan artifact evidence，
  不计算 QualityGateDecision，不创建 Report。

## 2026-06-30 Slice 16 Task 5 UnitTestPatch Generation/Review API 完成

本轮完成：

- 完成 Slice 16 Task 5：Add UnitTestPatch generation/review API。
- 新增 `POST /api/cicd/runs/{id}/unit-test-patches`，生成 deterministic
  mock UnitTestPatch candidate。
- 生成流程创建 succeeded mock `UnitTestAgent` AITask，写入
  `UnitTestPatch.scope_gate_result_json`，并返回 review UI 所需
  `scope_gate_result`。
- PatchScopeGate 通过时 patch 状态为 `scope_validated`，失败时为
  `scope_rejected`。
- 新增 approve/reject endpoints：
  `POST /api/cicd/unit-test-patches/{id}/approve` 与
  `POST /api/cicd/unit-test-patches/{id}/reject`。
- `scope_rejected` patch 不能 approve，会返回
  `UNIT_TEST_PATCH_INVALID_STATUS`。
- 任务未 apply patches，未运行测试命令，未创建 TestRun、
  QualityGateDecision 或 Report。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 6：Add UnitTestPatch apply
  API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `12 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 6：Add UnitTestPatch apply API。
- 该任务只能通过受控 service path apply 已批准且 scope gate 通过的测试
  patch；不能修改业务源码，不能运行测试命令。

## 2026-06-30 Slice 16 Task 4 PatchScopeGate Service 完成

本轮完成：

- 完成 Slice 16 Task 4：Add PatchScopeGate service。
- 新增 `evaluate_patch_scope()`，解析 UnitTestPatch unified diff 目标路径并返回
  `allowed`、`checked_paths`、`blocked_paths`、`forbidden_patterns`、
  `risk_level`、`reason`。
- 允许 `tests/`、`test/`、`__tests__/`、`test_*.py`、`*_test.py`、
  `.test.*`、`.spec.*` 等测试路径。
- 拒绝 source、config/build、migration、generated artifact、unknown
  non-test 路径，拒绝原因使用 `PATCH_SCOPE_REJECTED`。
- 修复审查发现的 generated 绕过风险：`dist/`、`coverage/`、`build/`
  等 generated 路径即使命名为 `.test/.spec` 也必须拒绝。
- 新增 `PatchScopeGateRead` schema，字段与 `patch_scope_gate.json`
  artifact metadata 对齐。
- 任务未 apply patches，未修改目标仓库文件，未运行 patch 内测试命令。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 5：Add UnitTestPatch
  generation/review API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `9 passed`

修改文件：

- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 5：Add UnitTestPatch
  generation/review API。
- 该任务只生成、校验、审批/拒绝 UnitTestPatch，不 apply patch，不运行测试。

## 2026-06-30 Slice 16 Task 3 UnitTestPatch/QualityGateDecision Model Schema 完成

本轮完成：

- 完成 Slice 16 Task 3：Add UnitTestPatch and QualityGateDecision
  model/schema。
- 新增 `UnitTestPatch` 模型，覆盖 `cicd_run_id`、`ai_task_id`、
  `patch_text`、`target_framework`、`scope_gate_result_json`、
  `test_intent`、`coverage_target_json`、`status`、`review_comment`。
- 新增 `QualityGateDecision` 模型，覆盖 `project_id`、`cicd_run_id`、
  `status`、`summary`、`blocking_reasons_json`、`evidence_artifact_ids`、
  `decided_by`、`status_detail_json`。
- 新增 UnitTestPatch / QualityGateDecision create/read schemas，使用 API
  层字段名 `scope_gate_result`、`coverage_target`、`blocking_reasons`、
  `status_detail`。
- 任务只做 persistence/schema，不 apply patches，不触发测试运行流程。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 4：Add PatchScopeGate
  service。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

验证结果：

- `4 passed`

修改文件：

- `backend/app/modules/cicd/models.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 4：Add PatchScopeGate service。
- 当前任务只做统一 diff 路径 scope gate，不 apply patches 或运行测试命令。

## 2026-06-30 Slice 16 Task 2 UnitTestPatch/Regression Contract Boundary 完成

本轮完成：

- 完成 Slice 16 Task 2：Add UnitTestPatch and regression contract boundary。
- 在数据模型合同中补充 UnitTestPatch review-gate、PatchScopeGate
  `scope_gate_result_json`、scope_rejected 不可 approve、applied patch
  evidence 规则。
- 在 API 合同中补充 UnitTestPatch generation/review/apply、run-new-tests、
  regression、QualityGateDecision、CI/CD quality report 的证据要求和非目标。
- 在状态机合同中补充 UnitTestPatch apply 前置条件和 QualityGateDecision
  不触发 merge/push/release/deployment/remote CI 行为。
- 在 artifact 合同中补充 `unit_test.patch`、`patch_scope_gate.json`、
  `regression_plan.json`、`quality_gate.json` 的 Slice 16 artifact rules。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 3：Add UnitTestPatch and
  QualityGateDecision model/schema。

本轮验证：

```bash
rg -n "UnitTestPatch|PatchScopeGate|QualityGateDecision|run-new-tests|run-regression" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

修改文件：

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 3：Add UnitTestPatch and
  QualityGateDecision model/schema。
- 当前任务只做 model/schema，不 apply patches 或 run tests。

## 2026-06-30 Slice 16 Task 1 UnitTestPatch/Regression Task Plan 完成

本轮完成：

- 完成 Slice 16 Task 1：Add UnitTestPatch And Regression task plan。
- 新增 `docs/implementation/slices/slice-16-unit-test-patch-regression.md`。
- 将 Slice 16 拆为 contract boundary、UnitTestPatch/QualityGateDecision
  model/schema、PatchScopeGate、patch generation/review、patch apply、
  new-test/regression API、QualityGateDecision API、CI/CD quality report API、
  frontend shell、golden smoke、completion gate。
- 明确 Slice 16 覆盖 review-gated UnitTestPatch、PatchScopeGate、pytest
  regression、QualityGateDecision 和 CI/CD quality report evidence。
- 明确不加入 merge/push/release/deployment、remote CI provider integration、
  RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 2：Add UnitTestPatch and
  regression contract boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-16-unit-test-patch-regression.md && rg -n "UnitTestPatch|PatchScopeGate|Verification Command|Non-goals" docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

修改文件：

- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 2：Add UnitTestPatch and regression
  contract boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 15 Completion Gate 完成

本轮完成：

- 完成 Slice 15 completion gate。
- 确认 Slice 15 所有任务均为 `done`，并记录提交号：
  `6133121`、`a8a5482`、`788d6c0`、`a0391fa`、`2e51d06`、
  `3a6df10`、`362ce0e`、`6e59820`。
- 完成组合验收：CI/CD Quality API、golden smoke、frontend shell 均已覆盖。
- 已在 `docs/implementation/slices/slice-15-cicd-quality-center.md` 写入
  completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 16 Task 1：Add UnitTestPatch And
  Regression task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/golden/test_cicd_quality_center_golden.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- CI/CD Quality API + golden smoke：`8 passed`
- Frontend workbench shell：`13 passed, 16 tests passed`

Slice 15 保持的非目标：

- 未创建 UnitTestPatch、QualityGateDecision、TestRun 或 Report records。
- 未加入 merge/release decisions、remote CI provider integration、webhooks、
  PR comments、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 16 Task 1：Add UnitTestPatch And
  Regression task plan。
- 这是 planning-only 任务，先创建
  `docs/implementation/slices/slice-16-unit-test-patch-regression.md`，不要直接改产品代码。

## 2026-06-30 Slice 15 Task 8 CI/CD Quality Golden Smoke 完成

本轮完成：

- 完成 Slice 15 Task 8：Add CI/CD Quality Center golden smoke。
- 新增 `backend/app/tests/golden/test_cicd_quality_center_golden.py`。
- Golden smoke 使用本地 diff 场景创建 Project/Repository fixture records。
- 通过 API 创建 CICDRun，验证 local_diff/manual/local、changed files 和
  pending quality_gate_status。
- 通过 API 触发 analyze，验证 succeeded AITask、risk_analysis artifact、
  analyzed status 和 medium overall_risk。
- 验证未创建 AutomationDraft、TestRun、Report 或 quality_gate_decisions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_center_golden.py -q
```

验证结果：

- CI/CD Quality Center golden smoke：`1 passed`

修改文件：

- `backend/app/tests/golden/test_cicd_quality_center_golden.py`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/golden/test_cicd_quality_center_golden.py -q && npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 15 Task 7 CI/CD Quality Frontend Shell 完成

本轮完成：

- 完成 Slice 15 Task 7：Add CI/CD Quality Center frontend shell。
- 新增 `frontend/src/api/cicd.ts`，覆盖 CICDRun create/get/list/analyze。
- 新增 `frontend/src/stores/cicd.ts`，管理 local_diff 输入、run 状态和
  analysis 刷新。
- 新增 `frontend/src/views/cicd/CicdQualityCenterView.vue`。
- 页面支持输入 Project/Repository/Base/Head/diff_text，创建 CICDRun 并触发
  mock risk_analysis。
- 页面展示 changed files、file_role、risk_level、risk_reasons 和
  risk_analysis artifact。
- CI/CD 质量中心导航由 `待接入` 更新为 `就绪`。
- 未展示 merge/release decisions 或 remote CI provider controls。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 8：Add CI/CD Quality Center
  golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
```

验证结果：

- Frontend workbench tests：`13 passed, 16 tests passed`

修改文件：

- `frontend/src/api/cicd.ts`
- `frontend/src/stores/cicd.ts`
- `frontend/src/views/cicd/CicdQualityCenterView.vue`
- `frontend/src/views/cicd/CicdQualityCenterView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 8：Add CI/CD Quality Center golden
  smoke。
- 当前任务不要创建 UnitTestPatch、QualityGateDecision、TestRun 或 Report
  records。

## 2026-06-30 Slice 15 Task 6 CI/CD Analyze API 完成

本轮完成：

- 完成 Slice 15 Task 6：Add CI/CD analyze API。
- 新增 `POST /api/cicd/runs/{id}/analyze`。
- Analyze 创建 succeeded AITask，`task_type=cicd_change_analysis`。
- Analyze 根据 changed_files 更新 CICDRun status 为 `analyzed`，
  overall_risk 为最高 changed file risk。
- 写入 `risk_analysis` artifact，owner 为 CICDRun，metadata 包含 provider、
  model、prompt、skill、overall_risk、changed_file_count 和 analysis_json。
- GET CI/CD run 会返回 analysis_artifacts。
- 未创建 UnitTestPatch、regression plan、QualityGateDecision、TestRun 或
  Report records。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 7：Add CI/CD Quality Center
  frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

验证结果：

- CI/CD Quality Center focused tests：`7 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_cicd_quality_center.py`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 7：Add CI/CD Quality Center
  frontend shell。
- 当前任务不要展示 merge/release decisions 或 remote CI provider controls。

## 2026-06-30 Slice 15 Task 5 CI/CD Run API 完成

本轮完成：

- 完成 Slice 15 Task 5：Add CI/CD run create/list/get API。
- 新增 `backend/app/modules/cicd/router.py` 并在 `backend/app/main.py`
  挂载 `/api/cicd`。
- `POST /api/cicd/runs` 支持 local_diff/manual/local 输入，解析 diff_text
  并持久化 CICDChangedFile rows。
- `GET /api/cicd/runs` 和 `GET /api/cicd/runs/{id}` 返回 changed_files。
- 创建 `diff_patch` 和 `changed_files` artifacts，owner 为 CICDRun。
- 未创建 UnitTestPatch、TestRun、QualityGateDecision 或 Report records。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 6：Add CI/CD analyze API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

验证结果：

- CI/CD Quality Center focused tests：`6 passed`

修改文件：

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_cicd_quality_center.py`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 6：Add CI/CD analyze API。
- 当前任务不要创建 UnitTestPatch、regression plan、QualityGateDecision、
  TestRun 或 Report records。

## 2026-06-30 Slice 15 Task 4 Local Diff Parser 完成

本轮完成：

- 完成 Slice 15 Task 4：Add local diff parser service。
- 新增 `backend/app/modules/cicd/service.py`。
- `parse_local_diff` 支持解析 modified、added、deleted、renamed unified
  diff file blocks。
- parser 可输出 `changed_files.json` 兼容的 manifest item。
- 支持按路径和扩展名确定 language 与 file_role：source、test、docs、
  config、migration、fixture、build、unknown。
- 支持基于 file_role、change_type 和变更行数生成 deterministic risk_level
  与 risk_reasons。
- 未调用远程 CI provider，也未执行 git remote 操作。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 5：Add CI/CD run
  create/list/get API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

验证结果：

- CI/CD Quality Center focused tests：`5 passed`

修改文件：

- `backend/app/modules/cicd/service.py`
- `backend/app/tests/api/test_cicd_quality_center.py`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 5：Add CI/CD run create/list/get
  API。
- 当前任务不要创建 UnitTestPatch、TestRun、QualityGateDecision 或 Report
  records。

## 2026-06-30 Slice 15 Task 3 CICDRun/CICDChangedFile Model Schema 完成

本轮完成：

- 完成 Slice 15 Task 3：Add CICDRun and CICDChangedFile model/schema。
- 新增 `backend/app/modules/cicd/` 模块。
- 新增 CICDRun model，覆盖 project、repository、source_type、
  trigger_type、provider、pipeline/base/head、summary、overall_risk、
  quality_gate_status 和 status。
- 新增 CICDChangedFile model，覆盖 path、old_path、change_type、language、
  file_role、risk_level、risk_reasons、lines_added、lines_deleted。
- 新增 create/read/list schemas，read schema 可嵌入 changed_files 和
  analysis_artifacts。
- 未创建 UnitTestPatch、QualityGateDecision、TestRun 或 Report records。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 4：Add local diff parser
  service。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

验证结果：

- CICDRun/CICDChangedFile model/schema tests：`4 passed`

修改文件：

- `backend/app/modules/cicd/__init__.py`
- `backend/app/modules/cicd/models.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_cicd_quality_center.py`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 4：Add local diff parser service。
- 当前任务只解析 local unified diff text，不调用远程 CI provider 或执行 git
  remote 操作。

## 2026-06-30 Slice 15 Task 2 CI/CD Quality Contract Boundary 完成

本轮完成：

- 完成 Slice 15 Task 2：Add CI/CD Quality Center contract boundary。
- 在数据模型合同中明确 CICDRun 的 Slice 15 边界：`local_diff` /
  `manual_check`、`trigger_type=manual`、`provider=local`，且
  `quality_gate_status` 在 Slice 15 保持 `pending`。
- 在 API 合同中明确 Slice 15 只实现 `/api/cicd/runs` create/list/get 和
  `/api/cicd/runs/{id}/analyze`。
- 将 UnitTestPatch、run-new-tests、regression、QualityGateDecision 和
  CI/CD quality report endpoints 标记为 Slice 16+ placeholder。
- 在 artifact 合同中定义 `diff.patch`、`changed_files.json`、
  `risk_analysis.json` 的 Slice 15 artifact 边界和 metadata 要求。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 3：Add CICDRun and
  CICDChangedFile model/schema。

本轮验证：

```bash
rg -n "CICDRun|CICDChangedFile|POST /api/cicd/runs|local_diff|remote CI" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-15-cicd-quality-center.md
```

修改文件：

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 3：Add CICDRun and CICDChangedFile
  model/schema。
- 当前任务只做 model/schema，不创建 UnitTestPatch、QualityGateDecision、
  TestRun 或 Report records。

## 2026-06-30 Slice 15 Task 1 CI/CD Quality Center Task Plan 完成

本轮完成：

- 完成 Slice 15 Task 1：Add CI/CD Quality Center task plan。
- 新增 `docs/implementation/slices/slice-15-cicd-quality-center.md`。
- 将 Slice 15 拆为 contract boundary、CICDRun/CICDChangedFile
  model/schema、local diff parser、run create/list/get API、analyze API、
  frontend shell、golden smoke、completion gate。
- 明确 Slice 15 只做 local-first CICDRun、CICDChangedFile、local diff
  analysis 和 evidence surface。
- 明确 UnitTestPatch、regression、QualityGateDecision、CI/CD quality report
  不在 Slice 15 实现。
- 明确不加入 merge/release decisions、remote CI provider integration、
  webhooks、PR comments、RAG runtime、MCP runtime、RBAC、tenants 或
  permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 2：Add CI/CD Quality Center
  contract boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-15-cicd-quality-center.md && rg -n "CI/CD Quality Center|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-15-cicd-quality-center.md
```

修改文件：

- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 2：Add CI/CD Quality Center
  contract boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 14 Completion Gate 完成

本轮完成：

- 完成 Slice 14 completion gate。
- 确认 Slice 14 所有任务均为 `done`，并记录提交号：
  `dcedd23`、`ee168bc`、`f9ebb7a`、`0f9a163`、`811316d`、
  `c4971a3`、`04b6425`。
- 完成组合验收：FailureAnalysis/Report API、golden smoke、frontend shell 均
  已覆盖。
- 已在 `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
  写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 15 Task 1：Add CI/CD Quality Center
  task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py backend/app/tests/golden/test_report_failure_analysis_golden.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- Report/FailureAnalysis API + golden smoke：`9 passed`
- Frontend workbench shell：`12 passed, 15 tests passed`

Slice 14 保持的非目标：

- 未加入 CI/CD quality gates、merge/release decisions、RAG runtime、MCP
  runtime、RBAC、tenants、permissions 或 broad report analytics。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 15 Task 1：Add CI/CD Quality Center task
  plan。
- 这是 planning-only 任务，先创建
  `docs/implementation/slices/slice-15-cicd-quality-center.md`，不要直接改产品代码。

## 2026-06-30 Slice 14 Task 7 Report/FailureAnalysis Golden Smoke 完成

本轮完成：

- 完成 Slice 14 Task 7：Add automation execution report golden smoke。
- 新增 `backend/app/tests/golden/test_report_failure_analysis_golden.py`。
- golden smoke 种子化 failed TestRun、stderr artifact 和 failed TestResult。
- 通过 API 创建 FailureAnalysis，并验证分类为 `test_script_issue`、
  AITask 为 `succeeded`。
- 通过 API 创建 automation_execution Report，并验证 conclusion、metrics、
  evidence_manifest、report artifacts 和持久化 metadata。
- 验证没有创建 `quality_gate_decisions` 表。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_report_failure_analysis_golden.py -q
```

验证结果：

- Report/FailureAnalysis golden smoke：`1 passed`

修改文件：

- `backend/app/tests/golden/test_report_failure_analysis_golden.py`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py backend/app/tests/golden/test_report_failure_analysis_golden.py -q && npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 14 Task 6 Report/FailureAnalysis Frontend Shell 完成

本轮完成：

- 完成 Slice 14 Task 6：Add Report and FailureAnalysis frontend shell。
- 新增 `frontend/src/api/reporting.ts`，覆盖 FailureAnalysis create/get 和
  automation_execution Report create/get。
- 新增 `frontend/src/stores/reporting.ts`，串联 TestRun ID、FailureAnalysis
  和 Report 状态。
- 新增 `frontend/src/views/reporting/ReportFailureAnalysisView.vue`，页面先展示
  evidence_manifest，再展示失败分析和报告结论。
- 报告中心导航由 `待接入` 更新为 `就绪`，路由为
  `/reports/failure-analysis`。
- 新增 `ReportFailureAnalysisView.spec.ts`，验证失败分析、执行报告和
  evidence-first 展示顺序。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 7：Add automation execution
  report golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
```

验证结果：

- Frontend workbench tests：`12 passed, 15 tests passed`

修改文件：

- `frontend/src/api/reporting.ts`
- `frontend/src/stores/reporting.ts`
- `frontend/src/views/reporting/ReportFailureAnalysisView.vue`
- `frontend/src/views/reporting/ReportFailureAnalysisView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 7：Add automation execution report
  golden smoke。
- 当前任务只补 golden smoke，不添加 CI/CD QualityGateDecision records。

## 2026-06-30 Slice 14 Task 5 Automation Execution Report API 完成

本轮完成：

- 完成 Slice 14 Task 5：Add automation execution Report API。
- 新增 `POST /api/reports`，支持 `report_type=automation_execution` 和
  `related_entity_type=TestRun`。
- 新增 `GET /api/reports/{id}`，返回 conclusion、summary、metrics、
  artifact_ids、evidence_manifest 和 report artifacts。
- Report 生成 `report_md`、`report_json` 和 `evidence_manifest.json`
  artifact metadata。
- conclusion 从 TestRun parsed_result、TestResult rows 和 TestRun artifacts
  推导；缺少 execution artifact 时不会返回 passed，而是
  `insufficient_evidence`。
- 未创建 CI/CD quality reports 或 QualityGateDecision records。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 6：Add Report and
  FailureAnalysis frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q
```

验证结果：

- Report/FailureAnalysis API focused tests：`8 passed`

修改文件：

- `backend/app/modules/reporting/router.py`
- `backend/app/modules/reporting/service.py`
- `backend/app/tests/api/test_report_failure_analysis.py`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 6：Add Report and FailureAnalysis
  frontend shell。
- 当前任务保持 evidence-first，不加入 CI/CD quality gates、RAG runtime、MCP
  runtime、RBAC、tenants 或 permissions。

## 2026-06-30 Slice 14 Task 4 FailureAnalysis API 完成

本轮完成：

- 完成 Slice 14 Task 4：Add FailureAnalysis API。
- 新增 `backend/app/modules/reporting/service.py`，从 TestRun、
  TestResult 和 TestRun artifacts 生成 deterministic mock FailureAnalysis。
- 新增 `backend/app/modules/reporting/router.py` 并在 `backend/app/main.py`
  挂载 `/api/test-runs/{id}/failure-analysis`。
- `POST /api/test-runs/{id}/failure-analysis` 会创建 succeeded AITask 和
  draft FailureAnalysis，不创建 Report 或 repair task。
- `GET /api/test-runs/{id}/failure-analysis` 返回 evidence-first read model。
- 缺少 stdout/stderr/TestResult/artifact evidence 时返回
  `classification=insufficient_evidence`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 5：Add automation execution
  Report API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q
```

验证结果：

- FailureAnalysis API focused tests：`6 passed`

修改文件：

- `backend/app/modules/reporting/router.py`
- `backend/app/modules/reporting/service.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_report_failure_analysis.py`
- `docs/contracts/02-api-contract.md`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 5：Add automation execution Report
  API。
- 当前任务不要创建 CI/CD quality reports 或 QualityGateDecision records。

## 2026-06-30 Slice 14 Task 3 FailureAnalysis/Report Model Schema 完成

本轮完成：

- 完成 Slice 14 Task 3：Add FailureAnalysis and Report model schema。
- 新增 `backend/app/modules/reporting/` 模块，包含 FailureAnalysis/Report
  SQLAlchemy models 和 create/read schemas。
- FailureAnalysis 覆盖 project、test_run、test_result、ai_task、
  classification、confidence、evidence_artifact_ids、summary、root_cause、
  suggested_actions 和 status。
- Report 覆盖 project、report_type、title、related entity、status、
  conclusion、summary、metrics_json 和 artifact_ids。
- 新增 `backend/app/tests/api/test_report_failure_analysis.py`，验证模型默认值、
  UUID artifact list 持久化、schema 字段名和 evidence_manifest response。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 4：Add FailureAnalysis API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q
```

验证结果：

- FailureAnalysis/Report focused model/schema tests：`4 passed`

修改文件：

- `backend/app/modules/reporting/__init__.py`
- `backend/app/modules/reporting/models.py`
- `backend/app/modules/reporting/schemas.py`
- `backend/app/tests/api/test_report_failure_analysis.py`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 4：Add FailureAnalysis API。
- 当前任务不要创建 repair tasks 或 reports。

## 2026-06-30 Slice 14 Task 2 Report And FailureAnalysis Contract 完成

本轮完成：

- 完成 Slice 14 Task 2：Add Report and FailureAnalysis API contract boundary。
- 收紧 `docs/contracts/02-api-contract.md` 的 FailureAnalysis create/get
  合同，要求 evidence-first、支持 deterministic mock provider、缺证据时返回
  `insufficient_evidence`。
- 收紧 automation_execution Report create/get 合同，要求
  `evidence_manifest.json`、report artifact ids、TestRun/TestResult/artifact
  evidence 支撑 conclusion。
- 在 `docs/contracts/04-artifact-contract.md` 补充 evidence_manifest artifact
  rules。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 3：Add FailureAnalysis and
  Report model schema。

本轮验证：

```bash
rg -n "FailureAnalysis|POST /api/test-runs/.*/failure-analysis|POST /api/reports|evidence_manifest" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-14-report-and-failure-analysis.md
```

修改文件：

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 3：Add FailureAnalysis and Report
  model schema。
- 当前任务只做 model/schema，不调用 AI providers 或写 report artifacts。

## 2026-06-30 Slice 14 Task 1 Report And Failure Analysis Task Plan 完成

本轮完成：

- 完成 Slice 14 Task 1：Add Report And Failure Analysis task plan。
- 新增 `docs/implementation/slices/slice-14-report-and-failure-analysis.md`。
- 将 Slice 14 拆为 API/artifact contract、FailureAnalysis/Report
  model/schema、FailureAnalysis API、automation_execution Report API、frontend
  shell、golden smoke、completion gate。
- 明确 Slice 14 只做 evidence-backed FailureAnalysis、evidence manifest 和
  automation_execution Report。
- 明确不加入 CI/CD quality gates、merge/release decisions、RAG runtime、MCP
  runtime、RBAC、tenants、permissions 或 broad report center analytics。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 2：Add Report and
  FailureAnalysis API contract boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-14-report-and-failure-analysis.md
rg -n "Report And Failure Analysis|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-14-report-and-failure-analysis.md
```

修改文件：

- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 2：Add Report and FailureAnalysis
  API contract boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 13 Completion Gate 完成

本轮完成：

- 完成 Slice 13 completion gate。
- 确认 Slice 13 所有任务均为 `done`，并记录提交号：
  `f882a4a`、`1205e95`、`b7c65f2`、`ac3f7c8`、`47d0618`、`a201335`。
- 完成组合验收：Playwright contract、runner adapter、execution API、
  frontend shell、golden smoke 均已覆盖。
- 已在 `docs/implementation/slices/slice-13-playwright-minimal-loop.md` 写入
  completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 14 Task 1：Add Report And Failure
  Analysis task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- Playwright API + golden smoke：`9 passed`
- Frontend workbench shell：`11 passed, 14 tests passed`

Slice 13 保持的非目标：

- 未加入 reports、failure analysis、CI/CD quality、RAG runtime、MCP runtime、
  RBAC、tenants、permissions、low-code UI automation 或 browser matrix。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 14 Task 1：Add Report And Failure Analysis
  task plan。
- 这是 planning-only 任务，先创建
  `docs/implementation/slices/slice-14-report-and-failure-analysis.md`，不要直接改产品代码。

## 2026-06-30 Slice 13 Task 6 Playwright Golden Smoke 完成

本轮完成：

- 完成 Slice 13 Task 6：Add Playwright golden smoke。
- 新增 `backend/app/tests/golden/test_playwright_minimal_loop_golden.py`。
- golden smoke 复用 reviewed golden UI TestCase -> AutomationDraft -> edit ->
  approve 链路。
- 已批准 Playwright AutomationDraft 通过 `POST /api/test-runs` +
  `runner_mode=playwright_local` 执行 controlled Playwright path。
- 使用 deterministic fake runner output，不依赖真实浏览器二进制。
- 验证 TestRun、TestResult、runtime_manifest/stdout/stderr/playwright_trace/
  screenshot Artifact metadata 均持久化。
- 验证没有创建 Report、FailureAnalysis 或 QualityGateDecision。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q
```

验证结果：

- Playwright minimal golden smoke：`1 passed`

修改文件：

- `backend/app/tests/api/test_playwright_minimal_loop.py`
- `backend/app/tests/golden/test_playwright_minimal_loop_golden.py`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py -q && npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 13 Task 5 Playwright Execution Frontend Shell 完成

本轮完成：

- 完成 Slice 13 Task 5：Add Playwright execution frontend shell。
- 扩展 `frontend/src/stores/execution.ts`，支持传入 `runnerMode` 和
  Playwright reason。
- 新增 `frontend/src/views/execution/PlaywrightExecutionView.vue`，通过
  `runner_mode=playwright_local` 启动 Playwright run。
- 页面展示 status、command、exit_code、duration、runner_mode、
  parsed_result metrics、trace/screenshot artifacts 和 TestResult rows。
- 新增 `PlaywrightExecutionView.spec.ts` 覆盖启动、刷新、trace/screenshot
  证据展示。
- 接入 `execution/playwright` 路由，并在工作台导航中加入
  `Playwright 执行`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 6：Add Playwright golden
  smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
```

验证结果：

- Frontend workbench shell tests：`11 passed, 14 tests passed`

修改文件：

- `frontend/src/stores/execution.ts`
- `frontend/src/views/execution/PlaywrightExecutionView.vue`
- `frontend/src/views/execution/PlaywrightExecutionView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 6：Add Playwright golden smoke。
- golden smoke 使用 deterministic fake runner output，不依赖真实浏览器二进制。

## 2026-06-30 Slice 13 Task 4 Playwright Execution API 完成

本轮完成：

- 完成 Slice 13 Task 4：Add Playwright execution API。
- 扩展 `backend/app/modules/execution/service.py`，通过既有
  `POST /api/test-runs` 支持 `runner_mode=playwright_local`。
- 支持 approved Playwright AutomationDraft 和 configured Playwright
  TestCommand 两条来源。
- Playwright draft 会复制到 Chtest-managed 临时运行目录后执行。
- 执行结果会持久化 TestRun、TestResult、stdout/stderr/runtime_manifest 以及
  playwright_trace/screenshot Artifact metadata。
- 新增 focused API tests 覆盖 approved draft、unapproved reject、configured
  TestCommand。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 5：Add Playwright execution
  frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/api/test_playwright_minimal_loop.py -q
```

验证结果：

- Playwright execution API focused tests：`8 passed`
- Pytest + Playwright execution API regression：`18 passed`

修改文件：

- `backend/app/modules/execution/service.py`
- `backend/app/tests/api/test_playwright_minimal_loop.py`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 5：Add Playwright execution frontend
  shell。
- 前端只做 minimal Playwright execution workbench shell，不加入 low-code
  automation editor、report 或 quality gate。

## 2026-06-30 Slice 13 Task 3 Playwright Runner Adapter 完成

本轮完成：

- 完成 Slice 13 Task 3：Add Playwright runner adapter。
- 新增 `backend/app/modules/execution/playwright_runner.py`。
- adapter 复用 TestCommand allowlist 口径，只接受 `npx playwright test ...`
  命令并拒绝 forbidden shell operators。
- adapter 捕获 stdout、stderr、exit_code、duration_ms，并解析
  passed/failed/skipped/error/total 计数。
- adapter 可发现 `playwright_trace` zip 和 `screenshot` png artifact
  candidates。
- 新增 `backend/app/tests/api/test_playwright_minimal_loop.py`，使用 fake npx
  可执行文件做确定性测试，不依赖真实浏览器或 Playwright 包。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 4：Add Playwright execution API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_playwright_minimal_loop.py -q
```

验证结果：

- Playwright runner adapter focused tests：`5 passed`

修改文件：

- `backend/app/modules/execution/playwright_runner.py`
- `backend/app/tests/api/test_playwright_minimal_loop.py`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 4：Add Playwright execution API。
- 通过 `POST /api/test-runs` + `runner_mode=playwright_local` 接入，不新增报告或质量门禁。

## 2026-06-30 Slice 13 Task 2 Playwright Execution Contract 完成

本轮完成：

- 完成 Slice 13 Task 2：Add Playwright execution API contract and task boundary。
- 在 `docs/contracts/02-api-contract.md` 中明确 Playwright minimal execution
  复用 `POST /api/test-runs`、`GET /api/test-runs/{id}`，通过
  `runner_mode=playwright_local` 区分。
- Request 支持 approved Playwright AutomationDraft 或 configured Playwright
  TestCommand，命令必须 backend assembled 或 allowlist validated。
- Response 复用 TestRun/TestResult evidence shape，并允许返回
  `playwright_trace` 和 `screenshot` artifact metadata。
- 在 `docs/contracts/04-artifact-contract.md` 补充 Playwright trace/screenshot
  artifact rules。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 3：Add Playwright runner
  adapter。

本轮验证：

```bash
rg -n "Playwright|POST /api/test-runs|playwright_trace|screenshot" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-13-playwright-minimal-loop.md
```

修改文件：

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 3：Add Playwright runner adapter。
- 当前任务只做 adapter，不接 router/API orchestration。

## 2026-06-30 Slice 13 Task 1 Playwright Minimal Loop Task Plan 完成

本轮完成：

- 完成 Slice 13 Task 1：Add Playwright Minimal Loop task plan。
- 新增 `docs/implementation/slices/slice-13-playwright-minimal-loop.md`。
- 将 Slice 13 拆为 API/artifact contract、Playwright runner adapter、
  Playwright execution API、frontend shell、golden smoke、completion gate。
- 明确 Slice 13 只做 minimal Playwright smoke execution、trace/screenshot
  evidence 和 frontend inspection。
- 明确不加入 reports、failure analysis、CI/CD quality gates、RAG runtime、
  MCP runtime、RBAC、tenants、permissions、low-code UI automation 或 browser
  matrix。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 2：Add Playwright execution API
  contract and task boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-13-playwright-minimal-loop.md
rg -n "Playwright Minimal Loop|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-13-playwright-minimal-loop.md
```

修改文件：

- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 2：Add Playwright execution API
  contract and task boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 12 Completion Gate 完成

本轮完成：

- 完成 Slice 12 completion gate。
- 确认 Slice 12 所有任务均为 `done`，并记录提交号：
  `bcd8974`、`db5de11`、`9f6c42c`、`44ac287`、`e40ccaa`、
  `fef7559`、`7185e5b`。
- 完成组合验收：TestRun/TestResult model/schema、pytest runner adapter、
  TestRun API、frontend execution shell、golden smoke 均已覆盖。
- 修复 pytest combined collection 的 import mismatch：golden smoke 文件名从
  `test_testrunner_pytest.py` 调整为 `test_testrunner_pytest_golden.py`。
- 已在 `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
  写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 13 Task 1：Add Playwright Minimal
  Loop task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/golden/test_testrunner_pytest_golden.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- TestRunner API + golden smoke：`11 passed`
- Frontend workbench shell：`10 passed, 13 tests passed`

Slice 12 保持的非目标：

- 未加入 Playwright execution、reports、CI/CD quality、RAG runtime、MCP
  runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 13 Task 1：Add Playwright Minimal Loop task
  plan。
- 这是 planning-only 任务，先创建
  `docs/implementation/slices/slice-13-playwright-minimal-loop.md`，不要直接改产品代码。

## 2026-06-30 Slice 12 Task 7 Pytest Execution Golden Smoke 完成

本轮完成：

- 完成 Slice 12 Task 7：Add Pytest Execution Golden Smoke。
- 新增 `backend/app/tests/golden/test_testrunner_pytest_golden.py`。
- golden smoke 复用 reviewed golden TestCase -> AutomationDraft -> edit ->
  approve 链路。
- 已批准 AutomationDraft 通过 `POST /api/test-runs` 执行 controlled pytest。
- 验证 TestRun、TestResult、runtime_manifest/stdout/stderr Artifact metadata
  均持久化。
- 验证没有创建 Report 或 QualityGateDecision 表/记录。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_testrunner_pytest_golden.py -q
```

验证结果：

- Pytest execution golden smoke：`1 passed`

修改文件：

- `backend/app/tests/golden/test_testrunner_pytest_golden.py`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/golden/test_testrunner_pytest_golden.py -q && npm --prefix frontend run test -- --run`。
- 完成后在 Slice 12 文档记录 completion evidence，并选择下一 V1 slice。

## 2026-06-30 Slice 12 Task 6 Pytest Execution Frontend Shell 完成

本轮完成：

- 完成 Slice 12 Task 6：Add Pytest Execution Frontend Shell。
- 新增 `frontend/src/api/execution.ts` 和 `frontend/src/stores/execution.ts`，
  接入 `POST /api/test-runs`、`GET /api/test-runs/{id}`。
- 新增 `frontend/src/views/execution/PytestExecutionView.vue`，支持从
  approved AutomationDraft 或 configured TestCommand 启动 pytest run。
- 页面展示 status、command、working_directory、exit_code、duration、
  runner_mode、readonly/network metadata、parsed_result metrics、Artifact
  rows 和 TestResult rows。
- 接入 `execution/pytest` 路由，并将工作台导航里的 `执行中心` 标为就绪。
- 新增 `PytestExecutionView.spec.ts` 覆盖启动、刷新和证据展示。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 7：Add Pytest Execution
  Golden Smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run
```

验证结果：

- Frontend workbench shell tests：`10 passed, 13 tests passed`

修改文件：

- `frontend/src/api/execution.ts`
- `frontend/src/stores/execution.ts`
- `frontend/src/views/execution/PytestExecutionView.vue`
- `frontend/src/views/execution/PytestExecutionView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 7：Add Pytest Execution Golden
  Smoke。
- 复用 golden reviewed case -> approved AutomationDraft setup，验证
  TestRun/TestResult/artifact metadata，不创建 Report 或 QualityGateDecision。

## 2026-06-30 Slice 12 Task 5 TestRun API 完成

本轮完成：

- 完成 Slice 12 Task 5：Add TestRun API。
- 新增 `backend/app/modules/execution/service.py` 和 `router.py`，接入
  `POST /api/test-runs`、`GET /api/test-runs/{id}`。
- `POST /api/test-runs` 支持 approved AutomationDraft 和 configured
  TestCommand 两条来源。
- approved AutomationDraft 会复制到 Chtest-managed 临时运行目录后通过
  pytest runner 执行；未批准 draft 返回 `TEST_RUN_INVALID_INPUT`。
- 执行结果会持久化 TestRun、TestResult、stdout/stderr/runtime_manifest
  Artifact metadata。
- 已在 `backend/app/main.py` 注册 execution router。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 6：Add Pytest Execution
  Frontend Shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

验证结果：

- TestRun API focused tests：`10 passed`

修改文件：

- `backend/app/main.py`
- `backend/app/modules/execution/router.py`
- `backend/app/modules/execution/service.py`
- `backend/app/tests/api/test_testrunner_pytest.py`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 6：Add Pytest Execution Frontend
  Shell。
- 前端只做 pytest execution workbench shell，不加入 report/quality gate。

## 2026-06-30 Slice 12 Task 4 Pytest Runner Adapter 完成

本轮完成：

- 完成 Slice 12 Task 4：Add Pytest Runner Adapter。
- 新增 `backend/app/modules/execution/pytest_runner.py`，提供
  `PytestRunner`、`PytestRunnerResult` 和 `PytestRunnerCommandError`。
- adapter 复用 TestCommand allowlist 口径，只接受 `pytest ...` 命令并拒绝
  forbidden shell operators。
- adapter 使用 `python -m pytest` 执行已验证命令，捕获 stdout、stderr、
  exit_code、duration_ms，并解析 passed/failed/skipped/error/total 计数。
- 新增测试覆盖成功执行、拒绝 shell operator、拒绝非 allowlisted
  `python -m pytest` 输入。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 5：Add TestRun API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

验证结果：

- TestRun/TestResult model/schema + pytest runner adapter：`7 passed`

修改文件：

- `backend/app/modules/execution/pytest_runner.py`
- `backend/app/tests/api/test_testrunner_pytest.py`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 5：Add TestRun API。
- 需要接 router/service/main，创建和读取 TestRun/TestResult evidence。
- 不要生成 report 或 QualityGateDecision。

## 2026-06-30 Slice 12 Task 3 TestRun/TestResult Model Schema 完成

本轮完成：

- 完成 Slice 12 Task 3：Add TestRun and TestResult model schema。
- 新增 `backend/app/modules/execution/` 模块，包含 TestRun/TestResult SQLAlchemy
  models 和 create/read schemas。
- TestRun 覆盖 project、automation_draft、test_command、command、working
  directory、runner metadata、artifact ids、status、exit_code、duration 和
  parsed_result_json。
- TestResult 覆盖 test_run、test_name、test_file、status、duration、
  failure_message、failure_artifact_ids 和 parser metadata。
- 新增 `backend/app/tests/api/test_testrunner_pytest.py`，验证模型默认值、
  UUID artifact list 持久化、schema 字段名和 embedded TestResult response。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 4：Add Pytest Runner Adapter。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_testrunner_pytest.py -q
```

验证结果：

- TestRun/TestResult focused model/schema tests：`4 passed`

修改文件：

- `backend/app/modules/execution/__init__.py`
- `backend/app/modules/execution/models.py`
- `backend/app/modules/execution/schemas.py`
- `backend/app/tests/api/test_testrunner_pytest.py`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 4：Add Pytest Runner Adapter。
- 当前任务只做 adapter，不接 router/API orchestration。
- 继续保持 pytest-only、local_subprocess、allowlisted command、no Playwright。

## 2026-06-30 Slice 12 Task 2 TestRun API Contract 完成

本轮完成：

- 完成 Slice 12 Task 2：Add TestRun API contract and task boundary。
- 优化 `docs/contracts/02-api-contract.md` 的 Test Run API 合同，明确
  `POST /api/test-runs`、`GET /api/test-runs/{id}` 和 TestResult 明细返回。
- 规定 V1 TestRun 只接受 approved AutomationDraft 或 configured
  TestCommand 作为执行源，pytest 命令由后端组装或通过 allowlist 验证。
- 明确 `runner_mode=local_subprocess`、repository readonly、network disabled、
  runtime/dependency/environment artifacts、stdout/stderr/JUnit artifact metadata。
- 明确该 API 不创建 reports、QualityGateDecision、CI/CD workflow state、
  FailureAnalysis、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 3：Add TestRun and TestResult
  model schema。

本轮验证：

```bash
rg -n "TestRun|POST /api/test-runs|TestResult" docs/contracts/02-api-contract.md docs/implementation/slices/slice-12-testrunner-pytest-execution.md
```

修改文件：

- `docs/contracts/02-api-contract.md`
- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 3：Add TestRun and TestResult
  model schema。
- 先写 `backend/app/tests/api/test_testrunner_pytest.py` 红灯，再补
  `backend/app/modules/execution/models.py` 和 `schemas.py`。
- 当前任务不要加入 subprocess execution。

## 2026-06-30 Slice 12 Task 1 TestRunner Pytest Execution Task Plan 完成

本轮完成：

- 完成 Slice 12 Task 1：新增 TestRunner Pytest Execution task plan。
- 新增 `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`，将 Slice 12 拆为 API contract、TestRun/TestResult model/schema、pytest runner adapter、TestRun API、frontend shell、golden smoke、completion gate。
- 明确 Slice 12 只做 approval-gated pytest execution 和证据捕获，不加入 Playwright、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 2：Add TestRun API contract and task boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-12-testrunner-pytest-execution.md
rg -n "TestRunner Pytest Execution|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-12-testrunner-pytest-execution.md
```

修改文件：

- `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 2：Add TestRun API contract and task boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 11 AutomationDraft Completion Gate 完成

本轮完成：

- 完成 Slice 11 completion gate。
- 确认 Slice 11 所有任务均为 `done`，并记录提交号：
  `7704bbf`、`2d5bdec`、`7824172`、`bb6162a`、`b75dc1a`、`9a821df`。
- 确认 AutomationDraft model/schema、generation API、review API、frontend shell、golden smoke 均已覆盖。
- 已在 `docs/implementation/slices/slice-11-automation-draft-foundation.md` 写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 12 Task 1：Add TestRunner Pytest Execution task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_test_case_library_golden.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- AutomationDraft API + golden draft + Test Case Library golden：`7 passed`
- Frontend workbench shell tests：`9 passed, 12 tests passed`

Slice 11 保持的非目标：

- 未加入 TestRun/TestResult execution、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 12 Task 1：Add TestRunner Pytest Execution task plan。
- 这是 planning-only 任务，先创建 `docs/implementation/slices/slice-12-testrunner-pytest-execution.md`，不要直接改产品代码。

## 2026-06-30 Slice 11 Task 6 AutomationDraft Golden Smoke 完成

本轮完成：

- 完成 Slice 11 Task 6：新增 AutomationDraft golden smoke。
- 新增 `backend/app/tests/golden/test_automation_draft_golden.py`，复用 golden Test Case Library setup。
- 验证 reviewed golden TestCase 可以创建 AutomationDraft，并包含 draft_code、suggested_file_path、execution_notes、risk_notes、draft_generated 状态。
- 验证 golden draft 可以 edit 后 approve。
- 验证 approved draft 未创建 runtime_artifact/promoted_artifact，且当前 DB 无 test_runs、test_results、reports 表，确认本 slice 没有执行/报告副作用。
- 为复用 golden setup，`test_test_case_library_golden.py` 提取 `create_reviewed_golden_cases` helper，并给 ASGIClient 增加 PATCH 支持。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_automation_draft_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_test_case_library_golden.py -q
```

验证结果：

- AutomationDraft golden smoke：`1 passed`
- AutomationDraft API / golden draft / Test Case Library golden regression：`7 passed`

修改文件：

- `backend/app/tests/golden/test_automation_draft_golden.py`
- `backend/app/tests/golden/test_test_case_library_golden.py`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_test_case_library_golden.py -q`
  和 `npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 11 Task 5 AutomationDraft Frontend Review Shell 完成

本轮完成：

- 完成 Slice 11 Task 5：新增 AutomationDraft frontend review shell。
- 新增 `frontend/src/api/automation.ts` 和 `frontend/src/stores/automation.ts`，支持 create/get/edit/approve API wiring。
- 新增 `AutomationDraftReviewView.vue`，展示草稿代码、建议路径、执行说明、风险说明、状态、审批要求，并支持保存评审编辑和批准草稿。
- 接入 `automation/drafts` 路由，并将工作台导航里的 `自动化草稿中心` 标为就绪。
- 扩展 `ApiClient.patchJson` 以支持合同中的 PATCH endpoint。
- 未添加执行/运行按钮、report 链接、CI/CD quality action、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 6：Add AutomationDraft golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/automation/AutomationDraftReviewView.spec.ts
npm --prefix frontend run test -- --run
```

验证结果：

- AutomationDraft frontend focused test：`1 passed`
- Frontend test suite：`9 passed, 12 tests passed`

修改文件：

- `frontend/src/api/client.ts`
- `frontend/src/api/automation.ts`
- `frontend/src/stores/automation.ts`
- `frontend/src/views/automation/AutomationDraftReviewView.vue`
- `frontend/src/views/automation/AutomationDraftReviewView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 6：Add AutomationDraft golden smoke。
- 复用 golden Test Case Library setup，验证 reviewed golden TestCase -> edit -> approve AutomationDraft 且无执行副作用。

## 2026-06-30 Slice 11 Task 4 AutomationDraft Review API 完成

本轮完成：

- 完成 Slice 11 Task 4：新增 AutomationDraft edit and approve API。
- 新增 `GET /api/automation/drafts/{id}`、`PATCH /api/automation/drafts/{id}`、`POST /api/automation/drafts/{id}/approve`。
- 支持 reviewer 编辑 draft_code、suggested_file_path、execution_notes、risk_notes、review_comment。
- 支持 `draft_generated/edited -> approved`，非法 approve action 返回 `AUTOMATION_DRAFT_INVALID_ACTION`。
- 未创建 TestRun、TestResult、runtime artifacts、reports 或执行副作用。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 5：Add AutomationDraft frontend review shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_test_case_library.py -q
```

验证结果：

- AutomationDraft focused test：`5 passed`
- AutomationDraft + Test Case Library API regression：`8 passed`

修改文件：

- `backend/app/modules/automation/router.py`
- `backend/app/modules/automation/service.py`
- `backend/app/tests/api/test_automation_draft.py`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 5：Add AutomationDraft frontend review shell。
- 先写 `frontend/src/views/automation/AutomationDraftReviewView.spec.ts` 红灯，再补 API/store/router/layout/view。

## 2026-06-30 Slice 11 Task 3 AutomationDraft Generation API 完成

本轮完成：

- 完成 Slice 11 Task 3：新增 AutomationDraft generation API。
- 新增 `POST /api/automation/drafts`。
- 创建 deterministic mock AutomationDraft，并同步创建 succeeded AITask。
- Draft 包含 draft_code、target_framework、suggested_file_path、execution_notes、risk_notes、approval_required、execution_strategy。
- 只生成 review-gated draft，不执行、不写入目标仓库、不创建 TestRun/TestResult/runtime artifact/report。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 4：Add AutomationDraft edit and approve API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_test_case_library.py -q
```

验证结果：

- AutomationDraft focused test：`3 passed`
- AutomationDraft + Test Case Library API regression：`6 passed`

修改文件：

- `backend/app/main.py`
- `backend/app/modules/automation/router.py`
- `backend/app/modules/automation/service.py`
- `backend/app/tests/api/test_automation_draft.py`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 4：Add AutomationDraft edit and approve API。
- 继续在 `backend/app/tests/api/test_automation_draft.py` 中先写红灯，再补 get/edit/approve service/router。

## 2026-06-30 Slice 11 Task 2 AutomationDraft Model Schema 完成

本轮完成：

- 完成 Slice 11 Task 2：新增 AutomationDraft model and schema alignment。
- 新增 `backend/app/modules/automation` 模块。
- 新增 `AutomationDraft` SQLAlchemy model，字段对齐数据模型合同：project_id、test_case_id、requirement_id、ai_task_id、target_framework、draft_code、execution_strategy、approval_required、status、runtime/promoted artifact 等。
- 新增 AutomationDraft create/edit/approve/read schemas，为后续 API 任务准备。
- 未加入 draft generation endpoint、edit/approve endpoint、execution、frontend、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 3：Add AutomationDraft generation API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_test_case_library.py -q
```

验证结果：

- AutomationDraft model/schema focused test：`2 passed`
- AutomationDraft + Test Case Library API regression：`5 passed`

修改文件：

- `backend/app/modules/automation/__init__.py`
- `backend/app/modules/automation/models.py`
- `backend/app/modules/automation/schemas.py`
- `backend/app/tests/api/test_automation_draft.py`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 3：Add AutomationDraft generation API。
- 继续在 `backend/app/tests/api/test_automation_draft.py` 中先写红灯，再补 service/router。

## 2026-06-30 Slice 11 Task 1 AutomationDraft Foundation Task Plan 完成

本轮完成：

- 完成 Slice 11 Task 1：新增 AutomationDraft Foundation task plan。
- 新增 `docs/implementation/slices/slice-11-automation-draft-foundation.md`，将 Slice 11 拆为 model/schema、generation API、edit/approve API、frontend review shell、golden smoke、completion gate。
- 明确 Slice 11 只做 draft generation/review/approval foundation，不加入 pytest/Playwright 执行、runtime copy、TestRun/TestResult、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 2：Add AutomationDraft model and schema alignment。

本轮验证：

```bash
test -f docs/implementation/slices/slice-11-automation-draft-foundation.md
rg -n "AutomationDraft Foundation|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-11-automation-draft-foundation.md
```

修改文件：

- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 2：Add AutomationDraft model and schema alignment。
- 先写 `backend/app/tests/api/test_automation_draft.py` 红灯，再补 model/schema。

## 2026-06-30 Slice 10 Test Case Library Completion Gate 完成

本轮完成：

- 完成 Slice 10 completion gate。
- 确认 Slice 10 所有任务均为 `done`，并记录提交号：
  `03114cd`、`11942b3`、`0e0ad8e`、`41f9518`、`b12f323`。
- 确认 Test Case Library API contract、backend API、frontend shell、golden smoke 均已覆盖。
- 已在 `docs/implementation/slices/slice-10-test-case-library.md` 写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 11 Task 1：Add AutomationDraft Foundation task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_requirement_to_case.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- Test Case Library API + golden library + requirement-to-case golden：`5 passed`
- Frontend workbench shell tests：`8 passed, 11 tests passed`

Slice 10 保持的非目标：

- 未加入 AutomationDraft generation、execution、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 11 Task 1：Add AutomationDraft Foundation task plan。
- 这是 planning-only 任务，先创建 `docs/implementation/slices/slice-11-automation-draft-foundation.md`，不要直接改产品代码。

## 2026-06-30 Slice 10 Task 5 Test Case Library Golden Smoke 完成

本轮完成：

- 完成 Slice 10 Task 5：新增 Test Case Library golden smoke。
- 新增 `backend/app/tests/golden/test_test_case_library_golden.py`，复用 golden requirement-to-case fixture setup 和 review plan。
- 验证评审后 library API 返回 4 条 reviewed TestCase。
- 验证编辑后的过期优惠券用例保留 `准备已过期优惠券` 步骤和 `coupon_state=expired` input data。
- 验证 keyword 过滤可以找到 golden UI 用例。
- 修复 golden/API 同名测试文件导致的 pytest collection import mismatch，golden 文件采用唯一文件名。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_case_library_golden.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_requirement_to_case.py -q
```

验证结果：

- Test Case Library golden smoke：`1 passed`
- Test Case Library API / golden library / requirement-to-case golden regression：`5 passed`

修改文件：

- `backend/app/tests/golden/test_test_case_library_golden.py`
- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_requirement_to_case.py -q`
  和 `npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 10 Task 4 Test Case Library Frontend Shell 完成

本轮完成：

- 完成 Slice 10 Task 4：新增 Test Case Library frontend shell。
- 前端 API/store 新增 `GET /api/test-cases` wiring。
- 新增 `frontend/src/views/cases/TestCaseLibraryView.vue`，展示已评审用例列表、关键词筛选、步骤、预期结果、标签、评审状态和来源信息。
- 接入 `cases/library` 路由，并将工作台导航里的 `用例库` 标为就绪。
- 未添加 AutomationDraft 按钮、执行按钮、reports、dashboard 图表、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 Task 5：Add Test Case Library golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/cases/TestCaseLibraryView.spec.ts
npm --prefix frontend run test -- --run
```

验证结果：

- Test Case Library frontend focused test：`1 passed`
- Frontend test suite：`8 passed, 11 tests passed`

修改文件：

- `frontend/src/api/cases.ts`
- `frontend/src/stores/cases.ts`
- `frontend/src/views/cases/TestCaseLibraryView.vue`
- `frontend/src/views/cases/TestCaseLibraryView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 Task 5：Add Test Case Library golden smoke。
- 复用 golden requirement-to-case fixture setup，验证已评审用例能从 library API 查询。

## 2026-06-30 Slice 10 Task 3 Test Case Library Backend API 完成

本轮完成：

- 完成 Slice 10 Task 3：新增 Test Case Library backend API。
- 新增 `GET /api/test-cases`，返回已持久化的 TestCase records，不返回未评审 GeneratedCaseCandidate。
- 支持 `project_id` 必填过滤，以及 module_id、status、test_type、priority、keyword 可选过滤。
- keyword 覆盖 title、precondition、steps、expected_results、input_data、tags 的简单匹配。
- 响应返回 `items` 和 `total`，并包含 TestCase Library 合同字段。
- 未新增 TestCase mutation、AutomationDraft、execution、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 Task 4：Add Test Case Library frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_case_library.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_case_metrics.py backend/app/tests/api/test_test_case_library.py -q
```

验证结果：

- Test Case Library API focused test：`3 passed`
- Case Generation / Case Review / Case Metrics / Test Case Library API regression：`15 passed`

修改文件：

- `backend/app/modules/cases/router.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/tests/api/test_test_case_library.py`
- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 Task 4：Add Test Case Library frontend shell。
- 先写 `frontend/src/views/cases/TestCaseLibraryView.spec.ts` 红灯，再补 API/store/router/layout/view。

## 2026-06-30 Slice 10 Task 2 Test Case Library API Contract 完成

本轮完成：

- 完成 Slice 10 Task 2：新增 Test Case Library API contract and task boundary。
- 在 `docs/contracts/02-api-contract.md` 增加 `GET /api/test-cases`。
- 合同定义了 `TestCaseListRead` 响应字段，以及 project_id、module_id、status、test_type、priority、keyword 查询过滤。
- 明确该端点只浏览已评审 TestCase，不创建/修改 TestCase，不加入 AutomationDraft、执行、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 Task 3：Add Test Case Library backend API。

本轮验证：

```bash
rg -n "Test Case Library|GET /api/test-cases|TestCaseList" docs/contracts/02-api-contract.md docs/implementation/slices/slice-10-test-case-library.md
```

修改文件：

- `docs/contracts/02-api-contract.md`
- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 Task 3：Add Test Case Library backend API。
- 先写 `backend/app/tests/api/test_test_case_library.py` 红灯，再补 schemas/service/router。

## 2026-06-30 Slice 10 Task 1 Test Case Library Task Plan 完成

本轮完成：

- 完成 Slice 10 Task 1：新增 Test Case Library task plan。
- 新增 `docs/implementation/slices/slice-10-test-case-library.md`，将 Slice 10 拆为 API contract、backend API、frontend shell、golden smoke、completion gate。
- 明确 Slice 10 只浏览/搜索已评审 TestCase，不加入 AutomationDraft、执行、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 Task 2：Add Test Case Library API contract and task boundary。

本轮验证：

```bash
test -f docs/implementation/slices/slice-10-test-case-library.md
rg -n "Test Case Library|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-10-test-case-library.md
```

修改文件：

- `docs/implementation/slices/slice-10-test-case-library.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 Task 2：Add Test Case Library API contract and task boundary。
- 这是 contract/documentation 任务，不要直接改产品代码。

## 2026-06-30 Slice 09 Case Metrics Completion Gate 完成

本轮完成：

- 完成 Slice 09 completion gate。
- 确认 Slice 09 所有任务均为 `done`，并记录提交号：
  `470fa23`、`0e1c81d`、`da6b606`、`46580ea`。
- 确认 Case Metrics 后端计算、API、前端 shell、golden metrics smoke 均已覆盖。
- 已在 `docs/implementation/slices/slice-09-case-metrics.md` 写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 10 Task 1：Add Test Case Library task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py -q
npm --prefix frontend run test -- --run
```

验证结果：

- Case Metrics API + golden requirement-to-case + golden metrics smoke：`6 passed`
- Frontend workbench shell tests：`7 passed, 10 tests passed`

Slice 09 保持的非目标：

- 未加入 Test Case Library workflow、AutomationDraft、执行、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 10 Task 1：Add Test Case Library task plan。
- 这是 planning-only 任务，先创建 `docs/implementation/slices/slice-10-test-case-library.md`，不要直接改产品代码。

## 2026-06-30 Slice 09 Task 5 Case Metrics Golden Smoke 完成

本轮完成：

- 完成 Slice 09 Task 5：新增 Case Metrics golden smoke。
- 新增 `backend/app/tests/golden/test_requirement_to_case_metrics.py`，复用现有 golden requirement-to-case fixture setup。
- golden smoke 按优惠券结算评审计划提交 approve、approve_after_edit、needs_optimization 动作后，调用 metrics API 验证 batch 指标。
- 断言 `generated_count >= 5`、`approved_count == 3`、`edited_count == 1`、`optimization_count == 1`、`review_progress >= 1.0`、`acceptance_rate == 0.8`。
- 未加入 browser automation、frontend、execution、AutomationDraft、reports、CI/CD quality、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 09 completion gate。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case_metrics.py -q
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/api/test_case_metrics.py -q
```

验证结果：

- Case Metrics golden smoke：`1 passed`
- Requirement To Case golden / Case Metrics golden / Case Metrics API regression：`6 passed`

修改文件：

- `backend/app/tests/golden/test_requirement_to_case_metrics.py`
- `docs/implementation/slices/slice-09-case-metrics.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 09 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py -q`
  和 `npm --prefix frontend run test -- --run`。

## 2026-06-30 Slice 09 Task 4 Case Metrics Frontend Shell 完成

本轮完成：

- 完成 Slice 09 Task 4：新增 Case Metrics frontend shell。
- 前端 API 新增 `GET /api/case-generation/tasks/{generation_task_id}/metrics` wiring。
- Pinia case store 在生成候选用例后加载 batch metrics，并在评审动作成功后刷新 metrics。
- `用例生成评审` shell 新增紧凑批次指标条，展示生成总数、直接通过、拒绝、采纳率、编辑率、评审进度、字段完整率。
- 未新增 dashboard route、chart dependency、Test Case Library、AutomationDraft、执行、reports、CI/CD、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 09 Task 5：Add Case Metrics golden smoke。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/cases/CaseGenerationReviewView.spec.ts
npm --prefix frontend run test -- --run
```

验证结果：

- Case Generation Review frontend focused test：`1 passed`
- Frontend test suite：`7 passed, 10 tests passed`

修改文件：

- `frontend/src/api/cases.ts`
- `frontend/src/stores/cases.ts`
- `frontend/src/views/cases/CaseGenerationReviewView.vue`
- `frontend/src/views/cases/CaseGenerationReviewView.spec.ts`
- `docs/implementation/slices/slice-09-case-metrics.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 09 Task 5：Add Case Metrics golden smoke。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case_metrics.py -q`。

## 2026-06-30 Slice 09 Task 3 Case Metrics API 完成

本轮完成：

- 完成 Slice 09 Task 3：新增 Case Metrics API。
- 新增 `GET /api/case-generation/tasks/{generation_task_id}/metrics`，返回 batch-level case metrics。
- API 复用 Task 2 的 `calculate_case_metrics`，不新增 metric table。
- 未加入 frontend、Test Case Library、AutomationDraft、执行、reports、CI/CD、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 09 Task 4：Add Case Metrics frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_case_metrics.py -q
git diff --check
```

验证结果：

- Case Metrics focused test：`4 passed`
- Case Generation / Case Review / Case Metrics regression：`12 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/cases/router.py`
- `backend/app/tests/api/test_case_metrics.py`
- `docs/implementation/slices/slice-09-case-metrics.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 09 Task 4：Add Case Metrics frontend shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

## 2026-06-29 Slice 09 Task 2 Case Metrics Backend Calculation 完成

本轮完成：

- 完成 Slice 09 Task 2：新增 case generation batch metrics service 计算。
- 新增 `CaseMetricsRead` schema。
- 新增 `calculate_case_metrics`，从 CaseGenerationTask/GeneratedCaseCandidate 计算 generated_count、approved_count、edited_count、rejected_count、optimization_count、reviewed_count、acceptance_rate、edit_rate、rejection_rate、optimization_rate、review_progress、field_complete_rate。
- 未新增 metric table，未加入 API route、frontend、Test Case Library、AutomationDraft、执行、reports、CI/CD、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 09 Task 3：Add Case Metrics API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_case_metrics.py -q
git diff --check
```

验证结果：

- Case Metrics focused test：`2 passed`
- Case Generation / Case Review / Case Metrics regression：`10 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/tests/api/test_case_metrics.py`
- `docs/implementation/slices/slice-09-case-metrics.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 09 Task 3：Add Case Metrics API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_metrics.py -q`。

## 2026-06-29 Slice 06 Requirement To Case Mainline 完成

本轮完成：

- 完成 Slice 06 completion gate。
- 确认 Slice 06 所有任务均为 `done` 且都有提交号。
- 后端已跑通 Requirement Review、Case Generation、Case Review、golden requirement-to-case smoke。
- 前端已接入 Requirement Review shell 和 Case Generation Review shell。
- 已在 `docs/implementation/slices/slice-06-requirement-to-case.md` 写入 completion evidence。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 09 Task 1：Add Case Metrics task plan。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/golden/test_requirement_to_case.py -q
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Backend Slice 06 chain：`15 passed`
- Frontend workbench shell tests：`7 passed, 10 tests passed`
- `git diff --check` 无输出。

Slice 06 保持的非目标：

- 未加入 AutomationDraft、执行、Playwright、CI/CD 质量中心、报告中心、真实 provider、RAG runtime、MCP runtime、RBAC、tenants 或 permissions。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 09 Task 1：Add Case Metrics task plan。
- 下一步先补 `docs/implementation/slices/slice-09-case-metrics.md`，不要直接写模型/API。

## 2026-06-29 Slice 06 Task 9 Case Generation Review Frontend Shell 完成

本轮完成：

- 完成 Slice 06 Task 9：新增 Case Generation Review frontend shell。
- 新增 `frontend/src/views/cases/CaseGenerationReviewView.vue`，支持启动 mock case generation、展示候选用例、查看步骤/预期结果/AI 理由，并提交 approve、approve_after_edit、reject、needs_optimization 评审动作。
- 新增 `frontend/src/api/cases.ts` 和 `frontend/src/stores/cases.ts`，最小接入 Case Generation 和 Case Review API。
- 把 `用例生成评审` 路由/导航状态接入现有 workbench shell。
- 未加入 AutomationDraft、执行、browser automation、真实 provider、RAG runtime、MCP runtime、RBAC 或 tenants。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 completion gate。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/cases/CaseGenerationReviewView.spec.ts
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Case Generation Review frontend focused test：`1 passed`
- Frontend test suite：`7 passed, 10 tests passed`
- `git diff --check` 无输出。

修改文件：

- `frontend/src/views/cases/CaseGenerationReviewView.vue`
- `frontend/src/views/cases/CaseGenerationReviewView.spec.ts`
- `frontend/src/api/cases.ts`
- `frontend/src/stores/cases.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 completion gate。
- 验证命令：
  `backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/golden/test_requirement_to_case.py -q`
  和 `npm --prefix frontend run test -- --run`。

风险提醒：

- completion gate 只做验证和记忆/进度收口；不要加入新的产品行为。

## 2026-06-29 Slice 06 Task 8 Requirement Review Frontend Shell 完成

本轮完成：

- 完成 Slice 06 Task 8：新增 Requirement Review frontend shell。
- 新增 `frontend/src/views/requirements/RequirementReviewView.vue`，支持录入需求、触发 mock RequirementReviewAgent、展示评分、问题、澄清问题、风险项和上下文使用。
- 新增 `frontend/src/api/requirements.ts` 和 `frontend/src/stores/requirements.ts`，最小接入 Requirement create、review start、review get API。
- 扩展 `ApiClient.postJson`，并把 `需求评审` 路由/导航状态接入现有 workbench shell。
- 未加入 Case Generation Review、AutomationDraft、执行、browser automation、真实 provider、RAG runtime、MCP runtime、RBAC 或 tenants。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 9：Add Case Generation Review frontend shell。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/requirements/RequirementReviewView.spec.ts
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Requirement Review frontend focused test：`1 passed`
- Frontend test suite：`6 passed, 9 tests passed`
- `git diff --check` 无输出。

修改文件：

- `frontend/src/views/requirements/RequirementReviewView.vue`
- `frontend/src/views/requirements/RequirementReviewView.spec.ts`
- `frontend/src/api/client.ts`
- `frontend/src/api/requirements.ts`
- `frontend/src/stores/requirements.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 9：Add Case Generation Review frontend shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

风险提醒：

- Task 9 只做 Case Generation Review frontend shell；不要加入 AutomationDraft、执行、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 7 Requirement To Case Golden Smoke 完成

本轮完成：

- 完成 Slice 06 Task 7：新增 fixture-aligned backend golden smoke。
- 新增 `backend/app/tests/golden/test_requirement_to_case.py`，覆盖项目/模块/需求创建、Requirement Review、Case Generation、候选用例列表和 Case Review。
- golden smoke 使用 `docs/fixtures/01-golden-requirement-to-case.md` 的优惠券结算规则、目标测试类型和人工评审动作。
- 验证 RequirementReview 六维评分、RiskItem、GeneratedCaseCandidate、TestCase 创建和批次指标。
- 未加入 browser automation、执行、AutomationDraft、frontend、真实 provider、RAG runtime、MCP runtime、RBAC 或 tenants。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 8：Add Requirement Review frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/golden/test_requirement_to_case.py -q
git diff --check
```

验证结果：

- Requirement To Case golden smoke：`1 passed`
- Requirement Review / Case Generation / Case Review / Golden regression：`15 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/tests/golden/test_requirement_to_case.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 8：Add Requirement Review frontend shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

风险提醒：

- Task 8 是 frontend shell；不要加入 Case Generation Review、AutomationDraft、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 6 Case Review API 完成

本轮完成：

- 完成 Slice 06 Task 6：新增 Case Review API。
- 新增 `POST /api/case-review/items/{candidate_id}/approve`，支持 `approve`、`approve_after_edit`、`reject`、`needs_optimization`。
- `approve` 会从 GeneratedCaseCandidate 创建官方 TestCase，并保留候选原始内容。
- `approve_after_edit` 会从人工编辑后的 case payload 创建官方 TestCase。
- `reject` 和 `needs_optimization` 只更新候选状态与 review comment，不创建 TestCase。
- 已阻止 `approved`、`approved_after_edit`、`rejected` 终态候选再次评审。
- 未加入 CaseReviewAgent 优化实现、执行、AutomationDraft、frontend、真实 provider、RAG runtime、MCP runtime、RBAC 或 tenants。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 7：Add Requirement To Case golden smoke。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_review.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py -q
git diff --check
```

验证结果：

- Case Review API focused test：`5 passed`
- Requirement Review / Case Generation / Case Review regression：`14 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/cases/router.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/tests/api/test_case_review.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 7：Add Requirement To Case golden smoke。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py -q`。

风险提醒：

- Task 7 只做 backend golden smoke；不要加入 frontend、AutomationDraft、browser automation、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 5 Case Generation Mock Flow 完成

本轮完成：

- 完成 Slice 06 Task 5：新增 Case Generation API 和 deterministic mock agent flow。
- 新增 `POST /api/case-generation/tasks`，同步运行 mock CaseGenerationAgent，创建 AITask、AI artifacts、LLMCallLog。
- 新增 `GET /api/case-generation/tasks/{id}/candidates`，返回 generated candidates 的 API 合同字段。
- 成功输出通过本任务 schema guard 后才写 CaseGenerationTask/GeneratedCaseCandidate。
- mock schema_invalid 路径会保留 AITask failed 状态、raw output artifact、schema_invalid LLMCallLog，但不写 CaseGenerationTask/GeneratedCaseCandidate/TestCase。
- 生成候选不会自动进入 TestCase library。
- 未加入 Case Review API、frontend、AutomationDraft、真实 provider、外部 RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 6：Add Case Review API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
git diff --check
```

验证结果：

- Case Generation API focused test：`3 passed`
- Requirement/Case Generation/AI Runtime regression：`31 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/cases/router.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_case_generation.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 6：Add Case Review API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_review.py -q`。

风险提醒：

- Task 6 只做 candidate review actions；不要执行 cases、不要加入 AutomationDraft、frontend、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 4 Case Generation Models 完成

本轮完成：

- 完成 Slice 06 Task 4：新增 CaseGenerationTask、GeneratedCaseCandidate、TestCase 模型与迁移。
- 新增 `backend/app/modules/cases/` 模块骨架和 read schema。
- 新增 Alembic migration `20260629_0005_case_generation.py`，沿用现有 UUID、timestamp、JSONB/SQLite JSON、Postgres text[]/SQLite JSON list 兼容模式。
- 为 target_test_types、steps、expected_results、input_data、tags、requirement/risk refs 等 JSON/list 字段启用 Mutable tracking。
- 未加入 Case Generation API、mock flow、Case Review API、frontend、AutomationDraft、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 5：Add Case Generation API and mock agent flow。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/db/test_prompt_skill_models.py backend/app/tests/db/test_requirement_review_models.py backend/app/tests/db/test_case_generation_models.py -q
git diff --check
```

验证结果：

- Case Generation model focused test：`4 passed`
- DB model regression：`25 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/cases/__init__.py`
- `backend/app/modules/cases/models.py`
- `backend/app/modules/cases/schemas.py`
- `backend/alembic/versions/20260629_0005_case_generation.py`
- `backend/app/tests/db/test_case_generation_models.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 5：Add Case Generation API and mock agent flow。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py -q`。

风险提醒：

- Task 5 可以复用 AI Runtime 和 deterministic mock provider，但仍不能加入 Case Review API、frontend、AutomationDraft、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 3 Requirement Review Mock Flow 完成

本轮完成：

- 完成 Slice 06 Task 3：新增 Requirement Review API 和 deterministic mock agent flow。
- 新增 `POST /api/requirements/{id}/review`，同步运行 mock RequirementReviewAgent，创建 AITask、AI artifacts、LLMCallLog。
- 新增 `GET /api/requirements/{id}/review`，返回 review scores、issues、clarification questions、test design notes、risk items、context usage 和 context manifest artifact id。
- 成功输出通过本任务 schema guard 后才写 RequirementReview/RiskItem。
- mock schema_invalid 路径会保留 AITask failed 状态和 raw output artifact，但不写 RequirementReview/RiskItem。
- 保留 `use_knowledge=false` 语义：不使用外部 RAG，但显式 `context_artifact_ids` 仍记录到 AITask 并作为 used context 返回。
- 未加入 case generation、frontend、真实 provider、外部 RAG runtime、MCP runtime、RBAC 或 tenants。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 4：Add Case Generation models and migration。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
git diff --check
```

验证结果：

- Requirement Review API focused test：`6 passed`
- Requirement/AI Runtime regression：`28 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/requirements/router.py`
- `backend/app/modules/requirements/service.py`
- `backend/app/modules/requirements/schemas.py`
- `backend/app/tests/api/test_requirement_review.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 4：Add Case Generation models and migration。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py -q`。

风险提醒：

- Task 4 只做 CaseGenerationTask、GeneratedCaseCandidate、TestCase models/migration/schema/test；不要加入 Case Generation API、mock flow、case review、frontend 或 AutomationDraft。

## 2026-06-29 Slice 06 Task 2 Requirement API 完成

本轮完成：

- 完成 Slice 06 Task 2：新增 Requirement create/get/list API。
- 新增 `POST /api/requirements`、`GET /api/requirements/{id}`、`GET /api/projects/{project_id}/requirements`。
- 新增 Requirement service，校验 project 存在和 module 归属同一 project。
- 扩展 Requirement schema：create、read、list envelope。
- 将 requirements router 注册到 FastAPI main。
- 未启动 RequirementReviewAgent，未创建 RequirementReview/RiskItem/CaseGeneration，未加入 frontend、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 3：Add Requirement Review API and mock agent flow。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py backend/app/tests/api/test_modules.py backend/app/tests/api/test_requirements.py -q
git diff --check
```

验证结果：

- Requirement API focused test：`9 passed`
- Project/Module/Requirement API regression：`25 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/requirements/router.py`
- `backend/app/modules/requirements/service.py`
- `backend/app/modules/requirements/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_requirements.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 3：Add Requirement Review API and mock agent flow。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py -q`。

风险提醒：

- Task 3 可以复用 AI Runtime 和 deterministic mock provider，但仍不能加入 case generation、frontend、真实 provider、外部 RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 06 Task 1 Requirement Review Models 完成

本轮完成：

- 完成 Slice 06 Task 1：新增 Requirement、RequirementReview、RiskItem 数据模型与迁移。
- 新增 `backend/app/modules/requirements/` 模块骨架和 read schema。
- 新增 Alembic migration `20260629_0004_requirement_review.py`，沿用现有 UUID、timestamp、JSONB/SQLite JSON 兼容模式。
- RequirementReview 的 issues、clarification questions、test design notes 使用 MutableList，支持 JSON list 原地更新持久化。
- 为 7 个评分字段添加 0-100 check constraint。
- 未加入 API、worker、mock agent flow、case generation、frontend、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 2：Add Requirement API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_requirement_review_models.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/db/test_prompt_skill_models.py backend/app/tests/db/test_requirement_review_models.py -q
git diff --check
```

验证结果：

- Requirement Review model focused test：`6 passed`
- DB model regression：`21 passed`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/requirements/__init__.py`
- `backend/app/modules/requirements/models.py`
- `backend/app/modules/requirements/schemas.py`
- `backend/alembic/versions/20260629_0004_requirement_review.py`
- `backend/app/tests/db/test_requirement_review_models.py`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 2：Add Requirement API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py -q`。

风险提醒：

- Task 2 只做 Requirement create/get/list API；不要启动 RequirementReviewAgent，不要生成 risks/cases，不要加入 frontend。

## 2026-06-29 Slice 06 Task 0 Requirement To Case Plan 完成

本轮完成：

- 完成 Slice 06 Task 0：新增 Requirement To Case mainline task plan。
- 新增 `docs/implementation/slices/slice-06-requirement-to-case.md`。
- 将 M3 Requirement To Case 拆成 9 个小任务：Requirement Review models、Requirement API、Requirement Review mock flow、Case Generation models、Case Generation mock flow、Case Review API、Golden smoke、Requirement Review frontend shell、Case Generation Review frontend shell。
- 每个任务包含 expected files、verification command、non-goals 和 commit message。
- 明确 Slice 06 不包含 AutomationDraft、执行、CI/CD、RAG runtime、MCP runtime、RBAC 或多用户权限。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 1：Add Requirement Review models and migration。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_prompt_skill_models.py -q
git diff --check
```

验证结果：

- Prompt/Skill model smoke：`5 passed in 0.34s`

修改文件：

- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 1：Add Requirement Review models and migration。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/db/test_requirement_review_models.py -q`。

风险提醒：

- Task 1 只做 Requirement、RequirementReview、RiskItem model/migration/schema/test；不要混入 API、AI worker flow、case generation 或 frontend。

## 2026-06-29 Slice 05 Task 7 Prompt/Skill Frontend Shell 完成

本轮完成：

- 完成 Slice 05 Task 7：新增 Prompt/Skill Center read-only frontend shell。
- 新增 frontend API client：加载 `/api/prompt-versions` 和 `/api/skill-versions`。
- 新增 Pinia store：跟踪 prompts、skills、loading、error 和基础计数。
- 新增 route `/prompt-skill`，并将侧边栏 `Prompt / Skill 中心` 标记为就绪。
- 页面展示 PromptVersion / SkillVersion 数量、active 计数、适用 Agent、hash、状态、schema required 字段、quality gates 和 tool permissions。
- 未加入 prompt editing、marketplace、真实 provider、RAG 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 06 Task 0：Create Slice 06 task plan。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/prompt-skill/PromptSkillCenterView.spec.ts
npm --prefix frontend run test -- --run
git diff --check
```

验证结果：

- Prompt/Skill Center focused spec：`1 passed`
- Frontend full test suite：`5 passed (5 files), 8 passed (8 tests)`
- `git diff --check` 无输出。

修改文件：

- `frontend/src/api/promptSkill.ts`
- `frontend/src/stores/promptSkill.ts`
- `frontend/src/views/prompt-skill/PromptSkillCenterView.vue`
- `frontend/src/views/prompt-skill/PromptSkillCenterView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `frontend/src/styles/global.css`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 06 Task 0：Create Slice 06 task plan。
- 创建 `docs/implementation/slices/slice-06-requirement-to-case.md` 后，将 `NEXT_AI_TASK.md` 切到 Slice 06 的第一个可执行小任务。

风险提醒：

- Slice 06 尚无独立 task plan 文件；不要直接开始写需求/用例模型，先建立小任务边界。

## 2026-06-29 Slice 05 Task 6 Prompt/Skill API 完成

本轮完成：

- 完成 Slice 05 Task 6：新增 read-only Prompt/Skill registry API。
- 新增 `/api/prompt-versions` 和 `/api/prompt-versions/{id}`。
- 新增 `/api/skill-versions` 和 `/api/skill-versions/{id}`。
- 响应包含 version identity、hash、status、agent/applicable agents、schema/gate metadata 和 content。
- 未添加 create/update/delete endpoint。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 7：Add Prompt/Skill frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_prompt_skill_registry.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_prompt_skill_registry.py backend/app/tests/api/test_ai_tasks.py -q
git diff --check
```

验证结果：

- Prompt/Skill registry API focused test：`5 passed in 0.57s`
- Prompt/Skill registry API + AI Task API regression：`9 passed in 0.67s`

修改文件：

- `backend/app/modules/prompt_skill/router.py`
- `backend/app/modules/prompt_skill/service.py`
- `backend/app/modules/prompt_skill/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_prompt_skill_registry.py`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 7：Add Prompt/Skill frontend shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

风险提醒：

- Task 7 只做 read-only frontend shell，不要加入 prompt editing、marketplace、真实 provider、RAG 或 MCP runtime。

## 2026-06-29 Slice 05 Task 5 Mock Provider Eval Bench 完成

本轮完成：

- 完成 Slice 05 Task 5：新增 deterministic mock-provider eval bench。
- 新增 `EvalSample` 和默认 eval samples，覆盖 requirements、code changes、failed runs、bug history 四类 fixture。
- 新增 eval bench 指标：`schema_valid_rate`、`evidence_complete_rate`、`unsafe_output_rate`、`manual_edit_rate`、`first_run_pass_rate`、`repair_success_rate`。
- Eval bench 使用运行时 Prompt Output Schema 校验 mock provider 输出，并将 schema mismatch 作为指标信号，不作为当前任务阻塞阈值。
- 新增 `docs/fixtures/eval-bench/*.md`，不包含真实 secrets 或 customer data。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 6：Add Prompt/Skill API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_eval_bench.py -q
git diff --check
```

验证结果：

- Eval bench focused test：`3 passed in 0.21s`

修改文件：

- `backend/app/modules/prompt_skill/eval_bench.py`
- `backend/app/modules/prompt_skill/eval_samples.py`
- `backend/app/tests/prompt_skill/test_eval_bench.py`
- `docs/fixtures/eval-bench/requirements.md`
- `docs/fixtures/eval-bench/code-changes.md`
- `docs/fixtures/eval-bench/failed-runs.md`
- `docs/fixtures/eval-bench/bug-history.md`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 6：Add Prompt/Skill API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_prompt_skill_registry.py -q`。

风险提醒：

- 当前 mock provider 输出与部分 Prompt Output Schema 不完全一致；eval bench 会量化该差异，后续可单独任务调整 mock 输出或 prompt schema。
- Task 6 只做 read-only registry API，不要加入 prompt editing、frontend、真实 provider、RAG 或 MCP runtime。

## 2026-06-29 Slice 05 Task 4 Registry Loader 完成

本轮完成：

- 完成 Slice 05 Task 4：新增 built-in Prompt/Skill registry loader。
- Loader 可发现运行时 `prompts/*/v1.md` 和 `skills/*/v1.md` 文件。
- Loader 解析 Prompt 的 Agent、Input Schema、Output Schema，解析 Skill 的 Applies To、Quality Gates、Forbidden Actions、Tool Permissions。
- Loader 使用稳定 `sha256:` 内容 hash，并可 idempotent 创建 PromptVersion / SkillVersion 记录。
- 对已有同名同版本但内容不同的 active record，loader 抛出 `RegistryContentConflict`，不覆盖已发布内容。
- 新增 `backend/app/modules/prompt_skill/service.py` 包装 seed 入口，供后续 API/启动流程复用。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 5：Add mock-provider eval bench。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_registry_loader.py -q
git diff --check
```

验证结果：

- Registry loader focused test：`4 passed in 0.31s`

修改文件：

- `backend/app/modules/prompt_skill/registry_loader.py`
- `backend/app/modules/prompt_skill/service.py`
- `backend/app/tests/prompt_skill/test_registry_loader.py`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 5：Add mock-provider eval bench。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_eval_bench.py -q`。

风险提醒：

- Task 5 只做 deterministic eval bench 和 fixture，不要引入真实 provider、API、frontend、RAG、MCP runtime 或公开 leaderboard。

## 2026-06-29 Slice 05 Task 3 Built-In Skill Files 完成

本轮完成：

- 完成 Slice 05 Task 3：新增 9 个内置 Skill v1 markdown 文件。
- Skill 文件从 `docs/fixtures/prompt-skill-seeds/skills/` 落位到运行时 `skills/` 目录。
- 新增 `backend/app/tests/prompt_skill/test_skill_files.py`，校验文件存在、必需章节、Applies To 映射、Quality Gates 和 Forbidden Actions 非空。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 4：Add registry loader and hash logic。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_skill_files.py -q
git diff --check
```

验证结果：

- Skill file focused test：`3 passed in 0.01s`

修改文件：

- `skills/automation-draft-skill/v1.md`
- `skills/failure-analysis-skill/v1.md`
- `skills/regression-selection-skill/v1.md`
- `skills/report-generation-skill/v1.md`
- `skills/requirement-review-skill/v1.md`
- `skills/test-case-generation-skill/v1.md`
- `skills/testcase-review-skill/v1.md`
- `skills/tool-execution-skill/v1.md`
- `skills/unit-test-generation-skill/v1.md`
- `backend/app/tests/prompt_skill/test_skill_files.py`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 4：Add registry loader and hash logic。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_registry_loader.py -q`。

风险提醒：

- Task 4 只添加 registry loader/service 和 focused test，不要混入 API、frontend、RAG、MCP runtime 或 prompt/skill 内容改写。

## 2026-06-29 Slice 05 Task 2 Built-In Prompt Files 完成

本轮完成：

- 完成 Slice 05 Task 2：新增 11 个内置 Prompt v1 markdown 文件。
- Prompt 文件从 `docs/fixtures/prompt-skill-seeds/prompts/` 落位到运行时 `prompts/` 目录。
- 新增 `backend/app/tests/prompt_skill/test_prompt_files.py`，校验文件存在、必需章节、Agent 映射、Input/Output Schema JSON 解析、JSON-only 指令和 Failure Output。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 3：Add built-in skill files。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_prompt_files.py -q
git diff --check
git diff --name-only
```

验证结果：

- Prompt file focused test：`4 passed in 0.01s`
- `git diff --check` 无输出。

修改文件：

- `prompts/automation_draft_generation/v1.md`
- `prompts/case_generation/v1.md`
- `prompts/case_review/v1.md`
- `prompts/cicd_change_analysis/v1.md`
- `prompts/failure_analysis/v1.md`
- `prompts/regression_selection/v1.md`
- `prompts/report_generation/v1.md`
- `prompts/requirement_review/v1.md`
- `prompts/risk_matrix/v1.md`
- `prompts/tool_execution/v1.md`
- `prompts/unit_test_generation/v1.md`
- `backend/app/tests/prompt_skill/test_prompt_files.py`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 3：Add built-in skill files。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_skill_files.py -q`。

风险提醒：

- Task 3 只添加 skill markdown 和对应 focused test，不要混入 registry loader、API、frontend、RAG 或 MCP runtime。

## 2026-06-29 Slice 04 Task 1 AI Runtime Models 完成

本轮完成：

- 完成 Slice 04 Task 1：新增 `AITask`、`Artifact`、`LLMCallLog` ORM models。
- 新增 AI Runtime Pydantic read schemas，并补齐 `created_at`、`updated_at`、`created_by`、`updated_by` 基字段。
- 新增 Alembic migration：`backend/alembic/versions/20260629_0002_ai_runtime_core.py`。
- `AITask.context_artifact_ids` 在 PostgreSQL 上使用 `UUID[]`，在 SQLite 测试路径使用 JSON 兼容存储，Python 层返回 `list[uuid.UUID]`。
- AI Runtime JSON dict 字段使用 `MutableDict`，避免 worker/provider 后续原地更新 `output_json`、`metadata_json` 等字段时静默丢失。
- PromptVersion / SkillVersion 仍按 Task 非目标不建表、不建 relationship、不加 FK；本任务仅保留 `prompt_version_id` 和 `skill_version_id` UUID 字段。
- Artifact 可表达 V1 ContextArtifact：`owner_entity_type=Project`、`owner_entity_id=project_id`、`artifact_type=context_markdown`、`metadata_json` 包含 `title/source_ref/safe_to_show/redaction_applied/allowed_for_prompt`。
- 额外新增 `backend/app/modules/ai_runtime/__init__.py` 作为包入口；这是 `NEXT_AI_TASK.md` expected files 外的必要 Python 包结构文件。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 2：Add Artifact store service。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py backend/app/tests/db/test_ai_runtime_models.py -q
git diff --check
```

验证结果：

- AI Runtime DB focused test：`6 passed in 0.40s`
- Project Core + AI Runtime DB regression：`10 passed in 0.49s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/ai_runtime/__init__.py`
- `backend/app/modules/ai_runtime/models.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/alembic/versions/20260629_0002_ai_runtime_core.py`
- `backend/app/tests/db/test_ai_runtime_models.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 2 Artifact store 尚未实现。
- 迁移层为 AI Runtime 三张表增加了 PostgreSQL `gen_random_uuid()` 和默认用户 UUID server default；早期 `20260626_0001_project_core.py` 仍保持原状，未在本任务中回改历史迁移。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 2：Add Artifact store service。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/artifacts/test_artifact_store.py -q`。

风险提醒：

- Artifact 文件写入、sha256 计算、atomic rename、path traversal 防护是 Task 2；不要在 Task 1 commit 中混入文件系统 store 逻辑。
- ContextArtifact API、redaction、mock provider、worker 状态流转和 AI Task API 仍属后续任务。

## 2026-06-29 Slice 04 Task 2 Artifact Store 完成

本轮完成：

- 完成 Slice 04 Task 2：新增本地 `LocalArtifactStore`。
- Artifact 写入使用同目录临时文件，并通过 `os.replace` 原子替换目标文件。
- 写入结果返回 artifact-relative `file_path`、`size_bytes` 和 `sha256`。
- 读取和写入均拒绝绝对路径、`..` 路径段、root escape 和 root 内 symlink escape。
- 写入失败时清理临时文件，不留下半成品目标文件。
- 新增 `ArtifactWriteResultRead` schema，供后续 API/service 复用。
- 修复 `.gitignore`：将 `artifacts/` 改为 `/artifacts/`，避免误忽略 `backend/app/tests/artifacts/` 测试目录。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 3：Add ContextArtifact API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/artifacts/test_artifact_store.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py -q
git diff --check
```

验证结果：

- Artifact store focused test：`10 passed in 0.11s`
- AI Runtime DB + Artifact store regression：`16 passed in 0.53s`
- `git diff --check` 无输出。

修改文件：

- `.gitignore`
- `backend/app/modules/ai_runtime/artifact_store.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/app/tests/artifacts/test_artifact_store.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 3 ContextArtifact API 尚未实现。
- Artifact store 本任务不做 DB 写入；Artifact row 创建属于 Task 3 service/API。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 3：Add ContextArtifact API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_context_artifacts.py -q`。

风险提醒：

- ContextArtifact 写入前的 secret scan / redaction 策略需要在 Task 3 API/service 中最小实现或明确保守拒绝；不要引入 RAG、vector index 或隐式上下文注入。

## 2026-06-29 Slice 04 Task 3 ContextArtifact API 完成

本轮完成：

- 完成 Slice 04 Task 3：新增 ContextArtifact create/list API。
- `POST /api/context-artifacts` 使用本地 Artifact store 写入内容，并创建 Artifact DB row。
- ContextArtifact Artifact row 使用 `owner_entity_type=Project`、`owner_entity_id=project_id`，客户端不能覆盖 owner fields。
- ContextArtifact `metadata_json` 同时包含 Artifact 基础 metadata：`created_by_component/source_entity_type/source_entity_id/description`，以及 ContextArtifact 专属字段：`title/source_ref/safe_to_show/redaction_applied/redaction_report_artifact_id/allowed_for_prompt`。
- MIME 校验按 `artifact_type` 绑定组合，拒绝 mismatched type/MIME。
- 内容大小限制为 V1 单个 ContextArtifact 1 MiB。
- 写入前对 `title`、`source_ref` 和 `content` 做基础 secret scan；发现高风险内容时返回 `CONTEXT_ARTIFACT_SECRET_DETECTED` 并拒绝保存。
- `GET /api/projects/{project_id}/context-artifacts` 只返回当前 project 的 project-level context artifacts。
- Create 响应不返回原始 content，避免绕过后续展示前 redaction view。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 4：Add Mock LLM Provider。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_context_artifacts.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py backend/app/tests/api/test_context_artifacts.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py -q
git diff --check
```

验证结果：

- ContextArtifact API focused test：`9 passed in 0.71s`
- Project API + ContextArtifact API regression：`16 passed in 0.80s`
- AI Runtime DB + Artifact store + ContextArtifact regression：`25 passed in 0.79s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/main.py`
- `backend/app/modules/ai_runtime/router.py`
- `backend/app/modules/ai_runtime/service.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/app/tests/api/test_context_artifacts.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 4 Mock LLM Provider 尚未实现。
- ContextArtifact API 当前只做保守拒绝式 secret scan，不做脱敏保存版本；后续若要 redaction artifact，需要单独任务补 `redaction_report.json`。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 4：Add Mock LLM Provider。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_mock_provider.py -q`。

风险提醒：

- 不要让 Mock Provider 调外部网络。
- 不要在 Task 4 顺手实现 worker handler、AI Task API 或业务 agent endpoint。

## 2026-06-29 Slice 04 Task 4 Mock LLM Provider 完成

本轮完成：

- 完成 Slice 04 Task 4：新增 deterministic Mock LLM Provider。
- 新增 provider base dataclass：`LLMProviderRequest`、`LLMProviderResponse`、`ProviderArtifactPayload`、provider error/timeout exceptions。
- Mock Provider 支持 `success`、`provider_error`、`schema_invalid`、`timeout` 四种测试模式。
- `mock-requirement-review` 输出六维评分、issues、clarification questions、risk items，并回显 `used_context_artifact_ids`。
- `mock-case-generator` 输出 Golden Path 候选用例基本结构。
- 按 mock provider contract 补齐 `mock-automation-draft`、`mock-cicd-analysis`、`mock-unit-test-generator`、`mock-failure-analysis`、`mock-report-generator` 的 deterministic 输出形状。
- Mock Provider 不调用网络、不读取 secrets、不引入真实 provider。
- 成功响应生成内存 artifact payload：`input.json`、`raw_output.json`、`parsed_output.json`、`schema_validation.json`；提供 context 时额外生成 `context_manifest.json`，内容包含 `context_artifact_ids` 和完整 `context_manifest`。
- 额外新增 `backend/app/modules/ai_runtime/providers/__init__.py` 作为包入口；这是 `NEXT_AI_TASK.md` expected files 外的必要 Python 包结构文件。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 5：Add AI Task Enqueue And Worker Handler。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_mock_provider.py -q
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/artifacts/test_artifact_store.py -q
git diff --check
```

验证结果：

- Mock Provider focused test：`11 passed in 0.01s`
- Mock Provider + ContextArtifact + Artifact store regression：`30 passed in 0.71s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/ai_runtime/providers/__init__.py`
- `backend/app/modules/ai_runtime/providers/base.py`
- `backend/app/modules/ai_runtime/providers/mock_provider.py`
- `backend/app/tests/ai_runtime/test_mock_provider.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 5 AI Task worker handler 尚未实现。
- 当前 provider 只产出内存 artifact payload；真正写 Artifact rows 由 Task 5 worker handler 完成。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 5：Add AI Task Enqueue And Worker Handler。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py -q`。

风险提醒：

- Task 5 可以使用 fake queue，不要引入真实 Redis worker CLI，除非当前项目已有稳定 Redis worker 入口。
- Worker 应记录 LLMCallLog 和 Artifact rows，但不要顺手实现 AI Task API 或前端。

## 2026-06-29 Slice 04 Task 5 AI Task Worker 完成

本轮完成：

- 完成 Slice 04 Task 5：新增 fake AI queue 和 AI task worker handler。
- `enqueue_ai_task()` 将 `created` 的 AITask 转为 `pending`，并推入 `FakeAIQueue`。
- Worker 将 `pending` 任务先持久化为 `running`，再调用 Mock Provider。
- 成功路径写入 `input.json`、`context_manifest.json`、`raw_output.json`、`parsed_output.json`、`schema_validation.json` Artifact rows，并创建 LLMCallLog。
- `schema_invalid` 路径将 AITask 标为 `failed`，保存 raw/schema/error artifacts，并记录 LLMCallLog `schema_invalid`。
- `provider_error` 和 `timeout` 路径保留 input/context artifacts，写 `error.json`，将 AITask 标为 `failed`，并记录 LLMCallLog `failed` 或 `timeout`。
- `cancelled` 任务不会被 worker 执行。
- Artifact 写入失败会将 AITask 标为 `failed` 并写入 `ARTIFACT_WRITE_FAILED` error_json。
- 额外新增 `backend/app/workers/__init__.py` 和 `backend/app/workers/handlers/__init__.py` 作为包入口；这是 `NEXT_AI_TASK.md` expected files 外的必要 Python 包结构文件。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 6：Add AI Task API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py -q
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py backend/app/tests/ai_runtime/test_mock_provider.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
git diff --check
```

验证结果：

- AI Task Worker focused test：`9 passed in 0.56s`
- Worker + Mock Provider regression：`20 passed in 0.59s`
- AI Runtime related regression：`45 passed in 1.03s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/ai_runtime/service.py`
- `backend/app/workers/__init__.py`
- `backend/app/workers/enqueue.py`
- `backend/app/workers/handlers/__init__.py`
- `backend/app/workers/handlers/ai_task_handler.py`
- `backend/app/tests/ai_runtime/test_ai_task_worker.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 6 AI Task API 尚未实现。
- Worker 当前使用 fake queue；没有引入真实 Redis worker CLI。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 6：Add AI Task API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_ai_tasks.py -q`。

风险提醒：

- AI Task API 只返回 artifact metadata 和路径，不要暴露 raw LLM output 内容。
- 不要在 Task 6 顺手实现 requirement review/case generation endpoint 或前端。

## 2026-06-29 Slice 04 Task 6 AI Task API 完成

本轮完成：

- 完成 Slice 04 Task 6：新增 AI Task status/detail API。
- 新增 `GET /api/ai-tasks/{ai_task_id}`，返回 task status、Agent、Prompt/Skill id、provider/model、token usage、context artifact ids、used context ids、context manifest artifact id、artifact summaries 和 LLM call logs。
- 新增 `GET /api/projects/{project_id}/ai-tasks`，按 project 返回最近 AI tasks 的最小列表。
- API 只返回 artifact metadata、safe flags、sha256 和路径，不返回 artifact 原始 content。
- `used_context_artifact_ids` 优先来自 task output，缺省时回退到 `AITask.context_artifact_ids`，保证前端能看见上下文使用。
- 按评审修复 worker artifact 安全 metadata：`raw_llm_output` 和 `error_json` 默认 `safe_to_show=false`，避免 API 把原始 LLM 输出标成可直接展示。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Task 7：Add AI task frontend status shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py::test_worker_runs_pending_task_and_records_artifacts_and_llm_log -q
backend/.venv/bin/python -m pytest backend/app/tests/ai_runtime/test_ai_task_worker.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ai_tasks.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ai_tasks.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_projects.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
git diff --check
```

验证结果：

- Worker raw artifact metadata regression：`1 passed in 0.35s`
- AI Task Worker focused test：`9 passed in 0.47s`
- AI Task API focused test：`4 passed in 0.57s`
- Project API + ContextArtifact API + AI Task API regression：`20 passed in 0.79s`
- AI Runtime related regression：`49 passed in 0.94s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/ai_runtime/router.py`
- `backend/app/modules/ai_runtime/service.py`
- `backend/app/modules/ai_runtime/schemas.py`
- `backend/app/tests/api/test_ai_tasks.py`
- `backend/app/tests/ai_runtime/test_ai_task_worker.py`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 7 AI Workbench frontend status shell 尚未实现。
- 当前 AI Task API 不提供 artifact download/read endpoint；前端只能展示 metadata 和 file path。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 7：Add AI task frontend status shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

风险提醒：

- Slice 02.5 Frontend Foundation 已完成，可以进入 Task 7。
- 前端必须保持中文优先、浅色 Arco 工作台风格，只做最近 AI 任务列表和详情壳。
- 不要在 Task 7 展示 raw LLM output content；只展示 artifact metadata、safe flags 和路径。
- 不要在 Task 7 顺手实现完整 requirement review/case generation UI、图表大屏、RAG runtime 或 MCP runtime。

## 2026-06-29 Slice 04 Task 7 AI Workbench 前端状态壳完成

本轮完成：

- 完成 Slice 04 Task 7：新增 AI Workbench frontend status shell。
- 新增 `frontend/src/api/aiTasks.ts`，按后端 schema 定义 AI task list/detail、artifact summary 和 LLM call log 类型，并封装 `GET /api/projects/{project_id}/ai-tasks` 与 `GET /api/ai-tasks/{id}`。
- 新增 `frontend/src/stores/aiTasks.ts` Pinia store，维护默认单用户 project、recent tasks、selected task、loading/error 状态和简要指标。
- 更新 `AI 工作台` 页面：保留后端健康 smoke，新增最近 AI 任务列表、任务详情、Prompt/Skill id、provider/model、token usage、上下文工件、已使用上下文、工件摘要和大模型调用日志。
- 工件区域只展示 artifact metadata、路径、MIME、大小、sha256、`safe_to_show` 和 `redaction_applied` 状态；不拉取或展示 raw LLM output content。
- 大模型调用日志展示 provider/model/status、response artifact id、latency 和 token usage，保留证据追溯入口。
- 页面继续使用 Vue 3 + Arco Design Vue，中文优先，浅色工作台布局，不新增完整需求评审 UI、case generation UI、RAG runtime 或 MCP runtime。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 04 Completion Gate。

本轮验证：

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run test -- --run
npm --prefix frontend run build
```

验证结果：

- AI Workbench focused test：`3 passed`
- Frontend Vitest suite：`7 passed`
- Frontend build：通过；仍有既有 Arco bundle size warning。

修改文件：

- `frontend/src/api/aiTasks.ts`
- `frontend/src/stores/aiTasks.ts`
- `frontend/src/views/ai-workbench/AiWorkbenchView.vue`
- `frontend/src/views/ai-workbench/AiWorkbenchView.spec.ts`
- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

未完成问题：

- Slice 04 completion gate 尚未执行。
- AI Workbench 当前只提供状态壳和 metadata 详情，不提供 artifact download/read、任务创建入口或完整业务评审动作。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Completion Gate。
- 完成后将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 1：Add PromptVersion and SkillVersion models。

风险提醒：

- Completion Gate 应跑 backend AI runtime regression、frontend tests、frontend build 和 `git diff --check`。
- 不要在 completion gate 顺手实现 Prompt/Skill models；先完成 Slice 04 总验收和 handoff。

## 2026-06-29 Slice 04 Completion Gate 完成

本轮完成：

- 完成 Slice 04 AI Runtime Core completion gate。
- `docs/implementation/slices/slice-04-ai-runtime-core.md` 中 Task 1-7 均为 `done`，并记录 commit：`11bb6cc`、`5b17d26`、`d7570ba`、`693e171`、`63efbc6`、`f006cb2`、`31ce363`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 1：Add PromptVersion and SkillVersion models。
- Slice 04 范围保持干净：未引入真实 provider、RAG/vector runtime、MCP runtime、requirement review endpoint 或 case generation endpoint。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/artifacts/test_artifact_store.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_ai_tasks.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_ai_task_worker.py -q
npm --prefix frontend run test -- --run
npm --prefix frontend run build
git diff --check
```

验证结果：

- AI Runtime backend regression：`49 passed in 1.58s`
- Frontend Vitest suite：`7 passed`
- Frontend build：通过；仍有既有 Arco bundle size warning。
- `git diff --check` 无输出。

修改文件：

- `docs/implementation/slices/slice-04-ai-runtime-core.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

未完成问题：

- Slice 05 Prompt And Skill Registry 尚未开始。
- AI Workbench 仍只展示 AI task/status/evidence metadata，不提供 artifact download/read 或任务创建入口。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 1：Add PromptVersion and SkillVersion models。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/db/test_prompt_skill_models.py -q`。

风险提醒：

- Slice 05 Task 1 只做 PromptVersion/SkillVersion models、schemas、migration 和 DB test。
- 不要在 Task 1 顺手添加 prompt markdown、skill markdown、registry loader、API、frontend、真实 provider、RAG/vector runtime 或 MCP runtime。

## 2026-06-29 Slice 05 Task 1 Prompt/Skill Models 完成

本轮完成：

- 完成 Slice 05 Task 1：新增 `PromptVersion` 和 `SkillVersion` models。
- 新增 `backend/app/modules/prompt_skill/models.py`，包含 `prompt_versions` 和 `skill_versions` 表定义。
- 新增 `backend/app/modules/prompt_skill/schemas.py`，提供 `PromptVersionRead` 和 `SkillVersionRead`。
- 新增 Alembic migration：`backend/alembic/versions/20260629_0003_prompt_skill_registry.py`。
- PromptVersion 字段覆盖：`name/version/hash/agent_name/content/input_schema_json/output_schema_json/status` 和通用 timestamp/user 字段。
- SkillVersion 字段覆盖：`name/version/hash/applicable_agents/content/quality_gates_json/forbidden_actions_json/tool_permissions_json/status` 和通用 timestamp/user 字段。
- 两张表均增加 `name + version` 唯一约束。
- JSON dict/list 字段使用 SQLAlchemy mutable 类型，支持 in-place 更新被持久化。
- `applicable_agents` 在 PostgreSQL 使用 `text[]`，SQLite 测试路径使用 JSON 兼容存储。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 05 Task 2：Add built-in prompt files。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_prompt_skill_models.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py backend/app/tests/db/test_ai_runtime_models.py backend/app/tests/db/test_prompt_skill_models.py -q
git diff --check
```

验证结果：

- Prompt/Skill model focused test：`5 passed in 0.36s`
- Project Core + AI Runtime + Prompt/Skill DB regression：`15 passed in 0.38s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/prompt_skill/__init__.py`
- `backend/app/modules/prompt_skill/models.py`
- `backend/app/modules/prompt_skill/schemas.py`
- `backend/alembic/versions/20260629_0003_prompt_skill_registry.py`
- `backend/app/tests/db/test_prompt_skill_models.py`
- `docs/implementation/slices/slice-05-prompt-skill-registry.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

未完成问题：

- Built-in prompt markdown files 尚未添加。
- Built-in skill markdown files、registry loader、Prompt/Skill API、Prompt/Skill frontend shell 尚未开始。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 05 Task 2：Add built-in prompt files。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/prompt_skill/test_prompt_files.py -q`。

风险提醒：

- Task 2 只添加 prompt markdown 和 prompt file tests；不要顺手实现 skill files、registry loader、API 或 frontend。
- Prompt 输出必须 JSON-only，不允许 markdown fences 作为模型主输出。

## 当前用户最新明确要求

- Chtest 项目必须放在 `/Users/yanchen/VscodeProject/Chtest`。
- 第一版就做单用户模式。
- 第一版直接使用 PostgreSQL + Redis。
- 不要一次性演示，要真实能大幅提高测试效率的 AI 工具。
- 最新定位已校准为：面向个人测试工程师、自动化测试工程师的 AI 测试设计与自动化落地工作台。
- 长期方向是小团队 AI 测试工作台 + Agent / Skill / MCP 测试工具生态。
- V1 三条最小闭环：需求到用例、用例到自动化、CI/CD 质量中心中的本地 diff 到质量门禁和证据报告。
- 用户可见 CI/CD 支线页面统一为 `CI/CD 质量中心`；当前契约名使用 `CICDRun`、`CICDChangedFile`、`QualityGateDecision`、`UnitTestPatch`。
- 新增用户可见页面 `RAG 知识库`；RAG 功能只保留 ContextArtifact + KnowledgeAdapter surface，后续外部搭建后接入。
- MCP / Skill / Prompt / Agent 要分层设计并贯穿各流程。
- 新代码 push/PR/diff 后生成单测、执行回归，并有独立页面查看 Git 情况。
- 增加 Web 自动化能力，但 V1 只做 Playwright 最小闭环；Newman/JMeter 后置。
- 文档必须足够详细，方便后续 AI 读取后继续完成项目。
- 长期 AI 开发必须遵循 `docs/implementation/04-ai-vibecoding-governance.md`：小步 Task、每步验证、每个完成 Task 提交、可回滚；Slice 完成和重大上下文变化时更新 memory。
- 当前前端设计必须中文优先；页面标题、导航、按钮、表头、空状态和状态文案都用中文。
- 当前前端最终设计采用 A 方案浅色系、Vue 3 + Arco Design Vue、工作台式信息密度，详见 `docs/product/08-frontend-design-spec.md`。
- `ContextArtifact`、`AITask`、`LLMCallLog`、`Artifact` 的用户可见名称分别写成 `上下文工件`、`AI 任务`、`大模型调用日志`、`工件`。

## 当前本地状态

- 本地目录：`/Users/yanchen/VscodeProject/Chtest`
- memory 目录：`/Users/yanchen/VscodeProject/Chtest/memory`
- WHartTest：`/Users/yanchen/VscodeProject/Chtest/参考框架/WHartTest`，参考提交 `927bff2`
- MeterSphere：`/Users/yanchen/VscodeProject/Chtest/参考框架/metersphere`，参考提交 `5dc6df5`
- 参考框架目录应保留本地，但默认不纳入 Chtest Git 提交记录。
- Chtest 已初始化为独立 Git 仓库。
- 当前工作分支：`codex/cicd-quality-docs`。
- Git remote `origin` 已设置为 `https://github.com/2696437448-cmyk/Chtest.git`。
- 当前最新已 push commit：`1fb52c1 docs(process): tighten vibecoding readiness docs`。
- 本轮一致性修复开始前的最新本地提交：`6ed134a docs(memory): hand off slice one worker task`。
- 当前最新本地提交以 `git log -1 --oneline` 为准。
- 当前未 push 的本地提交包括 Slice 1 Tasks 1-3 和后续 handoff 更新。
- GitHub 提示仓库已迁移到 `https://github.com/YanChen0111/Chtest.git`，但当前 origin 仍指向旧地址。
- 本轮 ContextArtifact 文档契约修复作为本地提交保存；push 仍需用户明确要求。
- Slice 02.5 Task 1 已完成并提交：`daf5b7c feat(frontend): scaffold vue workbench app`。
- Slice 02.5 Task 2 已完成并提交：`2ec1c7c feat(frontend): add workbench shell`。
- Slice 02.5 Task 3 已完成并提交：`6526a2b build(frontend): wire vite dev container`。
- Slice 02.5 Task 4 已完成并提交：`de1f5fd feat(frontend): add health probe smoke`。
- Slice 02.5 Frontend Foundation 已完成。
- Slice 03 Task 1 已完成：Add Project Core models and migration。
- 当前 `NEXT_AI_TASK.md` 已切换到 Slice 03 Task 2：Add Project CRUD API。
- 当前前端 shell 已有中文主导航、AI 工作台首页、Pinia、Vue Router、Arco Design Vue、`api/client.ts` 和 `/health` smoke。
- 当前前端 build 会给出 bundle 偏大的 warning，来源于 Arco baseline；不是阻塞问题，但后续可以在稳定后做按需优化。
- 2026-06-26 已固化最终前端设计文档：`docs/product/08-frontend-design-spec.md` 和 `docs/superpowers/specs/2026-06-26-chtest-final-frontend-design.md`。
- 后续实现前端页面时优先读取 `docs/product/08-frontend-design-spec.md`、`docs/product/03-user-journey-and-page-prd.md` 和 `docs/product/06-frontend-ui-guidelines.md`。

## 2026-06-26 Slice 03 Task 1 后端迁移完成

本轮完成：

- 新增后端 Python 依赖入口：`backend/pyproject.toml`。
- 新增 SQLAlchemy 基础包和 Project Core 模型：`Workspace`、`User`、`Project`、`Module`、`Repository`、`Environment`、`TestCommand`。
- 新增 Alembic migration：`backend/alembic/versions/20260626_0001_project_core.py`。
- 新增聚焦 DB 测试：`backend/app/tests/db/test_project_core_models.py`。
- 将 WHartTest 参考源码映射写入 `docs/reference/01-open-source-migration-map.md`，明确只吸收项目聚合根、模块树、环境变量、测试命令入口，不迁移 RBAC、凭据、远程执行器和完整任务编排。
- 更新 `docs/implementation/slices/slice-03-project-core.md` 和 `NEXT_AI_TASK.md`。

本轮验证：

```bash
UV_CACHE_DIR=.tmp/uv-cache uv --project backend run pytest backend/app/tests/db/test_project_core_models.py -q
```

验证结果：

- `4 passed in 0.32s`

下一步：

- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 2：Add Project CRUD API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q`。
- 不要在 Task 2 顺手实现 repository path validation、environment mutation API、TestCommand validation、AI task models、ToolInvocation 或多用户权限。

## 2026-06-29 Slice 03 Task 2 Project API 完成

本轮完成：

- 完成 Slice 03 Task 2：新增 Project create/read/update API。
- 新增 Project Settings bootstrap API：返回 project、modules、repositories、environments、test_commands 和空的 tool_definitions。
- 新增最小 FastAPI app 入口和 Project router。
- 扩展 Project schema 和 service，复用 Task 1 的 SQLAlchemy Project Core models。
- 新增聚焦 API 测试：`backend/app/tests/api/test_projects.py`。
- 根据只读 code review 修复两个 API 契约缺口：422 validation error envelope 和重复项目名 409 envelope。
- 因当前 `.venv` 未安装 `httpx2`，测试使用文件内最小 ASGI client 直接调用 FastAPI app，不新增依赖。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 03 Task 3：Add Module tree API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py -q
git diff --check
```

验证结果：

- Project API focused test：`7 passed in 0.53s`
- Project Core DB regression：`4 passed in 0.35s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/main.py`
- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/app/tests/api/test_projects.py`
- `docs/implementation/slices/slice-03-project-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 3 尚未实现 Module tree API。
- 当前 Project API 只覆盖 Project 自身和 settings bootstrap；Repository、Environment、TestCommand 的 mutation 和 validation 留给 Slice 03 Task 4/5。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 3：Add Module tree API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_modules.py -q`。

风险提醒：

- 当前测试未使用 `fastapi.testclient.TestClient`，因为 Starlette 版本要求额外安装 `httpx2`；后续若统一 API 测试 fixture，可选择补依赖或保留轻量 ASGI client。

## 2026-06-29 Slice 03 Task 3 Module API 完成

本轮完成：

- 完成 Slice 03 Task 3：新增 Module create/list/update API。
- Root module 自动派生 `level=1` 和 `path=/{name}`。
- Child module 校验 parent 属于同一 project，并自动派生 `level`、`parent_id` 和层级 path。
- 强制五级模块树限制。
- 同一 project + 同一 parent 下 module name 冲突返回 `MODULE_ALREADY_EXISTS`。
- 根据只读 code review 修复父模块重命名后 descendant path 陈旧问题，新增回归测试覆盖。
- 新增聚焦 API 测试：`backend/app/tests/api/test_modules.py`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 03 Task 4：Add Repository and Environment API。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_modules.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py -q
git diff --check
```

验证结果：

- Module API focused test：`9 passed in 0.61s`
- Project API regression：`7 passed in 0.48s`
- Project Core DB regression：`4 passed in 0.32s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/app/tests/api/test_modules.py`
- `docs/implementation/slices/slice-03-project-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 4 尚未实现 Repository and Environment API。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 4：Add Repository and Environment API。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_repository_environment.py -q`。

风险提醒：

- Repository path allowlist 属于 Task 4，不要在 Task 3 里补。

## 2026-06-29 Slice 03 Task 4 Repository/Environment API 完成

本轮完成：

- 完成 Slice 03 Task 4：新增 Repository create/list/update API。
- 新增 Environment create/list/update API。
- Repository `local_path` 会校验路径存在，并且必须位于 `CHTEST_REPOSITORY_ALLOWLIST_ROOTS` 配置的 allowlist 根目录下。
- Repository 路径保存为 resolve 后的绝对路径。
- Environment 拒绝 secret-like 明文变量值，要求使用 `ref:` 引用形式。
- 根据只读 code review 补充 raw secret 拒绝测试和实现。
- 新增聚焦 API 测试：`backend/app/tests/api/test_repository_environment.py`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 03 Task 5：Add TestCommand API and validation。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_repository_environment.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_modules.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py -q
git diff --check
```

验证结果：

- Repository/Environment API focused test：`10 passed in 0.69s`
- Module API regression：`9 passed in 0.70s`
- Project API regression：`7 passed in 0.61s`
- Project Core DB regression：`4 passed in 0.40s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/app/tests/api/test_repository_environment.py`
- `docs/implementation/slices/slice-03-project-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 5 尚未实现 TestCommand API and validation。
- Repository create/update 不运行 git 命令；`.git` 校验和 Git workflow 细化如需启用，应在后续明确任务中补充。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 5：Add TestCommand API and validation。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_commands.py -q`。

风险提醒：

- TestCommand allowlist、working_directory 校验和禁止 shell operator 是 Task 5，不要在 Task 4 commit 中混入命令执行。

## 2026-06-29 Slice 03 Task 5 TestCommand API 完成

本轮完成：

- 完成 Slice 03 Task 5：新增 TestCommand create/list/update/validate API。
- TestCommand command_type 支持 V1 安全 allowlist：`pytest`、`npm test` / `npm run test`、`npx playwright test`。
- 禁止 shell operator 和多命令拼接，包括 `&&`、`||`、`;`、`|`、单 `&`、重定向、反引号、`$()` 和换行。
- `working_directory` 必须存在且位于所选 Repository `local_path` 下。
- `environment_id` 必须为空或属于同一 project。
- Validate endpoint 只做静态校验，不执行命令。
- 根据只读 code review 修复单 `&`/换行绕过、Playwright 前缀边界过松、跨项目 environment_id 三个问题。
- 新增聚焦 API 测试：`backend/app/tests/api/test_test_commands.py`。
- 已将 `NEXT_AI_TASK.md` 切换到 Slice 03 Task 6：Add Project Settings frontend shell。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_commands.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_repository_environment.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_modules.py -q
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py -q
backend/.venv/bin/python -m pytest backend/app/tests/db/test_project_core_models.py -q
git diff --check
```

验证结果：

- TestCommand API focused test：`9 passed in 1.10s`
- Repository/Environment API regression：`10 passed in 0.86s`
- Module API regression：`9 passed in 0.91s`
- Project API regression：`7 passed in 0.69s`
- Project Core DB regression：`4 passed in 0.45s`
- `git diff --check` 无输出。

修改文件：

- `backend/app/modules/projects/router.py`
- `backend/app/modules/projects/schemas.py`
- `backend/app/modules/projects/service.py`
- `backend/app/tests/api/test_test_commands.py`
- `docs/implementation/slices/slice-03-project-core.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

未完成问题：

- Task 6 尚未实现 Project Settings frontend shell。
- Slice 03 completion gate 尚未执行。

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 6：Add Project Settings frontend shell。
- 验证命令：`npm --prefix frontend run test -- --run`。

风险提醒：

- Task 5 没有执行命令、没有 git 命令执行、没有 ToolInvocation；后续 runner slice 必须继续复用这些安全校验，而不是接受任意 shell。

## 2026-06-29 Slice 03 Task 6 Project Settings 前端壳完成

本轮完成：

- 完成 Slice 03 Task 6：新增 Project Settings frontend shell。
- 新增 `frontend/src/api/projects.ts` typed API helper，读取 `/api/projects/{id}/settings`。
- 扩展 `frontend/src/api/client.ts` 支持 JSON 响应。
- 新增 `frontend/src/stores/projectSettings.ts`，管理项目设置加载、错误和数据状态。
- 新增 `frontend/src/views/settings/ProjectSettingsView.vue`，以中文工作台页面展示项目概览、模块树、仓库、环境变量和测试命令。
- 接入 Vue Router：`/settings/project` / route name `project-settings`。
- 导航中的 `Git 质量中心` 已改为 `CI/CD 质量中心`，设置入口指向项目设置页。
- 更新 WorkbenchLayout 让顶部标题优先使用 route meta title。
- 根据只读 code review 修复侧栏“设置”仍 fallback 到 AI 工作台的问题，并补充导航链接断言。
- `client.ts`、`stores/index.ts`、`global.css` 和 `WorkbenchLayout.*` 虽不在原 Expected Files 列表内，但分别是 JSON API 支持、导航接入、页面样式和 route title 行为的必要最小改动。

本轮验证：

```bash
npm --prefix frontend run test -- --run
npm --prefix frontend run build
git diff --check
```

验证结果：

- Frontend test：`4 passed (4), 6 passed (6)`
- Frontend build：通过；仍有既有 Arco bundle size warning。
- `git diff --check` 无输出。

修改文件：

- `frontend/src/api/client.ts`
- `frontend/src/api/projects.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`
- `frontend/src/stores/projectSettings.ts`
- `frontend/src/layouts/WorkbenchLayout.vue`
- `frontend/src/layouts/WorkbenchLayout.spec.ts`
- `frontend/src/styles/global.css`
- `frontend/src/views/settings/ProjectSettingsView.vue`
- `frontend/src/views/settings/ProjectSettingsView.spec.ts`
- `docs/implementation/slices/slice-03-project-core.md`
- `memory/08-session-handoff.md`

未完成问题：

- Slice 03 completion gate 尚未执行。
- 当前前端使用默认 project id 作为 shell smoke；后续需要项目选择/创建流程后再改为真实当前项目上下文。

下次推荐任务：

- 执行 Slice 03 completion gate review。
- 若通过，更新 handoff 到 Slice 04 AI Runtime Core。

风险提醒：

- Project Settings 前端壳只做查看和基础刷新，不实现完整编辑表单、拖拽模块树或命令执行。

## 2026-06-29 Slice 03 Completion Gate 完成

本轮完成：

- Slice 03 Project Core 所有任务已完成并提交。
- `docs/implementation/slices/slice-03-project-core.md` task table 已更新 commit hash。
- `NEXT_AI_TASK.md` 已切换到 Slice 04 Task 1：Add AI Runtime models and migration。
- `memory/07-dev-log.md` 已追加 Slice 03 completion 记录。

本轮验证：

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_projects.py backend/app/tests/api/test_modules.py backend/app/tests/api/test_repository_environment.py backend/app/tests/api/test_test_commands.py backend/app/tests/db/test_project_core_models.py -q
npm --prefix frontend run test -- --run
npm --prefix frontend run build
git diff --check
```

验证结果：

- Backend Slice 03 related tests：`39 passed in 2.61s`
- Frontend test：`4 passed (4), 6 passed (6)`
- Frontend build：通过；仍有既有 Arco bundle size warning。
- `git diff --check` 无输出。

Slice 03 commits：

- `d87036d feat(projects): add project core backend`
- `6c12d64 feat(projects): add project settings api`
- `57e64f4 feat(projects): add module tree api`
- `7c8471f feat(projects): add repository and environment api`
- `47f6724 feat(projects): add test command validation`
- `524b7c7 feat(frontend): add project settings shell`

下次推荐任务：

- 按 `NEXT_AI_TASK.md` 执行 Slice 04 Task 1：Add AI Runtime models and migration。
- 验证命令：`backend/.venv/bin/python -m pytest backend/app/tests/db/test_ai_runtime_models.py -q`。

风险提醒：

- 当前本地分支领先远端多个提交，尚未 push。
- 前端 build 的 Arco chunk size warning 仍是已知非阻塞项。
- Slice 04 不要引入真实 LLM、RAG/vector runtime、PromptVersion/SkillVersion models 或 MCP runtime；Task 1 只做 AITask/Artifact/LLMCallLog 模型和 migration。

## 2026-06-26 前端最终设计文档同步

本轮完成：

- 根据用户确认的 A 方案浅色系，新增最终前端设计规格。
- 将用户可见 CI/CD 支线页面统一为 `CI/CD 质量中心`。
- 将当前契约和 Golden Path 对齐到 `CICDRun`、`CICDChangedFile`、`CICDChangeAnalysisAgent`、`QualityGateDecision`、`/api/cicd/runs` 和 `docs/fixtures/03-golden-cicd-quality.md`。
- 新增 `RAG 知识库` 页面设计和 V1 边界说明。
- 同步产品、架构、实施计划、memory 和入口文档，方便后续 AI coding。

本轮验证：

- 文档变更需以本轮最终 `git diff --check` 和旧命名 grep 审计为准。

修改文件：

- `docs/product/08-frontend-design-spec.md`
- `docs/superpowers/specs/2026-06-26-chtest-final-frontend-design.md`
- `docs/product/*`
- `docs/architecture/*`
- `docs/implementation/*`
- `docs/README.md`
- `START_HERE_FOR_AI.md`
- `NEXT_AI_TASK.md`
- `memory/*`

未完成问题：

- 当前实现任务仍以 `NEXT_AI_TASK.md` 的 Slice 03 Task 1 为准，本轮不进入前端页面实现。

下次推荐任务：

- 继续 Slice 03 Task 1：Add Project Core models and migration。

风险提醒：

- `CI/CD 质量中心` 是 V1 本地 diff 支线，不是云 CI/CD 平台。
- `RAG 知识库` 是 ContextArtifact 和 KnowledgeAdapter surface，不是内置 RAG/vector/rerank 平台。

## 2026-06-23 继续执行更新

本轮完成：

- 根据产品/市场评审结果收紧 vibecoding 执行准备文档。
- 切出工作分支 `codex/chtest-vibecoding-foundation`，避免继续在 `main` 上叠加实现提交。
- 完成 Slice 1 Task 1：初始化 `backend/`、`frontend/`、`worker/`、`deploy/`、`prompts/`、`skills/`、`mcp_tools/`、`artifacts/` 八个顶层目录，并为每个目录加入 `.gitkeep`。
- `artifacts/` 受 `.gitignore` 忽略，已使用 `git add -f artifacts/.gitkeep` 只跟踪占位文件，运行产物仍保持忽略。
- 完成 Slice 1 Task 2：添加 PostgreSQL 和 Redis 的 Docker Compose 基础。
- 完成 Slice 1 Task 3：添加 backend container placeholder。
- 已更新 `NEXT_AI_TASK.md`，当前下一任务为 Slice 1 Task 4：Add worker container placeholder。
- 修复全量文档复审发现的漏改：入口文档仍指向已完成任务、`.env.example` 容器连接串使用本地回环地址、Artifact Docker 路径不一致、裸 Compose 启动命令不匹配 `deploy/docker-compose.yml` 位置、历史评审/计划文档未标注历史状态。

本轮验证：

```bash
git diff --check --cached
find backend frontend worker deploy prompts skills mcp_tools artifacts -maxdepth 1 -type f -name .gitkeep
docker compose --env-file .env.example -f deploy/docker-compose.yml config
docker compose -f deploy/docker-compose.yml config
```

验证结果：

- `git diff --check --cached` 无输出。
- `find ... .gitkeep` 打印 8 个 `.gitkeep` 文件。
- 两个 Docker Compose config 命令均能渲染，backend 环境变量使用 `postgres`、`redis` 和 `/opt/chtest/artifacts`。

本轮提交：

| Commit | Content | Verification |
|---|---|---|
| `58104e5` | 收紧执行准备文档，统一 Slice 1 验收命令，补充 sample repository 前置，降低早期指标看板优先级 | `git diff --check` |
| `a7cd981` | 初始化 8 个平台目录和 `.gitkeep` | `find backend frontend worker deploy prompts skills mcp_tools artifacts -maxdepth 1 -type f -name .gitkeep` |
| `360ab7a` | 添加 PostgreSQL 和 Redis Docker Compose 服务及本地 `.env.example` | `docker compose -f deploy/docker-compose.yml config` |
| `4160695` | 添加 backend Dockerfile、README 和 Docker Compose backend service placeholder | `docker compose -f deploy/docker-compose.yml config` |

下次推荐任务：

- Slice 1 Task 4：添加 worker container placeholder。
- 必读：`NEXT_AI_TASK.md`、`docs/implementation/slices/slice-01-platform-foundation.md`、`docs/deployment/01-docker-environment.md`。
- 验证命令：`docker compose -f deploy/docker-compose.yml config`。

风险提醒：

- 当前分支尚未 push。
- `origin` 仍指向旧 GitHub 地址；是否切换 remote 仍需用户明确确认。
- 不要在 Task 4 实现 RQ worker、AI runtime 或队列业务逻辑。

## 本轮完成

本轮按用户整理的优化稿执行了系统性文档优化：

新增：

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/fixtures/01-golden-requirement-to-case.md`
- `docs/fixtures/02-golden-case-to-playwright.md`
- `docs/fixtures/03-golden-cicd-quality.md`
- `docs/implementation/01-v1-development-process.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/03-testing-and-acceptance.md`

更新：

- `docs/product/02-v1-product-prd.md`
- `docs/product/05-non-goals-and-version-boundaries.md`
- `docs/architecture/03-implementation-technology.md`
- `docs/implementation/01-v1-delivery-plan.md`
- `docs/README.md`
- `memory/README.md`
- `memory/00-ai-session-protocol.md`
- `memory/11-implementation-slices.md`
- `memory/13-ai-readable-project-brief.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

## 当前正式文档结构重点

- AI 开工入口：`START_HERE_FOR_AI.md`
- V0.1 早期闭环：`docs/implementation/00-v0.1-walking-skeleton.md`
- 定位：`docs/product/01-positioning-and-scope.md`
- 总 PRD：`docs/product/02-v1-product-prd.md`
- 页面 PRD：`docs/product/03-user-journey-and-page-prd.md`
- 数据模型契约：`docs/contracts/01-data-model-contract.md`
- API 契约：`docs/contracts/02-api-contract.md`
- 状态机：`docs/contracts/03-state-machines.md`
- Artifact：`docs/contracts/04-artifact-contract.md`
- Prompt/Skill：`docs/contracts/05-prompt-skill-contract.md`
- Golden Path 0：`docs/fixtures/00-v1-demo-path.md`
- Golden Path 1：`docs/fixtures/01-golden-requirement-to-case.md`
- Golden Path 2：`docs/fixtures/02-golden-case-to-playwright.md`
- Golden Path 3：`docs/fixtures/03-golden-cicd-quality.md`
- 开发流程：`docs/implementation/01-v1-development-process.md`
- 切片计划：`docs/implementation/02-v1-slice-plan.md`
- Slice 1 Task Plan：`docs/implementation/slices/slice-01-platform-foundation.md`
- Slice 2 Task Plan：`docs/implementation/slices/slice-02-backend-core.md`
- 测试验收：`docs/implementation/03-testing-and-acceptance.md`
- AI vibecoding 治理：`docs/implementation/04-ai-vibecoding-governance.md`

## 下次 AI 会话开工步骤

1. 进入 `/Users/yanchen/VscodeProject/Chtest`。
2. 读取 `START_HERE_FOR_AI.md`。
3. 读取 `memory/README.md`。
4. 读取 `memory/13-ai-readable-project-brief.md`。
5. 读取 `docs/product/01-positioning-and-scope.md`。
6. 读取 `docs/implementation/00-v0.1-walking-skeleton.md`。
7. 读取 `docs/contracts/*`。
8. 根据任务读取 `docs/fixtures/*`。
9. 查看 `docs/implementation/01-v1-development-process.md`。
10. 读取 `docs/implementation/04-ai-vibecoding-governance.md`。
11. 查看 `docs/implementation/02-v1-slice-plan.md` 或 `memory/11-implementation-slices.md`。
12. 查看 `git status --short`。
13. 进入 Slice 03 Task 1：Add Project Core models and migration。
14. Slice 03 先做 backend models/migration，再做 API，再做 frontend Project Settings shell。
15. 前端页面文案继续保持中文优先；backend 这一轮不要顺手扩成 AI runtime、ToolInvocation 或多用户权限。
16. 每次只做一个 Slice 内的 1-3 个 Task；每个完成 Task 必须验证并 commit；Slice 完成或重大上下文变化时更新 handoff。

## Memory 更新原则

```text
Git 记录代码历史。
Memory 记录会话接续。
Contracts 记录实现真相。
```

- 每个 Task：测试 + commit。
- 每个 Slice：测试汇总 + commit 汇总 + 更新 memory。
- 每个重大变化：立即更新 memory。
- `memory/07-dev-log.md` 写长期摘要。
- `memory/08-session-handoff.md` 写下一轮 AI 如何接手。

## AI Vibecoding Task Table Template

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| - | planned | - | - | - |

Allowed statuses: `planned`, `doing`, `blocked`, `done`, `reverted`.

## Commit Record Template

| Commit | Content | Verification |
|---|---|---|
| - | - | - |

## Verification / Risk Template

```text
Unverified items:
Risk:
Next verification command:
Latest stable commit:
Next recommended Task:
```

## 推荐下一步

开始实现 V1 平台骨架：

- 先读 `START_HERE_FOR_AI.md` 和 `docs/implementation/00-v0.1-walking-skeleton.md`。
- 按 `NEXT_AI_TASK.md` 执行 Slice 03 Task 1：先落 Project / Module / Repository / Environment / TestCommand 的 model 和 migration。
- PostgreSQL + Redis Compose 和 backend placeholder 已完成。
- 建 FastAPI 健康检查和数据库连接。
- 建 Alembic 迁移骨架。
- 建 Vue 3 + Arco 前端骨架。
- 做单用户上下文。
- 建 mock LLM provider，为后续 AI Task Core 铺路。
- 完成 Slice 1-5 后，优先跑 V0.1 Walking Skeleton，再扩展完整 V1 Minimum Demo。

## 仍需用户确认

- 是否需要把 Git remote `origin` 改为 `https://github.com/YanChen0111/Chtest.git`。
- 本轮 ContextArtifact 文档修复完成后，是否需要 push。
- LLM 第一接入方式：OpenAI 官方 API、Azure OpenAI、兼容代理网关，还是 Ollama。

## 2026-07-09 AutomationPlan Review Bridge And RAG Import

完成：

- RAG 知识库页面补齐 Markdown/TXT 文件选择导入；文件内容在浏览器读取后仍走 `POST /api/context-artifacts`，后端安全扫描和 ContextArtifact 合同不变。
- 新增 AutomationPlan 后端桥接：`POST /api/automation/plans` 从已审批且有 `source_candidate_id` 的 TestCase 派生方案；`approve` 后才能 `generate-draft`；生成草稿后 AutomationDraft 仍需单独审批才能进入 TestRun。
- AutomationPlan 可复用 deterministic local retrieval，命中时生成 `knowledge_retrieval` Artifact，并记录 `used_context_artifact_ids`。
- 前端自动化页改为默认读取最近审批通过的 TestCase，减少手填 ID；流程为生成方案、批准方案、生成草稿、编辑/批准草稿。
- 用例评审成功后写入 `chtest.latestApprovedTestCase` workflow context。
- 合同已同步：数据模型、API、状态机、Artifact、Prompt/Skill、错误码。

新增/重点文件：

- `backend/alembic/versions/20260709_0007_automation_plan.py`
- `backend/app/tests/api/test_automation_plan.py`
- `backend/app/modules/automation/{models.py,schemas.py,service.py,router.py}`
- `frontend/src/api/automation.ts`
- `frontend/src/stores/{automation.ts,cases.ts,workflowContext.ts}`
- `frontend/src/views/automation/AutomationDraftReviewView.vue`
- `frontend/src/views/extension/KnowledgeBaseView.vue`

验证：

- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_automation_plan.py backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_extension_surface.py backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/golden/test_deterministic_knowledge_retrieval_golden.py backend/app/tests/ai_runtime/test_openai_responses_provider.py -q` -> 73 passed.
- `npm --prefix frontend run test -- --run src/views/automation/AutomationDraftReviewView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts src/views/extension/KnowledgeBaseView.spec.ts` -> 7 passed.
- `npm --prefix frontend run build` -> passed，保留既有 Vite chunk-size warning。
- `git diff --check` -> passed.

## 2026-07-09 TestKnowledgeCard Evidence Slice

本轮完成用户选择的 V2/V3 第 1 项：TestKnowledgeCard + 知识证据驱动用例生成。

完成：
- 新增后端 `backend/app/modules/knowledge/`，支持从同项目、可展示、允许进 prompt 的 ContextArtifact 同步抽取 TestKnowledgeCard。
- 新增迁移 `backend/alembic/versions/20260709_0008_test_knowledge_cards.py`，创建 `test_knowledge_cards` 表，并为 `generated_case_candidates` 增加 `source_knowledge_evidence_json`。
- CaseGeneration 在 `use_knowledge=true` 时会检索 TestKnowledgeCard evidence，写入 AITask input，并让生成候选用例保留 `source_knowledge_evidence`。
- Mock provider 与 OpenAI Responses provider 的用例生成 schema/指令已支持 `source_knowledge_evidence`。
- RAG 知识库页面展示测试知识卡数量、列表和抽取入口；上传 ContextArtifact 后可直接抽取知识卡。
- 用例评审页展示候选用例引用的知识证据。
- 合同已同步：数据模型、API、状态机、Artifact、Prompt/Skill、错误码。

验证：
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_test_knowledge_cards.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/api/test_context_artifacts.py backend/app/tests/api/test_extension_surface.py backend/app/tests/api/test_deterministic_knowledge_retrieval.py backend/app/tests/api/test_automation_plan.py backend/app/tests/api/test_automation_draft.py backend/app/tests/ai_runtime/test_openai_responses_provider.py -q` -> 51 passed.
- `npm --prefix frontend run test -- --run src/views/extension/KnowledgeBaseView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts` -> 6 passed.
- `npm --prefix frontend run build` -> passed，保留既有 Vite chunk-size warning。

边界：
- 本轮未实现 vector DB、embedding、reranking、GraphRAG、外部 RAG provider 或 MCP runtime。
- TestKnowledgeCard 当前是确定性本地抽取 + prompt-safe evidence；审核态只在合同中预留，UI 暂未做卡片审核流。


## 2026-07-09 RAG Card Retrieval Polish

- Added POST /api/test-knowledge/cards/retrieve for deterministic TestKnowledgeCard evidence preview.
- RAG page extraction now targets all prompt-eligible ContextArtifacts instead of only the first one.
- RAG page now includes TestKnowledgeCard retrieval preview with matched terms and scores.
- Verified: backend 	est_test_knowledge_cards.py -> 3 passed; frontend KnowledgeBaseView.spec.ts -> 3 passed.
- Boundary unchanged: no vector DB, embeddings, reranking, external RAG provider, GraphRAG runtime, or MCP runtime.


## 2026-07-10 Testing GraphRAG Gate

- Added review-gated TestKnowledgeCard flow: extracted cards are previewable, CaseGeneration uses approved cards only.
- Added batch extraction API: POST /api/test-knowledge/cards/extract-batch.
- Added card review API: PATCH /api/test-knowledge/cards/{card_id} with approved/stale/unsafe/duplicate/archived statuses.
- Added derived TestKnowledgeGraph coverage API: GET /api/projects/{project_id}/test-knowledge/graph.
- RAG page now shows knowledge coverage ratio and card approve/archive actions.
- GraphRAG direction: current landing is deterministic coverage graph over TestKnowledgeCard -> GeneratedCaseCandidate -> TestCase; vector DB/embedding/pgvector remains the next infrastructure layer.
- Verified: backend focused suite 53 passed; frontend focused suite 6 passed; frontend build passed with existing chunk-size warning.

## 2026-07-10 RAG Vector Index Layer

- Added TestKnowledgeEmbeddingIndex with deterministic local embedding vectors stored in portable JSON.
- Added full index rebuild API: POST /api/test-knowledge/index/rebuild.
- Added index status API: GET /api/projects/{project_id}/test-knowledge/index.
- TestKnowledgeCard retrieval is now hybrid keyword + deterministic vector similarity when an index exists, returning semantic_score.
- GraphRAG coverage now includes embedding_index nodes, indexes_knowledge_card edges, embedding_indexed_card_count, and vector_index_coverage_ratio.
- RAG page now shows Vector Index / Vector Coverage, can rebuild the local vector index, and displays vector scores in retrieval results.
- KnowledgeBase non_goals changed from no_vector_index/no_embedding to no_external_vector_runtime/no_online_embedding_provider.
- Boundary: this is pgvector-ready local storage and deterministic embedding, not an external vector DB or online embedding provider integration.

## 2026-07-10 V2 Acceptance Stabilization

Completed:
- Added a working Alembic environment and repaired the missing
  `automation_drafts` migration predecessor. A brand-new SQLite database now
  upgrades to `20260710_0009`.
- Added local database bootstrap. A new database automatically receives the
  default project plus 12 active PromptVersion records and 10 active
  SkillVersion records.
- Added `automation_plan_generation:v1` and `automation-plan-skill:v1`.
- RequirementReview now merges approved TestKnowledgeCard evidence with the
  legacy deterministic ContextArtifact adapter and writes one auditable
  knowledge-retrieval artifact.
- AutomationPlan now inherits candidate TestKnowledgeCard evidence, performs
  fresh retrieval, preserves `knowledge_card_id`, and records real active
  PromptVersion/SkillVersion ids instead of synthetic UUIDs.
- OpenAI-compatible runtime now honors `wire_api`. When a Responses endpoint
  returns only a reasoning item and no text, it falls back to Chat Completions
  while preserving both raw responses and schema-validation evidence.
- Backend Docker startup now copies `prompts/` and `skills/`, runs Alembic
  before Uvicorn, and persists model connection configuration under
  `/app/storage`.

Acceptance evidence:
- Relevant backend suite: 84 passed.
- Frontend focused suite: 10 passed.
- Frontend production build: passed with the existing Vite chunk-size warning.
- Alembic empty-database upgrade test: passed.
- Docker Compose config: passed.
- `git diff --check`: passed.
- Fresh SQLite HTTP smoke completed:
  ContextArtifact -> TestKnowledgeCard extraction/approval/index ->
  RequirementReview -> downloadable RequirementDocument -> CaseGeneration ->
  candidate approval -> AutomationPlan approval -> AutomationDraft.
- Real saved model configuration completed a RequirementReview through
  `openai_chat_completions_fallback`: score 78, 6 issues, 7 clarification
  questions, and `used_knowledge=true`.

Known external blocker:
- Docker Desktop Linux Engine is unhealthy. Docker CLI `29.6.1` reaches the
  `desktop-linux` context, but `/v1.55/version` returns HTTP 500. Compose syntax
  and project container configuration are valid; container runtime acceptance
  must be rerun after Docker Desktop engine recovery.

Remaining product risks:
- Deterministic local embeddings are language-sensitive. Cross-language
  Chinese-query/English-card retrieval requires a multilingual embedding
  provider or translated/indexed aliases.
- The frontend production bundle is about 1 MB minified and still reports the
  existing chunk-size warning.

Follow-up fix after browser acceptance:
- `frontend/vite.config.ts` now resolves the dev-server `/api` proxy target
  from `VITE_API_PROXY_TARGET`, then `VITE_API_BASE_URL`, then the legacy
  `http://127.0.0.1:8000` fallback. A value like
  `http://127.0.0.1:8010/api` is normalized to `http://127.0.0.1:8010`.
- This was required because the frontend API client uses same-origin `/api`.
  The previous Vite proxy sent browser requests to port `8000`, while the
  active acceptance backend was on `8010`, so the RAG page rendered empty
  counts even though the backend smoke database had knowledge cards.
- Verified through `http://127.0.0.1:5174/api/...`: 3 TestKnowledgeCards,
  3 indexed vectors, knowledge coverage `0.6667`, vector coverage `1.0`.
- Browser page verification after restart:
  `ContextArtifact1`, `testKnowledgeCardCount=3`, `Vector Index3`,
  `Vector Coverage100%`, no visible error.
## 2026-07-10 Real Requirement Flow And Automation Draft Fix

Completed:
- Ran the user's electric/user App requirement through the real local flow:
  RequirementReview -> clarification supplement -> re-review -> RequirementDocument
  -> CaseGeneration -> Case approval -> AutomationPlan -> AutomationDraft ->
  draft approval -> TestRun.
- Real review score improved from 62 to 83 after supplement.
- Generated requirement document:
  `RD-CHTEST-DEMO-PROJ-20260710-0002`,
  artifact `0c483558-2ddb-4379-8cd3-f5d398eb88a6`.
- Real case generation produced 14 candidates and approved candidate
  `0eac0771-bfab-4c2d-b278-204c5c9af2b9` into TestCase
  `9a2fc84c-7e17-4855-86ac-04d18de691f6`.
- Found AutomationDraft was previously template-only (`assert True`) despite
  the workflow state succeeding.
- Fixed AutomationDraft generation to create a real AI task, call the configured
  provider through the worker, validate the returned JSON/code schema, and only
  persist a draft when model output is valid.
- Added OpenAI-compatible JSON task payload hardening:
  Responses requests now send `text.format=json_object` and low reasoning;
  Chat Completions fallback now sends `reasoning_effort=low`.
- Fixed model connection test so an empty model response is reported as
  `MODEL_CONNECTION_EMPTY_RESPONSE` instead of success.
- Tightened AutomationPlan RAG evidence filtering so unrelated low-score
  knowledge cards are dropped; the real App flow no longer pulls coupon
  evidence into the block-master automation plan.
- Real model AutomationDraft succeeded after provider hardening:
  draft `e4ce7c7a-490d-4f13-9061-c08ba72735a1`,
  AI task `f859b53b-e4b8-4a14-8f9c-1676998e2c66`.
- Approved the generated draft only as a demo execution, with review comment
  noting that it uses `FakeChargerAppAdapter` and is not a real App regression
  pass.
- TestRun `b67f603b-0188-4e0d-9142-df87ad3653d8` executed the approved pytest
  draft: 3 total, 3 passed, exit code 0.

Verification:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_model_connection_config.py backend/app/tests/ai_runtime/test_openai_responses_provider.py backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_automation_plan.py backend/app/tests/golden/test_automation_draft_golden.py -q`
  - Result: `35 passed in 1.81s`.
- Additional focused run:
  `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_automation_plan.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/api/test_case_generation.py backend/app/tests/ai_runtime/test_mock_provider.py backend/app/tests/ai_runtime/test_openai_responses_provider.py -q`
  - Result: `38 passed in 2.08s`.
- Could not run `git diff --check` in the active PowerShell because `git` was
  not available in PATH and `where.exe git` found no executable.

Known risks:
- The generated automation draft is executable but still uses a fake adapter.
  Real App automation needs project-local fixtures/selectors/API hooks before
  it can be treated as product regression evidence.
- Responses endpoint still intermittently returns HTTP 524 on long requests;
  Chat fallback now succeeds when it gets control, but gateway stability remains
  external.
- Chinese text appears mojibake in PowerShell JSON rendering, while artifact
  files previously verified as UTF-8. UI rendering should be checked separately
  if display quality is part of acceptance.
## 2026-07-10 Final-Version Acceptance Docker Blocker

Current task:
- User asked to complete functions toward the final version. Per
  `NEXT_AI_TASK.md`, the active acceptance follow-up is Docker/container-stack
  runtime verification after local dev-stack acceptance.

Completed:
- Re-read `START_HERE_FOR_AI.md`, `NEXT_AI_TASK.md`,
  `docs/product/01-positioning-and-scope.md`,
  `docs/implementation/04-ai-vibecoding-governance.md`,
  and current data/API contracts enough to reconfirm scope.
- Verified Docker Compose syntax still renders successfully:
  `C:\Program Files\Docker\Docker\resources\bin\docker.exe compose -f deploy/docker-compose.yml config`.
- Tried to recover Docker Desktop with `DockerCli.exe -Shutdown`, restarted
  Docker Desktop, and checked both `desktop-linux` and `default` contexts.
- Docker engine remains blocked outside the project:
  both contexts return HTTP 500 for Docker API `/version`.
- WSL status commands fail with `Wsl/0x8007041d`.
- DISM reports `Microsoft-Windows-Subsystem-Linux`,
  `VirtualMachinePlatform`, and `Microsoft-Hyper-V-All` feature names are
  unknown (`0x800f080c`) on this Windows image.
- Local non-container verification still passes:
  backend focused suite `43 passed`, frontend focused suite `9 passed`,
  frontend build passed with existing Vite chunk-size warning.
- `git diff --check` produced no output, but the worktree remains heavily dirty
  with broad pre-existing changes and deletions.

Blocked:
- Container runtime acceptance cannot proceed on this machine until Docker
  Desktop's Linux engine / WSL virtualization layer is repaired outside the
  repository. Compose configuration is valid, but `docker compose up --build`
  cannot run while Docker API `/version` returns HTTP 500.

Next recommended task:
- Repair Windows WSL/VirtualMachinePlatform/Docker Desktop engine or run the
  container acceptance on another Docker-capable machine, then execute:
  `C:\Program Files\Docker\Docker\resources\bin\docker.exe compose -f deploy/docker-compose.yml up --build`.
- After container startup succeeds, repeat the already-passing browser workflow
  against the container frontend/backend and fix only container-specific
  regressions.

## 2026-07-10 Non-Docker Acceptance Quality Gate Follow-up

Current task:
- User explicitly asked to skip Docker because the local Docker Desktop/WSL
  engine cannot be repaired in this session.
- Continue V2 acceptance stabilization through the local dev/browser path and
  address only concrete local evidence risks.

Completed:
- Stopped the Docker-focused investigation path. `docker version` still returns
  HTTP 500 for both `desktop-linux` and `default` contexts, confirming the
  blocker is outside the repo.
- Completed the interrupted AutomationDraft approval quality gate follow-up.
- `POST /api/automation/drafts/{draft_id}/approve` now maps
  `AutomationDraftQualityGateError` to `400` with
  `AUTOMATION_DRAFT_QUALITY_GATE_FAILED` instead of surfacing an unhandled
  error.
- Placeholder detection now treats `assert True # reviewed` as placeholder-only
  so a superficial review edit cannot bypass approval safety.
- AutomationDraft review UI now shows a visible quality-gate note near the
  draft code and renders backend approval errors through visible text.
- Frontend test coverage now verifies the quality-gate warning and a rejected
  placeholder approval response.

Verification:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_automation_draft.py -q`
  - Result: `6 passed in 1.20s`.
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_automation_plan.py -q`
  - Result: `8 passed in 1.92s`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/automation/AutomationDraftReviewView.spec.ts`
  - Result: `2 passed`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run build`
  - Result: passed with the existing chunk-size warning.
- `git diff --check`
  - Result: no output.

Changed files in this follow-up:
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`
- `backend/app/modules/automation/router.py`
- `backend/app/modules/automation/service.py`
- `backend/app/tests/api/test_automation_draft.py`
- `frontend/src/views/automation/AutomationDraftReviewView.vue`
- `frontend/src/views/automation/AutomationDraftReviewView.spec.ts`

Commits:
- None. The repository is still heavily dirty, and several touched files also
  contain earlier uncommitted acceptance work. Use path-limited or partial
  staging only after the full scope is reviewed.

Remaining risks:
- Generated automation can still use fake/stub adapters for demo execution.
  It is now harder to approve pure placeholder code, but real product
  regression evidence still requires project-local fixtures/selectors/API
  hooks or a stronger visible demo-evidence label.
- Docker runtime acceptance remains skipped by user direction until the machine
  Docker Desktop/WSL layer is repaired externally.

Next recommended task:
- Continue non-Docker V2 acceptance stabilization. The next smallest product
  risk is making fake/stub automation adapter evidence impossible to mistake
  for a real product regression pass, then rerun the focused automation tests
  and frontend build.

## 2026-07-13 AutomationDraft Demo Adapter Quality Gate

Current task:
- Continue non-Docker V2 acceptance stabilization and complete the current
  AutomationDraft review surface toward final-version evidence semantics.

Completed:
- Added a computed `quality_gate` to AutomationDraft read responses with
  `status`, `execution_evidence_level`, `approval_blocking_reasons`, and
  `evidence_warnings`.
- Approval now blocks draft code that references fake/stub/demo adapter-style
  evidence such as `FakeChargerAppAdapter`, `fakeAdapter`, `stubClient`,
  `FakeClientFactory`, `make_fake_client`, or `get_demo_client`.
- Placeholder-only drafts remain blocked, including `assert True # reviewed`.
- AutomationDraft review UI now renders the computed gate status, blockers,
  warnings, and disables approval when blockers are present.
- Synced data/API/error-code contracts for `quality_gate` and
  `AUTOMATION_DRAFT_QUALITY_GATE_FAILED`.
- Updated golden automation draft approval coverage so it no longer reviews
  placeholder-only `assert True` code.

Verification:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_automation_plan.py backend/app/tests/golden/test_automation_draft_golden.py -q`
  - Result: `17 passed in 2.10s`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/automation/AutomationDraftReviewView.spec.ts`
  - Result: `3 passed`.
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_test_knowledge_cards.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_model_connection_config.py backend/app/tests/api/test_extension_surface.py -q`
  - Result: `43 passed in 2.96s`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/settings/ProjectSettingsView.spec.ts src/views/extension/KnowledgeBaseView.spec.ts src/views/requirements/RequirementReviewView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts`
  - Result: `9 passed`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run build`
  - Result: passed with the existing Vite chunk-size warning.
- `git diff --check`
  - Result: no output.

Remaining risks:
- Drafts with mock/double wording in notes remain approvable with warnings when
  code does not reference fake/stub/demo adapters. Real product regression
  evidence still requires project-local fixtures, selectors, or API hooks.
- Docker runtime acceptance remains skipped by user direction until Docker
  Desktop/WSL is repaired outside this repo.

Next recommended task:
- Continue non-Docker V2 acceptance only if a real target app integration path
  is available; otherwise keep the acceptance path local-dev based and avoid
  treating demo adapter execution as product regression evidence.

## 2026-07-13 AutomationDraft Embedded Execution Types

Current task:
- User asked to put Playwright, JMeter, and API execution into the automation
  draft workflow because they are automation types.

Completed:
- Added an embedded execution panel to the AutomationDraft review page with
  pytest, Playwright, API/Newman, and JMeter type selection.
- pytest and Playwright execution starts from approved AutomationDraft records;
  API/Newman and JMeter execution starts from an explicit TestCommand ID to
  preserve the current backend execution contract.
- Execution evidence now renders on the draft page: run context, runtime
  manifest, metrics, artifacts, and result rows.
- Restricted automation plan target framework selection to currently supported
  draft generation paths: pytest and Playwright.
- Removed standalone Playwright/API/JMeter links from the primary workbench
  sidebar while preserving route compatibility.

Verification:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_automation_plan.py -q`
  - Result: `16 passed in 1.91s`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/automation/AutomationDraftReviewView.spec.ts`
  - Result: `4 passed`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/automation/AutomationDraftReviewView.spec.ts src/layouts/WorkbenchLayout.spec.ts src/views/execution/PytestExecutionView.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/JMeterExecutionView.spec.ts`
  - Result: `10 passed`.
- `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run build`
  - Result: passed with the existing Vite chunk-size warning.

Remaining risks:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_testrunner_pytest.py backend/app/tests/api/test_playwright_minimal_loop.py backend/app/tests/api/test_newman_execution.py backend/app/tests/api/test_jmeter_execution.py -q`
  currently reports `35 passed, 6 failed` on this Windows machine. The failures
  are `WinError 193` from launching fake `npx`, `newman`, or `jmeter` scripts
  directly via `subprocess`, not from the frontend embedding change.
- Docker runtime acceptance remains skipped by user direction until Docker
  Desktop/WSL is repaired outside this repo.

Next recommended task:
- Keep V2 acceptance local-dev based. A separate focused follow-up can make the
  Playwright/Newman/JMeter runner tests Windows-compatible before treating the
  broader backend execution suite as a local acceptance gate.

## 2026-07-13 Case Generation Flow UX Review

Current task:
- User asked to preserve the senior-test-engineer feedback for the reservation
  charging scenario and inspect the complete Chtest requirement-review to
  case-generation flow.

Observed flow:
- RequirementReview on `预约充电规则与权限` succeeded with score `58` and useful
  findings around 24-hour semantics, max-2 reservation counting, conflict
  policy, modify/delete behavior, plug state, current/limit/fallback rules,
  role permissions, and Bluetooth/cloud/Wi-Fi/4G delivery paths.
- Requirement document generation succeeded:
  `RD-CHTEST-DEMO-PROJ-20260713-0001`.
- The case generation page correctly carried the generated document,
  requirement id, and review id into the generation entry.
- Real-model CaseGeneration task `d7a9c64a-accb-4c4e-a1f2-fa26f6975c3b`
  failed after about two minutes with
  `OPENAI_PROVIDER_ERROR: OpenAI Responses request failed with HTTP 524`.
  During this wait, the UI showed only a loading button and did not surface
  task id, progress, timeout, retry, or the final recoverable error.
- Mock-model CaseGeneration task `cb482c97-9419-4063-870a-b9a05acffce1`
  succeeded and produced 5 candidates, proving the structural flow works.
  However, the generated candidates were coupon-checkout cases despite the
  reservation charging input, so mock output cannot validate domain quality.
- Candidate review actions work: one wrong-domain candidate was rejected, and
  another was edited into a reservation charging case with `approve_after_edit`,
  creating TestCase `a7718b22-b3eb-4408-8676-7d207e5bd319`.

Preserved senior testing feedback:
- Treat RequirementReview as the first quality gate, not as a direct green
  light for final case generation.
- High-risk ambiguities must be resolved or explicitly marked before final
  test cases are accepted: time window semantics, repeat template vs instance,
  max-2 counting dimension, conflict strategy, modify/delete effective scope,
  plug state behavior, current condition/fallback priority, role permissions,
  and multi-channel consistency.
- The case generation surface needs a coverage matrix that maps candidate
  cases back to these risk dimensions.
- The flow needs visible asynchronous task state, retry/cancel, and model error
  evidence before it can feel like a final-version daily testing tool.

Next recommended task:
- Implement the case generation optimization in small steps:
  async task visibility first, then requirement-clarification/quality gate,
  then risk-dimension coverage matrix and domain-alignment checks.

## 2026-07-13 Case Generation P0/P1 Optimization

Current task:
- User asked to complete P0/P1 optimizations from the case generation flow
  review.

Completed:
- CaseGeneration task creation is now observable through
  `GET /api/case-generation/tasks/{id}` with task status, linked AITask status,
  error code, and error message.
- `POST /api/case-generation/tasks` creates a pending task and schedules the
  generation run through FastAPI background tasks instead of making the UI wait
  for the full model call before it can see a task id.
- Wrong-domain model output is blocked by a domain-alignment gate. The
  reservation-charging input with fixed coupon mock output now fails with
  `CASE_GENERATION_DOMAIN_MISMATCH` and writes no candidates.
- Frontend case generation now polls the task read endpoint, displays
  CaseGenerationTask/AITask ids, AI status, and visible failure details, then
  loads candidates only after `status=succeeded`.
- Frontend candidate review page now includes a lightweight testing-dimension
  coverage matrix for main flow, negative path, boundary, state, permission,
  channel, device/current conditions, and risk references.
- Knowledge-card review now keeps vector-index coverage honest: when a card is
  archived, unsafe, stale, or duplicate, existing embedding indexes are marked
  `stale` and excluded from prompt-ready index coverage.
- API, data model, and state-machine contracts were updated for asynchronous
  CaseGeneration task behavior and prompt-ready knowledge index coverage.

Verification:
- Backend focused suite: `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_case_generation.py -q`
  - Result: `6 passed`.
- Backend related suite: `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_test_knowledge_cards.py -q`
  - Result: `25 passed`.
- Frontend related suite: `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/cases/CaseGenerationReviewView.spec.ts src/views/requirements/RequirementReviewView.spec.ts`
  - Result: `6 passed`.
- Backend acceptance suite: `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/api/test_test_knowledge_cards.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_model_connection_config.py backend/app/tests/api/test_extension_surface.py -q`
  - Result: `44 passed in 2.92s`.
- Frontend acceptance suite: `D:\Downloads\Chtest-env\node-v24.18.0-win-x64\npm.cmd --prefix frontend run test -- --run src/views/settings/ProjectSettingsView.spec.ts src/views/extension/KnowledgeBaseView.spec.ts src/views/requirements/RequirementReviewView.spec.ts src/views/cases/CaseGenerationReviewView.spec.ts`
  - Result: `11 passed`.
- Frontend build passed with the existing Vite chunk-size warning.
- `git diff --check`
  - Result: no output.

Remaining risks:
- There is no cancel endpoint yet; cancelled status is documented for the state
  machine but not implemented as a user action.
- The coverage matrix is heuristic and keyword-based. A later quality pass
  should persist explicit `coverage_dimensions` from CaseGenerationAgent output.
- Domain-alignment uses lightweight keyword/alias overlap. It catches the
  observed wrong-domain mock output but is not a semantic classifier.

Next recommended task:
- Add a requirement clarification/decision-table gate before final case
  generation, then extend CaseGenerationAgent output with persisted coverage
  dimensions instead of deriving coverage heuristically in the frontend.

## 2026-07-13 Automation Reviewer Asset Selection UX

Current task:
- Optimize the AutomationDraft review layout and interactions for test engineers
  while browser-smoking the current requirement-to-automation workflow.

Completed:
- Replaced raw TestCase UUID entry with a searchable active-TestCase selector
  showing title, priority, test type, review status, and short id.
- Replaced raw API/JMeter TestCommand UUID entry with compatible active-command
  selectors. Newman only lists `command_type=newman`; JMeter only lists
  `command_type=jmeter`.
- Removed the fake default TestCase id. A saved reviewed-case context is still
  restored, otherwise the generate action remains disabled until explicit
  selection.
- Added a four-stage workflow status strip for case selection, plan approval,
  draft review, and execution evidence.
- Added responsive 4/2/1-column stage layouts and explicit missing-command
  guidance.

Verification:
- Automation reviewer focused spec: `5 passed`.
- Automation reviewer, layout, and related execution suite: `6 files passed, 11
  tests passed`.
- Frontend build passed with the existing Vite chunk-size warning.
- Browser verified that the selector renders 5 real reviewed cases, selecting a
  case advances stage 1 to its business title, and enables plan generation.
- `git diff --check`: no output.

Browser blocker evidence:
- The pre-existing backend on `127.0.0.1:8000` is stale and does not expose
  `/api/automation/plans`.
- Current source on a separate port initially failed local bootstrap because the
  database PromptVersion content conflicts with current registry files.
- Skipping bootstrap for diagnosis allowed reads, but plan creation failed
  because the local database lacks
  `generated_case_candidates.source_knowledge_evidence_json` and other current
  schema fields.
- Migrating a copied database failed at the first migration because the database
  has application tables but no Alembic version record (`workspaces already
  exists`). The original database was not migrated.

Next recommended task:
- Build and verify a safe diagnostic/upgrade path for the unversioned local
  database and prompt-registry drift using a database copy, then resume the
  browser workflow from plan generation through execution selection.

## 2026-07-14 Final RAG Scope Promotion And Full Web Review

Current task:
- User explicitly promoted the final Test Knowledge RAG strategy and requested
  a full-route test-engineer UX review focused on efficiency, quality, logs,
  and traceability.

Completed:
- Reviewed all current frontend routes, including hidden Playwright/Newman/JMeter
  execution routes, using live DOM/layout inspection and representative visual
  screenshots.
- Recorded page-by-page P0/P1 changes in
  `docs/reviews/2026-07-14-full-web-test-experience-review.md`.
- Promoted ingestion, structured cards, reviewed safety, hybrid retrieval,
  evidence-backed cases, quality agents, relationship graph, feedback, and
  provider isolation into product scope.
- Added final data/API/state/artifact contracts for KnowledgeIngestionRun,
  KnowledgeRetrievalRun, KnowledgeEvidence, relationships, feedback, unified
  trace, and enhanced GeneratedCaseCandidate fields.
- Added Slice 47 with a design reason and verification target for every major
  capability.
- Validated the official direction: pgvector supports vector search inside
  PostgreSQL; Qdrant supports filtering/hybrid/vector search and now also has an
  Edge mode; Haystack provides modular components/pipelines; LlamaIndex defines
  loading/indexing/storing/querying/evaluation stages. All remain behind
  KnowledgeAdapter.

Key review risks:
- No unified run history, global search, or end-to-end evidence trace.
- Multiple pages still require raw ids and cannot resume prior work efficiently.
- Generic backend errors do not explain schema/registry/provider/runtime state.
- The RAG page mixes distinct workflows and has a metric-grid layout defect that
  creates an excessively long first load.
- AI Workbench contains useful logs and artifacts but other pages cannot open
  them through a shared correlation path.

Verification:
- Final RAG contract keyword/self-check passed.
- `git diff --check` passed.

Next recommended task:
- Continue Slice 47 Task 47.2: implement safe local database preflight and copied-
  database migration diagnostics before adding final RAG tables.

## 2026-07-14 Slice 47 Local Database Preflight

Current task:
- Completed Slice 47 Task 47.2: add a safe local acceptance database preflight
  and copied-database diagnostic path before any final RAG migration.

Completed:
- Added `python -m backend.app.db_preflight` with human-readable and JSON output.
- The source SQLite database is opened read-only with `query_only`; the command
  never imports the application bootstrap or calls `create_all`.
- Preflight detects a missing Alembic version record, a revision mismatch,
  missing current GeneratedCaseCandidate evidence/coverage columns, missing
  built-in prompts, and PromptVersion hash/content drift.
- `--copy-to` refuses the source path and existing targets, creates a consistent
  SQLite backup, inspects the copy, and suggests only `alembic current` while
  the baseline is unknown.
- Synced the existing empty-database migration test to the actual current head,
  `20260713_0010`; no migration file or runtime database was changed.

Live diagnostic evidence:
- Source: `D:\Desktop\chenyan\Chtest-docs-preflight-vibecoding-fixes\storage\chtest-dev.db`.
- Diagnostic copy:
  `C:\Users\Administrator\AppData\Local\Temp\chtest-task-47-2-diagnostic-copy.db`.
- Source before/after SHA-256:
  `d8fb34dc054cffc69675c92351ebfbdf6620e82dc76b31bcf7ee759f357a7e01`;
  unchanged, `source_mutation_performed=false`.
- Copy before/after `alembic current` SHA-256:
  `c6cf4abe1982bcfe795b1f8f5bfd132cd33e2431b3d679f452a7b43565ca5a3d`;
  unchanged by the diagnostic command.
- Live blockers: no `alembic_version` table; missing
  `source_knowledge_evidence_json` and `coverage_dimensions_json`; content drift
  in four built-in PromptVersion rows; one built-in PromptVersion row missing.
- `alembic current` on the copy exited successfully and returned no revision.
  No `upgrade`, `stamp`, schema DDL, or registry write was run.

Verification:
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/db/test_local_db_preflight.py backend/app/tests/db/test_alembic_upgrade_head.py backend/app/tests/prompt_skill/test_registry_loader.py -q`
  - Result: `11 passed`.
- `backend\.venv\Scripts\python.exe -m pytest backend/app/tests/db backend/app/tests/prompt_skill/test_registry_loader.py -q`
  - Result: `36 passed`.
- Source and copy fingerprint checks passed as recorded above.
- `git diff --check`: no output.

Next recommended task:
- Continue Slice 47 Task 47.3: add KnowledgeIngestionRun persistence and the
  contracted TestKnowledgeCard provenance/review fields with focused DB/API
  ingestion tests. Keep migration acceptance on empty/test databases until the
  copied local baseline recovery is explicitly designed and approved.

## 2026-07-14 Slice 47 Knowledge Ingestion Runs

Current task:
- Completed Slice 47 Task 47.3: persist observable KnowledgeIngestionRun rows,
  evidence Artifacts, and TestKnowledgeCard provenance/review fields.

Completed:
- Added Alembic revision `20260714_0011` after `20260713_0010`; the migration
  creates KnowledgeIngestionRun and adds card locator, source, run, review,
  duplicate, and verification fields.
- Added project-scoped canonical idempotency using stable Artifact id + sha256,
  parser, source type, and non-secret config. Repeated requests reuse the run;
  `force=true` preserves the prior run and creates a new attempt.
- Added create/list/read ingestion APIs with real totals, stable cursor paging,
  same-project prompt-safe source validation, and batched list serialization.
- Successful runs write ingestion manifest, parse, extraction, and safety
  Artifacts owned by KnowledgeIngestionRun. Artifact links require matching
  project, owner type, owner id, and evidence id.
- Runs with extracted cards remain `waiting_review` without a terminal time;
  they become `completed` after all owned cards are reviewed.
- Card review now records review time, rationale, verification time, canonical
  duplicate relation, and append-only ReviewHistory. Duplicate chains/cycles,
  unsafe reapproval, cross-project canonical targets, and invalid transitions
  are rejected.
- Source-level `allowed_for_prompt` is preserved for stale/duplicate/archived
  cards; final eligibility remains approved + safe + allowed.
- Added a populated `0010 -> 0011 -> 0010 -> 0011` SQLite migration test so
  existing cards survive upgrade and downgrade diagnostics.

Verification:
- Ingestion/migration/deterministic retrieval focused suite: `19 passed`.
- Knowledge consumers and ReviewHistory related API suite: `44 passed`.
- Complete backend DB suite: `30 passed`.
- Deterministic retrieval API/golden subset: `7 passed`.
- `git diff --check`: no output.
- Full backend run performed during subagent review: `379 passed, 14 failed`.
  The 14 failures are the previously recorded Windows fake executable
  `WinError 193` cases and stale golden CaseGeneration fixtures; no failure stack
  points to the knowledge ingestion implementation.

Migration safety:
- No migration, stamp, bootstrap, or registry write was run against
  `storage/chtest-dev.db`.
- `alembic check` on a fresh temporary head database still reports pre-existing
  repository-wide migration drift: several older ORM tables have no migrations
  and older migration indexes are absent from ORM metadata. The new 0011
  tables/indexes/constraints are not reported as drift.

Remaining risks:
- Retry/cancel ingestion endpoints remain planned; Task 47.3 intentionally
  implemented the smallest create/list/read path.
- Older TestKnowledgeCard fields such as `applicability` still contain pre-47.3
  ORM/contract type/default drift. This task changed only the contracted
  provenance/review surface.
- The blocked local acceptance database still requires an explicitly approved
  copied-baseline recovery before any migration can run against it.

Next recommended task:
- Continue Slice 47 Task 47.4: persist KnowledgeRetrievalRun and normalized
  KnowledgeEvidence, then expose create/list/read retrieval logs without adding
  pgvector, Qdrant, or external provider runtime yet.

## 2026-07-14 Slice 47 Knowledge Retrieval Evidence

Current task:
- Completed Slice 47 Task 47.4: persist provider-neutral
  KnowledgeRetrievalRun/KnowledgeEvidence logs and canonical retrieval Artifacts.

Completed:
- Added Alembic revision `20260714_0012` with retrieval run/evidence tables,
  score/count/consumer constraints, FKs, indexes, nullable vector score, and an
  isolated `0012 -> 0011 -> head` migration round trip.
- Routed deterministic TestKnowledgeCard retrieval through persisted runs and
  evidence rows with create/list/read APIs, real totals/cursors, query/filter
  safety, provider/mode snapshots, latency/count/error fields, empty-result
  Artifacts, and deterministic keyword/vector fallback behavior.
- Integrated RequirementReview, CaseGeneration, and AutomationPlan with stable
  evidence ids. Single-run card retrieval uses the canonical run Artifact;
  mixed ContextArtifact/card or multi-run evidence uses an id-only reference
  manifest without raw snippets/provider payload copies.
- Added current lifecycle fields beside evidence snapshots, same-project AITask
  correlation validation, prompt revalidation, candidate display whitelisting,
  governed-source exclusion from the legacy raw adapter, unsafe canonical and
  historical Artifact revocation, and fail-closed download for retrieval
  Artifacts lacking explicit `safe_to_show=true`.
- Updated Knowledge Base recent retrieval display to use current-safe AITask
  structured input while retaining the minimized Artifact file contract.

Verification:
- Focused retrieval/consumer/golden/DB/artifact suite: `64 passed`.
- Empty/temp database Alembic tests: included in the focused suite and passed.
- Complete backend: `398 passed, 13 failed`.
- Remaining failures are pre-existing/out-of-scope: six Windows fake executable
  `WinError 193` runner cases and seven golden CaseGeneration fixtures missing
  `decision_table_acknowledged=true`.
- `compileall`: passed.
- Ruff was unavailable in the workspace environment.
- `git diff --check`: no output.

Migration safety:
- No upgrade, stamp, bootstrap, or registry write was run against
  `storage/chtest-dev.db`.
- Read-only preflight reported source before/after SHA-256
  `d8fb34dc054cffc69675c92351ebfbdf6620e82dc76b31bcf7ee759f357a7e01`,
  size `1282048`, identical modified timestamp, and
  `source_mutation_performed=false`.
- The local acceptance database remains blocked by its missing Alembic baseline,
  missing candidate columns, and PromptVersion registry drift.

Next recommended task:
- Continue Slice 47 Task 47.5: add PostgreSQL full-text + pgvector behind the
  stable KnowledgeAdapter/evidence contracts with deterministic fallback and
  temporary-database verification only.

## 2026-07-14 Slice 47 PostgreSQL Hybrid Adapter (Blocked)

Current task:
- Task 47.5 remains in progress. Offline/provider-neutral implementation is
  complete enough for review, but real PostgreSQL/pgvector acceptance is blocked.

Implemented:
- Added Python `pgvector` dependency and optional Alembic revision
  `20260714_0013`. SQLite is a no-op; PostgreSQL emits a prompt-safe full-text
  GIN index and conditionally creates vector extension, native vector column,
  and default-dimension HNSW expression index without dropping the shared
  extension on downgrade.
- Added isolated PostgreSQL capability detection, native embedding sync, bound
  full-text/vector SQL, HNSW-compatible vector candidate CTE, embedding
  model/dimension/content freshness gates, safe local adapter configuration,
  provider-neutral score conversion, and deterministic keyword fallback.
- PostgreSQL provider fallback records actual keyword mode, capability snapshot,
  stable reason, and `vector_score=null`; sensitive queries remain redacted and
  do not execute vector search.

Verification:
- Focused Task 47.4 + 47.5 API/golden/DB/dialect suite: `74 passed`.
- Complete backend before the final SQL-shape review: `406 passed, 13 failed`;
  all 13 are the previously recorded Windows fake-runner and stale golden
  acknowledgement failures.
- PostgreSQL offline upgrade/downgrade SQL, SQLite 0013 no-op, SQL binding,
  capability failure, native normalization, dimension mismatch, and fallback
  tests pass.
- `compileall` and `git diff --check` pass.

Blocking environment evidence:
- No PostgreSQL binaries/service/listener or test URL is available.
- Docker client exists, but the desktop-linux engine returns HTTP 500.
- Real online migration, extension privilege behavior, `<=>` execution, HNSW
  plan use, and recall comparison cannot be claimed until a dedicated empty
  PostgreSQL test database and pgvector-enabled peer are provided.

Next action:
- Resume Task 47.5 with dedicated PostgreSQL test URLs. Run online Alembic and
  full-text fallback smoke first, then pgvector native ordering/plan/recall
  smoke. Do not advance to Task 47.6 before this acceptance gap closes.

## 2026-07-15 PostgreSQL Hybrid Candidate Review Fix

Current task:
- Task 47.5 remains blocked only on real PostgreSQL/pgvector integration.

Completed after offline implementation review:
- Split native retrieval into materialized full-text candidates and an
  HNSW-ordered vector pool, then applied similarity filtering outside the
  ordered pool before provider-neutral merging.
- Matched vector casts and filters to configured dimensions, preserved the
  default 64-dimension HNSW expression, and excluded text candidates from
  vector-only mode.
- Made capability probe/index state explicit and distinguished an unavailable
  pgvector capability from a usable capability with no matching fresh vector.
- Added SQL-shape, vector-only, capability failure, fake-native normalization,
  dimension mismatch, and provider leakage assertions.

Verification:
- Focused Task 47.4/47.5 API/golden/DB/dialect suite: `76 passed`.
- Complete backend: `410 passed, 13 failed`; the remaining failures are the
  unchanged Windows fake executable and stale golden acknowledgement cases.
- `compileall` and `git diff --check`: passed.
- Read-only source preflight: SHA-256
  `d8fb34dc054cffc69675c92351ebfbdf6620e82dc76b31bcf7ee759f357a7e01`,
  `source_mutation_performed=false`.

Blocker:
- No PostgreSQL server/test URL or pgvector-enabled peer exists, and Docker
  Desktop still returns HTTP 500. Online migration, real `<=>`, HNSW plan, and
  recall acceptance remain unverified. Do not advance to Task 47.6.

## 2026-07-15 PostgreSQL Hybrid Online Acceptance

Task 47.5 is complete; the next task is Slice 47 Task 47.6.

- Created an isolated PostgreSQL 16.14 + pgvector 0.8.3 environment outside
  the repository and ran it under the Windows `NetworkService` account.
- Upgraded both empty `chtest_plain_test` and `chtest_vector_test` databases
  online to Alembic head `20260714_0013`.
- Plain database: GIN full-text index present, pgvector extension/column/index
  absent; the limited role cannot create the extension and the adapter reports
  deterministic keyword-only capability.
- Vector database: pgvector extension, native `embedding_vector vector`, and
  the default 64-dimensional HNSW index present. A real adapter query returned
  a provider-neutral match with keyword score `0.033333335` and vector score
  `1.0`; native `<=>` and an HNSW index scan were also verified.
- The blocked `storage/chtest-dev.db` fingerprint remains unchanged and was
  never used for migration or smoke data.

Docker Desktop/WSL remains unavailable, but it no longer blocks Task 47.5.

## 2026-07-15 Slice 47.6 Optional Provider Contracts

Current task:
- Task 47.6 implementation is complete pending commit; next is Task 47.7.

Implemented:
- Added dependency-free Qdrant/Haystack/LlamaIndex fake-client contracts in
  `backend/app/modules/knowledge/optional_providers.py`.
- Normalization keeps only Chtest card UUIDs, bounded source locators, bounded
  snippets, normalized component scores, and stable retrieval reasons.
- Added deterministic capability snapshots and no-client/search-failure/
  invalid-candidate reasons without persisting provider payloads or exception
  messages.
- Extended safe provider configuration and visible provider routing; optional
  providers degrade to keyword retrieval when no client is registered.
- Clarified the pre-final stub contract versus Final Test Knowledge provider
  promotion rules in the API/data contracts.

Verification:
- Focused optional-provider, extension, retrieval, PostgreSQL adapter, and
  migration suite: `46 passed`.
- Temporary PostgreSQL service was stopped and its service/ACL cleanup was
  completed after Task 47.5 acceptance.

## 2026-07-15 Slice 47.7 Evidence-Backed CaseGeneration

Task 47.7 is complete; the next task is Task 47.8 CaseReviewAgent and
CoverageGapAgent quality gates.

- Added migration `20260715_0014` and matching ORM/API fields for explicit
  covered requirement/risk ids, case type, generation reason, coverage gap
  notes, automation readiness, and quality assessment.
- Extended output validation, persistence, candidate listing, and completeness
  checks while preserving deterministic defaults for older model fixtures.
- Updated the GeneratedCaseCandidate contract and migration assertions.

Verification:
- CaseGeneration and Alembic suite: `13 passed`.
- Existing optional-provider/PostgreSQL focused suite remains `46 passed`.
- Source acceptance database remains untouched.

## 2026-07-15 Slice 47.8 Case Quality Agents

Task 47.8 is complete; the next task is Task 47.9 typed relationships and graph
queries.

- Added deterministic local CaseReviewAgent and CoverageGapAgent functions and
  automation readiness assessment.
- Candidate persistence writes quality findings and blockers using only
  provider-neutral evidence ids and coverage dimensions.
- Focused quality/CaseGeneration verification: `12 passed`.
- The broader golden collection retains known missing-fixture and stale
  acknowledgement failures unrelated to this change.

## 2026-07-15 Slice 47.9 Typed Relationships

Task 47.9 is complete; the next task is Task 47.10 reviewed feedback.

- Added migration `20260715_0015`, ORM model, same-project validation, and a
  relationship creation endpoint.
- Persisted relationship edges are included in the existing deterministic graph
  response; no graph database is required.
- Migration/API verification: `28 passed`.

## 2026-07-15 Slice 47.10 Reviewed Feedback

Task 47.10 is complete; next is Task 47.11 final RAG workbench frontend.

- Added migration `20260715_0016`, feedback proposal/review APIs, same-project
  source validation, and secret-safe content validation.
- Approved feedback creates an `extracted` card only; rejected feedback creates
  no card and approved-card trust remains separately reviewed.
- Migration/API verification: `29 passed`.

## 2026-07-15 Slice 47.11 Final RAG Workbench

Task 47.11 is complete and committed; next is Task 47.12 unified trace and
global evidence search.

- Added the tester-first `/extension/knowledge-workbench` route and navigation
  item with KPI cards, next actions, provider health, retrieval filters,
  evidence/trace columns, and coverage/graph summary.
- Added focused component coverage and preserved HTTP status codes in
  `frontend/src/api/client.ts` for actionable diagnostics.
- Frontend verification: `25 test files / 50 tests passed`; production build
  passed with the known chunk-size warning; desktop and `390x844` mobile smoke
  passed.
- Source `storage/chtest-dev.db` remains read-only and unchanged.

## 2026-07-15 Slice 47.12 Unified Evidence Trace

Task 47.12 is complete and committed; next is Task 47.13 recent-run navigation
and named selectors across the remaining pages.

- Added `GET /api/projects/{project_id}/evidence-trace` with bounded global
  search and entity trace roots for ingestion, retrieval/evidence, cards,
  feedback, and generated cases.
- Trace nodes preserve provider/requested/effective mode, fallback, degraded
  state, latency, evidence ids, source locators, and safe artifact refs while
  filtering unsafe content and enforcing project scope.
- Added workbench global trace search, stage filtering, responsive result rows,
  and a details drawer for source inspection before navigation.
- Verification: backend focused knowledge API `27 passed`; frontend `25 test
  files / 50 tests passed`; build passed with existing chunk-size warning;
  desktop and `390x844` browser smoke passed.

## 2026-07-15 Slice 47.13 Recent Run Navigation

Task 47.13 is complete and committed; next is Task 47.14 final eval and
acceptance.

- Added bounded recent execution history and resume actions shared by pytest,
  Playwright, Newman, JMeter, automation, and reporting.
- Added explicit recent/resume/retry/stale/empty selectors and state handling
  across knowledge, case review/library, execution, reporting, automation, and
  CI/CD surfaces.
- Resume actions refresh current evidence or clear downstream state that no
  longer belongs to the selected run.
- Verification: frontend `26 test files / 53 tests passed`; production build
  passed with the known chunk-size warning; desktop and `390x844` multi-page
  smoke passed without horizontal overflow.

## 2026-07-15 Slice 47.14 Final Acceptance

Slice 47 is complete; no Slice 47 implementation task remains.

- Added final provider-neutral RAG eval fixture and isolated golden test.
- Final focused backend acceptance: `69 passed`; frontend: `26 files / 53
  tests`; build and responsive multi-page smoke passed.
- Fixed-fixture metrics: recall `1.0`, precision `1.0`, unsafe/cross-project
  exclusion `1.0`; optional provider fallback is visible and degraded.
- Source DB remains unchanged at SHA256
  `d8fb34dc054cffc69675c92351ebfbdf6620e82dc76b31bcf7ee759f357a7e01`.
- Known unrelated full-suite baseline failures are Windows fake runner
  `WinError 193` and stale golden inputs missing the decision-table gate.

## 2026-07-20 Slice 48.1 Runtime Policy Authority

Task 48.1 is complete but not committed in this dirty worktree.

- Added a fail-closed RuntimePolicyBundle compiled from the exact PromptVersion
  and SkillVersion referenced by each queued AITask.
- Runtime compilation verifies active state, content hashes, prompt-agent
  assignment, and skill applicability.
- OpenAI-compatible transport now consumes the policy bundle; task-specific
  business instructions and task-name output routing were removed.
- Each successful queued task records `runtime_policy.json` with prompt, skill,
  schemas, gates, permissions, versions, and hashes.
- Updated legacy test seeds to use hashes derived from their published content.
- Verification: provider focused `14 passed`; backend full suite `458 passed`;
  runtime DB prompt/skill hash audit found no mismatches.
- Next scoped task: immutable requirement claims and per-case grounding checks.

## 2026-07-24 Slice 48.3 Claim Grounding EvalOps

Task 48.3 is complete; next is Task 49.1 human-gated workflow transition
policy.

- Added a fixed offline corpus for explicit v1/v2 Prompt/Skill pairs and an
  explicit v1 baseline.
- Added deterministic citation recall, unsupported rejection, requirement
  coverage, signed drift, missing/unexpected Claim ids, and per-case diagnostics.
- Evaluation reuses production grounding on deep copies and fails closed for
  empty metric inputs, duplicate pairs, or an unknown baseline.
- Fixed results: v1 recall/coverage `0.0`; v2 recall/coverage `1.0`; v2 drift
  `+1.0`; unsupported rejection `5/5`.
- Verification: focused `23 passed`; backend `471 passed, 1 deselected` because
  Windows lacks symlink creation privilege; frontend `25 files / 54 tests`;
  production build passed with the existing chunk-size warning.
- Source `storage/chtest-dev.db` was not used.

## 2026-07-24 Slice 49.1 Human-Controlled Transition Policy

Task 49.1 is complete; next is Task 49.2 persistence for workflow positions,
snapshots, human decisions, and approval fingerprints.

- Added a pure workflow policy with explicit AI, human, and deterministic
  system actors.
- Human approval is scoped to workflow, subject, stage, action, and canonical
  immutable input SHA-256; changed input invalidates the grant.
- Workflow-specific ordered prefixes block stage skips. Advancing creates a new
  target-stage snapshot and is never an AI action.
- Automation plan/draft approvals and CI/CD patch gates remain independent.
- Verification: focused `29 passed`; backend `500 passed, 1 deselected` for the
  known Windows symlink privilege test; frontend `25 files / 54 tests`; build
  passed with the existing chunk-size warning.
- The policy is intentionally not integrated into existing domain services or
  the database yet. Source `storage/chtest-dev.db` was not used.

## 2026-07-28 Slice 49.2 Workflow-Control Persistence

Task 49.2 is complete; next is Task 49.3 RequirementReview integration as the
first API/frontend vertical slice.

- Added migration `20260728_0019` and ORM models for WorkflowRun, immutable
  WorkflowStageSnapshot, WorkflowHumanDecision, and WorkflowTransitionEvent.
- The project-scoped service rebuilds policy positions from trusted rows,
  verifies canonical stage hashes, and uses run `lock_version` compare-and-swap.
- Advance consumes one exact approval decision through a unique transition
  event. ABA restoration requires a new decision even when stage/hash match.
- Snapshots reject secret-like keys, payloads over 1 MiB, mutation, deletion,
  and hash tampering. No API route or existing domain integration was added.
- Focused policy/persistence/migration verification: `44 passed`; backend
  `511 passed, 1 deselected` for the known Windows symlink privilege test;
  frontend `25 files / 54 tests`; production build passed with the existing
  chunk-size warning.
- `backend/alembic/env.py` and the existing migration-head test were necessary
  writes outside the initial file list. Source `storage/chtest-dev.db` was not
  used.

## 2026-07-29 Slice 49.3 RequirementReview Workflow Integration

Task 49.3 is complete; the next smallest task is RiskReview workflow
integration without migrating Case, Automation, execution, CI/CD, report, or
knowledge flows in the same task.

- RequirementReview creation now creates an authoritative WorkflowRun and
  immutable candidate snapshot before entering `waiting_review`.
- Project-scoped read, complete, edit, approve, reject, selected-regeneration,
  continue, and atomic approve-and-continue APIs fail closed on stale versions,
  cross-project access, forged state, missing approval, and replay.
- Formal RequirementDocument creation requires current approval or evidence
  that the exact approval was consumed by a successful advance.
- The frontend now reads server `can_*` actions, supports candidate editing,
  approval comments, rejection, approval, controlled continue, stale-input
  blocking, authoritative refresh, and fail-closed formal document generation.
- Backend focused verification: `68 passed`; full backend: `515 passed`.
  Frontend: `25 files / 55 tests`; production build passed with the existing
  large-chunk warning. `git diff --check` passed.
- `backend/app/tests/api/test_case_generation.py` was a necessary write outside
  the default Task 49.3 list because its old fixture created a formal document
  without the newly required human approval. Source `storage/chtest-dev.db` was
  not used.

## 2026-07-29 Slice 49.4 RiskReview Workflow Integration

Task 49.4 is complete; the next smallest task is TestPlanReview workflow
integration.

- RiskReview input preserves the exact consumed RequirementReview snapshot id
  and hash; TestPlanReview input preserves the exact approved RiskReview
  snapshot id and hash.
- Project-scoped RiskReview submit, complete, edit, approve, reject, continue,
  and atomic approve-and-continue actions reject stale versions, stage skips,
  missing approval, cross-project access, and approval replay.
- Risk edits create a new immutable snapshot, immediately re-enter human
  review, and invalidate old approval.
- The frontend now switches its human gate controls by authoritative stage and
  does not navigate from RequirementReview directly to case generation.
- Verification: focused backend `60 passed`; full backend `516 passed`; frontend
  `25 files / 55 tests`; production build passed with the existing chunk-size
  warning. Source `storage/chtest-dev.db` was not used.

## 2026-07-29 Slice 49.5 TestPlanReview Workflow Integration

Task 49.5 is complete. Backend integration and frontend TestPlanReview wiring
are implemented and verified. Node/npm were restored only for this shell from a
temporary official Node distribution under `%TEMP%\chtest-task49-node`.

- TestPlanReview now has project-scoped read, submit, complete, edit, approve,
  reject, continue, and atomic approve-and-continue backend actions using the
  same authoritative WorkflowRun and optimistic compare-and-swap pattern.
- The TestPlanReview draft preserves the exact approved RiskReview snapshot id
  and hash. Advancing from TestPlanReview creates the adjacent CaseReview draft
  from the exact approved TestPlanReview snapshot without migrating Case
  workflow behavior.
- Human test plan edits create a new immutable snapshot, re-enter review, and
  invalidate old approval. High or critical risk items require a non-empty test
  strategy before plan approval or advancement.
- Frontend RequirementReview now switches submit, complete, edit, approve,
  reject, and continue actions by authoritative workflow stage, including the
  TestPlanReview strategy/plan-item editor and review panel.
- Contracts were updated for the TestPlanReview API/state-machine boundary.
- Verification: focused `backend\\.venv\\Scripts\\python.exe -m pytest backend/app/tests/api/test_requirement_review.py -q` => `21 passed`; focused workflow suite `backend\\.venv\\Scripts\\python.exe -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/workflow_control -q` => `61 passed`; full backend `backend\\.venv\\Scripts\\python.exe -m pytest backend/app/tests -q` => `517 passed`; focused frontend `npm.cmd --prefix frontend test -- --run src/views/requirements/RequirementReviewView.spec.ts` with temporary Node `v24.18.0` => `1 file / 2 tests passed`; full frontend `npm.cmd --prefix frontend test -- --run` with temporary Node `v24.18.0` => `25 files / 55 tests passed`; production build `npm.cmd --prefix frontend run build` with temporary Node `v24.18.0` passed with the existing large-chunk warning; `git diff --check` passed.
- No commit was created in this pass because the workspace already contains many
  uncommitted changes from prior Task 49.x/frontend work; committing safely
  requires staging only the intended Task 49.5 files after owner review.
- Next: Task 49.6 integrates persisted workflow control into CaseReview using
  the exact approved TestPlanReview snapshot as input.

## 2026-08-03 Slice 49.14 Controlled TestCampaign Scope Frontend

Task 49.14 is complete; next is Task 49.15 exact TestCampaign restoration from
the AI Workbench workflow queue.

- Added the `/campaigns/scope` workbench route, navigation entry, typed
  TestCampaign API, and a dedicated Pinia store.
- The page presents immutable input/evidence context, an editable candidate,
  persisted coverage/gap rows, deterministic validation state, and a fixed set
  of human review actions.
- Save, submit, complete review, approve, reject, refresh, and continue use the
  authoritative campaign projection, exact lock version, and approval decision
  id. A `409` marks the page stale and locks mutations until refresh.
- Successful continue navigates only after the backend returns
  `requirement_review`; the frontend cannot synthesize advancement.
- Focused frontend: `1 file / 3 tests passed`; full frontend: `26 files / 64
  tests passed`; full backend: `524 passed`; production build passed with the
  existing large-chunk warning; `git diff --check` passed.
- Real browser QA completed create through continue on an isolated database.
  Desktop and `390x844` layouts had no horizontal overflow or overlapping
  controls. The protected `storage/chtest-dev.db` was not used.
- `frontend/src/stores/index.ts` was a necessary write outside the planned list
  because it owns the existing navigation data; the planned shared
  `frontend/src/api/types.ts` does not exist, so campaign types remain colocated
  with their API.

Next: return an exact Scope route from the read-only workflow queue and make the
page fail closed when an explicit campaign id cannot be restored.

## 2026-08-04 Slice 49.15 Exact TestCampaign Scope Resume

Task 49.15 is complete; next is Task 49.16 exact RequirementReview restoration
from the AI Workbench workflow queue.

- The read-only workflow queue now returns
  `/campaigns/scope?campaign_id={id}` only when an active Scope run's UUID
  subject resolves to an active TestCampaign in the same project.
- Malformed, missing, inactive, cross-project, non-Scope, and unsupported
  subjects retain a null route.
- The Scope store and page load an explicit campaign id directly. Failed
  explicit restore clears campaign state, disables save and workflow actions,
  and refresh retries the same id without listing or selecting another
  campaign.
- The API contract records the exact route and fail-closed restore semantics.
- Focused backend queue verification passed with `2 passed`; full backend
  regression passed with `525 passed`.
- Focused Scope + AI Workbench frontend verification passed with `2 files / 10
  tests`; full frontend passed with `26 files / 66 tests`.
- Production build passed with the existing large-chunk warning, and
  `git diff --check` passed.
- Historical `.pytest-tmp-*` and `.t49/` scratch directories were preserved and
  excluded from the commit. The protected `storage/chtest-dev.db` was not used.

Next: expose an exact route only for standard same-project RequirementReview
subjects and make explicit page restore fail closed without local-storage or
recent-record fallback. TestCampaign-origin RequirementReview runs remain null
until their adjacent-stage domain contract is defined.

## 2026-08-04 Slice 49.16 Exact RequirementReview Resume

Task 49.16 is complete; next is Task 49.17 exact RiskReview restoration from
the AI Workbench workflow queue.

- The queue returns a RequirementReview route only when the run is at
  `requirement_review`, its UUID subject resolves to a RequirementReview, and
  the owning active Requirement belongs to the same project.
- The route carries exact Requirement, RequirementReview, and WorkflowRun ids.
  The page loads the Requirement and review directly, then verifies project,
  relationship, active status, current stage, and run id.
- Any explicit parameter activates fail-closed mode. Missing, malformed,
  cross-project, mismatched-review, and mismatched-run input clears review state,
  disables new review creation, hides workflow actions, and never reads the
  latest local-storage context.
- TestCampaign-origin RequirementReview runs retain a null route because their
  subject remains a campaign id and they do not own a RequirementReview row.
- Focused backend queue verification passed with `3 passed`; full backend
  regression passed with `526 passed`.
- Focused RequirementReview + AI Workbench frontend verification passed with
  `2 files / 10 tests`; full frontend passed with `26 files / 69 tests`.
- Production build passed with the existing large-chunk warning, and
  `git diff --check` passed.
- The protected `storage/chtest-dev.db` and historical pytest scratch
  directories were not modified.

Next: apply the same exact-subject and exact-run restoration rule only to the
standard RiskReview stage through its existing project-scoped API. Do not add
later stages or invent a TestCampaign RequirementReview domain row.

## 2026-08-04 Slice 49.17 Exact RiskReview Resume

Task 49.17 is complete; next is Task 49.18 exact TestPlanReview restoration from
the AI Workbench workflow queue.

- The queue now resolves standard `risk_review` runs only when their UUID
  subject is an active same-project RequirementReview owner.
- RiskReview routes retain exact Requirement, RequirementReview, and WorkflowRun
  ids and add `workflow_stage=risk_review`.
- The page uses the existing project-scoped RiskReview API and verifies project,
  relationship, run id, and exact returned stage before exposing controls.
- A RequirementReview response, unsupported stage, invalid id, cross-project
  subject, inactive Requirement, or run mismatch fails closed without local
  storage or recent-record fallback.
- Focused backend queue verification passed with `4 passed`; full backend
  regression passed with `527 passed`.
- Focused RequirementReview + AI Workbench frontend verification passed with
  `2 files / 12 tests`; full frontend passed with `26 files / 71 tests`.
- Production build passed with the existing large-chunk warning, and
  `git diff --check` passed.
- TestCampaign-origin RequirementReview runs, later stages, the protected
  source database, and historical pytest scratch directories were untouched.

Next: apply the same exact-subject, exact-run, and exact-stage rule only to the
standard TestPlanReview stage through its existing project-scoped API.
