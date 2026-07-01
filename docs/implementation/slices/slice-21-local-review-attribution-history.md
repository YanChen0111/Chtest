# Slice 21: Local Review Attribution History Task Plan

## Goal

Add local review attribution and append-only review history across the existing
review-gated evidence loop.

This slice lets an individual test engineer see who performed a local review
action, when it happened, what changed, and which evidence artifacts supported
the decision. It strengthens traceability without turning Chtest into a
multi-user governance, RBAC, or enterprise audit platform.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- `docs/implementation/slices/slice-06-requirement-to-case.md`
- `docs/implementation/slices/slice-11-automation-draft-foundation.md`
- `docs/implementation/slices/slice-15-cicd-quality-center.md`
- `docs/implementation/slices/slice-16-unit-test-patch-regression.md`

## Preconditions

- V1 has review-gated TestCase, AutomationDraft, UnitTestPatch, and
  QualityGateDecision workflows.
- Slice 18, Slice 19, and Slice 20 expanded runner evidence, knowledge
  evidence, and imported CI evidence without changing the local-first boundary.
- Chtest remains a single-user local workbench. Review attribution can use a
  deterministic local reviewer such as `Default User`.

## Product Value Answer

After this slice, a test engineer can inspect local review history for case
review, AutomationDraft review, UnitTestPatch review, and QualityGateDecision
compute events, including reviewer, action, status transition, comments,
timestamp, and evidence artifact references. This makes Chtest's review-gated
evidence loop easier to trust and hand off without adding team management.

## Non-goals

- No RBAC, roles, permissions, tenants, departments, SSO, or enterprise audit.
- No login, user account, session, identity-provider, or organization model.
- No assignment workflow, approval delegation, notifications, team inbox,
  comment threads, or collaboration workspace.
- No changes to existing approval authority or state-machine rules.
- No remote CI provider governance, PR comments, deploy/release controls, or
  provider credentials.
- No RAG runtime, MCP runtime, marketplace, cloud sync, or release automation.

## Slice Boundary

- Add an append-only local review event/history record.
- Record only deterministic local attribution fields:
  - `entity_type`
  - `entity_id`
  - `action`
  - `from_status`
  - `to_status`
  - `reviewer`
  - `comment`
  - `evidence_artifact_ids`
  - `created_at`
- Cover existing review actions first:
  - TestCase / case candidate review.
  - AutomationDraft approve/edit/reject where supported by current workflows.
  - UnitTestPatch approve/reject.
  - QualityGateDecision compute.
- Display compact local history panels in the existing review surfaces.
- Keep all review events local evidence. They must not grant permissions,
  assign work, or change who can perform an action.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add Local Review Attribution History task plan | done | `test -f docs/implementation/slices/slice-21-local-review-attribution-history.md && rg -n "Local Review Attribution History|Product Value Answer|Non-goals|Task Table|append-only" docs/implementation/slices/slice-21-local-review-attribution-history.md` | `f121483` | planning-only scope |
| Define review history contract boundary | done | `rg -n "ReviewHistory|review history|review attribution|Default User|RBAC|permissions" docs/contracts docs/implementation/slices/slice-21-local-review-attribution-history.md` | `b77262b` | contract-only before code |
| Add review history model and service | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py -q` | `31bb8cc` | append-only local events |
| Attach history to existing review actions | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_unit_test_patch_regression.py -q` | pending | no state-machine changes |
| Add frontend review history panels | planned | `npm --prefix frontend run test -- --run` | pending | compact local attribution UI |
| Add review history golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_review_history_golden.py -q` | pending | cross-entity evidence proof |
| Slice 21 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/golden/test_review_history_golden.py -q && npm --prefix frontend run test -- --run && git diff --check` | pending | docs and handoff |

## Task 1: Add Local Review Attribution History Task Plan

Goal: Define the smallest local attribution slice before implementation.

Expected files:

- `docs/implementation/slices/slice-21-local-review-attribution-history.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-21-local-review-attribution-history.md
rg -n "Local Review Attribution History|Product Value Answer|Non-goals|Task Table|append-only|RBAC|permissions" docs/implementation/slices/slice-21-local-review-attribution-history.md docs/implementation/10-v2-scope-options.md
git diff --check
```

