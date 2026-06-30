# Slice 11: AutomationDraft Foundation Task Plan

## Goal

Create the review-gated AutomationDraft foundation that turns reviewed TestCase
records into AI-generated automation draft assets without executing them.

This slice must stop at draft generation, edit, and approval state. It must not
run pytest or Playwright, copy files into runtime workspaces, create TestRun or
TestResult evidence, generate reports, add CI/CD quality, add RAG runtime, add
MCP runtime, or add RBAC, tenants, or permissions.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/slices/slice-10-test-case-library.md`

## Preconditions

- Slice 10 Test Case Library is complete.
- Reviewed TestCase records can be listed through `GET /api/test-cases`.
- AutomationDraft is already defined in the data model and API contracts.
- PromptVersion and SkillVersion registry can seed deterministic mock versions.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add AutomationDraft task plan | done | `test -f docs/implementation/slices/slice-11-automation-draft-foundation.md && rg -n "AutomationDraft Foundation|Task Table|Verification Command|Non-goals" docs/implementation/slices/slice-11-automation-draft-foundation.md` | `7704bbf` | scoped Slice 11 plan |
| Add AutomationDraft model and schema alignment | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q` | `2d5bdec` | model/schema/read contracts only |
| Add AutomationDraft generation API | done | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q` | pending commit | mock draft from reviewed TestCase |
| Add AutomationDraft edit and approve API | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q` | - | edit -> edited -> approve -> approved |
| Add AutomationDraft frontend review shell | planned | `npm --prefix frontend run test -- --run` | - | draft review, edit, approve shell only |
| Add AutomationDraft golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_automation_draft.py -q` | - | reviewed golden case produces approved draft |
| Slice 11 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py backend/app/tests/golden/test_automation_draft.py -q && npm --prefix frontend run test -- --run` | - | docs and handoff only |

## Task 1: Add AutomationDraft Model And Schema Alignment

Goal: Ensure AutomationDraft model and API schemas match the existing contracts
before implementing behavior.

Expected files:

- `backend/app/modules/automation/models.py`
- `backend/app/modules/automation/schemas.py`
- `backend/app/modules/automation/__init__.py`
- `backend/app/tests/api/test_automation_draft.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
```

Acceptance:

- Defines AutomationDraft fields from the data model contract.
- Adds read/request schemas for create, get, edit, and approve endpoints.
- Does not add execution, TestRun, TestResult, runtime artifact copy, reports,
  CI/CD quality, RAG runtime, MCP runtime, RBAC, tenants, or permissions.

Commit message:

```text
feat(automation): add automation draft model schema
```

## Task 2: Add AutomationDraft Generation API

Goal: Generate deterministic mock AutomationDraft records from reviewed TestCase
or Requirement input.

Expected files:

- `backend/app/modules/automation/router.py`
- `backend/app/modules/automation/service.py`
- `backend/app/modules/automation/schemas.py`
- `backend/app/tests/api/test_automation_draft.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
```

Acceptance:

- Adds `POST /api/automation/drafts`.
- Requires a reviewed TestCase or Requirement reference.
- Creates an AITask and persisted AutomationDraft in `draft_generated` status.
- Mock output includes draft_code, target_framework, suggested_file_path,
  execution_notes, risk_notes, approval_required, and execution_strategy.
- Does not execute or write draft code into a target repository.

Commit message:

```text
feat(automation): add automation draft generation api
```

## Task 3: Add AutomationDraft Edit And Approve API

Goal: Let a human reviewer edit and approve an AutomationDraft without
executing it.

Expected files:

- `backend/app/modules/automation/router.py`
- `backend/app/modules/automation/service.py`
- `backend/app/modules/automation/schemas.py`
- `backend/app/tests/api/test_automation_draft.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_automation_draft.py -q
```

Acceptance:

- Adds `GET /api/automation/drafts/{id}`.
- Adds `PATCH /api/automation/drafts/{id}` for reviewer edits.
- Adds `POST /api/automation/drafts/{id}/approve`.
- Enforces `edit -> edited -> approve -> approved` and rejects invalid payloads.
- Does not create TestRun, TestResult, runtime artifacts, reports, or execution
  side effects.

Commit message:

```text
feat(automation): add automation draft review api
```

## Task 4: Add AutomationDraft Frontend Review Shell

Goal: Let users inspect, edit, and approve generated AutomationDraft records in
the workbench.

Expected files:

- `frontend/src/api/automation.ts`
- `frontend/src/stores/automation.ts`
- `frontend/src/views/automation/AutomationDraftReviewView.vue`
- `frontend/src/views/automation/AutomationDraftReviewView.spec.ts`
- `frontend/src/router/index.ts`
- `frontend/src/layouts/WorkbenchLayout.vue`
- `frontend/src/stores/index.ts`

Verification Command:

```bash
npm --prefix frontend run test -- --run
```

Acceptance:

- Adds workbench navigation for AutomationDraft review.
- Shows draft code, suggested path, execution notes, risk notes, status, and
  approval_required.
- Supports edit and approve actions through the API.
- Does not add execution/run buttons, report links, CI/CD quality actions, RAG
  runtime, MCP runtime, RBAC, tenants, or permissions.

Commit message:

```text
feat(frontend): add automation draft review shell
```

## Task 5: Add AutomationDraft Golden Smoke

Goal: Prove a reviewed golden TestCase can produce, edit, and approve an
AutomationDraft without execution.

Expected files:

- `backend/app/tests/golden/test_automation_draft.py`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_automation_draft.py -q
```

Acceptance:

- Reuses golden requirement-to-case and Test Case Library setup.
- Creates an AutomationDraft for a reviewed golden TestCase.
- Verifies draft_code, suggested_file_path, execution_notes, risk_notes, and
  status.
- Edits then approves the draft.
- Asserts no TestRun/TestResult/report is created by this slice.

Non-goals:

- Do not run pytest or Playwright.
- Do not copy draft files to a runtime workspace.
- Do not add execution, reports, CI/CD quality, RAG runtime, or MCP runtime.

Commit message:

```text
test(golden): add automation draft smoke
```

## Slice Completion Gate

- AutomationDraft model/schema aligns with contracts.
- Draft generation API creates review-gated draft records from reviewed cases.
- Edit and approve APIs work without execution side effects.
- Frontend can review, edit, and approve drafts without run buttons.
- Golden smoke proves reviewed case -> approved draft.
- No TestRun/TestResult execution, reports, CI/CD quality, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions are added.
