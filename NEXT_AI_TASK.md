# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 03: Project Core.

## Current Task

Task 5: Add TestCommand API and validation.

## Product Value Answer

After this task, Chtest can store safe pytest and frontend test commands tied to
a repository and environment, giving later runner workflows a validated command
record instead of arbitrary shell input.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-03-project-core.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Backend architecture deep dives.
- Open-source migration references.
- Frontend page polish docs beyond shell level.
- CI/CD Quality Center implementation docs.
- Playwright, Newman, JMeter, Appium, traffic-capture roadmap docs.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/modules/projects/service.py
backend/app/modules/projects/schemas.py
backend/app/modules/projects/router.py
backend/app/main.py
backend/app/tests/api/test_test_commands.py
```

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_test_commands.py -q
```

Expected result: the new TestCommand API and validation test passes.

## Acceptance

- TestCommand create/update/list APIs follow `docs/contracts/02-api-contract.md` and Slice 03 Task 5.
- TestCommand validation rejects commands outside the V1 allowlist.
- `working_directory` must stay under the selected repository `local_path`.
- Forbidden shell operators are rejected.
- No command execution, git command execution, AI task models, ToolInvocation, frontend, or multi-user permissions are added in this task.
- `git status --short` shows only the expected TestCommand API files before commit.

## Commit Message

```text
feat(projects): add test command validation
```

## Next Task

Slice 03 Task 6: add project settings frontend shell.
