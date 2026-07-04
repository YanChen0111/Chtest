# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 43: TestKnowledgeCard Prompt Context Audit Summary Contract.

## Current Task

Slice 43 Task 2: Define TestKnowledgeCard prompt context audit summary contracts.

## Product Value Answer

After this task, Chtest contracts define how future review/report surfaces may
summarize TestKnowledgeCard prompt context consumption evidence without
implementing frontend pages, report generation behavior, prompt assembly,
provider calls, or retrieval runtime behavior.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/contracts/05-prompt-skill-contract.md`
8. `docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md`
9. `docs/implementation/slices/slice-42-test-knowledge-card-prompt-context-consumption-contract.md`
10. `docs/fixtures/30-test-knowledge-card-prompt-context-consumption-golden.md`
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
docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract-only task. Do not add frontend code, backend runtime feature code,
report generation behavior changes, migrations, package upgrades, broad
TestKnowledgeCard CRUD implementation, backend feature API, frontend page,
automatic prompt eligibility, prompt assembly implementation, prompt runtime
execution, provider calls, deterministic retrieval behavior change, automatic
card creation from model output, automatic knowledge ingestion, external
provider integrations, vector database, embeddings, reranking, graph runtime,
MCP runtime, provider SDK, credentials, artifact upload/mutation/delete,
historical evidence mutation, generated-case auto-approval, runner behavior
changes, remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
rg -n "TestKnowledgeCard Prompt Context Audit Summary|prompt_context_audit_summary|summarize_prompt_context_consumption|used_knowledge|output citations|skipped evidence|unsupported claims|PromptVersion|SkillVersion|ReviewHistory|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md
git diff --check
```

Expected result: required contract terms are present and diff check passes.

## Acceptance

- Contracts define audit summary inputs, prompt context consumption artifact
  references, context manifest links, cited TestKnowledgeCard ids, source
  hashes, output citations, skipped evidence, unsupported claims,
  PromptVersion/SkillVersion trace, ReviewHistory ids, usage status, failure
  behavior, and forbidden side effects.
- Contracts require audit summaries to be read-only and to preserve
  `used_knowledge` and citation evidence without inventing or mutating
  evidence.
- Contracts keep frontend page, report generation behavior, prompt assembly
  implementation, prompt runtime execution, provider calls, retrieval ranking
  changes, vector indexes, embeddings, reranking, graph jobs, MCP runtime,
  broad CRUD, automatic eligibility, and historical evidence mutation out of
  scope.
- `NEXT_AI_TASK.md` points to Task 3.

## Commit Message

```text
docs(v2): define test knowledge card prompt context audit summary contracts
```

## Next Task

Slice 43 Task 3: Add TestKnowledgeCard prompt context audit summary golden smoke.
