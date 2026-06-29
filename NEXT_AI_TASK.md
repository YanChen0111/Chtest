# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 06: Requirement To Case Mainline.

## Current Task

Task 4: Add Case Generation models and migration.

## Product Value Answer

After this task, Chtest has the CaseGenerationTask, GeneratedCaseCandidate, and
TestCase database foundation needed to persist generated case candidates and
reviewed test cases.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-06-requirement-to-case.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/03-state-machines.md`
5. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Case generation API docs beyond model field checks.
- Case review, frontend, AutomationDraft, Playwright, CI/CD, report center, RAG
  runtime, MCP runtime, and migration reference docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/cases/__init__.py
backend/app/modules/cases/models.py
backend/app/modules/cases/schemas.py
backend/alembic/versions/<revision>_case_generation.py
backend/app/tests/db/test_case_generation_models.py
```

Read nearby Requirement, AI Runtime, and Prompt/Skill model patterns only to
align UUID, timestamp, JSON/list, and SQLite/PostgreSQL compatibility.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/db/test_case_generation_models.py -q
```

Expected result: Case Generation model focused test passes.

## Acceptance

- CaseGenerationTask, GeneratedCaseCandidate, and TestCase models match
  `docs/contracts/01-data-model-contract.md`.
- Migration creates the three contract tables and can run under the existing
  SQLite migration smoke style with prior migrations.
- JSON/list fields track in-place updates where needed.
- No Case Generation API, mock generation flow, case review API, frontend,
  AutomationDraft, RAG runtime, MCP runtime, RBAC, tenants, or permissions are
  added in this task.
- `git status --short` shows only expected model/migration/test files and
  required task docs before commit.

## Commit Message

```text
feat(cases): add case generation models
```

## Next Task

Slice 06 Task 5: Add Case Generation API and mock agent flow.
