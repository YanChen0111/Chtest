# Next AI Task

This file is the short operational handoff for the next Chtest AI coding
session. Update it whenever the active task changes. It is intentionally
smaller than the full docs so an AI worker can start fast without rereading
the full planning set.

## Current Slice

Slice 59: Generated Case Human Review Decision Application Contract.

## Current Task

Slice 59 Task 1: Add Generated Case Human Review Decision Application task
plan.

## Product Value Answer

After this task, Chtest has a narrow Slice 59 plan for defining how a future
Generated Case Human Review Decision Application contract may consume eligible
Slice 58 preflight evidence and map it to existing review actions only after
explicit human confirmation, without adding runtime APIs, UI, provider
behavior, prompt execution, or real candidate mutations.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/contracts/05-prompt-skill-contract.md`
9. `memory/08-session-handoff.md`
10. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  runtime retrieval docs, and provider SDK docs unless a concrete blocker
  requires them.

## Expected Files

Update only these files for the current task:

```text
docs/implementation/slices/slice-59-generated-case-human-review-decision-application-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Planning docs only. Do not edit contract docs or add frontend code, backend
runtime feature code, backend feature API, endpoint, router, service, worker,
queue, scheduler, migration, package upgrade, provider integration, provider
SDK, external call, vector database, embeddings, reranking, graph runtime, MCP
runtime, runtime retrieval, prompt execution, AITask orchestration, automatic
`used_knowledge=true`, TestCase promotion, GeneratedCaseCandidate
approve/reject mutation, status mutation, request optimization mutation,
automation draft creation, runner behavior changes, artifact upload, report
generation behavior, report renderer, export/download endpoint, RBAC,
tenants, or permissions.

## Verification Command

```bash
if (-not (Test-Path docs/implementation/slices/slice-59-generated-case-human-review-decision-application-contract.md)) { exit 1 }
rg -n "Generated Case Human Review Decision Application|generated_case_human_review_decision_application|apply_generated_case_human_review_decision|generated_case_human_review_decision_application_preflight_artifact_id|mapped review action|actual review action|application status|applied candidate ids|skipped candidate ids|required human confirmation|ReviewHistory result links|failure code|visible reason|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-59-generated-case-human-review-decision-application-contract.md NEXT_AI_TASK.md docs/implementation/10-v2-scope-options.md memory/08-session-handoff.md
git diff --check
```

Expected result: required planning terms are present and diff check passes.

## Acceptance

- Slice 59 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit message.
- The plan names application preflight artifact linkage, audit handoff
  artifact linkage, summary export artifact linkage, decision artifact
  linkage, evidence package artifact linkage, eligible candidate ids, current
  candidate status, mapped review action, actual review action, application
  status, applied candidate ids, skipped candidate ids, required human
  confirmation, required edit application summary, ReviewHistory result links,
  future TestCase references, failure behavior, artifact boundaries, and
  forbidden side effects.
- The plan excludes runtime APIs, frontend, provider integration, provider
  SDKs, external calls, vector database, embeddings, reranking, prompt
  execution, AITask orchestration, actual candidate approval/rejection
  mutation, request optimization mutation, TestCase promotion, automation
  draft creation, report rendering, export/download endpoints, RBAC, tenants,
  permissions, and package upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

## Commit Message

```text
docs(v2): add generated case human review decision application plan
```

## Next Task

Slice 59 Task 2: Define Generated Case Human Review Decision Application
contracts.
