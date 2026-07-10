# Slice 41: AI Workbench Artifact Link Accessibility

## Goal

Add row-specific accessible labels to AI Workbench artifact summary open links.

The AI Workbench artifact summary can render multiple compact `打开` links. They
are visually efficient, but assistive technology cannot distinguish which
artifact each link opens without row-specific labels.

## Product Value Answer

After this slice, reviewers using assistive technology can distinguish AI task
artifact links by artifact type and id while visible table text and artifact
URLs remain unchanged.

## Preconditions

- Slice 40 keeps AI Workbench schema-validation evidence frontend-only.
- AI task detail already includes artifact summaries and safe-to-show metadata.

## Non-goals

- No backend feature code, migrations, API shape changes, provider behavior
  changes, prompt or skill edits, contract changes, fixture changes, package
  upgrades, RAG runtime, MCP runtime, RBAC, tenants, or permissions.
- No raw LLM output rendering.
- No artifact upload, mutation, delete, sharing, signed URLs, or external
  artifact fetch.
- No execution page shell/form refactor.

## Slice Boundary

- Update AI Workbench artifact summary open-link attributes only.
- Preserve visible link text, href generation, safe-to-show link condition, and
  existing table layout.
- Add focused component assertions.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add AI Workbench Artifact Link Accessibility task plan | done | `rg -n "Slice 41|AI Workbench Artifact Link Accessibility|row-specific accessible labels|Non-goals|Task Table" docs/implementation/slices/slice-41-ai-workbench-artifact-link-accessibility.md NEXT_AI_TASK.md && git diff --check` | pending | planning only |
| Add accessible labels to AI Workbench artifact links | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | focused test passed; build passed with existing chunk warning; diff check clean |
| Slice 41 completion gate | done | `npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts && npm --prefix frontend run build && git diff --check` | pending | no artifact URL or backend/provider changes |

## Verification Command

```bash
npm --prefix frontend run test -- --run src/views/ai-workbench/AiWorkbenchView.spec.ts
npm --prefix frontend run build
git diff --check
```

## Acceptance

- AI Workbench local artifact summary links include row-specific `aria-label`
  and `title` attributes.
- Visible link text remains `打开`.
- Links still render only when an artifact is safe to show.
- No artifact URL, backend, provider, prompt, skill, contract, fixture,
  execution page, or package behavior changes.

Commit message:

```text
fix(frontend): label ai workbench artifact links
```
