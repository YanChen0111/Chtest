# Slice 15: CI/CD Quality Center Foundation Task Plan

## Goal

Add the local-first CI/CD Quality Center foundation for CICDRun,
CICDChangedFile, local diff analysis, and an evidence surface.

This slice must not add merge/release decisions, remote CI provider integration,
webhooks, PR comments, UnitTestPatch application, QualityGateDecision records,
RAG runtime, MCP runtime, RBAC, tenants, or permissions.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/product/03-user-journey-and-page-prd.md`
- `docs/product/06-frontend-ui-guidelines.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/fixtures/03-golden-cicd-quality.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`

## Preconditions

- Slice 3 Project Core exists with Project and Repository records.
- Slice 12 TestRunner Pytest Execution exists for later regression tasks.
- Slice 14 Report And Failure Analysis is complete.
- API contract already defines `/api/cicd` workflow boundaries.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add CI/CD Quality Center task plan | done | `test -f docs/implementation/slices/slice-15-cicd-quality-center.md && rg -n "CI/CD Quality Center|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-15-cicd-quality-center.md` | pending commit | scoped local-first Slice 15 plan |
| Add CI/CD Quality Center contract boundary | planned | `rg -n "CICDRun|CICDChangedFile|POST /api/cicd/runs|local_diff|remote CI" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-15-cicd-quality-center.md` | - | tighten Slice 15 subset before code |
| Add CICDRun and CICDChangedFile model/schema | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q` | - | persistence only, no patch/gate |
| Add local diff parser service | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q` | - | deterministic parser for unified diff text |
| Add CI/CD run create/list/get API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q` | - | `/api/cicd/runs` local_diff only |
| Add CI/CD analyze API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q` | - | mock risk_analysis artifact |
| Add CI/CD Quality Center frontend shell | planned | `npm --prefix frontend run test -- --run` | - | local diff evidence view; no quality gate decision |
| Add CI/CD Quality Center golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_center_golden.py -q` | - | local diff -> CICDRun -> changed files -> analysis artifact |
| Slice 15 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py backend/app/tests/golden/test_cicd_quality_center_golden.py -q && npm --prefix frontend run test -- --run` | - | docs and handoff only |

## Task 1: Add CI/CD Quality Center Contract Boundary

Goal: Tighten the existing CI/CD Quality contract to the Slice 15 foundation
subset before implementation.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "CICDRun|CICDChangedFile|POST /api/cicd/runs|local_diff|remote CI" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-15-cicd-quality-center.md
```

Acceptance:

- Contract states Slice 15 supports local_diff/manual source only.
- Contract separates foundation endpoints from Slice 16 UnitTestPatch,
  regression, and QualityGateDecision work.
- Contract defines changed file evidence and risk_analysis artifact metadata.
- Contract explicitly excludes merge/release decisions, remote CI provider
  integration, webhooks, PR comments, RAG runtime, MCP runtime, RBAC, tenants,
  and permissions.

Commit message:

```text
docs(cicd): define quality center foundation boundary
```

## Task 2: Add CICDRun And CICDChangedFile Model Schema

Goal: Persist CICDRun and CICDChangedFile records aligned with the data model
contract.

Expected files:

- `backend/app/modules/cicd/__init__.py`
- `backend/app/modules/cicd/models.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_cicd_quality_center.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

Acceptance:

- Defines CICDRun fields from the data model contract.
- Defines CICDChangedFile fields from the data model contract.
- Defines create/read/list schemas for CICDRun and changed files.
- Does not create UnitTestPatch, QualityGateDecision, TestRun, or Report
  records in this task.

Commit message:

```text
feat(cicd): add quality center run schema
```

## Task 3: Add Local Diff Parser Service

Goal: Convert a local unified diff into deterministic CICDChangedFile records
and a changed_files artifact shape.

Expected files:

- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_cicd_quality_center.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

Acceptance:

- Parses added/modified/deleted/renamed file headers from unified diff text.
- Classifies file_role as source, test, docs, config, migration, fixture,
  build, or unknown.
