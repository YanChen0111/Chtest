# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 06: Requirement To Case Mainline.

## Current Task

Task 2: Add Requirement API.

## Product Value Answer

After this task, Chtest can create, read, and list manual Requirement records so
the requirement-to-case mainline has an API entry point before AI review starts.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-06-requirement-to-case.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement Review agent/mock flow docs beyond route shape checks.
- Case generation, case review, frontend, AutomationDraft, Playwright, CI/CD,
  report center, RAG runtime, MCP runtime, and migration reference docs unless a
  concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/requirements/router.py
backend/app/modules/requirements/service.py
backend/app/modules/requirements/schemas.py
backend/app/main.py
backend/app/tests/api/test_requirements.py
```

Read existing Project API patterns only to align FastAPI routing, session
dependency, error shape, pagination defaults, and schema style.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirements.py -q
```

Expected result: Requirement API focused test passes.

## Acceptance

- Add create, get, and list endpoints for manual Requirement records.
- API persists contract fields: project_id, module_id, title, content,
  source_type, source_ref, and status.
- API validates project existence and optional module belongs to the same
  project when module_id is provided.
- Do not start AI review, generate risks, or create case generation records.
- No worker, mock agent flow, frontend, RAG runtime, MCP runtime, RBAC, tenants,
  or permissions are added in this task.
- `git status --short` shows only expected API/schema/service/main/test files
  and required task docs before commit.

## Commit Message

```text
feat(requirements): add requirement api
```

## Next Task

Slice 06 Task 3: Add Requirement Review API and mock agent flow.
