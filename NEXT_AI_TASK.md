# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 06: Requirement To Case Mainline.

## Current Task

Task 8: Add Requirement Review frontend shell.

## Product Value Answer

After this task, Chtest has the first Requirement Review frontend shell for
creating a requirement and viewing mock review and risk results.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/slices/slice-06-requirement-to-case.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- Case Generation Review, AutomationDraft, Playwright, CI/CD, report center,
  RAG runtime, MCP runtime, and migration reference docs unless a concrete
  blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
frontend/src/views/requirements/RequirementReviewView.vue
frontend/src/api/requirements.ts
frontend/src/stores/requirements.ts
frontend/src/router/index.ts
frontend/src/stores/index.ts
frontend/src/views/requirements/RequirementReviewView.spec.ts
```

Read existing frontend route, store, API client, and component test patterns
only as needed to match the current frontend foundation.

## Verification Command

```bash
npm --prefix frontend run test -- --run
```

Expected result: frontend test suite passes.

## Acceptance

- Add a Requirement Review view shell that can create a requirement and display
  review scores, issues, clarification questions, risk items, and context usage.
- Add minimal API and store wiring needed by the shell.
- Keep behavior aligned to existing backend Requirement Review contracts.
- Do not add full case review UI, AutomationDraft entry points, browser
  automation, real provider, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions.
- `git status --short` shows only expected frontend files and required task
  docs before commit.

## Commit Message

```text
feat(frontend): add requirement review shell
```

## Next Task

Slice 06 Task 9: Add Case Generation Review frontend shell.
