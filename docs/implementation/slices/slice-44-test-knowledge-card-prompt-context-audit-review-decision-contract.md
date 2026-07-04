# Slice 44: TestKnowledgeCard Prompt Context Audit Review Decision Contract Task Plan

## Goal

Define the prompt context audit review decision contract for future human review
of TestKnowledgeCard prompt context audit summaries before any frontend page,
report generation behavior change, prompt assembly implementation, prompt
runtime execution, provider call, deterministic retrieval behavior change,
vector index, backend feature API, broad TestKnowledgeCard CRUD, or automatic
prompt eligibility exists.

This slice is contract-first. It documents how a future reviewer may accept,
question, or reject a prompt context audit summary while preserving audit
summary artifact ids, prompt context consumption artifact ids, output
citations, skipped evidence, unsupported claims, source hashes,
PromptVersion, SkillVersion, ReviewHistory, review decision evidence,
follow-up flags, and failure behavior boundaries.

## Product Value Answer

After this slice, Chtest can describe how a human review gate evaluates future
knowledge-usage audit summaries without changing knowledge evidence or report
behavior. Users get an auditable review decision contract: reviewer action,
reason, cited/skipped evidence, unsupported claims, and ReviewHistory remain
visible before any UI, report generator, provider, or prompt runtime uses the
decision.

## Current Evidence Baseline

- Slice 19 defined deterministic local ContextArtifact retrieval evidence and
  `knowledge_retrieval.json` without adding vector search, embeddings,
  reranking, graph runtime, MCP runtime, or external providers.
- Existing PromptVersion and SkillVersion contracts require prompt input
  artifacts and context manifests for traceability.
- Slice 30 defined `TestKnowledgeCard` and `KnowledgeEvidence` contract shapes,
  including `safe_to_show` and `allowed_for_prompt`.
- Slice 39 defined human-reviewed prompt eligibility for TestKnowledgeCard
  records.
- Slice 40 defined a read-only TestKnowledgeCard Retrieval Boundary with
  `select_prompt_eligible_cards`, selected/excluded card evidence, and
  `excluded_card_reason`.
- Slice 41 defined bounded TestKnowledgeCard Prompt Context Evidence with
  `build_prompt_context_evidence`, safe bounded snippet/source hash entries,
  source manifests, retrieval boundary artifacts, PromptVersion/SkillVersion
  trace, context manifest links, omission reasons, and failure behavior.
- Slice 42 defined TestKnowledgeCard Prompt Context Consumption with
  `consume_prompt_context_evidence`, `prompt_context_consumption`,
  `used_knowledge` semantics, output citations, skipped evidence, source hash
  references, PromptVersion/SkillVersion trace, ReviewHistory links, and
  failure behavior.
- Slice 43 defined TestKnowledgeCard Prompt Context Audit Summary with
  `summarize_prompt_context_consumption`, `prompt_context_audit_summary`,
  usage status, cited/skipped entries, unsupported claim summaries, source
  hashes, context manifest links, PromptVersion/SkillVersion trace,
  ReviewHistory, review flags, and failure behavior.
- Current contracts do not define a human review decision boundary for prompt
  context audit summaries.

## Non-goals

- No frontend page, report generation behavior change, report renderer, export
  behavior, dashboard, backend feature API, endpoint, router, service, worker,
  queue, scheduler, or background job.
- No prompt assembly implementation, prompt runtime execution, LLM/provider
  call, provider SDK, credentials, OAuth, remote URL fetch, prompt runner,
  AITask execution behavior change, model output behavior implementation,
  automatic citation generation, automatic `used_knowledge=true` marking,
  prompt input generation, or runtime prompt template rendering.
- No prompt runtime retrieval implementation, deterministic retrieval behavior
  change, deterministic retrieval ranking change, vector database, embeddings,
  reranking, background indexing, graph runtime, GraphRAG job, MCP runtime, or
  external KnowledgeAdapter provider call.
- No broad TestKnowledgeCard CRUD implementation, migration, card table change,
  automatic prompt eligibility, automatic card creation from model output,
  automatic card approval, automatic knowledge ingestion, or
  KnowledgeIngestionAgent runtime.
