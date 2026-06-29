# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 06: Requirement To Case Mainline.

## Current Task

Slice 06 completion gate.

## Product Value Answer

After this task, Chtest verifies the requirement-to-case mainline across backend
golden smoke and frontend requirement/case review shells.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-06-requirement-to-case.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- AutomationDraft, Playwright, CI/CD, report center, RAG runtime, MCP runtime,
  and migration reference docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-06-requirement-to-case.md
memory/07-dev-log.md
memory/08-session-handoff.md
NEXT_AI_TASK.md
```

Read Slice 06 task plan and recent handoff only as needed to verify the slice
completion gate.

## Verification Command

```bash
backend/.venv/bin/python -m pytest backend/app/tests/api/test_requirement_review.py backend/app/tests/api/test_case_generation.py backend/app/tests/api/test_case_review.py backend/app/tests/golden/test_requirement_to_case.py -q
npm --prefix frontend run test -- --run
```

Expected result: backend Slice 06 chain and frontend test suite pass.

## Acceptance

- Verify all Slice 06 completed task tests and frontend shells.
- Confirm task table has commit ids for every done task.
- Update long-term dev log and handoff with Slice 06 completion status.
- Move the next task pointer to the next planned V1 slice/task after Slice 06.
- Do not add new product behavior in the completion gate.
- `git status --short` shows only expected docs/memory files before commit.

## Commit Message

```text
docs(memory): complete requirement to case slice
```

## Next Task

Next V1 slice/task after Slice 06 completion.
