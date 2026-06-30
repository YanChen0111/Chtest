# Slice 16: UnitTestPatch And Regression Task Plan

## Goal

Add the review-gated UnitTestPatch and regression workflow on top of Slice 15
local CI/CD quality evidence.

This slice covers UnitTestPatch generation, PatchScopeGate validation, explicit
human review, approved patch application, pytest new-test/regression execution,
QualityGateDecision evidence, and CI/CD quality report generation. It must not
perform merge, push, release, deployment, remote CI provider integration, RAG
runtime, MCP runtime, RBAC, tenants, or permissions work.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/product/03-user-journey-and-page-prd.md`
- `docs/product/06-frontend-ui-guidelines.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/contracts/06-error-code-contract.md`
- `docs/fixtures/03-golden-cicd-quality.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`

## Preconditions

- Slice 15 CI/CD Quality Center Foundation is complete.
- CICDRun and CICDChangedFile records exist.
- `risk_analysis.json` artifact metadata can be created for CICDRun.
- Slice 12 pytest execution is available for new tests and regression.
- Slice 14 Report API can create evidence-backed reports.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add UnitTestPatch And Regression task plan | done | `test -f docs/implementation/slices/slice-16-unit-test-patch-regression.md && rg -n "UnitTestPatch|PatchScopeGate|Verification Command|Non-goals" docs/implementation/slices/slice-16-unit-test-patch-regression.md` | `c0db91c` | scoped Slice 16 plan |
| Add UnitTestPatch and regression contract boundary | done | `rg -n "UnitTestPatch|PatchScopeGate|QualityGateDecision|run-new-tests|run-regression" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-16-unit-test-patch-regression.md` | `c164d88` | contract-first Slice 16 subset |
| Add UnitTestPatch and QualityGateDecision model/schema | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q` | pending commit | persistence only |
| Add PatchScopeGate service | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q` | - | blocks non-test path changes |
| Add UnitTestPatch generation/review API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q` | - | generate/approve/reject only |
| Add UnitTestPatch apply API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q` | - | applies approved test-only patch artifact |
| Add run-new-tests and regression API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q` | - | creates CICD-linked TestRun records |
| Add QualityGateDecision API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q` | - | passed/failed/needs_review evidence |
| Add CI/CD quality report API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q` | - | Report with report_type=cicd_quality |
| Add UnitTestPatch frontend shell | planned | `npm --prefix frontend run test -- --run` | - | patch review, scope gate, regression status |
| Add UnitTestPatch golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q` | - | golden diff -> patch -> tests -> gate/report |
| Slice 16 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q && npm --prefix frontend run test -- --run` | - | docs and handoff only |

## Task 1: Add UnitTestPatch And Regression Contract Boundary

Goal: Tighten the Slice 16 contract before implementation.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `NEXT_AI_TASK.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "UnitTestPatch|PatchScopeGate|QualityGateDecision|run-new-tests|run-regression" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

Acceptance:

- Contract requires UnitTestPatch to be review-gated.
- Contract requires PatchScopeGate to reject non-test path modifications.
- Contract defines new-test and regression TestRun evidence.
- Contract defines QualityGateDecision `passed`, `failed`, and `needs_review`
  evidence requirements.
- Contract excludes merge, push, release, deployment, remote CI provider
  integration, RAG runtime, MCP runtime, RBAC, tenants, and permissions.

Commit message:

```text
docs(cicd): define unit test patch boundary
```

## Task 2: Add UnitTestPatch And QualityGateDecision Model Schema

Goal: Persist UnitTestPatch and QualityGateDecision records aligned with the
data model contract.

Expected files:

- `backend/app/modules/cicd/models.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Acceptance:

- Defines UnitTestPatch fields from the data model contract.
- Defines QualityGateDecision fields from the data model contract.
- Defines create/read schemas for patch and gate records.
- Does not apply patches or run tests in this task.

Commit message:

```text
feat(cicd): add unit test patch schema
```

## Task 3: Add PatchScopeGate Service

Goal: Validate UnitTestPatch unified diff scope before approval/application.

Expected files:

- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Acceptance:

- Allows changes under test directories only.
- Rejects business source path changes with `PATCH_SCOPE_REJECTED` semantics.
- Produces `patch_scope_gate.json` compatible metadata.
- Does not mutate repository files.

Commit message:

```text
feat(cicd): add patch scope gate
```

## Task 4: Add UnitTestPatch Generation And Review API

Goal: Generate deterministic mock UnitTestPatch candidates and review them.

Expected files:

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Acceptance:

- Adds `POST /api/cicd/runs/{id}/unit-test-patches`.
- Adds approve/reject endpoints.
- Creates succeeded AITask with mock UnitTestAgent output.
- Persists UnitTestPatch with scope_gate_result_json.
- `scope_rejected` patches cannot be approved.
- Does not apply patches or run tests in this task.

