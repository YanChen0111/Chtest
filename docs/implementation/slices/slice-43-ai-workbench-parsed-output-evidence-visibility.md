# Slice 43: AI Workbench Parsed Output Evidence Visibility

## Goal

Show parsed output evidence for each LLM call in the AI Workbench.

AI task LLM call logs already expose `parsed_artifact_id`, but the AI Workbench
call table only shows response artifact id and schema-validation evidence.
Reviewers should be able to see whether parsed output evidence was recorded and
open it only when it is a safe persisted Artifact.

## Product Value Answer

After this slice, reviewers can trace each LLM call to its parsed output
evidence without opening raw LLM output or changing AI runtime behavior.

## Preconditions

- `frontend/src/api/aiTasks.ts` already exposes `parsed_artifact_id`.
- AI task details already include artifact summaries and safe-to-show metadata.
- Slice 40 and Slice 42 introduced reusable frontend-only evidence visibility
  patterns in the AI Workbench.

## Non-goals

- No backend feature code, migrations, API shape changes, provider behavior
  changes, prompt or skill edits, contract changes, fixture changes, package
  upgrades, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- No raw LLM output rendering.
- No artifact upload, mutation, delete, sharing, signed URLs, or external
  artifact fetch.
- No execution page shell/form refactor.

## Slice Boundary

- Update the AI Workbench LLM call log table only.
- Show parsed output evidence as recorded or not recorded.
- Render a local open link only when `parsed_artifact_id` matches an existing
  selected-task artifact with `safe_to_show=true`.
- Preserve response artifact metadata-only display and raw output safety.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add AI Workbench Parsed Output Evidence Visibility task plan | done | `rg -n "Slice 43|AI Workbench Parsed Output Evidence Visibility|parsed output evidence|Non-goals|Task Table" docs/implementation/slices/slice-43-ai-workbench-parsed-output-evidence-visibility.md NEXT_AI_TASK.md && git diff --check` | pending | planning only |
| Show parsed output evidence in AI Workbench | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | focused test passed; build passed with existing chunk warning; diff check clean |
| Slice 43 completion gate | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | no backend/provider/API changes |

## Verification Command

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run build
git diff --check
```

## Acceptance

- AI Workbench LLM call rows show parsed output evidence as recorded or not
  recorded.
- A local open link appears only when the parsed output artifact id matches an
  existing selected-task artifact with `safe_to_show=true`.
- Raw LLM output remains metadata-only and is not rendered inline.
- No backend, provider, prompt, skill, contract, fixture, execution page, or
  package behavior changes.

Commit message:

```text
feat(frontend): show ai task parsed output evidence
```
