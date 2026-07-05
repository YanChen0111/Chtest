# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 50: KnowledgeAdapter Provider Evaluation Plan Contract.

## Current Task

Slice 50 Task 2: Define KnowledgeAdapter provider evaluation plan contracts.

## Product Value Answer

After this task, Chtest has contract definitions for evaluating future
KnowledgeAdapter providers before any Haystack/LlamaIndex integration,
provider SDK, external call, vector database, embedding, reranking, runtime
retrieval, or provider-backed prompt context behavior exists.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/contracts/01-data-model-contract.md`
5. `docs/contracts/02-api-contract.md`
6. `docs/contracts/03-state-machines.md`
7. `docs/contracts/04-artifact-contract.md`
8. `docs/contracts/05-prompt-skill-contract.md`
9. `docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md`
10. `docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md`
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
docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract-only task. Do not add frontend code, backend runtime feature code,
report generation behavior changes, export/download endpoints, migrations,
package upgrades, broad TestKnowledgeCard CRUD implementation, backend feature
API, frontend page, automatic prompt eligibility, prompt assembly
implementation, prompt runtime execution, provider calls, deterministic
retrieval behavior change, automatic card creation from model output,
automatic knowledge ingestion, external provider integrations, vector database,
embeddings, reranking, graph runtime, MCP runtime, provider SDK, credentials,
provider enablement, runtime retrieval, provider-backed prompt context
evidence, artifact upload/mutation/delete, historical evidence mutation,
generated-case auto-approval, runner behavior changes, remote CI provider
behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
rg -n "KnowledgeAdapter Provider Evaluation Plan|knowledge_adapter_provider_evaluation_plan|evaluate_knowledge_adapter_provider_plan|Haystack|LlamaIndex|KnowledgeEvidence|provider_state|fallback behavior|license review|reference intake|disabled by default|ReviewHistory" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md
git diff --check
```

Expected result: required terms are present and diff check passes.

## Acceptance

- Contracts define provider evaluation inputs, outputs, status labels,
  KnowledgeEvidence normalization, provider_state, disabled by default policy,
  fallback behavior, license/version/reference intake, metrics, ReviewHistory,
  failure behavior, and forbidden side effects.
- Contracts keep Haystack/LlamaIndex provider integration, SDKs, external
  calls, vector database, embeddings, reranking, background indexing, runtime
  retrieval, UI, RBAC, tenants, permissions, and package upgrades out of
  scope.
- `NEXT_AI_TASK.md` points to Task 3.

## Commit Message

```text
docs(v2): define knowledge adapter provider evaluation plan contracts
```

## Next Task

Slice 50 Task 3: Add KnowledgeAdapter provider evaluation plan golden smoke.
