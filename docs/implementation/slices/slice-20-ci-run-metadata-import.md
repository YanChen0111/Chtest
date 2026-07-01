# Slice 20: CI Run Metadata Import Task Plan

## Goal

Add an import-only CI evidence bridge for CI/CD Quality Center.

This slice lets a test engineer import static CI run metadata into Chtest and
map it into the existing CICDRun evidence model. It must treat imported CI
status as evidence, not authority. It must not call remote CI provider APIs,
receive webhooks, trigger pipelines, rerun jobs, comment on PRs, deploy,
release, store provider credentials, or manage organization permissions.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
- `docs/implementation/slices/slice-18-newman-api-execution.md`
- `docs/implementation/slices/slice-19-deterministic-knowledge-retrieval.md`

## Preconditions

- Slice 15 CI/CD Quality Center Foundation exists with CICDRun,
  CICDChangedFile, local diff evidence, and risk analysis artifacts.
- Slice 16 UnitTestPatch and QualityGateDecision records exist for downstream
  local quality decisions.
- CI/CD Quality Center frontend can display CICDRun evidence.
- Slice 18 and Slice 19 are complete, so V2 has already expanded runner
  evidence and knowledge evidence without changing the local-first boundary.

## Product Value Answer

After this slice, a test engineer can import a static CI run JSON file or
deterministic uploaded CI metadata payload, see CI status, changed files, and
artifact references mapped into CICDRun evidence, and use that evidence inside
CI/CD Quality Center without Chtest controlling any remote CI provider.

## Non-goals

- No remote CI provider API calls.
- No webhook receiver.
- No pipeline trigger, rerun, cancellation, or scheduling.
- No PR comments, commit status updates, branch protection, merge, push, tag,
  deploy, or release management.
- No provider credentials, OAuth, secret storage, token storage, or organization
  permissions.
- No broad GitHub Actions, GitLab CI, Jenkins, CircleCI, or Buildkite parity.
- No automatic QualityGateDecision pass from imported status alone.
- No RBAC, tenants, departments, SSO, permissions, enterprise audit, marketplace,
  RAG runtime, MCP runtime, cloud sync, or release automation.

## Slice Boundary

- Import input is static JSON or an uploaded JSON payload handled locally.
- The provider is an inert label such as `imported`, `github_actions`,
  `gitlab_ci`, or `jenkins`; it does not enable provider-specific API behavior.
- Imported external URLs are stored as references only. Chtest does not fetch,
  execute, authenticate to, or mutate external systems.
- Imported CI conclusion maps to a local evidence status, not a quality gate
  decision.
- Imported changed files map into CICDChangedFile rows or deterministic changed
  file evidence compatible with Slice 15.
- Imported artifact references are preserved in evidence artifacts without
  downloading remote artifact content.
- QualityGateDecision remains governed by existing Chtest evidence rules and
  review workflow.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add CI Run Metadata Import task plan | done | `test -f docs/implementation/slices/slice-20-ci-run-metadata-import.md && rg -n "CI Run Metadata Import|Product Value Answer|Non-goals|Task Table|import-only" docs/implementation/slices/slice-20-ci-run-metadata-import.md` | `b1acde6` | planning-only scope |
| Define CI import contract boundary | done | `rg -n "ci_import|CI import|imported CI|ci_run_metadata|remote CI provider" docs/contracts docs/implementation/slices/slice-20-ci-run-metadata-import.md` | `2201b94` | contract-only before code |
| Add deterministic CI metadata parser | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q` | `21ce127` | parse static JSON only |
| Add CI run import API | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q` | pending commit | import-only endpoint |
| Add CI import frontend evidence display | planned | `npm --prefix frontend run test -- --run` | pending | CI/CD 管理 import evidence |
| Add CI import golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_run_metadata_import_golden.py -q` | pending | fixture -> CICDRun evidence |
| Slice 20 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py backend/app/tests/golden/test_ci_run_metadata_import_golden.py -q && npm --prefix frontend run test -- --run && git diff --check` | pending | docs and handoff |

## Task 1: Add CI Run Metadata Import Task Plan

Goal: Define the smallest import-only CI evidence slice before implementation.

Expected files:

- `docs/implementation/slices/slice-20-ci-run-metadata-import.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-20-ci-run-metadata-import.md
rg -n "CI Run Metadata Import|Product Value Answer|Non-goals|Task Table|import-only|remote CI provider" docs/implementation/slices/slice-20-ci-run-metadata-import.md docs/implementation/10-v2-scope-options.md
git diff --check
```

Acceptance:

- Creates the Slice 20 plan.
- Defines product value, non-goals, slice boundary, task table, expected files,
  and verification commands.
- Selects import-only CI metadata evidence as the next V2 slice.
- Does not add implementation code or frontend code.

Commit message:

```text
docs(v2): add ci run metadata import slice plan
```

## Task 2: Define CI Import Contract Boundary

