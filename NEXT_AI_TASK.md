# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 06: Requirement To Case Mainline.

## Current Task

Task 1: Add Requirement Review models and migration.

## Product Value Answer

After this task, Chtest has the Requirement, RequirementReview, and RiskItem
database foundation needed to persist AI-assisted requirement review evidence.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-06-requirement-to-case.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/03-state-machines.md`
5. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Requirement Review API docs beyond model field checks.
- Case generation, case review, frontend, AutomationDraft, Playwright, CI/CD,
  report center, RAG runtime, MCP runtime, and migration reference docs unless a
  concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/requirements/__init__.py
backend/app/modules/requirements/models.py
backend/app/modules/requirements/schemas.py
backend/alembic/versions/<revision>_requirement_review.py
backend/app/tests/db/test_requirement_review_models.py
```

Read nearby Project and AI Runtime model patterns only to align UUID, timestamp,
JSON, and SQLite/PostgreSQL compatibility.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_requirement_review_models.py -q
```

Expected result: Requirement Review model focused test passes.

## Acceptance

- Requirement, RequirementReview, and RiskItem models match
  `docs/contracts/01-data-model-contract.md`.
- Migration creates the three contract tables and can run under the existing
  SQLite migration smoke style.
- JSON fields track in-place updates where needed.
- No API, worker, mock agent flow, case generation, frontend, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions are added in this task.
- `git status --short` shows only expected model/migration/test files and
  required task docs before commit.

## Commit Message

```text
feat(requirements): add requirement review models
```

## Next Task

Slice 06 Task 2: Add Requirement API.
