# Slice 25: Execution Evidence Summary Task Plan

## Goal

Make execution evidence easier to understand after artifacts become openable.

This slice connects the existing report evidence manifest, TestRun artifacts,
and Slice 24 local artifact download links into a compact evidence summary. It
helps a test engineer answer: which evidence exists, which claim it supports,
which artifacts can be opened locally, and which evidence is missing.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- Recent evidence slices:
  - `docs/implementation/slices/slice-14-report-and-failure-analysis.md`
  - `docs/implementation/slices/slice-24-local-artifact-access-links.md`

## Product Value Answer

After this slice, the report/evidence surface explains the execution evidence
package instead of only listing raw artifact rows. Reviewers can see required
evidence, supporting claims, missing evidence, and local download links in one
place.

## Preconditions

- `GET /api/artifacts/{artifact_id}/download` already provides read-only local
  artifact access.
- `GET /api/test-runs/{id}` already returns TestRun artifact metadata.
- `GET /api/reports/{id}` already returns `evidence_manifest` and report
  artifacts.
- The report frontend page already renders an evidence manifest table and a
  report artifact table.

## Non-goals

- No report generation behavior changes.
- No automatic Report, FailureAnalysis, QualityGateDecision, or repair task
  creation.
- No pytest, Playwright, Newman, JMeter, ToolDefinition, or runner behavior
  changes.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  retention policy, indexing, search, dashboard, or broad artifact browser.
- No external artifact fetch, remote CI provider calls, credentials, OAuth,
  RBAC, tenants, permissions, RAG runtime, MCP runtime, marketplace, cloud sync,
  analytics, trend charts, or model benchmark.

## Slice Boundary

- Define a read-only execution evidence summary contract for existing Report and
  TestRun evidence.
- Prefer deriving summary rows from existing `ReportRead.evidence_manifest` and
  `ReportRead.artifacts`; add backend schema only if needed for stable UI.
- Add local artifact links for evidence/report artifacts that are persisted
  local Artifact rows.
- Mark missing evidence and external imported references as not locally
  openable.
- Add focused frontend and golden coverage for summary readability and artifact
  access boundaries.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Execution Evidence Summary task plan | done | `test -f docs/implementation/slices/slice-25-execution-evidence-summary.md && rg -n "Execution Evidence Summary|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-25-execution-evidence-summary.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md && git diff --check` | pending | planning-only scope |
| Define execution evidence summary contract | done | `rg -n "execution evidence summary|evidence summary|download|missing evidence" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-25-execution-evidence-summary.md && git diff --check` | pending | contract-only |
| Add report evidence summary frontend | planned | `npm --prefix frontend run test -- --run src/views/reporting/ReportFailureAnalysisView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | report page only |
| Add execution evidence summary golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_evidence_summary_golden.py -q && git diff --check` | pending | evidence summary proof |
| Slice 25 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_evidence_summary_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q && npm --prefix frontend run build && npm --prefix frontend run test -- --run && git diff --check` | pending | docs and handoff |

## Task 1: Add Execution Evidence Summary Task Plan

Goal: Define the smallest execution evidence summary slice before contracts or
frontend changes.

Expected files:

- `docs/implementation/slices/slice-25-execution-evidence-summary.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-25-execution-evidence-summary.md
rg -n "Execution Evidence Summary|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-25-execution-evidence-summary.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 25 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to read-only evidence summary and local artifact links.
- Does not add product code, backend code, frontend code, migrations, package
  upgrades, or tests.

Commit message:

```text
docs(v2): add execution evidence summary plan
```

## Task 2: Define Execution Evidence Summary Contract

Goal: Clarify the read-only evidence summary shape and artifact access boundary.

Expected files:

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-25-execution-evidence-summary.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "execution evidence summary|evidence summary|download|missing evidence" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-25-execution-evidence-summary.md
git diff --check
```

Acceptance:

- API contract defines how report evidence summary rows align
  `evidence_manifest.evidence[]`, local Artifact metadata, downloadability, and
  missing evidence.
- Artifact contract states evidence summary display is read-only and must use
  the existing local artifact access endpoint for local Artifact rows.
- External imported artifact references remain inert and not locally openable.
- Contract excludes report generation, runner behavior, QualityGateDecision,
  and broad artifact browser changes.

Commit message:

```text
docs(v2): define execution evidence summary contract
```

## Task 3: Add Report Evidence Summary Frontend

Goal: Make the report page show evidence summary rows with local artifact links.

Expected files:

- `frontend/src/views/reporting/ReportFailureAnalysisView.vue`
- `frontend/src/views/reporting/ReportFailureAnalysisView.spec.ts`
- `docs/implementation/slices/slice-25-execution-evidence-summary.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run test -- --run src/views/reporting/ReportFailureAnalysisView.spec.ts
npm --prefix frontend run build
git diff --check
```

Acceptance:

- Evidence summary rows show supporting claim, required status, local artifact
  type, and open link when a local Artifact id is available.
- Missing evidence stays visible and is not shown as downloadable.
- Existing failure analysis, report summary, metrics, and report artifact
  metadata remain visible.
- Does not add a report editor, broad redesign, export workflow, upload, delete,
  sharing, or cloud storage UI.

Commit message:

```text
feat(frontend): summarize execution evidence
```

## Task 4: Add Execution Evidence Summary Golden Smoke

Goal: Prove the execution evidence summary stays tied to persisted evidence and
local artifact access boundaries.

Expected files:

- `backend/app/tests/golden/test_execution_evidence_summary_golden.py`
- `docs/fixtures/13-execution-evidence-summary-golden.md`
- `docs/implementation/slices/slice-25-execution-evidence-summary.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_evidence_summary_golden.py -q
git diff --check
```

Acceptance:

- Golden proves report evidence manifest rows cite persisted local Artifact ids.
- Golden proves locally cited artifacts can be read through the artifact access
  endpoint and match persisted sha256/size metadata.
- Golden proves missing evidence remains explicit and is not treated as passed
  evidence.
- Golden keeps external imported artifact references inert.

Commit message:

```text
test(golden): add execution evidence summary smoke
```

## Slice 25 Completion Gate

Goal: Validate execution evidence summary end to end and hand off the next V2
task.

Expected files:

- `docs/implementation/slices/slice-25-execution-evidence-summary.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_execution_evidence_summary_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- All Slice 25 task rows are marked done with commit ids.
- Completion evidence records golden, frontend build/test, and diff
  verification.
- Non-goals remain excluded.
- Handoff names the next V2 slice or planning task.

Commit message:

```text
docs(v2): complete execution evidence summary slice
```
