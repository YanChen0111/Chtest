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

## Task 2 Contract Detail

Task 2 is a contract-only documentation step. It updates API, state-machine,
PromptVersion, and SkillVersion seed contracts plus this slice plan. It does
not add runtime orchestration, backend feature code, migrations, frontend
code, provider calls, RAG runtime, or MCP runtime.

### Global Guardrails

- The workflow is seed/contract only. It does not enable runtime
  orchestration, agent scheduling, provider calls, RAG runtime, MCP runtime,
  vector search, graph runtime, external URL fetch, tool execution, or
  background indexing.
- The write permission for every step is limited to its declared draft output
  plus trace metadata that a future AITask/artifact record would carry.
- Every step must preserve `PromptVersion`, `SkillVersion`, prompt hash, skill
  hash, input evidence ids, output ids, schema result, quality gate result, and
  failure behavior in traceable form.
- Human gates remain authoritative. Agent output can recommend, score, group,
  or flag generated candidates, but it cannot approve as a human reviewer and
  cannot automatically promote a GeneratedCaseCandidate into TestCase.
- Missing or conflicting evidence must produce a structured failure output. No
  step may silently fall back to generic cases, hidden knowledge, or remote
  retrieval.

### Agent Step Matrix

| Order | Agent | Classification | PromptVersion / SkillVersion seed | Input evidence | Output contract and write permission | Quality gates | Forbidden actions | Human gate | Failure behavior |
|---|---|---|---|---|---|---|---|---|---|
| 1 | RequirementUnderstandingAgent | synchronous planning step | `requirement_understanding:v1` / `requirement-review-skill:v1` | Requirement id, source text, requirement artifact ids, ContextArtifact manifest when supplied, requester notes, prior review findings. | Requirement understanding draft with intent, actors, flows, constraints, ambiguities, assumptions, evidence refs, and used context ids; write permission is AITask output plus draft artifact only. | Every normalized claim cites requirement text or artifact evidence; ambiguities and assumptions are explicit; schema passes. | Do not rewrite the requirement, close ambiguity without evidence, fetch remote knowledge, or create cases. | Human gate is required when ambiguities, assumptions, or conflicts remain before downstream output is treated as accepted. | `UNABLE_TO_UNDERSTAND_REQUIREMENT`; block downstream acceptance and retain original requirement unchanged. |
| 2 | RiskAnalysisAgent | synchronous planning step | `risk_analysis:v1` / `risk-analysis-skill:v1` | Requirement understanding, requirement refs, domain risk notes, local historical defect or knowledge evidence ids when supplied. | Risk analysis draft with risk ids, severity, likelihood, affected flows, evidence refs, and mitigation notes; write permission is AITask output plus risk draft artifact only. | P0/P1 risks cite input evidence and affected behavior; ids are stable inside the output; schema passes. | Do not fabricate incidents, alter requirement priority, approve mitigation, or query external risk sources. | Human gate requires test lead review for P0/P1 risks and unresolved mitigation gaps. | `UNABLE_TO_ANALYZE_RISK`; block risk-derived prioritization and keep upstream understanding unchanged. |
| 3 | CoverageAnalysisAgent | synchronous planning step | `coverage_analysis:v1` / `coverage-analysis-skill:v1` | Requirement understanding, risk analysis, existing reviewed case ids when supplied, coverage matrix evidence, local knowledge evidence ids. | Coverage draft with covered behaviors, gaps, risk-to-coverage mapping, and evidence refs; write permission is AITask output plus coverage draft artifact only. | Each gap maps to a requirement or risk; coverage claims cite reviewed cases or supplied evidence; schema passes. | Do not declare full coverage without evidence, mutate existing cases, pull external cases, or promote candidates. | Human gate requires reviewer confirmation for residual gaps or coverage-complete claims. | `UNABLE_TO_ANALYZE_COVERAGE`; downstream design must carry an explicit coverage-gap marker. |
| 4 | TestDesignAgent | synchronous planning step | `test_design:v1` / `test-design-skill:v1` | Requirement understanding, risk analysis, coverage analysis, constraints, target test levels/types, local methodology notes. | Test design draft with scenario groups, techniques, priorities, negative/boundary/state coverage, data needs, and trace refs; write permission is AITask output plus design draft artifact only. | Scenario groups trace to requirement/risk/coverage evidence; positive, negative, boundary, and state considerations are present where applicable; schema passes. | Do not create executable automation, create TestCase records, omit P0/P1 negative paths without rationale, or use hidden knowledge. | Human gate requires test designer review before design guidance is accepted for candidate generation. | `UNABLE_TO_DESIGN_TESTS`; case generation stops unless a human-supplied design override is recorded. |
| 5 | CaseGenerationAgent | asynchronous or review-batched draft step | `evidence_case_generation:v1` / `test-case-generation-skill:v1` | Human-accepted or draft design, requirement/risk/coverage evidence, ContextArtifact manifest, existing case refs for avoidance only. | GeneratedCaseCandidate drafts with title, priority, type, preconditions, steps, expected results, input data, requirement refs, risk refs, knowledge evidence ids, and AI reason; write permission is AITask output plus generated candidate drafts only. | Every candidate has steps, expected results, requirement refs, evidence refs, and AI reason; P0/P1 flows include negative or boundary cases unless justified; schema passes. | Do not create canonical TestCase, auto-approve, execute tools, mutate requirements, or enable RAG/provider/vector/graph/MCP runtime. | Human gate requires reviewer action before candidate acceptance, rejection, or any later non-agent promotion path. | `UNABLE_TO_GENERATE_CASES`; no empty success and no generic "verify it works" fallback cases. |
| 6 | CaseReviewAgent | review-batched draft step | `evidence_case_review:v1` / `testcase-review-skill:v1` | GeneratedCaseCandidate drafts, requirement/risk/coverage/design evidence, duplicate hints, reviewer policy, local knowledge evidence ids. | Review draft with per-case findings, quality score, coverage gap notes, correction suggestions, reject/needs-fix recommendation, and evidence refs; write permission is AITask output plus review findings on candidate draft only. | Findings cite candidate fields and evidence; severity and recommendation are structured; pass recommendation checks steps, expected results, refs, and duplicates; schema passes. | Do not approve as a human, promote TestCase, delete candidates, rewrite requirements, or call external tools/reviewers. | Human gate is mandatory: a human reviewer decides accept, reject, needs-fix, and any TestCase promotion outside this contract. | `UNABLE_TO_REVIEW_CASE`; candidate remains pending/needs-review and cannot advance by agent output alone. |
| 7 | DedupAgent | review-batched analysis step | `case_dedup:v1` / `testcase-review-skill:v1` | GeneratedCaseCandidate drafts, reviewed case ids when supplied, titles, steps, expected results, requirement/risk refs, review findings. | Dedup draft with duplicate groups, similarity reasons, keep/merge/split suggestions, and evidence refs; write permission is AITask output plus dedup suggestion artifact only. | Duplicate claims cite matching fields; suggestions preserve requirement/risk coverage; schema passes. | Do not delete, merge, hide, mutate, infer duplicates from title alone, or promote candidates. | Human gate requires reviewer confirmation before merge, removal, or canonical case change. | `UNABLE_TO_DEDUP_CASES`; all candidates remain unchanged and dedup status is inconclusive. |
| 8 | AutomationReadinessAgent | synchronous or review-batched assessment step | `automation_readiness:v1` / `automation-draft-skill:v1` | Reviewed candidate drafts, review findings, dedup suggestions, target framework notes, execution constraints, known test data/dependency evidence. | Automation readiness draft with readiness status, blockers, fixture/data needs, framework fit, risk notes, and trace refs; write permission is AITask output plus readiness fields on candidate draft only. | Readiness distinguishes automatable, manual-only, blocked, and needs-design states; blockers cite evidence; readiness claims include preconditions and expected results; schema passes. | Do not generate automation code, execute tests, create runner commands, mutate repos, call providers, or promote candidates. | Human gate requires automation owner review before automation drafting or implementation is scheduled. | `UNABLE_TO_ASSESS_AUTOMATION_READINESS`; readiness remains unknown and no automation task is created from the failed output. |

