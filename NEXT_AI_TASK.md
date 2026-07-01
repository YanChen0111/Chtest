# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 20: CI Run Metadata Import.

## Current Task

Slice 20 Task 1: Add CI Run Metadata Import task plan.

## Product Value Answer

After this task, the import-only CI metadata slice has a precise plan, product
value, task table, verification commands, and non-goals before any product code
is written.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/04-ai-vibecoding-governance.md`
4. `docs/implementation/10-v2-scope-options.md`
5. `docs/implementation/slices/slice-15-cicd-quality-center.md`
6. `docs/implementation/slices/slice-16-unit-test-patch-regression.md`
7. `docs/implementation/slices/slice-20-ci-run-metadata-import.md`
8. `memory/08-session-handoff.md`

## Do Not Read Unless Needed

- Remote CI provider integration docs, webhooks, PR bots, release management,
  RAG runtime, MCP runtime, RBAC, tenants, permissions, and marketplace docs
  unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
docs/implementation/10-v2-scope-options.md
docs/implementation/slices/slice-20-ci-run-metadata-import.md
```

Planning-only task. Do not add product code, frontend code, tests, migrations,
remote CI provider calls, webhooks, pipeline triggers, reruns, PR comments,
deploy/release controls, credentials, RBAC, tenants, permissions, marketplace,
RAG runtime, or MCP runtime.

## Verification Command

```bash
test -f docs/implementation/slices/slice-20-ci-run-metadata-import.md
rg -n "CI Run Metadata Import|Product Value Answer|Non-goals|Task Table|import-only|remote CI provider" docs/implementation/slices/slice-20-ci-run-metadata-import.md docs/implementation/10-v2-scope-options.md
git diff --check
```

Expected result: Slice 20 plan and V2 scope recommendation are documented and
diff check passes.

## Acceptance

- Records Slice 19 as completed in V2 planning context.
- Creates Slice 20 plan with product value, non-goals, slice boundary, task
  table, expected files, and verification commands.
- Selects import-only CI metadata evidence as the next V2 slice.
- Does not add implementation code or frontend code.

## Commit Message

```text
docs(v2): add ci run metadata import slice plan
```

## Next Task

Slice 20 Task 2: Define CI import contract boundary.
