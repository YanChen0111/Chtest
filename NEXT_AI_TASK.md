# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 54: Generated Case Human Review Evidence Package Contract.

## Current Task

Slice 54 Task 2: Define Generated Case Human Review Evidence Package
contracts.

## Product Value Answer

After this task, Chtest has data, API, state-machine, artifact, and
prompt/skill contracts for packaging GeneratedCaseCandidate review evidence
into a human-review evidence package without approving or rejecting
candidates, promoting TestCases, creating automation drafts, adding runtime
APIs, or changing provider/retrieval behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/contracts/05-prompt-skill-contract.md`
9. `docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md`
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
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/contracts/05-prompt-skill-contract.md
docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract docs only. Do not add frontend code, backend runtime feature code,
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
rg -n "Generated Case Human Review Evidence Package|generated_case_human_review_evidence_package|build_generated_case_human_review_evidence_package|GeneratedCaseCandidate|source_knowledge_evidence_ids|knowledge_evidence_refs_json|quality_score|review_findings_json|coverage_gap_notes|automation_readiness|dedup findings|human review checklist|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-54-generated-case-human-review-evidence-package-contract.md
git diff --check
```

Expected result: required contract terms are present and diff check passes.

## Acceptance

- Contracts define generated case human review evidence package inputs,
  outputs, candidate summary, knowledge evidence linkage, prompt-context
  lineage, review findings, quality score, coverage gap notes, automation
  readiness, dedup findings, evidence chain completeness, missing/conflicting
  evidence summaries, review blocker summary, human review checklist,
  ReviewHistory, failure behavior, and forbidden side effects.
- Contracts keep backend runtime APIs, frontend, provider integrations, SDKs,
  external calls, vector database, embeddings, reranking, prompt execution,
  candidate approval/rejection, TestCase promotion, automation draft creation,
  RBAC, tenants, permissions, and package upgrades out of scope.
- `NEXT_AI_TASK.md` points to Slice 54 Task 3.

## Commit Message

```text
docs(v2): define generated case human review evidence package contracts
```

## Next Task

Slice 54 Task 3: Add Generated Case Human Review Evidence Package golden smoke.
