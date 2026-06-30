# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 16: UnitTestPatch And Regression.

## Current Task

Task 4: Add PatchScopeGate service.

## Product Value Answer

After this task, Chtest can validate UnitTestPatch unified diffs before review
or application and block non-test path changes.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/01-positioning-and-scope.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- RAG runtime, MCP runtime, RBAC, tenants, permissions, release management, and
  remote CI provider integration docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
backend/app/modules/cicd/schemas.py
backend/app/modules/cicd/service.py
backend/app/tests/api/test_unit_test_patch_regression.py
docs/implementation/slices/slice-16-unit-test-patch-regression.md
```

Do not apply patches, mutate the repository, or run external test commands from
the generated patch in this task.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_unit_test_patch_regression.py -q
```

Expected result: focused UnitTestPatch/PatchScopeGate tests pass.

## Acceptance

- Parses unified diff target paths for UnitTestPatch candidates.
- Allows test-only paths such as `tests/`, `test/`, `__tests__/`, and common
  frontend test suffixes.
- Rejects source, config, migration, generated artifact, and unknown non-test
  paths with structured reasons.
- Returns `allowed`, `checked_paths`, `blocked_paths`, `forbidden_patterns`,
  `risk_level`, and rejection `reason` fields.
- Does not apply patches or run tests in this task.
- Updates handoff and sets the next task to UnitTestPatch generation/review API.

## Commit Message

```text
feat(cicd): add patch scope gate
```

## Next Task

Slice 16 Task 5: Add UnitTestPatch generation/review API.
