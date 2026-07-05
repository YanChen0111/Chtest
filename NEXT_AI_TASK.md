# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 51: KnowledgeAdapter Provider Evaluation Review Decision Contract.

## Current Task

Slice 51 Task 2: Define KnowledgeAdapter provider evaluation review decision
contracts.

## Product Value Answer

After this task, Chtest has data, API, state-machine, artifact, and
prompt/skill contracts for reviewing KnowledgeAdapter provider evaluation plan
evidence before any provider integration, SDK, external call, vector database,
embedding, reranking, runtime retrieval, provider-backed prompt context
behavior, frontend page, RBAC, tenants, or permissions exist.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md`
5. `docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md`
6. `docs/contracts/01-data-model-contract.md`
7. `docs/contracts/02-api-contract.md`
8. `docs/contracts/03-state-machines.md`
9. `docs/contracts/04-artifact-contract.md`
10. `docs/contracts/05-prompt-skill-contract.md`
11. `memory/08-session-handoff.md`
12. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, provider implementation docs,
  and runtime retrieval docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/contracts/01-data-model-contract.md
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/04-artifact-contract.md
docs/contracts/05-prompt-skill-contract.md
docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract-only task. Do not add frontend code, backend runtime feature code,
report generation behavior changes, export/download endpoints, migrations,
package upgrades, broad KnowledgeAdapter CRUD implementation, backend feature
API, frontend page, automatic prompt eligibility, prompt assembly
implementation, prompt runtime execution, provider calls, deterministic
retrieval behavior change, automatic knowledge ingestion, external provider
integrations, vector database, embeddings, reranking, graph runtime, MCP
runtime, provider SDK, credentials, provider enablement, runtime retrieval,
provider-backed prompt context evidence, artifact upload/mutation/delete,
historical evidence mutation, generated-case auto-approval, runner behavior
changes, remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
rg -n "KnowledgeAdapter Provider Evaluation Review Decision|knowledge_adapter_provider_evaluation_review_decision|review_knowledge_adapter_provider_evaluation|provider evaluation plan artifact id|license review|reference intake|KnowledgeEvidence normalization|provider_state|fallback behavior|ReviewHistory|failure code|visible reason" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-51-knowledge-adapter-provider-evaluation-review-decision-contract.md
git diff --check
```

Expected result: required contract terms are present and diff check passes.

## Acceptance

- Contracts define provider evaluation review inputs, outputs, review decision
  labels, review status labels, provider suitability status,
  KnowledgeEvidence normalization, provider_state, disabled by default policy,
  fallback behavior, license/version/reference intake, metrics, ReviewHistory,
  failure behavior, and forbidden side effects.
- Contracts keep provider enablement, provider integration, provider SDKs,
  external calls, vector database, embeddings, reranking, background indexing,
  runtime retrieval, UI, RBAC, tenants, permissions, and package upgrades out
  of scope.
- `NEXT_AI_TASK.md` points to Task 3.

## Commit Message

```text
docs(v2): define knowledge adapter provider evaluation review decision contracts
```

## Next Task

Slice 51 Task 3: Add KnowledgeAdapter provider evaluation review decision
golden smoke.
