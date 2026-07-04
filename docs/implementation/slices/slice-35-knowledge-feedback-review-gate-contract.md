# Slice 35: Knowledge Feedback Review Gate Contract Task Plan

## Goal

Define the human review gate for KnowledgeFeedbackDraft outputs before any
feedback review runtime API, frontend page, or TestKnowledgeCard CRUD exists.

This slice is contract-first. It documents how a reviewer may accept, reject,
or request revision for draft knowledge feedback, and how prompt eligibility
must remain separate from model confidence and draft generation.

## Product Value Answer

After this slice, Chtest can safely route draft knowledge feedback toward a
future reviewed knowledge-card workflow without letting AI output silently enter
the knowledge base or prompt context. Users get an auditable human gate between
draft feedback and any reusable testing knowledge.

## Current Evidence Baseline

- Slice 34 defined KnowledgeFeedbackDraft as draft-only agent output.
- `prompts/knowledge_feedback/v1.md` and
  `skills/knowledge-feedback-skill/v1.md` forbid marking feedback as approved
  or prompt-eligible.
- `ReviewHistory` already records local append-only review attribution events.
- `TestKnowledgeCard.allowed_for_prompt` already represents prompt eligibility
  and must be server-side/human-review controlled.
- Existing Artifact contracts preserve source evidence and unsupported claims.

## Non-goals

- No feedback review runtime API, frontend review page, TestKnowledgeCard CRUD,
  KnowledgeFeedbackAgent runtime, orchestration, queue, background job, or
  scheduler.
- No automatic prompt eligibility, automatic TestKnowledgeCard creation,
  automatic knowledge ingestion, or automatic knowledge-card approval.
- No mutation of historical ReviewHistory, FailureAnalysis, Report, TestRun,
  TestResult, TestCase, GeneratedCaseCandidate, or Artifact rows.
- No vector database, embeddings, reranking, background indexing, graph
  runtime, GraphRAG job, MCP runtime, provider SDK, external provider calls,
  credentials, OAuth, remote URL fetch, or remote CI/CD provider behavior.
- No migration, package upgrade, runner behavior change, report generation
  behavior change, generated-case auto-approval, RBAC, tenants, or permissions.

## Contract Boundary To Define

The follow-up contract task should define:

- Review actions:
  - approve_feedback;
  - reject_feedback;
  - request_revision;
  - mark_prompt_eligible after explicit human approval;
  - create_knowledge_card_candidate as a future handoff, not CRUD here.
- Review input evidence:
  - KnowledgeFeedbackDraft fields;
  - source Artifact ids;
  - source entity ids;
  - unsupported claims;
  - schema validation output;
  - reviewer comment.
- Review outputs:
  - review decision;
  - ReviewHistory append-only event;
  - feedback review artifact;
  - prompt eligibility decision reason;
  - optional future TestKnowledgeCard handoff payload.
- Prompt eligibility boundary:
  - prompt eligibility is false by default;
  - model confidence never grants eligibility;
  - mark_prompt_eligible requires human approval, safe_to_show evidence, and
    reviewed source citations.
- Failure and fallback behavior:
  - invalid source evidence rejects or requests revision;
  - unsupported claims stay visible;
  - rejected feedback remains auditable and cannot be reused as positive
    knowledge.
- Trace rules:
  - review actor label;
  - action;
  - source feedback id;
  - evidence artifact ids;
  - prompt eligibility decision;
  - ReviewHistory id when created.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add knowledge feedback review gate task plan | done | `test -f docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md && rg -n "Knowledge Feedback Review Gate|KnowledgeFeedbackDraft|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md NEXT_AI_TASK.md && git diff --check` | `b3faec3` | planning-only scope |
| Define KnowledgeFeedbackDraft review gate contracts | done | `rg -n "KnowledgeFeedbackDraft|approve_feedback|reject_feedback|request_revision|mark_prompt_eligible|ReviewHistory|prompt eligibility|feedback review artifact" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md && git diff --check` | `a523a76` | contract-only |
| Add knowledge feedback review gate golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_knowledge_feedback_review_gate_contract_golden.py -q && git diff --check` | `65d51d0` | no review runtime |
| Slice 35 completion gate | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_knowledge_feedback_review_gate_contract_golden.py backend/app/tests/golden/test_knowledge_feedback_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add Knowledge Feedback Review Gate Task Plan

Goal: Create a narrow plan for the human review gate before contract edits or
runtime implementation.

Expected files:

- `docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md
rg -n "Knowledge Feedback Review Gate|KnowledgeFeedbackDraft|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 35 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names KnowledgeFeedbackDraft review actions, human review,
  ReviewHistory, artifact evidence, TestKnowledgeCard handoff, prompt
  eligibility, unsupported claims, and fallback.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add knowledge feedback review gate plan
```

## Task 2: Define KnowledgeFeedbackDraft Review Gate Contracts

Goal: Update data, API, state-machine, and artifact contracts with review gate
rules for KnowledgeFeedbackDraft.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "KnowledgeFeedbackDraft|approve_feedback|reject_feedback|request_revision|mark_prompt_eligible|ReviewHistory|prompt eligibility|feedback review artifact" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md
git diff --check
```

Acceptance:

- Contracts define review actions and allowed transitions.
- Contracts define ReviewHistory and artifact evidence outputs.
- Contracts define prompt eligibility requirements and human gate.
- Contracts forbid automatic TestKnowledgeCard creation, prompt eligibility,
  historical evidence mutation, provider calls, MCP runtime, vector/graph
  runtime, and review bypass.

Commit message:

```text
docs(v2): define knowledge feedback review gate contracts
```

## Task 3: Add Knowledge Feedback Review Gate Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving review-gated
feedback cannot bypass human approval or prompt eligibility rules.

Expected files:

- `backend/app/tests/golden/test_knowledge_feedback_review_gate_contract_golden.py`
- `docs/fixtures/23-knowledge-feedback-review-gate-golden.md`
- `docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_knowledge_feedback_review_gate_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names KnowledgeFeedbackDraft review actions, ReviewHistory, feedback
  review artifact, prompt eligibility, TestKnowledgeCard handoff, unsupported
  claims, human review, and forbidden side effects.
- Golden proves no runtime review API, TestKnowledgeCard CRUD, prompt-eligible
  auto-marking, historical evidence mutation, provider call, vector index,
  graph job, MCP runtime, artifact mutation, review bypass, or auto-promotion
  is created by the contract.

Commit message:

```text
test(golden): add knowledge feedback review gate smoke
```

## Slice 35 Completion Gate

Goal: Validate Slice 35 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-35-knowledge-feedback-review-gate-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_knowledge_feedback_review_gate_contract_golden.py backend/app/tests/golden/test_knowledge_feedback_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 35 task table records completed task commits.
- Focused golden verification passes.
- `NEXT_AI_TASK.md` points to the next narrow V2 task.

Commit message:

```text
docs(v2): complete knowledge feedback review gate slice
```
