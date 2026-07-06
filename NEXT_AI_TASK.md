# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. Update it whenever the active task changes. It is intentionally
smaller than the full docs so an AI worker can start fast without rereading
the full planning set.

## Current Slice

Slice 58: Generated Case Human Review Decision Application Preflight Contract.

## Current Task

Slice 58 Task 3: Add Generated Case Human Review Decision Application
Preflight golden smoke.

## Product Value Answer

After this task, Chtest has a golden smoke fixture and test proving the
Generated Case Human Review Decision Application Preflight contract remains
eligibility evidence only and cannot approve or reject GeneratedCaseCandidate
records, request optimization, promote TestCases, create automation drafts,
render reports, expose export/download endpoints, or create runtime,
provider, prompt-execution, or retrieval behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/contracts/05-prompt-skill-contract.md`
9. `docs/implementation/slices/slice-58-generated-case-human-review-decision-application-preflight-contract.md`
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
backend/app/tests/golden/test_generated_case_human_review_decision_application_preflight_contract_golden.py
docs/fixtures/46-generated-case-human-review-decision-application-preflight-golden.md
docs/implementation/slices/slice-58-generated-case-human-review-decision-application-preflight-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden test and fixture only. Do not add frontend code, backend runtime
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
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_generated_case_human_review_decision_application_preflight_contract_golden.py -q
git diff --check
```

Expected result: golden smoke passes and diff check passes.

## Acceptance

- Golden names Generated Case Human Review Decision Application Preflight,
  `generated_case_human_review_decision_application_preflight`,
  `preflight_generated_case_human_review_decision_application`, audit handoff
  artifact id, summary export artifact id, decision artifact id, evidence
  package artifact id, mapped review action, eligibility status, eligible
  candidate ids, ineligible candidate ids, blocked action reasons, required
  edit summary, required human confirmation summary, ReviewHistory handoff
  links, failure code, and visible reason.
- Golden asserts the preflight remains eligibility evidence and cannot perform
  runtime APIs, frontend, report rendering, export/download endpoints,
  provider integrations, SDKs, external calls, vector database, embeddings,
  reranking, prompt execution, candidate approval/rejection, request
  optimization, TestCase promotion, automation draft creation, RBAC, tenants,
  permissions, or package upgrades.
- `NEXT_AI_TASK.md` points to Slice 58 completion gate.

## Commit Message

```text
test(golden): add generated case human review decision application preflight smoke
```

## Next Task

Slice 58 completion gate.
