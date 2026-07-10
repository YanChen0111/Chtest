# Slice 42: AI Workbench Context Manifest Evidence Visibility

## Goal

Show AI task context manifest evidence in the AI Workbench task detail.

AI task details already expose `context_manifest_artifact_id`, but the AI
Workbench currently shows only context artifact ids and used context artifact
ids. Reviewers should be able to see whether the context manifest evidence was
recorded, and open it only when it is a safe persisted Artifact.

## Product Value Answer

After this slice, reviewers can confirm whether an AI task has a context
manifest evidence artifact without changing AI runtime behavior or exposing raw
LLM output.

## Preconditions

- `frontend/src/api/aiTasks.ts` already exposes `context_manifest_artifact_id`.
- AI task details already include artifact summaries and safe-to-show metadata.
- Slice 40 and Slice 41 keep AI Workbench evidence changes frontend-only.

## Non-goals

- No backend feature code, migrations, API shape changes, provider behavior
  changes, prompt or skill edits, contract changes, fixture changes, package
  upgrades, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- No raw LLM output rendering.
- No artifact upload, mutation, delete, sharing, signed URLs, or external
  artifact fetch.
- No execution page shell/form refactor.

## Slice Boundary

- Update the AI Workbench task detail context section only.
- Show context manifest evidence as recorded or not generated.
- Render a local open link only when `context_manifest_artifact_id` matches an
  existing selected-task artifact with `safe_to_show=true`.
- Preserve existing AI task loading, artifact summary, LLM call log, raw output
  safety, and provider/runtime behavior.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add AI Workbench Context Manifest Evidence Visibility task plan | done | `rg -n "Slice 42|AI Workbench Context Manifest Evidence Visibility|context manifest evidence|Non-goals|Task Table" docs/implementation/slices/slice-42-ai-workbench-context-manifest-evidence-visibility.md NEXT_AI_TASK.md && git diff --check` | pending | planning only |
| Show context manifest evidence in AI Workbench | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | focused test passed; build passed with existing chunk warning; diff check clean |
| Slice 42 completion gate | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | no backend/provider/API changes |

## Verification Command

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run build
git diff --check
```

## Acceptance

- AI Workbench task details show context manifest evidence as recorded or not
  generated.
- A local open link appears only when the context manifest artifact id matches
  an existing selected-task artifact with `safe_to_show=true`.
- Raw LLM output remains metadata-only and is not rendered inline.
- No backend, provider, prompt, skill, contract, fixture, execution page, or
  package behavior changes.

Commit message:

```text
feat(frontend): show ai task context manifest evidence
```
