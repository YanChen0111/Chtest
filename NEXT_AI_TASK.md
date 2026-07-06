# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. Update it whenever the active task changes. It is intentionally
smaller than the full docs so an AI worker can start fast without rereading
the full planning set.

## Current Slice

Slice 57: Generated Case Human Review Decision Audit Handoff Contract.

## Current Task

Slice 57 Task 3: Add Generated Case Human Review Decision Audit Handoff golden
smoke.

## Product Value Answer

After this task, Chtest has a contract-level golden fixture and smoke test
proving Generated Case Human Review Decision Audit Handoff remains
evidence-chain packaging only. It preserves Slice 56 summary export linkage,
source decision artifacts, linked evidence package artifacts, evidence chain
status, included/excluded artifact reasons, unresolved follow-up flags, source
traceability handoff summary, ReviewHistory links, failure code, and visible
reason without performing actual GeneratedCaseCandidate approval/rejection,
request optimization, TestCase promotion, automation draft creation, runtime
API work, UI work, report/export endpoints, or provider/retrieval behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/contracts/05-prompt-skill-contract.md`
9. `docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md`
10. `memory/08-session-handoff.md`
11. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  runtime retrieval docs, and provider SDK docs unless a concrete blocker
  requires them.

## Expected Files

Update only these files for the current task:

```text
backend/app/tests/golden/test_generated_case_human_review_decision_audit_handoff_contract_golden.py
docs/fixtures/45-generated-case-human-review-decision-audit-handoff-golden.md
docs/implementation/slices/slice-57-generated-case-human-review-decision-audit-handoff-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden smoke only. Do not add frontend code, backend runtime feature code,
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

Expected result: focused golden smoke passes and diff check passes.

## Acceptance

- Golden names Generated Case Human Review Decision Audit Handoff,
  `generated_case_human_review_decision_audit_handoff`,
  `build_generated_case_human_review_decision_audit_handoff`, summary export
  artifact id, decision artifact id, evidence package artifact id, evidence
  chain status, included artifact ids, excluded artifact reasons, unresolved
  follow-up flags, source traceability handoff summary, ReviewHistory, failure
  behavior, and forbidden side effects.
- Golden proves no backend runtime API, frontend, report renderer,
  export/download endpoint, provider SDK, external call, vector database,
  embedding, reranking, prompt execution, candidate approval/rejection,
  request optimization mutation, TestCase promotion, automation draft
  creation, RBAC, tenants, permissions, package upgrade, or source evidence
  mutation is created by the contract.
- `NEXT_AI_TASK.md` points to Slice 57 Completion Gate.

## Commit Message

```text
test(golden): add generated case human review decision audit handoff smoke
```

## Next Task

Slice 57 Completion Gate.
