# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 39: TestKnowledgeCard Prompt Eligibility Contract.

## Current Task

Slice 39 Task 2: Define TestKnowledgeCard prompt eligibility contracts.

## Product Value Answer

After this task, Chtest has explicit data/API/state/artifact contracts for
human-reviewed TestKnowledgeCard prompt eligibility before retrieval or prompt
runtime changes exist.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-38-reviewed-test-knowledge-card-creation-contract.md`
8. `docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md`
9. `docs/fixtures/26-reviewed-test-knowledge-card-creation-golden.md`
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
docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract-only task. Do not add frontend code, backend runtime feature code,
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
rg -n "TestKnowledgeCard Prompt Eligibility|mark_card_prompt_eligible|deny_card_prompt_eligibility|request_prompt_eligibility_revision|revoke_card_prompt_eligibility|allowed_for_prompt|safe_to_show|prompt eligibility reason|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-39-test-knowledge-card-prompt-eligibility-contract.md
git diff --check
```

Expected result: required prompt eligibility contract terms are present across
data/API/state/artifact contracts and the slice plan, and diff check passes.

## Acceptance

- Contracts define prompt eligibility input, review actions, source evidence,
  safe_to_show/redaction requirements, outputs, artifact evidence, revocation,
  and failure behavior.
- Contracts keep prompt runtime retrieval, vector indexes, embeddings,
  reranking, graph jobs, provider calls, broad CRUD, automatic eligibility, and
  historical evidence mutation out of scope.
- Contracts require human review and prompt eligibility reason before
  `allowed_for_prompt=true`.
- `NEXT_AI_TASK.md` points to Task 3.

## Commit Message

```text
docs(v2): define test knowledge card prompt eligibility contracts
```

## Next Task

Slice 39 Task 3: Add TestKnowledgeCard prompt eligibility golden smoke.
