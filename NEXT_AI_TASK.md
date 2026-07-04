# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 38: Reviewed TestKnowledgeCard Creation Contract.

## Current Task

Slice 38 Task 2: Define reviewed TestKnowledgeCard creation contracts.

## Product Value Answer

After this task, Chtest has explicit data/API/state/artifact contracts for
reviewed TestKnowledgeCard creation from approved candidates without broad CRUD
or automatic prompt eligibility.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-37-test-knowledge-card-candidate-review-contract.md`
8. `docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md`
9. `docs/fixtures/25-test-knowledge-card-candidate-review-golden.md`
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
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract-only task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, broad TestKnowledgeCard CRUD implementation,
backend feature API, frontend page, automatic card creation from model output,
automatic prompt eligibility, automatic knowledge ingestion, external provider
integrations, vector database, embeddings, reranking, graph runtime, MCP
runtime, provider SDK, credentials, artifact upload/mutation/delete,
historical evidence mutation, generated-case auto-approval, runner behavior
changes, report generation behavior changes, remote CI provider behavior,
RBAC, tenants, or permissions.

## Verification Command

```bash
rg -n "Reviewed TestKnowledgeCard Creation|create_reviewed_test_knowledge_card|approved candidate|candidate review artifact|source manifest|allowed_for_prompt=false|duplicate|merge|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md
git diff --check
```

Expected result: required reviewed creation contract terms are present across
data/API/state/artifact contracts and the slice plan, and diff check passes.

## Acceptance

- Contracts define reviewed creation input, created card field mapping,
  source evidence, source manifest, creation outputs, duplicate/merge
  preconditions, prompt eligibility separation, and failure behavior.
- Contracts keep broad CRUD, update/delete/list APIs, prompt eligibility,
  automatic card creation, and duplicate merge/archive/delete behind later
  explicitly scoped workflows.
- Contracts require `allowed_for_prompt=false` by default and preserve
  unsupported claims.
- `NEXT_AI_TASK.md` points to Task 3.

## Commit Message

```text
docs(v2): define reviewed test knowledge card creation contracts
```

## Next Task

Slice 38 Task 3: Add reviewed TestKnowledgeCard creation golden smoke.
