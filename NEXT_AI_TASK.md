# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 54: Generated Case Human Review Evidence Package Contract.

## Current Task

Slice 54 Task 1: Add Generated Case Human Review Evidence Package task plan.

## Product Value Answer

After this task, Chtest has a narrow plan for packaging GeneratedCaseCandidate
review evidence into a human-review evidence package without approving or
rejecting candidates, promoting TestCases, creating automation drafts, adding
runtime APIs, or changing provider/retrieval behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/05-prompt-skill-contract.md`
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
docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Task plan only. Do not update contracts yet. Do not add frontend code, backend
runtime feature code, backend feature API, endpoint, router, service, worker,
queue, scheduler, migration, package upgrade, provider integration, provider
SDK, external call, vector database, embeddings, reranking, graph runtime, MCP
runtime, runtime retrieval, prompt execution, AITask orchestration,
automatic `used_knowledge=true`, TestCase promotion, GeneratedCaseCandidate
approve/reject mutation, automation draft creation, runner behavior changes,
artifact upload/mutation outside declared package evidence, RBAC, tenants, or
permissions.

## Verification Command

```bash
if (-not (Test-Path docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md)) { exit 1 }
rg -n "Generated Case Human Review Evidence Package|generated_case_human_review_evidence_package|GeneratedCaseCandidate|source_knowledge_evidence_ids|knowledge_evidence_refs_json|quality_score|review_findings_json|coverage_gap_notes|automation_readiness|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Expected result: Slice 54 plan exists, required terms are present, and diff
check passes.

## Acceptance

- Slice 54 task plan exists with product value, non-goals, task table,
  expected files, verification commands, and commit message.
- The plan names GeneratedCaseCandidate ids, `source_knowledge_evidence_ids`,
  `knowledge_evidence_refs_json`, `quality_score`, `review_findings_json`,
  `coverage_gap_notes`, `automation_readiness`, dedup findings, prompt context
  evidence/consumption/audit/discrepancy handoff artifact ids, ReviewHistory,
  failure behavior, and forbidden side effects.
- The plan excludes runtime APIs, frontend, provider integration, provider
  SDKs, external calls, vector database, embeddings, reranking, prompt
  execution, TestCase promotion, GeneratedCaseCandidate approve/reject
  mutation, automation draft creation, artifact upload, RBAC, tenants, and
  permissions.
- `NEXT_AI_TASK.md` points to Slice 54 Task 2.

## Commit Message

```text
docs(v2): add generated case human review evidence package plan
```

## Next Task

Slice 54 Task 2: Define Generated Case Human Review Evidence Package contracts.
