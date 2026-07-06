# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. Update it whenever the active task changes. It is intentionally
smaller than the full docs so an AI worker can start fast without rereading
the full planning set.

## Current Slice

Slice 57: Generated Case Human Review Decision Audit Handoff Contract.

## Current Task

Slice 57 Completion Gate.

## Product Value Answer

After this task, Slice 57 is closed out with the task table recording Task
1-3 commits, focused golden verification passing, memory updated, and the next
narrow V2 task selected. The slice remains evidence-chain packaging only and
does not create GeneratedCaseCandidate approval/rejection, request
optimization, TestCase promotion, automation draft creation, runtime APIs,
frontend surfaces, report/export endpoints, provider integration, or
retrieval behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md`
5. `NEXT_AI_TASK.md`
6. `memory/08-session-handoff.md`
7. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  runtime retrieval docs, and provider SDK docs unless a concrete blocker
  requires them.

## Expected Files

Update only these files for the current task:

```text
docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Completion gate only. Do not add frontend code, backend runtime feature code,
backend feature API, endpoint, router, service, worker, queue, scheduler,
migration, package upgrade, provider integration, provider SDK, external call,
vector database, embeddings, reranking, graph runtime, MCP runtime, runtime
retrieval, prompt execution, AITask orchestration, automatic
`used_knowledge=true`, TestCase promotion, GeneratedCaseCandidate
approve/reject mutation, request optimization mutation, automation draft
creation, runner behavior changes, artifact upload, report generation
behavior, report renderer, export/download endpoint, RBAC, tenants, or
permissions.

## Verification Command

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_audit_handoff_contract_golden.py -q
git diff --check
```

Expected result: focused golden verification passes and diff check passes.

## Acceptance

- Slice 57 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

## Commit Message

```text
docs(v2): complete generated case human review decision audit handoff slice
```

## Next Task

Select the next narrow V2 slice after reviewing
`docs/implementation/10-v2-scope-options.md`.
