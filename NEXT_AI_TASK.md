# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 50: KnowledgeAdapter Provider Evaluation Plan Contract.

## Current Task

Slice 50 Task 3: Add KnowledgeAdapter provider evaluation plan golden smoke.

## Product Value Answer

After this task, Chtest has a focused golden smoke proving KnowledgeAdapter
provider evaluation remains planning evidence before any Haystack/LlamaIndex
integration, provider SDK, external call, vector database, embedding,
reranking, runtime retrieval, or provider-backed prompt context behavior
exists.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/implementation/10-v2-scope-options.md`
4. `docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md`
5. `backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py`
6. `docs/fixtures/21-mcp-ready-tool-knowledge-safety-golden.md`
7. `docs/contracts/01-data-model-contract.md`
8. `docs/contracts/02-api-contract.md`
9. `docs/contracts/03-state-machines.md`
10. `docs/contracts/04-artifact-contract.md`
11. `docs/contracts/05-prompt-skill-contract.md`
12. `memory/08-session-handoff.md`
13. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py
docs/fixtures/38-knowledge-adapter-provider-evaluation-plan-golden.md
docs/implementation/slices/slice-50-knowledge-adapter-provider-evaluation-plan-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Golden-only task. Do not add frontend code, backend runtime feature code,
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
backend/.venv/Scripts/python.exe -m pytest backend/app/tests/golden/test_knowledge_adapter_provider_evaluation_plan_contract_golden.py -q
git diff --check
```

Expected result: focused golden smoke passes and diff check passes.

## Acceptance

- Golden names KnowledgeAdapter Provider Evaluation Plan, Haystack,
  LlamaIndex, provider evaluation, KnowledgeEvidence, provider_state, fallback
  behavior, license review, reference intake, disabled by default policy,
  metrics, ReviewHistory, failure behavior, and forbidden side effects.
- Golden proves no provider SDK, external call, vector database, embedding,
  reranking, background indexing, runtime retrieval, provider-backed prompt
  context evidence, UI, RBAC, tenants, permissions, or package upgrade is
  created by the contract.
- `NEXT_AI_TASK.md` points to Slice 50 Completion Gate.

## Commit Message

```text
test(golden): add knowledge adapter provider evaluation plan smoke
```

## Next Task

Slice 50 Completion Gate.
