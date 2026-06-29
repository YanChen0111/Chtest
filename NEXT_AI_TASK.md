# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 06: Requirement To Case Mainline.

## Current Task

Task 5: Add Case Generation API and mock agent flow.

## Product Value Answer

After this task, Chtest can generate deterministic mock case candidates from a
Requirement and RequirementReview, then list those candidates for user review.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-06-requirement-to-case.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/05-prompt-skill-contract.md`
7. `docs/contracts/08-mock-provider-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Case review, frontend, AutomationDraft, Playwright, CI/CD, report center, RAG
  runtime, MCP runtime, and migration reference docs unless a concrete blocker
  requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/cases/router.py
backend/app/modules/cases/service.py
backend/app/modules/cases/schemas.py
backend/app/main.py
backend/app/tests/api/test_case_generation.py
```

Read existing Requirement Review mock flow and AI Runtime worker/provider
patterns only as needed to reuse deterministic mock provider behavior.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_case_generation.py -q
```

Expected result: Case Generation API focused test passes.

## Acceptance

- Add `POST /api/case-generation/tasks` and
  `GET /api/case-generation/tasks/{id}/candidates`.
- Start generation creates an AITask using active prompt/skill versions and
  deterministic mock provider output.
- Persist CaseGenerationTask and GeneratedCaseCandidate rows only after
  schema-valid mock output.
- Do not let generated candidates enter the TestCase library automatically.
- Do not add Case Review API, frontend, AutomationDraft, real provider, external
  RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- `git status --short` shows only expected cases API/service/schema/main/test
  files and required task docs before commit.

## Commit Message

```text
feat(cases): add mock case generation flow
```

## Next Task

Slice 06 Task 6: Add Case Review API.
