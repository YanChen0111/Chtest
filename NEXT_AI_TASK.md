# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 56: Generated Case Human Review Decision Summary Export Contract.

## Current Task

Slice 56 Task 3: Add Generated Case Human Review Decision Summary Export golden smoke.

## Product Value Answer

After this task, Chtest has a focused golden fixture and smoke test proving
Generated Case Human Review Decision Summary Export stays contract-only audit
evidence and cannot approve or reject candidates, request optimization,
promote TestCases, create AutomationDrafts, render reports, expose
export/download endpoints, or create runtime/provider/retrieval behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md`
5. `docs/fixtures/44-generated-case-human-review-decision-summary-export-golden.md`
6. `backend/app/tests/golden/test_generated_case_human_review_decision_summary_export_contract_golden.py`
7. `memory/08-session-handoff.md`
8. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  runtime retrieval docs, and provider SDK docs unless a concrete blocker
  requires them.

## Expected Files

Update only these files for the current task:

```text
backend/app/tests/golden/test_generated_case_human_review_decision_summary_export_contract_golden.py
docs/fixtures/44-generated-case-human-review-decision-summary-export-golden.md
docs/implementation/slices/slice-56-generated-case-human-review-decision-summary-export-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden fixture and test only. Do not add frontend code, backend runtime
feature code, backend feature API, endpoint, router, service, worker, queue,
scheduler, migration, package upgrade, provider integration, provider SDK,
external call, vector database, embeddings, reranking, graph runtime, MCP
runtime, runtime retrieval, prompt execution, AITask orchestration, automatic
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

- Golden names Generated Case Human Review Decision Summary Export,
  `generated_case_human_review_decision_summary_export`,
  `build_generated_case_human_review_decision_summary_export`, decision
  artifact id, evidence package artifact id, decision labels, exported
  decision groups, included/excluded decision artifact ids, source
  traceability summary, ReviewHistory, failure behavior, and forbidden side
  effects.
- Golden proves no backend runtime API, frontend, report renderer,
  export/download endpoint, provider SDK, external call, vector database,
  embedding, reranking, prompt execution, candidate approval/rejection,
  request optimization mutation, TestCase promotion, automation draft
  creation, RBAC, tenants, permissions, package upgrade, or source evidence
  mutation is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 56 Completion Gate.

## Commit Message

```text
test(golden): add generated case human review decision summary export smoke
```

## Next Task

Slice 56 Completion Gate.
