# Slice 46: AI Workbench Evidence Table Empty States

## Goal

Show explicit empty states for selected AI tasks that have no evidence artifacts
or LLM call logs.

The AI Workbench already has a page-level empty state when there are no tasks,
but selected task detail tables can look blank when a task has not recorded
artifacts or LLM calls yet. Reviewers should see a clear evidence-specific
empty state.

## Product Value Answer

After this slice, reviewers can tell that a selected AI task has no recorded
artifact evidence or LLM call logs yet, instead of mistaking an empty table for
a loading or rendering issue.

## Preconditions

- AI Workbench already loads selected task details.
- Slice 40-45 introduced frontend-only evidence visibility and empty-state
  patterns in the AI Workbench.

## Non-goals

- No backend feature code, migrations, API shape changes, provider behavior
  changes, prompt or skill edits, contract changes, fixture changes, package
  upgrades, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- No raw prompt, raw request, or raw LLM output rendering.
- No artifact generation, mutation, upload, delete, sharing, signed URLs, or
  external artifact fetch.
- No execution page shell/form refactor.

## Slice Boundary

- Update the selected-task AI Workbench detail view only.
- Add explicit empty states below artifact summary and LLM call log tables when
  their selected-task arrays are empty.
- Preserve all existing evidence links, safe-to-show gates, and metadata-only
  raw output behavior.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add AI Workbench Evidence Table Empty States task plan | done | `rg -n "Slice 46|AI Workbench Evidence Table Empty States|empty state|Non-goals|Task Table" docs/implementation/slices/slice-46-ai-workbench-evidence-table-empty-states.md NEXT_AI_TASK.md && git diff --check` | pending | planning only |
| Show selected-task evidence table empty states | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | focused test passed; build passed with existing chunk warning; diff check clean |
| Slice 46 completion gate | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | display-only frontend change |

## Verification Command

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run build
git diff --check
```

## Acceptance

- A selected task with no artifacts shows an explicit artifact evidence empty
  state.
- A selected task with no LLM call logs shows an explicit LLM call log empty
  state.
- Existing populated artifact and LLM call tables still render as before.
- Raw prompt, raw request, and raw LLM output remain metadata-only and are not
  rendered inline.
- No backend, provider, prompt, skill, contract, fixture, execution page, or
  package behavior changes.

Commit message:

```text
feat(frontend): show ai evidence table empty states
```
