# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 41: TestKnowledgeCard Prompt Context Evidence Contract.

## Current Task

Slice 41 Task 2: Define TestKnowledgeCard prompt context evidence contracts.

## Product Value Answer

After this task, Chtest has data/API/state/artifact/prompt-skill contracts
describing what selected TestKnowledgeCard evidence may be placed into future
prompt context without implementing prompt assembly, provider calls, or
retrieval runtime behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/implementation/slices/slice-40-test-knowledge-card-retrieval-boundary-contract.md`
8. `docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md`
9. `docs/fixtures/28-test-knowledge-card-retrieval-boundary-golden.md`
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
docs/contracts/05-prompt-skill-contract.md
docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract-only task. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, broad TestKnowledgeCard CRUD implementation,
backend feature API, frontend page, automatic prompt eligibility, prompt
assembly implementation, prompt runtime execution, provider calls,
deterministic retrieval behavior change, automatic card creation from model
output, automatic knowledge ingestion, external provider integrations, vector
database, embeddings, reranking, graph runtime, MCP runtime, provider SDK,
credentials, artifact upload/mutation/delete, historical evidence mutation,
generated-case auto-approval, runner behavior changes, report generation
behavior changes, remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
rg -n "TestKnowledgeCard Prompt Context Evidence|prompt_context_evidence|bounded snippet|source hash|retrieval boundary artifact|PromptVersion|SkillVersion|omission reason|context manifest|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-41-test-knowledge-card-prompt-context-evidence-contract.md
git diff --check
```

Expected result: prompt context evidence contract terms are present and diff
check passes.

## Acceptance

- Contracts define prompt context evidence input, safe bounded context entries,
  source hashes, source evidence references, PromptVersion/SkillVersion trace,
  context manifest links, omitted-card summaries, and failure behavior.
- Contracts keep prompt assembly implementation, prompt runtime execution,
  provider calls, retrieval ranking changes, vector indexes, embeddings,
  reranking, graph jobs, MCP runtime, broad CRUD, automatic eligibility, and
  historical evidence mutation out of scope.
- Contracts require `safe_to_show=true`, reviewed redaction, source evidence,
  retrieval boundary evidence, and prompt eligibility artifact evidence before
  card text can enter prompt context.
- `NEXT_AI_TASK.md` points to Slice 41 Task 3.

## Commit Message

```text
docs(v2): define test knowledge card prompt context evidence contracts
```

## Next Task

Slice 41 Task 3: Add TestKnowledgeCard prompt context evidence golden smoke.
