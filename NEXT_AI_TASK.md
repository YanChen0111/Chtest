# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Next V2 slice selection after Slice 20 completion.

## Current Task

Select the next V2 small slice after Slice 20 completion.

## Product Value Answer

After this task, the next small V2 slice is selected from current product value,
contracts, and completed Slice 20 evidence without expanding forbidden scope.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/04-ai-vibecoding-governance.md`
8. `docs/implementation/slices/slice-15-cicd-quality-center.md`
9. `docs/implementation/slices/slice-20-ci-run-metadata-import.md`
10. `docs/implementation/10-v2-scope-options.md`

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
docs/implementation/slices/<next-slice>.md
```

Planning task only. Do not add implementation code, frontend code, migrations,
remote CI provider calls, webhooks, pipeline triggers, reruns, PR comments,
deploy/release controls, credentials, RBAC, tenants, permissions, marketplace,
RAG runtime, or MCP runtime.

## Verification Command

```bash
rg -n "Slice 20|CI Run Metadata Import|next V2|recommended" docs/implementation/10-v2-scope-options.md NEXT_AI_TASK.md
git diff --check
```

Expected result: next V2 slice selection docs and diff check pass.

## Acceptance

- Records Slice 20 completion in V2 scope options.
- Selects one next small V2 slice with product value, non-goals, task table,
  expected files, and verification commands.
- Updates `NEXT_AI_TASK.md` to the first task of that slice.
- Keeps forbidden scope excluded unless a later approved task explicitly changes
  contracts.

## Commit Message

```text
docs(v2): select next slice after ci import
```

## Next Task

First task of the selected next V2 slice.
