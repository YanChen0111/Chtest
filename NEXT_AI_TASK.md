# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 56: Generated Case Human Review Decision Summary Export Contract.

## Current Task

Slice 56 Completion Gate.

## Product Value Answer

After this task, Chtest has a closed Slice 56 handoff with Task 1-3 commits
recorded, the focused Generated Case Human Review Decision Summary Export
golden smoke verified, and the next narrow V2 slice selected.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md`
5. `backend/app/tests/golden/test_generated_case_human_review_decision_summary_export_contract_golden.py`
6. `docs/fixtures/44-generated-case-human-review-decision-summary-export-golden.md`
7. `docs/implementation/10-v2-scope-options.md`
8. `memory/08-session-handoff.md`
9. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  runtime retrieval docs, and provider SDK docs unless a concrete blocker
  requires them.

## Expected Files

Update only these files for the current task:

```text
docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Completion docs only. Do not add frontend code, backend runtime feature code,
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
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_summary_export_contract_golden.py -q
git diff --check
```

Expected result: focused golden smoke passes and diff check passes.

## Acceptance

- Slice 56 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.
- `NEXT_AI_TASK.md` points to the next task.

## Commit Message

```text
docs(v2): complete generated case human review decision summary export slice
```

## Next Task

Select the next narrow V2 slice from `docs/implementation/10-v2-scope-options.md`.
