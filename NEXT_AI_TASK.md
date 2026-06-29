# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 06: Requirement To Case Mainline.

## Current Task

Task 7: Add Requirement To Case golden smoke.

## Product Value Answer

After this task, Chtest has one fixture-aligned backend smoke test proving the
mainline from requirement creation through review, case generation, and case
approval into official TestCase records.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-06-requirement-to-case.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/fixtures/01-golden-requirement-to-case.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Frontend, AutomationDraft, Playwright, CI/CD, report center, RAG runtime, MCP
  runtime, and migration reference docs unless a concrete blocker requires
  them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/tests/golden/test_requirement_to_case.py
```

Read existing Requirement Review, Case Generation, and Case Review API tests
only as needed to reuse their fixtures and request patterns.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py -q
```

Expected result: Requirement-to-case golden smoke passes.

## Acceptance

- Exercise the golden requirement fixture through requirement creation,
  requirement review, case generation, candidate listing, and candidate approval.
- Assert persisted RequirementReview/RiskItem evidence, GeneratedCaseCandidate
  records, and official TestCase creation from an approved candidate.
- Keep the smoke deterministic with mock provider behavior only.
- Do not add browser automation, execution, AutomationDraft, frontend, real
  provider, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- `git status --short` shows only expected golden test and required task docs
  before commit.

## Commit Message

```text
test(golden): add requirement to case smoke
```

## Next Task

Slice 06 Task 8: Add Requirement Review frontend shell.