Commit message:

```text
feat(cicd): add unit test patch review api
```

## Task 5: Add UnitTestPatch Apply API

Goal: Apply approved test-only patches as evidence artifacts in a controlled
local workflow.

Expected files:

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Acceptance:

- Adds `POST /api/cicd/unit-test-patches/{id}/apply`.
- Only approved patches can be applied.
- PatchScopeGate must pass before application.
- Writes `unit_test.patch` and applied patch artifact metadata.
- Does not modify business source files.

Commit message:

```text
feat(cicd): add unit test patch apply api
```

## Task 6: Add New-Test And Regression API

Goal: Execute new tests and selected regression commands as CICD-linked TestRun
records.

Expected files:

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Acceptance:

- Adds `POST /api/cicd/runs/{id}/run-new-tests`.
- Adds `POST /api/cicd/runs/{id}/select-regression`.
- Adds `POST /api/cicd/runs/{id}/run-regression`.
- Creates TestRun records with `cicd_run_id` set.
- Writes `regression_plan.json` artifact metadata.
- Uses allowlisted TestCommand records.

Commit message:

```text
feat(cicd): add regression execution api
```

## Task 7: Add QualityGateDecision API

Goal: Compute evidence-backed CI/CD quality decisions.

Expected files:

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Acceptance:

- Adds `POST /api/cicd/runs/{id}/quality-gate`.
- Creates a new QualityGateDecision on each compute.
- Updates `CICDRun.quality_gate_status`.
- Missing required evidence returns `needs_review`, not `passed`.
- QualityGateDecision does not trigger merge, push, release, or deployment.

Commit message:

```text
feat(cicd): add quality gate decision api
```

## Task 8: Add CI/CD Quality Report API

Goal: Generate a CI/CD quality report backed by QualityGateDecision and evidence
artifacts.

Expected files:

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_unit_test_patch_regression.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Acceptance:

- Adds `POST /api/cicd/runs/{id}/generate-report`.
- Creates Report with `report_type=cicd_quality`.
- Report conclusion cites latest QualityGateDecision and evidence artifacts.
- Does not override gate status without evidence.

Commit message:

```text
feat(cicd): add quality report api
```

## Task 9: Add UnitTestPatch Frontend Shell

Goal: Let users review generated UnitTestPatch candidates, scope gate results,
and test/regression evidence.

Expected files:

- `frontend/src/api/cicd.ts`
- `frontend/src/stores/cicd.ts`
- `frontend/src/views/cicd/CicdQualityCenterView.vue`
- `frontend/src/views/cicd/CicdQualityCenterView.spec.ts`

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- Shows UnitTestPatch diff, test intent, coverage target, and scope gate result.
- Supports approve/reject actions.
- Shows new-test and regression TestRun summaries.
- Shows QualityGateDecision and report artifact references.
- Does not expose merge, release, or remote CI provider controls.

Commit message:

```text
feat(frontend): add unit test patch shell
```

## Task 10: Add UnitTestPatch Golden Smoke

Goal: Prove the golden local diff can flow through UnitTestPatch review, test
execution, regression selection, quality gate, and report evidence.

Expected files:

- `backend/app/tests/golden/test_unit_test_patch_regression_golden.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
```

Acceptance:

- Uses `docs/fixtures/03-golden-cicd-quality.md`.
- Creates CICDRun from local diff.
- Generates UnitTestPatch and verifies PatchScopeGate.
- Approves and applies test-only patch.
- Runs new tests and regression as CICD-linked TestRun records.
- Computes QualityGateDecision.
- Generates CI/CD quality Report.
- Verifies no merge, push, release, deployment, remote CI provider, RAG runtime,
  MCP runtime, RBAC, tenants, or permissions behavior.

Commit message:

```text
test(golden): add unit test patch smoke
```

## Slice Completion Gate

- UnitTestPatch and QualityGateDecision contracts are aligned.
- PatchScopeGate blocks non-test file modifications.
- UnitTestPatch lifecycle is review-gated.
- Approved patches can be applied through controlled local evidence flow.
- New-test and regression execution create CICD-linked TestRun records.
- QualityGateDecision uses evidence and never triggers merge/release actions.
- CI/CD quality Report cites latest gate and artifacts.
- Frontend exposes patch review and evidence without remote CI controls.
- Golden smoke proves local diff -> UnitTestPatch -> tests/regression -> gate ->
  report evidence.

## Non-goals

- Do not trigger merge, push, release, or deployment actions.
- Do not integrate GitHub Actions, GitLab CI, Jenkins, webhooks, PR comments, or
  remote status checks.
- Do not add RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- Do not allow UnitTestPatch to modify business source files.
