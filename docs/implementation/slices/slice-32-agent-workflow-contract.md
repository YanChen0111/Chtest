# Slice 32: Agent Workflow Contract Task Plan

## Goal

Define the requirement-to-reviewed-case agent workflow contract before adding
any orchestration runtime.

Slice 30 defined testing knowledge evidence contracts. Slice 31 persisted those
evidence fields in the real case-generation flow and added prompt/skill seeds
for the final knowledge-driven agents. Slice 32 connects those pieces at the
contract level: which agent runs when, what it may read, what it may write, what
evidence it must cite, which failures block progression, and where human review
remains mandatory.

## Source Documents

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/04-ai-vibecoding-governance.md`
- `docs/implementation/10-v2-scope-options.md`
- `docs/implementation/11-final-rag-agent-strategy.md`
- `docs/implementation/slices/slice-30-test-knowledge-card-contract.md`
- `docs/implementation/slices/slice-31-generated-case-knowledge-evidence-persistence.md`
- `docs/implementation/slices/slice-31-knowledge-prompt-skill-seeds.md`

## Product Value Answer

After this slice, a test engineer can inspect the planned AI workflow from a
requirement to reviewed generated cases and see each agent's allowed inputs,
outputs, write permission, human gate, failure behavior, and evidence trail
before any orchestration code exists.

## Preconditions

- `AITask`, `Artifact`, `PromptVersion`, `SkillVersion`, and `LLMCallLog`
  already exist.
- Requirement review, case generation, generated candidate review, and
  review-state contracts already exist.
- `TestKnowledgeCard`, `KnowledgeEvidence`, and generated-case evidence fields
  are defined.
- GeneratedCaseCandidate persistence already carries knowledge evidence ids,
  review findings, coverage gap notes, automation readiness, and quality score.
- Knowledge prompt/skill seed files exist but are not a runtime orchestration
  engine.

## Non-goals

- No agent orchestration runtime, workflow engine, queue graph, scheduler,
  retries, cancellation, streaming status, or multi-agent execution service.
- No backend feature code, database migrations, API endpoints, frontend pages,
  stores, package upgrades, or seed data mutation.
- No TestKnowledgeCard CRUD, knowledge ingestion runtime, vector database,
  embeddings, reranking, background indexing, graph runtime, external provider
  calls, provider SDK, OAuth, API keys, or remote URL fetch.
- No MCP runtime, MCP server/client transport, marketplace, plugin install,
  remote MCP call, or ToolDefinition behavior change.
- No generated-case auto-approval, automatic TestCase promotion, review bypass,
  automation execution, runner behavior, report generation behavior, artifact
  upload/mutation/delete, cloud storage, RBAC, tenants, permissions, remote CI
  provider behavior, PR comments, deploy, release, merge, push, or scheduling.

## Slice Boundary

- Define a read-only contract for the requirement-to-reviewed-case workflow:
  - `RequirementUnderstandingAgent`;
  - `RiskAnalysisAgent`;
  - `CoverageAnalysisAgent`;
  - `TestDesignAgent`;
  - `CaseGenerationAgent`;
  - `CaseReviewAgent`;
  - `DedupAgent`;
  - `AutomationReadinessAgent`.
- For each agent step, define:
  - synchronous, asynchronous, or review-batched classification;
  - required input evidence;
  - prompt and skill seed names;
  - output artifact or entity shape;
  - allowed write permission;
  - human gate;
  - failure and fallback behavior;
  - required trace fields on AITask/artifacts.
- Define progression rules from requirement analysis to reviewed generated
  candidates without promoting candidates into TestCase automatically.
- Add one fixture/golden proof later showing the contract can be checked without
  running providers or creating runtime side effects.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add agent workflow contract task plan | done | `test -f docs/implementation/slices/slice-32-agent-workflow-contract.md && rg -n "Agent Workflow Contract|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-32-agent-workflow-contract.md NEXT_AI_TASK.md && git diff --check` | pending | planning-only scope |
| Define requirement-to-reviewed-case agent workflow contract | planned | `rg -n "RequirementUnderstandingAgent|CaseReviewAgent|human gate|write permission|failure behavior" docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-32-agent-workflow-contract.md && git diff --check` | pending | contract-only |
| Add agent workflow contract golden smoke | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_agent_workflow_contract_golden.py -q && git diff --check` | pending | no runtime orchestration |
| Slice 32 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_agent_workflow_contract_golden.py backend/app/tests/golden/test_generated_case_knowledge_evidence_persistence_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add Agent Workflow Contract Task Plan

Goal: Define the smallest agent workflow contract slice before changing
contracts or adding tests.

Expected files:

- `docs/implementation/slices/slice-32-agent-workflow-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-32-agent-workflow-contract.md
rg -n "Agent Workflow Contract|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-32-agent-workflow-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Creates the Slice 32 plan.
- Defines product value, source documents, preconditions, non-goals, slice
  boundary, task table, expected files, verification commands, and commit
  messages.
- Keeps scope limited to contract planning.
- Does not add backend runtime code, migrations, frontend code, external
  provider behavior, RAG runtime, MCP runtime, auto-approval, RBAC, tenants, or
  permissions.

Commit message:

```text
docs(v2): add agent workflow contract plan
```

## Task 2: Define Requirement-To-Reviewed-Case Agent Workflow Contract

Goal: Clarify the read-only contract for agent sequence, inputs, outputs,
write permissions, human gates, and failure behavior.

Expected files:

- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-32-agent-workflow-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "RequirementUnderstandingAgent|CaseReviewAgent|human gate|write permission|failure behavior" docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-32-agent-workflow-contract.md
git diff --check
```

Acceptance:

- Contracts define agent sequence from requirement understanding to reviewed
  generated candidates.
- Contracts define per-agent read inputs, write outputs, prompt/skill seed,
  evidence requirements, human gate, and fallback behavior.
- Contracts state generated candidates remain review-gated and are not
  promoted automatically.
- Contracts preserve no runtime orchestration, provider, RAG, MCP, frontend,
  migration, runner, report, RBAC, tenant, or permission expansion.

Commit message:

```text
docs(v2): define agent workflow contract
```

## Task 3: Add Agent Workflow Contract Golden Smoke

Goal: Prove the workflow contract can be validated as evidence-only planning
data without running agents or providers.

Expected files:

- `backend/app/tests/golden/test_agent_workflow_contract_golden.py`
- `docs/fixtures/20-agent-workflow-contract-golden.md`
- `docs/implementation/slices/slice-32-agent-workflow-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_agent_workflow_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden proves the contract names all requirement-to-reviewed-case agents.
- Golden proves each step has prompt/skill seed, input evidence, output,
  write permission, human gate, failure behavior, and trace requirement.
- Golden proves no TestCase, TestRun, Report, provider call, vector index,
  graph job, MCP runtime, or artifact mutation is created by the contract.

Commit message:

```text
test(golden): add agent workflow contract smoke
```

## Slice 32 Completion Gate

Goal: Validate Slice 32 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-32-agent-workflow-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_agent_workflow_contract_golden.py backend/app/tests/golden/test_generated_case_knowledge_evidence_persistence_golden.py -q
git diff --check
```

Acceptance:

- Slice 32 task table records completed task commits.
- Focused golden verification passes.
- `NEXT_AI_TASK.md` points to the next narrow V2 task.

Commit message:

```text
docs(v2): complete agent workflow contract slice
```