Goal: Update contracts so imported CI metadata is evidence-only before code.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/06-error-code-contract.md`
- `docs/implementation/slices/slice-20-ci-run-metadata-import.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "ci_import|CI import|imported CI|ci_run_metadata|remote CI provider|QualityGateDecision|CI_IMPORT_" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/06-error-code-contract.md docs/implementation/slices/slice-20-ci-run-metadata-import.md
git diff --check
```

Acceptance:

- Data contract defines `source_type=ci_import` or an equivalent import-only
  value for CICDRun.
- API contract defines an import endpoint or narrowed import operation.
- State-machine contract states imported CI conclusion cannot automatically
  pass QualityGateDecision.
- Artifact contract defines `ci_run_metadata.json` and imported artifact
  reference rules.
- Error-code contract defines CI import rejection codes.
- Contract rejects remote CI provider control, webhooks, triggers, reruns, PR
  comments, deploy, release, credentials, RBAC, tenants, and permissions.

Commit message:

```text
docs(cicd): define ci metadata import boundary
```

## Task 3: Add Deterministic CI Metadata Parser

Goal: Parse static CI metadata JSON into a deterministic internal import model.

Expected files:

- CI/CD service/parser files needed under `backend/app/modules/cicd/`
- `backend/app/tests/api/test_ci_run_metadata_import.py`
- deterministic parser fixtures if needed under backend tests

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
```

Acceptance:

- Parses provider label, pipeline name, job name, conclusion, started/finished
  timestamps, duration, base/head refs, changed files, and artifact references.
- Rejects secret-like fields, credentials, webhook payload actions, trigger
  commands, rerun requests, deploy/release fields, and malformed changed files.
- Normalizes changed file roles and risks using the existing CICDChangedFile
  classification rules where possible.
- Does not fetch external artifact URLs or call remote providers.

Commit message:

```text
feat(cicd): add ci metadata import parser
```

## Task 4: Add CI Run Import API

Goal: Persist imported CI metadata as CICDRun evidence.

Expected files:

- `backend/app/modules/cicd/router.py`
- `backend/app/modules/cicd/service.py`
- `backend/app/modules/cicd/schemas.py`
- `backend/app/tests/api/test_ci_run_metadata_import.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py -q
```

Acceptance:

- Adds an import-only endpoint such as `POST /api/cicd/runs/import`.
- Creates CICDRun with import-only source metadata.
- Creates CICDChangedFile rows from imported changed files.
- Writes `ci_run_metadata.json` and compatible `changed_files.json` artifacts.
- Stores imported artifact references as inert evidence references.
- Does not create QualityGateDecision automatically and does not trigger remote
  CI behavior.

Commit message:

```text
feat(cicd): add ci metadata import api
```

## Task 5: Add CI Import Frontend Evidence Display

Goal: Show imported CI evidence inside CI/CD 管理 without adding provider
controls.

Expected files:

- frontend CI/CD API/store files needed for import evidence
- focused CI/CD 管理 view updates
- focused frontend tests

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- Shows imported CI source, conclusion, changed files, artifact references, and
  import evidence status.
- Keeps UI Chinese-facing while preserving product terms such as CI/CD,
  CICDRun, Artifact, QualityGateDecision, and TestRun.
- Does not add provider connection settings, tokens, webhook URLs, trigger
  buttons, rerun buttons, PR comment controls, deploy controls, or release
  controls.

Commit message:

```text
feat(frontend): show ci import evidence
```

## Task 6: Add CI Import Golden Smoke

Goal: Prove static CI metadata becomes auditable Chtest evidence.

Expected files:

- `docs/fixtures/09-ci-run-metadata-import-golden.md`
- `backend/app/tests/golden/test_ci_run_metadata_import_golden.py`
- focused backend import tests when needed
- `docs/implementation/slices/slice-20-ci-run-metadata-import.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_ci_run_metadata_import_golden.py -q
git diff --check
```

Acceptance:

- Imports deterministic CI metadata fixture.
- Creates CICDRun and CICDChangedFile evidence.
- Persists `ci_run_metadata.json`, changed file evidence, and imported artifact
  references.
- Confirms imported CI conclusion is evidence only and does not automatically
  pass QualityGateDecision.
- Confirms no remote CI provider API, webhook, trigger, rerun, credentials,
  deploy, release, RBAC, tenants, or permissions dependency is introduced.

Commit message:

```text
test(golden): add ci metadata import smoke
```

## Slice 20 Completion Gate

Goal: Validate all CI metadata import work and prepare the next V2 task.

Expected files:

- `docs/implementation/slices/slice-20-ci-run-metadata-import.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_ci_run_metadata_import.py backend/app/tests/golden/test_ci_run_metadata_import_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- All Slice 20 task rows are marked done with commit ids.
- Completion evidence records backend, golden, frontend, and diff verification.
- Handoff names the next V2 slice or planning task.
- Non-goals remain excluded.

Commit message:

```text
docs(v2): complete ci metadata import slice
```
