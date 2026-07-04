# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 39: TestKnowledgeCard Prompt Eligibility Contract.

## Current Task

Slice 39 Task 1: Add TestKnowledgeCard Prompt Eligibility Contract task plan.

## Product Value Answer

After this task, Chtest has a narrow plan for human-reviewed
TestKnowledgeCard prompt eligibility before retrieval or prompt runtime changes
exist.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md`
8. `docs/fixtures/26-reviewed-test-knowledge-card-creation-golden.md`
9. `docs/implementation/10-v2-scope-options.md`
10. `memory/08-session-handoff.md`
11. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Planning-only task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, broad TestKnowledgeCard CRUD implementation,
backend feature API, frontend page, automatic prompt eligibility, prompt
runtime retrieval change, automatic card creation from model output, automatic
knowledge ingestion, external provider integrations, vector database,
embeddings, reranking, graph runtime, MCP runtime, provider SDK, credentials,
artifact upload/mutation/delete, historical evidence mutation,
generated-case auto-approval, runner behavior changes, report generation
behavior changes, remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
test -f docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md
rg -n "TestKnowledgeCard Prompt Eligibility|allowed_for_prompt|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md NEXT_AI_TASK.md
git diff --check
```

Expected result: Slice 39 plan file exists, required plan terms are present,
and diff check passes.

## Acceptance

- Slice 39 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names TestKnowledgeCard prompt eligibility actions, safe_to_show,
  redaction, source evidence, ReviewHistory, prompt eligibility reason,
  artifact evidence, revocation/failure behavior, human review, and non-goals.
- `NEXT_AI_TASK.md` points to Task 2.

## Commit Message

```text
docs(v2): add test knowledge card prompt eligibility plan
```

## Next Task

Slice 39 Task 2: Define TestKnowledgeCard prompt eligibility contracts.
