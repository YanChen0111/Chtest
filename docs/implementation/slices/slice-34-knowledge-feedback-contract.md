# Slice 34: Knowledge Feedback Contract Task Plan

## Goal

Define the KnowledgeFeedbackAgent contract before any feedback runtime,
TestKnowledgeCard CRUD, or prompt-eligibility automation exists.

This slice is contract-first. It documents how accepted cases, rejected cases,
review comments, failures, reports, execution evidence, and normalized
KnowledgeEvidence may become draft knowledge feedback for human review.

## Product Value Answer

After this slice, Chtest can close the testing evidence loop without silently
polluting its knowledge base. Reviewed project outcomes can be proposed as
draft knowledge feedback, but human review remains the only authority that may
approve a TestKnowledgeCard or make feedback prompt-eligible.

## Current Evidence Baseline

- `prompts/knowledge_feedback/v1.md` and
  `skills/knowledge-feedback-skill/v1.md` already exist as seed files.
- Slice 30 defined TestKnowledgeCard and KnowledgeEvidence contracts.
- Slice 31 persisted generated-case knowledge evidence fields.
- Slice 32 defined the requirement-to-reviewed-case agent workflow contract.
- Slice 33 defined MCP-ready ToolDefinition and KnowledgeAdapter safety
  boundaries before any provider/runtime work.
- `docs/implementation/11-final-rag-agent-strategy.md` names
  KnowledgeFeedbackAgent as the agent that converts accepted/rejected cases,
  review comments, failures, and reports into improved knowledge.

## Non-goals

- No KnowledgeFeedbackAgent runtime, orchestration, queue, background job,
  scheduler, or backend feature API.
- No TestKnowledgeCard CRUD, automatic card creation, prompt-eligible
  auto-marking, automatic knowledge ingestion, or knowledge-card approval.
- No mutation of historical ReviewHistory, FailureAnalysis, Report, TestRun,
  TestCase, GeneratedCaseCandidate, or Artifact rows.
- No vector database, embeddings, reranking, background indexing, graph
  runtime, GraphRAG job, MCP runtime, provider SDK, external provider calls,
  credentials, OAuth, remote URL fetch, or remote CI/CD provider behavior.
- No frontend page, migration, package upgrade, runner behavior change, report
  generation behavior change, generated-case auto-approval, RBAC, tenants, or
  permissions.

## Contract Boundary To Define

The follow-up contract task should define:

- KnowledgeFeedbackAgent input evidence:
  - accepted and rejected GeneratedCaseCandidate summaries;
  - reviewed TestCase summaries;
  - ReviewHistory comments and decisions;
  - FailureAnalysis summaries;
  - Report summaries and evidence manifests;
  - TestRun/TestResult execution evidence summaries;
  - normalized KnowledgeEvidence and existing TestKnowledgeCard summaries.
- Draft feedback output:
  - feedback_type;
  - draft_knowledge_type;
  - source_entity_type and source_entity_id;
  - source_quote_or_hash and source_span;
  - recommendation;
  - confidence;
  - used_knowledge_evidence_ids;
  - unsupported_claims;
  - review_findings.
- Review and prompt-eligibility boundary:
  - feedback remains draft until a human reviews it;
  - model confidence must not imply approval;
  - feedback must not become prompt-eligible automatically;
  - accepted and rejected examples must remain separate.
- Failure and fallback behavior:
  - insufficient source evidence returns
    `UNABLE_TO_CREATE_KNOWLEDGE_FEEDBACK`;
  - unsupported claims remain visible;
  - fallback must not fabricate knowledge.
- Artifact and trace rules:
  - feedback draft artifacts cite source evidence ids;
  - raw provider payloads, secrets, credentials, and free-floating model text
    are not valid source evidence;
  - feedback outputs must preserve prompt_version, skill_version, schema
    validation, input evidence ids, output artifact ids, and failure code.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add knowledge feedback contract task plan | done | `test -f docs/implementation/slices/slice-34-knowledge-feedback-contract.md && rg -n "Knowledge Feedback Contract|KnowledgeFeedbackAgent|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-34-knowledge-feedback-contract.md NEXT_AI_TASK.md && git diff --check` | pending | planning-only scope |
