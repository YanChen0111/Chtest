# Slice 45: AI Workbench Token Usage Empty State

## Goal

Show an explicit empty state when AI Workbench token usage metadata is empty.

AI task and LLM call details already show token usage metadata, but an empty
token usage object currently renders as a blank cell. Reviewers should see a
clear "not recorded" value instead of guessing whether the UI failed to load
data.

## Product Value Answer

After this slice, reviewers can distinguish recorded token usage from missing
token usage evidence without changing AI runtime behavior or exposing raw
prompt/request/LLM output content.

## Preconditions

- AI Workbench already displays task-level and LLM-call token usage metadata.
- Slice 40-44 kept AI Workbench evidence changes frontend-only and safe.

## Non-goals

- No backend feature code, migrations, API shape changes, provider behavior
  changes, prompt or skill edits, contract changes, fixture changes, package
  upgrades, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- No raw prompt, raw request, or raw LLM output rendering.
- No token accounting recalculation or model-provider behavior change.
- No execution page shell/form refactor.

## Slice Boundary

- Update AI Workbench display helpers only.
- Render empty token usage objects as not recorded.
- Preserve formatted token usage labels for non-empty metadata.
- Keep raw prompt, request, and LLM output metadata-only.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add AI Workbench Token Usage Empty State task plan | done | `rg -n "Slice 45|AI Workbench Token Usage Empty State|token usage|Non-goals|Task Table" docs/implementation/slices/slice-45-ai-workbench-token-usage-empty-state.md NEXT_AI_TASK.md && git diff --check` | pending | planning only |
| Show not-recorded token usage empty state | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | focused test passed; build passed with existing chunk warning; diff check clean |
| Slice 45 completion gate | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | display-only frontend change |

## Verification Command

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run build
git diff --check
```

## Acceptance

- AI Workbench task and LLM-call token usage renders formatted token labels
  when metadata is present.
- Empty token usage metadata renders as not recorded instead of a blank cell.
- Raw prompt, raw request, and raw LLM output remain metadata-only and are not
  rendered inline.
- No backend, provider, prompt, skill, contract, fixture, execution page, or
  package behavior changes.

Commit message:

```text
fix(frontend): show ai token usage empty state
```
