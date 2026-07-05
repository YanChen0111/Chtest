# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 54: Generated Case Human Review Evidence Package Contract.

## Current Task

Slice 54 Task 3: Add Generated Case Human Review Evidence Package golden
smoke.

## Product Value Answer

After this task, Chtest has a contract-level fixture and golden smoke proving
Generated Case Human Review Evidence Package remains human-review evidence
packaging only. Future work can verify candidate evidence, review findings,
dedup/readiness signals, prompt-context lineage, and ReviewHistory without
approving or rejecting candidates, promoting TestCases, creating automation
drafts, adding runtime APIs, or changing provider/retrieval behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md`
5. `backend/app/tests/golden/test_generated_case_human_review_evidence_package_contract_golden.py`
6. `docs/fixtures/42-generated-case-human-review-evidence-package-golden.md`
7. `docs/contracts/01-data-model-contract.md`
8. `docs/contracts/02-api-contract.md`
9. `docs/contracts/03-state-machines.md`
10. `docs/contracts/04-artifact-contract.md`
11. `docs/contracts/05-prompt-skill-contract.md`
12. `memory/08-session-handoff.md`
13. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  runtime retrieval docs, and provider SDK docs unless a concrete blocker
  requires them.

## Expected Files

Update only these files for the current task:

```text
backend/app/tests/golden/test_generated_case_human_review_evidence_package_contract_golden.py
docs/fixtures/42-generated-case-human-review-evidence-package-golden.md
docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md
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
approve/reject mutation, automation draft creation, runner behavior changes,
artifact upload/mutation outside declared package evidence, RBAC, tenants, or
permissions.

## Verification Command

```bash
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_evidence_package_contract_golden.py -q
git diff --check
```

Expected result: focused golden smoke passes and diff check passes.

## Acceptance

- Golden names Generated Case Human Review Evidence Package,
  `generated_case_human_review_evidence_package`,
  `build_generated_case_human_review_evidence_package`, GeneratedCaseCandidate
  ids, `source_knowledge_evidence_ids`, `knowledge_evidence_refs_json`,
  `quality_score`, `review_findings_json`, `coverage_gap_notes`,
  `automation_readiness`, dedup findings, prompt-context artifact lineage,
  ReviewHistory, failure behavior, and forbidden side effects.
- Golden proves no backend runtime API, frontend, provider SDK, external call,
  vector database, embedding, reranking, prompt execution, candidate
  approval/rejection, TestCase promotion, automation draft creation, RBAC,
  tenants, permissions, package upgrade, or source evidence mutation is
  created by the contract.
- `NEXT_AI_TASK.md` points to Slice 54 Completion Gate.

## Commit Message

```text
test(golden): add generated case human review evidence package smoke
```

## Next Task

Slice 54 Completion Gate.