- No artifact upload, artifact mutation, artifact delete, source artifact
  mutation, audit summary mutation, prompt context consumption mutation, prompt
  context evidence mutation, retrieval boundary artifact mutation, prompt
  eligibility artifact mutation, historical evidence mutation, ReviewHistory
  mutation outside declared review decision evidence, FailureAnalysis mutation,
  Report mutation, TestRun/TestResult mutation, TestCase mutation,
  GeneratedCaseCandidate mutation, KnowledgeEvidence mutation, PromptVersion
  mutation, SkillVersion mutation, or existing TestKnowledgeCard content
  mutation.
- No automatic duplicate merge, card replacement, card archive/delete,
  generated-case auto-approval, TestCase auto-promotion, runner behavior
  change, remote CI provider behavior, RBAC, tenants, permissions, or package
  upgrades.

## Contract Boundary To Define

The follow-up contract task should define:

- Review decision input:
  - prompt request id or AITask id when available;
  - audit summary artifact id;
  - prompt context consumption artifact id;
  - prompt context evidence artifact id;
  - context manifest artifact id;
  - `used_knowledge` decision;
  - usage status;
  - output citation ids;
  - cited TestKnowledgeCard ids;
  - cited context entry ids;
  - cited source hashes or source quote/hash pointers;
  - skipped evidence ids and skip reasons;
  - unsupported claims;
  - review flags and failure reasons from the audit summary;
  - PromptVersion id/name/version and SkillVersion id/name/version;
  - prior ReviewHistory ids when present.
- Review decision fields:
  - review decision id or artifact id when a later slice defines one;
  - reviewer label or local reviewer id when available;
  - review action such as accepted, needs_clarification,
    rejected_for_missing_evidence, rejected_for_unsupported_claim,
    rejected_for_citation_mismatch, rejected_for_stale_evidence, or
    rejected_for_cross_project_evidence;
  - reviewer comment;
  - accepted citation ids;
  - questioned citation ids;
  - rejected citation ids;
  - follow-up flags and requested clarification fields;
  - ReviewHistory id for the decision evidence;
  - failure code when the review decision input is invalid.
- Safety requirements:
  - review decisions are evidence about the audit summary, not mutation of the
    audit summary or underlying knowledge evidence;
  - accepted does not create prompt eligibility, approve TestKnowledgeCard
    content, approve generated cases, or alter `used_knowledge`;
  - rejected or needs_clarification must preserve cited/skipped evidence,
    unsupported claims, and source hashes instead of deleting or rewriting
    them;
  - invalid, stale, mismatched, unsafe, revoked, cross-project, or unsupported
    input must fail without appending a successful review decision.
- Outputs:
  - prompt context audit review decision artifact id when a later scoped
    workflow persists one;
  - review action;
  - reviewer comment;
  - accepted/questioned/rejected citations;
  - follow-up flags;
  - ReviewHistory link;
  - source manifest ids and source hashes;
  - PromptVersion/SkillVersion trace;
  - context manifest references;
  - failure code and visible reason.
- Runtime boundary:
  - this slice defines review decision artifact and contract semantics only;
  - it does not render a frontend page, change report generation behavior,
    assemble prompts, call providers, run AITasks, change retrieval ranking,
    write runtime `prompt_input.json`, auto-mark `used_knowledge`, generate
    model citations, or mutate artifacts outside declared review decision
    evidence.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard prompt context audit review decision task plan | done | `test -f docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md && rg -n "TestKnowledgeCard Prompt Context Audit Review Decision|audit summary|review decision|accepted|needs_clarification|rejected_for_missing_evidence|rejected_for_unsupported_claim|rejected_for_citation_mismatch|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md NEXT_AI_TASK.md && git diff --check` | `3f1920f` | planning-only scope |