### Progression Rules

- Progression from one step to the next requires schema-valid output and a
  passing quality gate, or a recorded human override that names the evidence
  being accepted despite the failed or incomplete agent output.
- Requirement understanding, risk analysis, coverage analysis, and test design
  may be recalculated from immutable input evidence, but this contract does not
  define runtime retry, cancellation, queue, or orchestration behavior.
- Case generation creates only GeneratedCaseCandidate drafts. Case review,
  deduplication, and automation readiness can add structured findings or
  recommendations, but they cannot promote, delete, merge, execute, or deploy.
- Human gate decisions are separate from model output. Future runtime work must
  record who made the decision, when it was made, and which evidence/artifacts
  were reviewed before any state transition outside this seed contract.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add agent workflow contract task plan | done | `test -f docs/implementation/slices/slice-32-agent-workflow-contract.md && rg -n "Agent Workflow Contract|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-32-agent-workflow-contract.md NEXT_AI_TASK.md && git diff --check` | pending | planning-only scope |
| Define requirement-to-reviewed-case agent workflow contract | done | `rg -n "RequirementUnderstandingAgent|CaseReviewAgent|human gate|write permission|failure behavior" docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-32-agent-workflow-contract.md && git diff --check` | pending | contract-only; no runtime behavior |
| Add agent workflow contract golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_agent_workflow_contract_golden.py -q && git diff --check` | pending | no runtime orchestration |
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
