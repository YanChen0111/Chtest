# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 55: Generated Case Human Review Decision Contract.

## Current Task

Slice 55 Task 1: Add Generated Case Human Review Decision task plan.

## Product Value Answer

After this task, Chtest has a narrow plan for a Generated Case Human Review
Decision contract that consumes the Slice 54 evidence package without
performing actual GeneratedCaseCandidate approval/rejection, TestCase
promotion, automation draft creation, runtime API work, UI work, or
provider/retrieval behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md`
5. `docs/contracts/01-data-model-contract.md`
6. `docs/contracts/02-api-contract.md`
7. `docs/contracts/03-state-machines.md`
8. `docs/contracts/04-artifact-contract.md`
9. `docs/contracts/05-prompt-skill-contract.md`
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
docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Task plan only. Do not update contracts yet. Do not add frontend code, backend
runtime feature code, backend feature API, endpoint, router, service, worker,
queue, scheduler, migration, package upgrade, provider integration, provider
SDK, external call, vector database, embeddings, reranking, graph runtime, MCP
runtime, runtime retrieval, prompt execution, AITask orchestration, automatic
`used_knowledge=true`, TestCase promotion, GeneratedCaseCandidate
approve/reject mutation, automation draft creation, runner behavior changes,
artifact upload/mutation outside declared decision evidence, RBAC, tenants, or
permissions.

## Verification Command

```bash
if (-not (Test-Path docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md)) { exit 1 }
rg -n "Generated Case Human Review Decision|generated_case_human_review_decision|review_generated_case_human_review_evidence_package|generated_case_human_review_evidence_package_artifact_id|accepted_for_future_promotion|accepted_with_required_edits|needs_optimization|rejected_for_insufficient_evidence|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-55-generated-case-human-review-decision-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Expected result: Slice 55 plan exists, required terms are present, and diff
check passes.

## Acceptance

- Slice 55 task plan exists with product value, non-goals, task table,
  expected files, verification commands, and commit message.
- The plan names evidence package artifact linkage, GeneratedCaseCandidate
  id/status, candidate summary, evidence chain completeness, missing/conflicting
  evidence summaries, review blocker summary, dedup/readiness summary, human
  review checklist, decision labels, reviewer label/comment, requested edit
  fields, duplicate notes, ReviewHistory, failure behavior, and forbidden side
  effects.
- The plan excludes runtime APIs, frontend, provider integration, provider
  SDKs, external calls, vector database, embeddings, reranking, prompt
  execution, actual candidate approval/rejection mutation, TestCase promotion,
  automation draft creation, artifact upload, RBAC, tenants, and permissions.
- `NEXT_AI_TASK.md` points to Slice 55 Task 2.

## Commit Message

```text
docs(v2): add generated case human review decision plan
```

## Next Task

Slice 55 Task 2: Define Generated Case Human Review Decision contracts.