- Assigns deterministic low/medium/high risk from file role and line counts.
- Produces changed_files metadata compatible with `changed_files.json`.
- Does not run git commands against remote providers.

Commit message:

```text
feat(cicd): add local diff parser
```

## Task 4: Add CI/CD Run Create/List/Get API

Goal: Create and retrieve local-first CICDRun records with changed file evidence.

Expected files:

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/main.py`
- `backend/app/tests/api/test_cicd_quality_center.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

Acceptance:

- Adds `POST /api/cicd/runs`.
- Adds `GET /api/cicd/runs`.
- Adds `GET /api/cicd/runs/{id}`.
- Supports V1 `source_type=local_diff`, `trigger_type=manual`,
  `provider=local`.
- Persists CICDChangedFile rows when diff text is supplied.
- Does not create UnitTestPatch, TestRun, QualityGateDecision, or Report
  records.

Commit message:

```text
feat(cicd): add quality run api
```

## Task 5: Add CI/CD Analyze API

Goal: Add deterministic mock change analysis for CICDRun evidence.

Expected files:

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_cicd_quality_center.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_cicd_quality_center.py -q
```

Acceptance:

- Adds `POST /api/cicd/runs/{id}/analyze`.
- Creates a succeeded AITask with mock CICDChangeAnalysisAgent output.
- Updates CICDRun status to `analyzed` and overall_risk from changed files.
- Writes risk_analysis artifact metadata owned by CICDRun.
- Does not create UnitTestPatch, regression plan, QualityGateDecision, or Report
  records.

Commit message:

```text
feat(cicd): add change analysis api
```

## Task 6: Add CI/CD Quality Center Frontend Shell

Goal: Let users inspect local diff evidence and change risk before UnitTestPatch
work begins.

Expected files:

- `frontend/src/api/cicd.ts`
- `frontend/src/stores/cicd.ts`
- `frontend/src/views/cicd/CicdQualityCenterView.vue`
- `frontend/src/views/cicd/CicdQualityCenterView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/stores/index.ts`

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- Adds workbench navigation for `CI/CD 质量中心`.
- Creates a local_diff CICDRun from project/repository/base/head inputs and
  diff text fixture.
- Shows changed files, file roles, risk levels, risk reasons, and analysis
  artifact references.
- Does not show merge/release decisions or remote CI provider controls.

Commit message:

```text
feat(frontend): add cicd quality shell
```

## Task 7: Add CI/CD Quality Center Golden Smoke

Goal: Prove local diff evidence can create a CICDRun, changed files, and a mock
analysis artifact.

Expected files:

- `backend/app/tests/golden/test_cicd_quality_center_golden.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_center_golden.py -q
```

Acceptance:

- Uses `docs/fixtures/03-golden-cicd-quality.md` as scenario intent.
- Creates Project/Repository fixture records.
- Creates CICDRun from local diff input.
- Persists CICDChangedFile rows and risk_analysis artifact metadata.
- Verifies no UnitTestPatch, QualityGateDecision, TestRun, or Report records are
  created in Slice 15.

Commit message:

```text
test(golden): add cicd quality smoke
```

## Slice Completion Gate

- CICDRun and CICDChangedFile contracts are aligned.
- Local diff parser produces deterministic changed file evidence.
- CI/CD run API creates/list/gets local-first runs.
- Analyze API creates mock risk analysis evidence.
- Frontend shows local diff evidence before later UnitTestPatch or gate work.
- Golden smoke proves local diff -> CICDRun -> changed files -> analysis
  artifact evidence.

## Non-goals

- Do not add UnitTestPatch generation, approval, or application in Slice 15.
- Do not run new tests or regression from CI/CD endpoints in Slice 15.
- Do not compute QualityGateDecision records in Slice 15.
- Do not create CI/CD quality Reports in Slice 15.
- Do not integrate GitHub Actions, GitLab CI, Jenkins, webhooks, PR comments, or
  remote status checks.
- Do not trigger merge, push, release, or deployment actions.
- Do not add RAG runtime, MCP runtime, RBAC, tenants, or permissions.