| Define KnowledgeFeedbackAgent draft feedback contracts | done | `rg -n "KnowledgeFeedbackAgent|knowledge_feedback|draft feedback|prompt-eligible|UNABLE_TO_CREATE_KNOWLEDGE_FEEDBACK|ReviewHistory|FailureAnalysis|Report|KnowledgeEvidence" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-34-knowledge-feedback-contract.md && git diff --check` | pending | contract-only |
| Add knowledge feedback contract golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_knowledge_feedback_contract_golden.py -q && git diff --check` | pending | no feedback runtime |
| Slice 34 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_knowledge_feedback_contract_golden.py backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add Knowledge Feedback Contract Task Plan

Goal: Create a narrow plan for KnowledgeFeedbackAgent contracts before contract
edits or runtime implementation.

Expected files:

- `docs/implementation/slices/slice-34-knowledge-feedback-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-34-knowledge-feedback-contract.md
rg -n "Knowledge Feedback Contract|KnowledgeFeedbackAgent|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-34-knowledge-feedback-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 34 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names KnowledgeFeedbackAgent, accepted/rejected cases,
  ReviewHistory, FailureAnalysis, Report, KnowledgeEvidence, draft feedback,
  human review, prompt eligibility, unsupported claims, and fallback.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add knowledge feedback contract plan
```

## Task 2: Define KnowledgeFeedbackAgent Draft Feedback Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with draft-only knowledge feedback rules.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-34-knowledge-feedback-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "KnowledgeFeedbackAgent|knowledge_feedback|draft feedback|prompt-eligible|UNABLE_TO_CREATE_KNOWLEDGE_FEEDBACK|ReviewHistory|FailureAnalysis|Report|KnowledgeEvidence" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-34-knowledge-feedback-contract.md
git diff --check
```

Acceptance:

- Contracts define input evidence sources and safe source eligibility.
- Contracts define draft feedback output fields and trace requirements.
- Contracts define human review and prompt-eligibility gates.
- Contracts forbid TestKnowledgeCard auto-creation, prompt-eligible
  auto-marking, historical evidence mutation, provider calls, MCP runtime,
  vector/graph runtime, and review bypass.

Commit message:

```text
docs(v2): define knowledge feedback contracts
```

## Task 3: Add Knowledge Feedback Contract Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving knowledge feedback
remains draft-only and review-gated.

Expected files:

- `backend/app/tests/golden/test_knowledge_feedback_contract_golden.py`
- `docs/fixtures/22-knowledge-feedback-contract-golden.md`
- `docs/implementation/slices/slice-34-knowledge-feedback-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_knowledge_feedback_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names KnowledgeFeedbackAgent, knowledge_feedback prompt,
  knowledge-feedback-skill, input evidence sources, draft feedback fields,
  unsupported claims, human review, prompt eligibility, and failure behavior.
- Golden proves no TestKnowledgeCard auto-creation, prompt-eligible
  auto-marking, historical evidence mutation, provider call, vector index,
  graph job, MCP runtime, artifact mutation, review bypass, or auto-promotion
  is created by the contract.

Commit message:

```text
test(golden): add knowledge feedback contract smoke
```

## Slice 34 Completion Gate

Goal: Validate Slice 34 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-34-knowledge-feedback-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_knowledge_feedback_contract_golden.py backend/app/tests/golden/test_mcp_ready_tool_knowledge_safety_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 34 task table records completed task commits.
- Focused golden verification passes.
- `NEXT_AI_TASK.md` points to the next narrow V2 task.

Commit message:

```text
docs(v2): complete knowledge feedback contract slice
```
