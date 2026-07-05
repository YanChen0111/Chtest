# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 50: KnowledgeAdapter Provider Evaluation Plan Contract.

## Current Task

Slice 50 Task 1: Add KnowledgeAdapter Provider Evaluation Plan task plan.

## Product Value Answer

After this task, Chtest has a narrow plan for evaluating future
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
9. `docs/implementation/slices/slice-33-mcp-ready-tool-knowledge-safety-contract.md`
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
docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md
docs/implementation/10-v2-scope-options.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Planning-only task. Do not add frontend code, backend runtime feature code,
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
test -f docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md
rg -n "KnowledgeAdapter Provider Evaluation Plan|Haystack|LlamaIndex|provider evaluation|KnowledgeEvidence|provider_state|fallback behavior|license|reference intake|disabled by default|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md NEXT_AI_TASK.md
git diff --check
```

Expected result: plan file exists, required terms are present, and diff check
passes.

## Acceptance

- Slice 50 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names provider evaluation inputs and outputs, KnowledgeEvidence
  normalization, provider_state, fallback behavior, license/version/reference
  intake, disabled-by-default policy, metrics, ReviewHistory, failure behavior,
  and non-goals.
- The plan excludes Haystack/LlamaIndex integration, provider SDK, external
  calls, vector database, embeddings, reranking, background indexing, runtime
  retrieval, UI, RBAC, tenants, permissions, and package upgrades.
- `NEXT_AI_TASK.md` points to Task 2.

## Commit Message

```text
docs(v2): add knowledge adapter provider evaluation plan
```

## Next Task

Slice 50 Task 2: Define KnowledgeAdapter provider evaluation plan contracts.
