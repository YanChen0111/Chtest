# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the whole planning set.

## Current Slice

Slice 1: Repository and Deploy Skeleton.

## Current Task

Task 1: Initialize repository directories.

## Product Value Answer

After this task, Chtest has a committed local project skeleton that future backend,
frontend, worker, prompt, skill, MCP-tool, and artifact work can build on.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-01-platform-foundation.md`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/implementation/05-execution-efficiency-plan.md`

## Do Not Read Unless Needed

- Full PRD and page PRD files.
- Architecture deep dives.
- Open-source migration references.
- Git Quality docs.
- Playwright, Newman, JMeter, Appium, traffic-capture roadmap docs.

## Expected Files

Create only these files/directories for the current task:

```text
backend/.gitkeep
frontend/.gitkeep
worker/.gitkeep
deploy/.gitkeep
prompts/.gitkeep
skills/.gitkeep
mcp_tools/.gitkeep
artifacts/.gitkeep
```

## Verification Command

```bash
find backend frontend worker deploy prompts skills mcp_tools artifacts -maxdepth 1 -type f -name .gitkeep
```

Expected result: the command prints the eight `.gitkeep` files above.

## Acceptance

- The eight top-level directories exist.
- Each directory has one `.gitkeep`.
- No backend, frontend, worker, Docker, database, AI runtime, or UI behavior is added in this task.
- `git status --short` shows only the expected skeleton files before commit.

## Commit Message

```text
chore(repo): initialize platform directories
```

## Next Task

Slice 1 Task 2: Add Docker Compose for PostgreSQL and Redis.

