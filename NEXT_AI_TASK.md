# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 09: Case Metrics.

## Current Task

Task 1: Add Case Metrics task plan.

## Product Value Answer

After this task, Chtest has a small, executable Slice 09 plan for measuring AI
case generation quality without expanding into AutomationDraft or execution.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/implementation/02-v1-slice-plan.md`
3. `docs/product/04-ai-quality-metrics.md`
4. `docs/fixtures/01-golden-requirement-to-case.md`
5. `docs/implementation/04-ai-vibecoding-governance.md`

## Do Not Read Unless Needed

- AutomationDraft, execution, Playwright, CI/CD, report center, RAG runtime,
  MCP runtime, and migration reference docs unless a concrete blocker requires
  them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-06-requirement-to-case.md
docs/implementation/slices/slice-09-case-metrics.md
NEXT_AI_TASK.md
```

Do not implement models, APIs, or frontend in this planning task. Create only
the smallest task table needed for subsequent coding sessions.

## Verification Command

```bash
rg -n "Case Metrics|CaseQualityMetric|acceptance_rate|edit_rate|review_progress" docs/implementation/slices/slice-09-case-metrics.md
```

Expected result: Slice 09 task plan references the required metrics and has a
focused next verification command.

## Acceptance

- Create `docs/implementation/slices/slice-09-case-metrics.md` with small tasks
  for backend metrics, API, frontend shell, and golden metric smoke.
- Metrics must include generated_count, approved_count, rejected_count,
  acceptance_rate, edit_rate, and review_progress.
- Keep Slice 09 local to case quality metrics; do not add Test Case Library,
  AutomationDraft, execution, reports, CI/CD, RAG runtime, MCP runtime, RBAC, or
  tenants.
- `git status --short` shows only expected docs before commit.

## Commit Message

```text
docs(metrics): add case metrics task plan
```

## Next Task

Slice 09 Task 2: Add Case Metrics backend calculation.