| Define TestKnowledgeCard prompt context audit review decision contracts | done | `rg -n "TestKnowledgeCard Prompt Context Audit Review Decision|prompt_context_audit_review_decision|review_prompt_context_audit_summary|accepted|needs_clarification|rejected_for_missing_evidence|rejected_for_unsupported_claim|rejected_for_citation_mismatch|ReviewHistory|follow-up flags|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md && git diff --check` | `2eac56d` | contract-only |
| Add TestKnowledgeCard prompt context audit review decision golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_decision_contract_golden.py -q && git diff --check` | pending | no frontend/report runtime |
| Slice 44 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_decision_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_summary_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Prompt Context Audit Review Decision Task Plan

Goal: Create a narrow plan for prompt context audit review decisions before
contract edits, frontend/report changes, or runtime implementation.

Expected files:

- `docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md
rg -n "TestKnowledgeCard Prompt Context Audit Review Decision|audit summary|review decision|accepted|needs_clarification|rejected_for_missing_evidence|rejected_for_unsupported_claim|rejected_for_citation_mismatch|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 44 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names review decision inputs, reviewer action outputs, `accepted`,
  `needs_clarification`, rejected states, ReviewHistory, follow-up flags,
  failure behavior, and non-goals.
- The plan excludes frontend page, report generation behavior, prompt assembly
  implementation, prompt runtime execution, provider calls, retrieval ranking
  changes, vector indexes, embeddings, reranking, graph jobs, MCP runtime,
  broad CRUD, automatic eligibility, and historical evidence mutation.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card prompt context audit review decision plan
```

## Task 2: Define TestKnowledgeCard Prompt Context Audit Review Decision Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the human review decision boundary for future prompt context audit
summaries.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard Prompt Context Audit Review Decision|prompt_context_audit_review_decision|review_prompt_context_audit_summary|accepted|needs_clarification|rejected_for_missing_evidence|rejected_for_unsupported_claim|rejected_for_citation_mismatch|ReviewHistory|follow-up flags|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md
git diff --check
```

Acceptance:

- Contracts define review decision input, audit summary artifact references,
  prompt context consumption artifact references, reviewer actions,
  accepted/questioned/rejected citation ids, follow-up flags, ReviewHistory,
  source hashes, context manifest links, PromptVersion/SkillVersion trace,
  failure behavior, and forbidden side effects.
- Contracts require review decisions to preserve the underlying audit summary,
  consumption evidence, and knowledge artifacts without inventing or mutating
  evidence.
- Contracts keep frontend page, report generation behavior, prompt assembly
  implementation, prompt runtime execution, provider calls, retrieval ranking
  changes, vector indexes, embeddings, reranking, graph jobs, MCP runtime,
  broad CRUD, automatic eligibility, and historical evidence mutation out of
  scope.

Commit message:

```text
docs(v2): define test knowledge card prompt context audit review decision contracts
```

## Task 3: Add TestKnowledgeCard Prompt Context Audit Review Decision Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving prompt context
audit review decisions cannot mutate audit summaries, create prompt eligibility,
rewrite `used_knowledge`, or imply frontend/report behavior.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_decision_contract_golden.py`
- `docs/fixtures/32-test-knowledge-card-prompt-context-audit-review-decision-golden.md`
- `docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_decision_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names audit summary artifact id, prompt context consumption artifact
  id, review action, accepted, needs_clarification,
  rejected_for_missing_evidence, rejected_for_unsupported_claim,
  rejected_for_citation_mismatch, ReviewHistory, follow-up flags, failure
  behavior, and forbidden side effects.
- Golden proves no frontend page, report generation behavior, prompt assembly
  implementation, prompt runtime execution, provider call, retrieval ranking
  change, vector index, embedding, reranking, graph job, MCP runtime, broad
  CRUD, automatic eligibility, historical evidence mutation, RBAC, tenants, or
  permissions is created by the contract.

Commit message:

```text
test(golden): add test knowledge card prompt context audit review decision smoke
```

## Slice 44 Completion Gate

Goal: Validate Slice 44 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-44-test-knowledge-card-prompt-context-audit-review-decision-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_review_decision_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_summary_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 44 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.

Commit message:

```text
docs(v2): complete test knowledge card prompt context audit review decision slice
```
