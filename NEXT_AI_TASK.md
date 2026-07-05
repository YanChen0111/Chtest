# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 47: TestKnowledgeCard Prompt Context Discrepancy Resolution Review Contract.

## Current Task

Slice 47 Task 2: Define TestKnowledgeCard prompt context discrepancy resolution review contracts.

## Product Value Answer

After this task, Chtest has data/API/state/artifact/prompt-skill contracts for
future prompt context discrepancy resolution review without mutating review
summaries, review decisions, audit summaries, prompt context evidence,
knowledge evidence, frontend pages, report generation, export endpoints, or
prompt runtime behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/slices/slice-47-test-knowledge-card-prompt-context-discrepancy-resolution-review-contract.md`
4. `docs/implementation/slices/slice-46-test-knowledge-card-prompt-context-review-discrepancy-tracking-contract.md`
5. `docs/contracts/01-data-model-contract.md`
6. `docs/contracts/02-api-contract.md`
7. `docs/contracts/03-state-machines.md`
8. `docs/contracts/04-artifact-contract.md`
9. `docs/contracts/05-prompt-skill-contract.md`
10. `docs/implementation/10-v2-scope-options.md`
11. `memory/08-session-handoff.md`
12. `memory/07-dev-log.md`

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
docs/contracts/05-prompt-skill-contract.md
docs/implementation/slices/slice-47-test-knowledge-card-prompt-context-discrepancy-resolution-review-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract-only task. Do not add frontend code, backend runtime feature code,
report generation behavior changes, export/download endpoints,
migrations, package upgrades, broad TestKnowledgeCard CRUD implementation,
backend feature API, frontend page, automatic prompt eligibility, prompt
assembly implementation, prompt runtime execution, provider calls,
deterministic retrieval behavior change, automatic card creation from model
output, automatic knowledge ingestion, external provider integrations, vector
database, embeddings, reranking, graph runtime, MCP runtime, provider SDK,
credentials, artifact upload/mutation/delete, historical evidence mutation,
generated-case auto-approval, runner behavior changes, remote CI provider
behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
rg -n "TestKnowledgeCard Prompt Context Discrepancy Resolution Review|prompt_context_discrepancy_resolution_review|review_prompt_context_discrepancy_resolution|resolution action|accepted discrepancy ids|rejected discrepancy ids|acknowledged discrepancy ids|affected citation ids|evidence gap summary|mismatch reason|resolution status|ReviewHistory|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-47-test-knowledge-card-prompt-context-discrepancy-resolution-review-contract.md
git diff --check
```

Expected result: required contract terms are present and diff check passes.

## Acceptance

- Contracts define resolution review inputs, discrepancy artifact references,
  review summary export artifact references, affected citation ids, resolution
  action, accepted/rejected/acknowledged discrepancy ids, evidence gap summary,
  mismatch reason, reviewer note, resulting resolution status, ReviewHistory,
  source hashes, context manifest links, PromptVersion/SkillVersion trace,
  failure behavior, and forbidden side effects.
- Contracts require resolution review to preserve underlying discrepancy
  records, review summary exports, review decisions, audit summaries,
  consumption evidence, and knowledge artifacts without inventing, mutating, or
  automatically resolving evidence.
- Contracts keep frontend page, report generation behavior, export/download
  endpoint, prompt assembly implementation, prompt runtime execution, provider
  calls, retrieval ranking changes, vector indexes, embeddings, reranking,
  graph jobs, MCP runtime, broad CRUD, automatic eligibility, and historical
  evidence mutation out of scope.
- `NEXT_AI_TASK.md` points to Task 3.

## Commit Message

```text
docs(v2): define test knowledge card prompt context discrepancy resolution review contracts
```

## Next Task

Slice 47 Task 3: Add TestKnowledgeCard prompt context discrepancy resolution review golden smoke.
