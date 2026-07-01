# Slice 28: CI/CD Quality Gate Evidence Summary Task Plan

## Goal

Make CI/CD quality gate decisions easier to understand by showing the required
evidence, blocking reasons, and local artifact availability in the CI/CD
Quality Center.

Slice 16 already computes QualityGateDecision from UnitTestPatch, new-test, and
regression evidence. Slice 24 made local artifacts openable. Slice 25 clarified
report evidence summaries. Slice 28 applies the same evidence-readability
pattern to the CI/CD quality gate panel without changing gate computation.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- Recent evidence slices:
  - `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
  - `docs/implementation/slices/slice-24-local-artifact-access-links.md`
  - `docs/implementation/slices/slice-25-execution-evidence-summary.md`
  - `docs/implementation/slices/slice-27-ai-task-evidence-artifact-links.md`

## Product Value Answer

After this slice, a test engineer can read why a CI/CD quality gate passed,
failed, or needs review from the quality panel itself. The page should show
which required evidence is present, which evidence is missing or blocking, and
which persisted local artifacts can be opened.

## Preconditions

- QualityGateDecision already records `status`, `summary`,
  `blocking_reasons`, `evidence_artifact_ids`, and `status_detail`.
- CI/CD Quality Center already calls `computeQualityGate` and stores the latest
  QualityGateDecision in frontend state.
- Local artifact access already supports persisted local Artifact rows.
- CI/CD quality reports already write an evidence manifest, but report
  generation is not required for gate summary display.

## Non-goals

- No QualityGateDecision computation changes.
- No new quality gate scoring model, risk analytics, dashboards, trends, report
  generation behavior, automatic report creation, or FailureAnalysis behavior.
- No remote CI provider API calls, external artifact fetch, PR comments, commit
  statuses, reruns, deploy/release controls, credentials, OAuth, webhooks, or
  scheduling.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  broad artifact browser, indexing, search, RBAC, tenants, permissions, RAG
  runtime, MCP runtime, marketplace, or package upgrades.

## Slice Boundary

- Define a read-only CI/CD quality gate evidence summary contract derived from
  existing QualityGateDecision fields and existing Artifact metadata.
- Add a compact frontend summary in the CI/CD Quality Center quality gate panel:
  - gate status and summary;
  - required evidence rows for UnitTestPatch, new-test, and regression;
  - blocking reasons translated into readable Chinese labels;
  - local artifact links only for persisted local Artifact ids;
  - missing evidence shown as unavailable, not hidden.
- Add focused frontend coverage and one golden/API smoke proving summary inputs
  remain evidence-only.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add CI/CD Quality Gate Evidence Summary task plan | done | `test -f docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md && rg -n "CI/CD Quality Gate Evidence Summary|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md && git diff --check` | `3ca3db0` | planning-only scope |
| Define quality gate evidence summary contract | done | `rg -n "quality gate evidence summary|required evidence|blocking reasons|local artifact" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md && git diff --check` | pending | contract-only |
| Add CI/CD quality gate frontend summary | planned | `npm --prefix frontend run test -- --run src/views/cicd/CicdQualityCenterView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | CI/CD page only |
| Add quality gate evidence summary golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_gate_evidence_summary_golden.py -q && git diff --check` | pending | evidence-only proof |
| Slice 28 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_gate_evidence_summary_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q && npm --prefix frontend run build && npm --prefix frontend run test -- --run && git diff --check` | pending | docs and handoff |

## Task 1: Add CI/CD Quality Gate Evidence Summary Task Plan

Goal: Define the smallest quality gate evidence summary slice before contracts
or frontend changes.

Expected files:

- `docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md
rg -n "CI/CD Quality Gate Evidence Summary|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 28 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to quality gate evidence readability.
- Does not add product code, backend code, frontend code, migrations, package
  upgrades, or tests.

Commit message:

```text
docs(v2): add quality gate evidence summary plan
```

## Task 2: Define Quality Gate Evidence Summary Contract

Goal: Clarify the read-only summary derived from existing QualityGateDecision
and Artifact evidence.

Expected files:

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "quality gate evidence summary|required evidence|blocking reasons|local artifact" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md
git diff --check
```

Acceptance:

- API contract defines the evidence summary as presentation derived from
  QualityGateDecision fields and existing Artifact metadata.
- Artifact contract states summary links are read-only local Artifact links and
  missing evidence remains visible but not downloadable.
- Contract preserves the no computation, report generation, runner, or remote
  provider behavior change boundary.

Commit message:

```text
docs(v2): define quality gate evidence summary contract
```

## Task 3: Add CI/CD Quality Gate Frontend Summary

Goal: Make quality gate evidence readable in the CI/CD Quality Center.

Expected files:

- `frontend/src/views/cicd/CicdQualityCenterView.vue`
- `frontend/src/views/cicd/CicdQualityCenterView.spec.ts`
- `docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/cicd/CicdQualityCenterView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Quality gate panel shows status, summary, required evidence, and blocking
  reasons in readable Chinese.
- Missing UnitTestPatch, new-test, or regression evidence is visible as
  unavailable evidence.
- Local artifact links are rendered only for persisted local Artifact ids.
- Page still excludes remote provider control wording or actions.

Commit message:

```text
feat(frontend): summarize quality gate evidence
```

## Task 4: Add Quality Gate Evidence Summary Golden Smoke

Goal: Prove quality gate evidence summary inputs remain existing evidence and
do not change gate behavior.

Expected files:

- `backend/app/tests/golden/test_cicd_quality_gate_evidence_summary_golden.py`
- `docs/fixtures/16-cicd-quality-gate-evidence-summary-golden.md`
- `docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_gate_evidence_summary_golden.py -q
git diff --check
```

Acceptance:

- Golden proves QualityGateDecision keeps `status_detail`, blocking reasons,
  and evidence Artifact ids available for summary display.
- Golden proves missing evidence produces `needs_review` rather than `passed`.
- Golden proves summary display inputs do not create Report, FailureAnalysis,
  remote provider side effects, or artifact mutations.

Commit message:

```text
test(golden): add quality gate evidence summary smoke
```

## Slice 28 Completion Gate

Goal: Validate quality gate evidence summary end to end and hand off the next V2
task.

Expected files:

- `docs/implementation/slices/slice-28-cicd-quality-gate-evidence-summary.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_cicd_quality_gate_evidence_summary_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- All Slice 28 task rows are marked done with commit ids.
- Completion evidence records frontend build/test, golden checks, and diff
  verification.
- Non-goals remain excluded.
- Handoff names the next V2 slice or planning task.

Commit message:

```text
docs(v2): complete quality gate evidence summary slice
```
