# Slice 24: Local Artifact Access Links Task Plan

## Goal

Make local evidence artifacts directly accessible from Chtest without changing
runner behavior or adding cloud storage.

This slice turns artifact rows that are already persisted for TestRun evidence
into controlled local read/download links. It is intentionally read-only and
local-first.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- Recent execution slices:
  - `docs/implementation/slices/slice-18-newman-api-execution.md`
  - `docs/implementation/slices/slice-22-jmeter-local-execution.md`

## Product Value Answer

After this slice, a test engineer can open or download local TestRun artifacts
from the execution evidence table, instead of seeing only a file path. This
strengthens the evidence loop for stdout/stderr, parsed output, JTL, Newman
JSON, traces, screenshots, and future runner artifacts.

## Preconditions

- Artifact metadata and `LocalArtifactStore.read_bytes` already exist.
- TestRun execution APIs already return artifact metadata.
- Frontend execution pages already render artifact tables for pytest,
  Playwright, Newman, and JMeter.

## Non-goals

- No artifact upload UI, mutation, delete, retention policy, search, indexing,
  broad artifact browser, or dashboard.
- No cloud storage, signed URLs, public sharing, external provider fetch,
  remote CI artifact download, credentials, secrets, OAuth, RBAC, tenants,
  permissions, marketplace, RAG runtime, or MCP runtime.
- No runner behavior changes.
- No report auto-generation or QualityGateDecision changes.

## Slice Boundary

- Define a read-only local artifact access API for persisted Artifact rows.
- Restrict access to local artifact files under the configured artifact root.
- Use existing artifact metadata for MIME type and filename behavior.
- Add frontend links only to existing execution artifact tables.
- Keep external CI imported artifact references inert and out of this slice.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Local Artifact Access Links task plan | done | `test -f docs/implementation/slices/slice-24-local-artifact-access-links.md && rg -n "Local Artifact Access Links|artifact|download|Non-goals|Task Table" docs/implementation/slices/slice-24-local-artifact-access-links.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md` | `e06c94b` | planning-only scope |
| Define local artifact access contract | done | `rg -n "artifact access|download|GET /api/artifacts|Artifact" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-24-local-artifact-access-links.md && git diff --check` | pending | contract-only |
| Add backend artifact download API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py -q` | pending | read-only local files |
| Add frontend artifact links | planned | `npm --prefix frontend run build && npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts` | pending | execution tables only |
| Add artifact access golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_artifact_access_golden.py -q` | pending | evidence open proof |
| Slice 24 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py backend/app/tests/golden/test_artifact_access_golden.py -q && npm --prefix frontend run build && npm --prefix frontend run test -- --run && git diff --check` | pending | docs and handoff |

## Task 1: Add Local Artifact Access Links Task Plan

Goal: Define the smallest local artifact access slice before contracts or code.

Expected files:

- `docs/implementation/slices/slice-24-local-artifact-access-links.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-24-local-artifact-access-links.md
rg -n "Local Artifact Access Links|artifact|download|Non-goals|Task Table" docs/implementation/slices/slice-24-local-artifact-access-links.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 24 plan.
- Defines product value, non-goals, slice boundary, task table, expected files,
  verification commands, and commit messages.
- Keeps scope read-only and local-first.
- Does not add product code, backend code, frontend code, migrations, package
  upgrades, or tests.

Commit message:

```text
docs(v2): add local artifact access plan
```

## Task 2: Define Local Artifact Access Contract

Goal: Define the API and artifact-safety contract before implementation.

Expected files:

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-24-local-artifact-access-links.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "artifact access|download|GET /api/artifacts|Artifact" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-24-local-artifact-access-links.md
git diff --check
```

Acceptance:

- API contract defines a read-only artifact content/download endpoint.
- Artifact contract defines local-root path safety, MIME/filename handling, and
  content access boundaries.
- External imported artifact references remain inert and unavailable through the
  local download endpoint.
- Non-goals remain explicit.

Commit message:

```text
docs(v2): define artifact access contract
```

## Task 3: Add Backend Artifact Download API

Goal: Add the read-only local artifact access endpoint.

Expected files:

- backend artifact API/router/service files needed for local read access
- `backend/app/tests/api/test_artifact_access.py`
- `docs/implementation/slices/slice-24-local-artifact-access-links.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py -q
```

Acceptance:

- Reads only persisted Artifact rows with local `file_path` values under the
  artifact root.
- Returns content with recorded MIME type and safe download filename behavior.
- Rejects missing artifacts and unsafe paths.
- Does not mutate artifact rows or files.

Commit message:

```text
feat(artifact): add local artifact access api
```

## Task 4: Add Frontend Artifact Links

Goal: Add controlled links to existing execution artifact tables.

Expected files:

- `frontend/src/api/execution.ts` or a focused artifact API helper
- execution view files that render artifact tables
- focused execution view tests
- `docs/implementation/slices/slice-24-local-artifact-access-links.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run src/views/execution/JMeterExecutionView.spec.ts src/views/execution/NewmanExecutionView.spec.ts src/views/execution/PytestExecutionView.spec.ts src/views/execution/PlaywrightExecutionView.spec.ts
```

Acceptance:

- Execution artifact tables expose local artifact access links.
- Links preserve existing artifact metadata display.
- Chinese-facing labels remain readable while keeping product terms such as
  Artifact, TestRun, JTL, and trace unchanged.
- Does not add a broad artifact dashboard, upload, delete, sharing, or cloud
  storage UI.

Commit message:

```text
feat(frontend): link local execution artifacts
```

## Task 5: Add Artifact Access Golden Smoke

Goal: Prove a persisted execution artifact can be accessed through the local
evidence loop.

Expected files:

- `backend/app/tests/golden/test_artifact_access_golden.py`
- `docs/fixtures/12-local-artifact-access-golden.md`
- `docs/implementation/slices/slice-24-local-artifact-access-links.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_artifact_access_golden.py -q
```

Acceptance:

- Golden proves a TestRun artifact can be read through the local artifact
  endpoint.
- Golden proves artifact content matches persisted sha256/size metadata.
- Golden proves external imported artifact references remain inert.

Commit message:

```text
test(golden): add local artifact access smoke
```

## Slice 24 Completion Gate

Goal: Validate local artifact access end to end and hand off the next V2 task.

Expected files:

- `docs/implementation/slices/slice-24-local-artifact-access-links.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_artifact_access.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- All Slice 24 task rows are marked done with commit ids.
- Completion evidence records backend, golden, frontend build/test, and diff
  verification.
- Non-goals remain excluded.
- Handoff names the next V2 slice or planning task.

Commit message:

```text
docs(v2): complete local artifact access slice
```
