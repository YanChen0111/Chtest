# Slice 40: AI Task Schema Validation Evidence Visibility

## Goal

Show schema-validation evidence status for each LLM call in the AI Workbench.

AI task details already expose `schema_validation_artifact_id` on LLM call logs,
but the AI Workbench only shows response artifact ids. Reviewers should be able
to tell whether schema validation evidence was recorded without opening raw LLM
output or changing provider/runtime behavior.

## Product Value Answer

After this slice, reviewers can see per LLM call whether schema-validation
evidence exists, and can open the local evidence artifact only when it is a
safe persisted Artifact.

## Preconditions

- `frontend/src/api/aiTasks.ts` already exposes `schema_validation_artifact_id`.
- AI task details already include safe artifact summaries.
- Slice 39 is verified but intentionally remains uncommitted because shared
  docs/memory files contain large unrelated dirty-worktree changes; do not use
  broad staging.

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
- Show recorded vs not recorded schema-validation evidence status.
- Render a local open link only when `schema_validation_artifact_id` matches an
  existing selected-task artifact with `safe_to_show=true`.
- Preserve existing AI task loading, artifact summary, raw output safety, and
  provider/runtime behavior.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add AI Task Schema Validation Evidence Visibility task plan | done | `rg -n "Slice 40|AI Task Schema Validation Evidence Visibility|schema-validation evidence|Non-goals|Task Table" docs/implementation/slices/slice-40-ai-task-schema-validation-evidence-visibility.md NEXT_AI_TASK.md && git diff --check` | pending | planning only |
| Show schema-validation evidence in AI Workbench | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | focused test passed; build passed with existing chunk warning; diff check clean |
| Slice 40 completion gate | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | no backend/provider/API changes |

## Verification Command

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run build
git diff --check
```

## Acceptance

- AI Workbench LLM call rows show schema-validation evidence as recorded or not
  recorded.
- A local open link appears only when the schema-validation artifact id matches
  an existing safe artifact summary.
- Raw LLM output remains metadata-only and is not rendered inline.
- No backend, provider, prompt, skill, contract, fixture, execution page, or
  package behavior changes.

Commit message:

```text
feat(frontend): show ai task schema validation evidence
```
