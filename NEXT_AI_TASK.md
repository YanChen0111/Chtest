# Next AI Task

This file is the short operational handoff for the next Chtest AI coding session.
Update it whenever the active task changes. It is intentionally smaller than the
full docs so an AI worker can start fast without rereading the full planning set.

## Current Slice

Slice 32: Agent Workflow Contract.

## Current Task

Slice 32 Task 2: Define requirement-to-reviewed-case agent workflow contract.

## Product Value Answer

After this task, Chtest contracts define the requirement-to-reviewed-case agent
sequence, inputs, outputs, write permissions, human gates, failure behavior,
and evidence trace rules.

## Must Read

1. `START_HERE_FOR_AI.md`
2. `docs/product/01-positioning-and-scope.md`
3. `docs/contracts/01-data-model-contract.md`
4. `docs/contracts/02-api-contract.md`
5. `docs/contracts/03-state-machines.md`
6. `docs/contracts/04-artifact-contract.md`
7. `docs/contracts/05-prompt-skill-contract.md`
8. `docs/implementation/10-v2-scope-options.md`
9. `docs/implementation/11-final-rag-agent-strategy.md`
10. `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
11. `docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md`
12. `docs/implementation/slices/slice-31-knowledge-prompt-skill-seeds.md`
13. `memory/08-session-handoff.md`
14. `memory/07-dev-log.md`

## Do Not Read Unless Needed

- Broad architecture, migration, enterprise collaboration, marketplace,
  distributed execution, cloud storage, cloud CI/provider integration, RBAC,
  tenants, permissions, frontend redesign docs, and provider implementation
  docs unless a concrete blocker requires them.

## Expected Files

Create or update only these files for the current task:

```text
docs/contracts/02-api-contract.md
docs/contracts/03-state-machines.md
docs/contracts/05-prompt-skill-contract.md
docs/implementation/slices/slice-32-agent-workflow-contract.md
NEXT_AI_TASK.md
memory/08-session-handoff.md
memory/07-dev-log.md
```

Contract task only. Do not add frontend code, backend runtime feature code,
migrations, package upgrades, external provider integrations, vector database,
embeddings, reranking, background indexing, graph runtime, MCP runtime,
TestKnowledgeCard CRUD, artifact upload/mutation/delete, generated-case
auto-approval, runner behavior changes, report generation behavior changes,
remote CI provider behavior, RBAC, tenants, or permissions.

## Verification Command

```bash
rg -n "RequirementUnderstandingAgent|CaseReviewAgent|human gate|write permission|failure behavior" docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-32-agent-workflow-contract.md
git diff --check
```

Expected result: API/state/prompt-skill contracts and the Slice 32 plan describe
agent workflow gates and diff check passes.

## Acceptance

- Contracts define agent sequence from requirement understanding to reviewed
  generated candidates.
- Contracts define per-agent read inputs, write outputs, prompt/skill seed,
  evidence requirements, human gate, and fallback behavior.
- Contracts state generated candidates remain review-gated and are not promoted
  automatically.
- Contracts preserve no runtime orchestration, provider, RAG, MCP, frontend,
  migration, runner, report, RBAC, tenant, or permission expansion.

## Commit Message

```text
docs(v2): define agent workflow contract
```

## Next Task

Slice 32 Task 3: Add agent workflow contract golden smoke.
