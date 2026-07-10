# Slice 44: AI Workbench Request Evidence Visibility

## Goal

Show request/input evidence for each LLM call in the AI Workbench.

AI task LLM call logs already expose `request_artifact_id`, but the AI
Workbench call table does not show whether request evidence was recorded.
Reviewers should be able to see this evidence status and open it only when it
is a safe persisted Artifact.

## Product Value Answer

After this slice, reviewers can trace each LLM call to its recorded request
evidence without rendering raw prompt/input content or changing AI runtime
behavior.

## Preconditions

- `frontend/src/api/aiTasks.ts` already exposes `request_artifact_id`.
- AI task details already include artifact summaries and safe-to-show metadata.
- Slice 40-43 introduced reusable frontend-only evidence visibility patterns in
  the AI Workbench.

## Non-goals

- No backend feature code, migrations, API shape changes, provider behavior
  changes, prompt or skill edits, contract changes, fixture changes, package
  upgrades, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- No raw prompt, raw request, or raw LLM output rendering.
- No artifact upload, mutation, delete, sharing, signed URLs, or external
  artifact fetch.
- No execution page shell/form refactor.

## Slice Boundary

- Update the AI Workbench LLM call log table only.
- Show request evidence as recorded or not recorded.
- Render a local open link only when `request_artifact_id` matches an existing
  selected-task artifact with `safe_to_show=true`.
- Preserve response artifact metadata-only display and raw output safety.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add AI Workbench Request Evidence Visibility task plan | done | `rg -n "Slice 44|AI Workbench Request Evidence Visibility|request evidence|Non-goals|Task Table" docs/implementation/slices/slice-44-ai-workbench-request-evidence-visibility.md NEXT_AI_TASK.md && git diff --check` | pending | planning only |
| Show request evidence in AI Workbench | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | focused positive/negative test passed; build passed with existing chunk warning; diff check clean |
| Slice 44 completion gate | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | no backend/provider/API changes |

## Verification Command

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run build
git diff --check
```

## Acceptance

- AI Workbench LLM call rows show request evidence as recorded or not recorded.
- A local open link appears only when the request artifact id matches an
  existing selected-task artifact with `safe_to_show=true`.
- Raw prompt, raw request, and raw LLM output remain metadata-only and are not
  rendered inline.
- No backend, provider, prompt, skill, contract, fixture, execution page, or
  package behavior changes.

Commit message:

```text
feat(frontend): show ai task request evidence
```
