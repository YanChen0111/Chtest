# Slice 26: CI Imported Artifact Reference Clarity Task Plan

## Goal

Make imported CI artifact references clearly readable as inert external
references.

Slice 20 already stores external CI artifact references as inert metadata, and
Slice 24 ensures those references cannot be downloaded through local artifact
access. This slice improves the CI/CD Quality Center display so users can see
which references are external, why they are not locally openable, and that no
remote fetch was performed.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- Recent evidence slices:
  - `docs/implementation/slices/slice-20-ci-run-metadata-import.md`
  - `docs/implementation/slices/slice-24-local-artifact-access-links.md`
  - `docs/implementation/slices/slice-25-execution-evidence-summary.md`

## Product Value Answer

After this slice, a user viewing imported CI evidence can distinguish local
Chtest artifacts from external CI artifact references. External references are
shown as useful evidence metadata, while the UI makes clear they are not
locally downloaded or remotely fetched.

## Preconditions

- CI import stores artifact references in `ci_run_metadata.json` metadata.
- Imported artifact references include inert metadata such as name, kind,
  `external_url`, sha256, size, and `inert_reference=true` when supplied.
- Local artifact access rejects external references with `ARTIFACT_NOT_LOCAL`.
- CI/CD Quality Center already renders imported artifact references.

## Non-goals

- No remote CI provider API calls, remote artifact download, proxying,
  authentication, OAuth, credentials, token storage, webhooks, reruns, pipeline
  triggers, cancellation, PR comments, commit statuses, deploy, release, merge,
  push, tag, or scheduling.
- No artifact upload, mutation, delete, sharing, signed URL, cloud storage,
  retention policy, indexing, search, dashboard, or broad artifact browser.
- No QualityGateDecision behavior changes.
- No TestRun, Report, FailureAnalysis, UnitTestPatch, runner, RAG runtime, MCP
  runtime, marketplace, RBAC, tenants, permissions, SSO, or enterprise audit
  work.

## Slice Boundary

- Clarify the API/artifact contract for imported artifact reference display.
- Improve the CI/CD Quality Center imported reference list with:
  - inert/local-openability status;
  - remote-fetch-performed status;
  - external URL as plain reference text;
  - no local download action for external references.
- Add focused frontend coverage and one golden/API smoke proving imported
  external artifact references remain inert.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add CI Imported Artifact Reference Clarity task plan | done | `test -f docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md && rg -n "CI Imported Artifact Reference Clarity|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md && git diff --check` | pending | planning-only scope |
| Define imported artifact reference display contract | planned | `rg -n "imported artifact reference|inert reference|remote_fetch_performed|not locally openable" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md && git diff --check` | pending | contract-only |
| Add CI imported reference frontend clarity | planned | `npm --prefix frontend run test -- --run src/views/cicd/CicdQualityCenterView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | CI/CD page only |
| Add imported reference inert golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py -q && git diff --check` | pending | inert reference proof |
| Slice 26 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q && npm --prefix frontend run build && npm --prefix frontend run test -- --run && git diff --check` | pending | docs and handoff |

## Task 1: Add CI Imported Artifact Reference Clarity Task Plan

Goal: Define the smallest imported artifact reference clarity slice before
contracts or frontend changes.

Expected files:

- `docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md
rg -n "CI Imported Artifact Reference Clarity|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 26 plan.
- Defines product value, preconditions, non-goals, slice boundary, task table,
  expected files, verification commands, and commit messages.
- Keeps scope limited to display clarity and inert-reference proof.
- Does not add product code, backend code, frontend code, migrations, package
  upgrades, or tests.

Commit message:

```text
docs(v2): add ci imported reference clarity plan
```

## Task 2: Define Imported Artifact Reference Display Contract

Goal: Clarify how imported external artifact references must be displayed and
why they are not locally openable.

Expected files:

- `docs/contracts/02-api-contract.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "imported artifact reference|inert reference|remote_fetch_performed|not locally openable" docs/contracts/02-api-contract.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md
git diff --check
```

Acceptance:

- API contract states imported artifact references are display-only external
  references, not local Artifact files.
- Artifact contract states external references must show inert/not-local status
  and must not receive local download links.
- Contract preserves `remote_fetch_performed=false` and external-provider
  non-goals.

Commit message:

```text
docs(v2): define imported reference clarity contract
```

## Task 3: Add CI Imported Reference Frontend Clarity

Goal: Make imported artifact references readable and clearly not locally
openable in CI/CD Quality Center.

Expected files:

- `frontend/src/views/cicd/CicdQualityCenterView.vue`
- `frontend/src/views/cicd/CicdQualityCenterView.spec.ts`
- `docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md`
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

- Imported artifact reference rows show name, kind, external URL, inert status,
  and local-openability status.
- External references do not render local download links.
- The page still excludes remote provider control wording or actions.

Commit message:

```text
feat(frontend): clarify ci imported artifact references
```

## Task 4: Add Imported Reference Inert Golden Smoke

Goal: Prove imported external artifact references remain inert and not locally
openable.

Expected files:

- `backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py`
- `docs/fixtures/14-ci-imported-artifact-reference-clarity-golden.md`
- `docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py -q
git diff --check
```

Acceptance:

- Golden proves imported artifact references are stored as metadata with inert
  status.
- Golden proves no remote fetch was performed.
- Golden proves local artifact access rejects the external reference with
  `ARTIFACT_NOT_LOCAL`.
- Golden proves no TestRun, Report, FailureAnalysis, QualityGateDecision, or
  remote-provider side effect is created by import-only metadata.

Commit message:

```text
test(golden): add ci imported reference clarity smoke
```

## Slice 26 Completion Gate

Goal: Validate imported artifact reference clarity end to end and hand off the
next V2 task.

Expected files:

- `docs/implementation/slices/slice-26-ci-imported-artifact-reference-clarity.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_imported_artifact_reference_clarity_golden.py backend/app/tests/golden/test_artifact_access_golden.py -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- All Slice 26 task rows are marked done with commit ids.
- Completion evidence records golden, frontend build/test, and diff
  verification.
- Non-goals remain excluded.
- Handoff names the next V2 slice or planning task.

Commit message:

```text
docs(v2): complete ci imported reference clarity slice
```
