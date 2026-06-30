# Slice 14: Report And Failure Analysis Task Plan

## Goal

Add evidence-backed FailureAnalysis and automation_execution Report generation
for existing TestRun/TestResult artifacts.

This slice must stay limited to failure analysis, evidence manifests, and
automation execution reports. It must not add CI/CD quality gates, merge/release
decisions, RAG runtime, MCP runtime, RBAC, tenants, permissions, or broad report
center analytics.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/product/03-user-journey-and-page-prd.md`
- `docs/product/06-frontend-ui-guidelines.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/fixtures/00-v1-demo-path.md`
- `docs/fixtures/04-real-user-scenarios.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-13-playwright-minimal-loop.md`

## Preconditions

- Slice 12 TestRunner Pytest Execution is complete.
- Slice 13 Playwright Minimal Loop is complete.
- TestRun/TestResult and execution artifact metadata exist.
- Mock FailureAnalysisAgent and ReportAgent contracts exist.
- Artifact contract defines report files and `evidence_manifest.json`.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Report And Failure Analysis task plan | done | `test -f docs/implementation/slices/slice-14-report-and-failure-analysis.md && rg -n "Report And Failure Analysis|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-14-report-and-failure-analysis.md` | `dcedd23` | scoped Slice 14 plan |
| Add Report and FailureAnalysis API contract boundary | done | `rg -n "FailureAnalysis|POST /api/test-runs/.*/failure-analysis|POST /api/reports|evidence_manifest" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-14-report-and-failure-analysis.md` | pending commit | contract-first report and analysis shape |
| Add FailureAnalysis and Report model/schema | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q` | - | persisted model/schema only |
| Add FailureAnalysis API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q` | - | deterministic mock analysis from failed TestRun evidence |
| Add automation execution Report API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q` | - | evidence_manifest + report artifacts |
| Add Report and FailureAnalysis frontend shell | planned | `npm --prefix frontend run test -- --run` | - | evidence-first report/detail views |
| Add automation execution report golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_report_failure_analysis_golden.py -q` | - | TestRun -> FailureAnalysis -> Report evidence |
| Slice 14 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py backend/app/tests/golden/test_report_failure_analysis_golden.py -q && npm --prefix frontend run test -- --run` | - | docs and handoff only |

## Task 1: Add Report And FailureAnalysis API Contract Boundary

Goal: Tighten the existing FailureAnalysis and Report API contracts before
implementation.

Expected files:

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "FailureAnalysis|POST /api/test-runs/.*/failure-analysis|POST /api/reports|evidence_manifest" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-14-report-and-failure-analysis.md
```

Acceptance:

- Contract defines create/get FailureAnalysis endpoints with evidence artifact
  references and deterministic mock-provider fields.
- Contract defines create/get automation_execution Report endpoints.
- Report contract requires `evidence_manifest.json` and report artifact ids.
- Report conclusions must reference TestRun/TestResult/artifact evidence.
- No CI/CD quality gates, merge/release decisions, RAG runtime, MCP runtime,
  RBAC, tenants, permissions, or broad report analytics are added.

Commit message:

```text
docs(report): define failure analysis api
```

## Task 2: Add FailureAnalysis And Report Model Schema

Goal: Add persisted FailureAnalysis and Report records aligned with the data
model contract.

Expected files:

- `backend/app/modules/reporting/__init__.py`
- `backend/app/modules/reporting/models.py`
- `backend/app/modules/reporting/schemas.py`
- `backend/app/tests/api/test_report_failure_analysis.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q
```

Acceptance:

- Defines FailureAnalysis fields from the data model contract.
- Defines Report fields from the data model contract.
- Defines create/read schemas for FailureAnalysis and Report.
- Does not call AI providers or write report artifacts in this task.

Commit message:

```text
feat(reporting): add failure analysis report schema
```

## Task 3: Add FailureAnalysis API

Goal: Create deterministic mock FailureAnalysis records from failed TestRun or
TestResult evidence.

Expected files:

- `backend/app/modules/reporting/router.py`
- `backend/app/modules/reporting/service.py`
- `backend/app/modules/reporting/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_report_failure_analysis.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q
```

Acceptance:

- Adds `POST /api/test-runs/{id}/failure-analysis`.
- Adds `GET /api/test-runs/{id}/failure-analysis`.
- Creates a succeeded AITask with mock FailureAnalysis output.
- Classifies from available stdout/stderr/TestResult/artifact evidence.
- Returns `insufficient_evidence` when evidence is missing.
- Does not create repair tasks or reports.

Commit message:

```text
feat(reporting): add failure analysis api
```

## Task 4: Add Automation Execution Report API

Goal: Create evidence-backed automation_execution reports for TestRun records.

Expected files:

- `backend/app/modules/reporting/router.py`
- `backend/app/modules/reporting/service.py`
- `backend/app/modules/reporting/schemas.py`
- `backend/app/tests/api/test_report_failure_analysis.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_report_failure_analysis.py -q
```

Acceptance:

- Adds `POST /api/reports`.
- Adds `GET /api/reports/{id}`.
- Supports `report_type=automation_execution` with `related_entity_type=TestRun`.
- Writes report_md/report_json/evidence_manifest artifact metadata.
- Report conclusion cites TestRun parsed_result, TestResult rows, and artifacts.
- Does not create CI/CD quality reports or QualityGateDecision records.

Commit message:

```text
feat(reporting): add automation execution report api
```

## Task 5: Add Report And FailureAnalysis Frontend Shell

Goal: Let users inspect failure analysis and automation execution reports with
evidence shown before AI explanation.

Expected files:

- `frontend/src/api/reporting.ts`
- `frontend/src/stores/reporting.ts`
- `frontend/src/views/reporting/ReportFailureAnalysisView.vue`
- `frontend/src/views/reporting/ReportFailureAnalysisView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- Adds workbench navigation for Report/FailureAnalysis.
- Starts FailureAnalysis for a TestRun and shows classification/confidence.
- Starts automation_execution Report generation and shows conclusion, summary,
  metrics, artifact references, and evidence manifest status.
- Shows evidence before AI explanation.
- Does not add CI/CD quality gates, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions.

Commit message:

```text
feat(frontend): add report failure analysis shell
```

## Task 6: Add Automation Execution Report Golden Smoke

Goal: Prove a golden TestRun can produce FailureAnalysis when failed and an
automation_execution Report with evidence manifest artifacts.

Expected files:

- `backend/app/tests/golden/test_report_failure_analysis_golden.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_report_failure_analysis_golden.py -q
```

Acceptance:

- Reuses golden pytest or Playwright TestRun setup.
- Creates FailureAnalysis for a failed run or verifies skipped analysis for a
  passed run.
- Creates automation_execution Report for a TestRun.
- Persists `evidence_manifest.json` artifact metadata.
- Report conclusion references TestRun/TestResult/artifact evidence.
- Does not create CI/CD QualityGateDecision records.

Non-goals:

- Do not add CI/CD quality gates.
- Do not add repair task execution.
- Do not add RAG runtime or MCP runtime.
- Do not add RBAC, tenants, or permissions.
- Do not build broad report center analytics.

Commit message:

```text
test(golden): add report failure analysis smoke
```

## Slice Completion Gate

- FailureAnalysis and Report contracts are aligned.
- FailureAnalysis API creates evidence-backed classifications.
- Report API creates automation_execution reports with evidence manifests.
- Frontend shows evidence before AI explanation.
- Golden smoke proves TestRun -> FailureAnalysis/Report evidence.
- No CI/CD quality gates, RAG runtime, MCP runtime, RBAC, tenants, permissions,
  or broad report analytics are added.