Acceptance:

- Creates the Slice 21 plan.
- Defines product value, non-goals, slice boundary, task table, expected files,
  and verification commands.
- Selects local review attribution/history as the next V2 slice.
- Explicitly excludes RBAC, tenants, permissions, login/session redesign, and
  enterprise audit.
- Does not add implementation code or frontend code.

Commit message:

```text
docs(v2): add local review history slice plan
```

## Task 2: Define Review History Contract Boundary

Goal: Update contracts so review history is local, append-only evidence.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-21-local-review-attribution-history.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "ReviewHistory|review history|review attribution|Default User|RBAC|permissions" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-21-local-review-attribution-history.md
git diff --check
```

Acceptance:

- Data contract defines append-only review history records.
- API contract defines a local read surface for review history.
- State-machine contract states review history records transitions but does not
  change approval rules.
- Artifact contract defines evidence references only when needed.
- Contracts explicitly reject RBAC, permissions, tenants, SSO, enterprise audit,
  assignment workflow, and remote provider governance.

Commit message:

```text
docs(review): define local review history contract
```

## Task 3: Add Review History Model And Service

Goal: Add append-only local review event persistence.

Expected files:

- backend model/schema/service files needed for review history
- `backend/app/tests/api/test_review_history.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py -q
```

Acceptance:

- Creates local review history records with entity, action, status transition,
  reviewer, comment, evidence ids, and timestamp.
- Uses deterministic `Default User` attribution unless a local reviewer label
  is explicitly supplied by an existing workflow.
- Records are append-only from the public service surface.
- Does not add users, roles, permissions, tenants, login, or audit policy.

Commit message:

```text
feat(review): add local review history service
```

## Task 4: Attach History To Existing Review Actions

Goal: Record local review history for existing review-gated workflows.

Expected files:

- backend service/router files for cases, automation, and cicd where review
  actions already exist
- `backend/app/tests/api/test_review_history.py`
- focused existing workflow tests as needed

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/api/test_automation_draft.py backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Acceptance:

- Records history for generated case review where current APIs support it.
- Records history for AutomationDraft review actions where current APIs support
  them.
- Records history for UnitTestPatch approve/reject.
- Records history for QualityGateDecision compute.
- Does not change whether an action is allowed.

Commit message:

```text
feat(review): record review history events
```

## Task 5: Add Frontend Review History Panels

Goal: Show compact local review history in existing review surfaces.

Expected files:

- frontend API/store files needed for review history reads
- existing review views and focused tests

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- Shows local review history entries with action, reviewer, status transition,
  comment, timestamp, and evidence reference count.
- Uses Chinese-facing labels while keeping product model terms such as
  TestCase, AutomationDraft, UnitTestPatch, and QualityGateDecision unchanged.
- Keeps panels compact and secondary to the existing review action controls.
- Does not add user management, roles, permissions, assignment, notifications,
  or team inbox controls.

Commit message:

```text
feat(frontend): show local review history
```

## Task 6: Add Review History Golden Smoke

Goal: Prove local review history spans existing review-gated evidence.

Expected files:

- `backend/app/tests/golden/test_review_history_golden.py`
- `docs/fixtures/10-local-review-history-golden.md`
- `docs/implementation/slices/slice-21-local-review-attribution-history.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_review_history_golden.py -q
```

Acceptance:

- Golden creates at least two existing review actions, such as UnitTestPatch
  approval and QualityGateDecision compute.
- Golden confirms append-only review history records exact entity/action/status
  transitions and evidence references.
- Golden confirms no RBAC, tenants, permissions, login/session, assignment,
  notification, or remote provider dependency is introduced.

Commit message:

```text
test(golden): add local review history smoke
```

## Slice 21 Completion Gate

Goal: Validate all local review attribution work and prepare the next V2 task.

Expected files:

- `docs/implementation/slices/slice-21-local-review-attribution-history.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_review_history.py backend/app/tests/golden/test_review_history_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Acceptance:

- All Slice 21 task rows are marked done with commit ids.
- Completion evidence records backend, golden, frontend, and diff
  verification.
- Handoff names the next V2 slice or planning task.
- Non-goals remain excluded.

Commit message:

```text
docs(v2): complete local review history slice
```
