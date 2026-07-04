# Slice 43: TestKnowledgeCard Prompt Context Audit Summary Contract Task Plan

## Goal

Define the prompt context audit summary contract for future review surfaces that
summarize TestKnowledgeCard prompt context consumption evidence before any
frontend page, report generation behavior change, prompt assembly
implementation, prompt runtime execution, provider call, deterministic
retrieval behavior change, vector index, backend feature API, broad
TestKnowledgeCard CRUD, or automatic prompt eligibility exists.

This slice is contract-first. It documents how future read-only audit summaries
may explain what TestKnowledgeCard knowledge was used, cited, skipped,
unsupported, or failed while preserving prompt context consumption artifact ids,
prompt context evidence artifact ids, `used_knowledge`, output citations,
source hashes, context manifest links, PromptVersion, SkillVersion,
ReviewHistory, unsupported claim summaries, and failure behavior boundaries.

## Product Value Answer

After this slice, Chtest can describe how a future review or report surface
would summarize knowledge usage without changing runtime behavior. Users get an
auditable summary contract: consumed citations, skipped evidence, unsupported
claims, source hashes, prompt/skill trace, and ReviewHistory links remain
visible before any UI or report generator renders them.

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
- Current contracts do not define a frontend review page, report generator
  output, or runtime rendering behavior for prompt context consumption audit.

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
  mutation, prompt context consumption mutation, prompt context evidence
  mutation, retrieval boundary artifact mutation, prompt eligibility artifact
  mutation, historical evidence mutation, ReviewHistory mutation,
  FailureAnalysis mutation, Report mutation, TestRun/TestResult mutation,
  TestCase mutation, GeneratedCaseCandidate mutation, KnowledgeEvidence
  mutation, PromptVersion mutation, SkillVersion mutation, or existing
  TestKnowledgeCard content mutation.
- No automatic duplicate merge, card replacement, card archive/delete,
  generated-case auto-approval, TestCase auto-promotion, runner behavior
  change, remote CI provider behavior, RBAC, tenants, permissions, or package
  upgrades.

## Contract Boundary To Define

The follow-up contract task should define:

- Audit summary input:
  - prompt request id or AITask id when available;
  - consuming agent step name and intended output artifact type;
  - prompt context consumption artifact id;
  - prompt context evidence artifact id;
  - context manifest artifact id;
  - `used_knowledge` decision;
  - output citation ids;
  - cited TestKnowledgeCard ids;
  - cited context entry ids;
  - cited source hashes or source quote/hash pointers;
  - skipped evidence ids and skip reasons;
  - unsupported claims;
  - PromptVersion id/name/version and SkillVersion id/name/version;
  - ReviewHistory ids;
  - failure code when applicable.
- Audit summary fields:
  - audit summary id or artifact id when a later slice defines one;
  - knowledge usage status such as knowledge_used, knowledge_not_used,
    knowledge_skipped, knowledge_failed, or knowledge_unsupported;
  - cited evidence summaries;
  - skipped evidence summaries;
  - unsupported claim summaries;
  - source hash/context entry references;
  - prompt/skill trace;
  - ReviewHistory links;
  - review flags and failure reasons.
- Safety requirements:
  - audit summaries are read-only views of prompt context consumption evidence;
  - summaries must not invent new citations, rewrite `used_knowledge`, or
    promote unsupported claims;
  - raw large source text must remain out of the summary unless a bounded safe
    snippet was already present in prompt context evidence;
  - stale, unsafe, revoked, cross-project, redaction-failed, unbounded,
    citation-mismatched, context-mismatched, or evidence-mismatched input must
    produce failure flags or skipped summary rows.
- Outputs:
  - prompt context audit summary artifact id when a later scoped workflow
    persists one;
  - usage status;
  - cited entries;
  - skipped entries;
  - unsupported claim summary;
  - failure reasons;
  - source manifest ids and source hashes;
  - PromptVersion/SkillVersion trace;
  - context manifest references;
  - ReviewHistory links.
- Runtime boundary:
  - this slice defines audit summary artifact and contract semantics only;
  - it does not render a frontend page, change report generation behavior,
    assemble prompts, call providers, run AITasks, change retrieval ranking,
    write runtime `prompt_input.json`, auto-mark `used_knowledge`, generate
    model citations, or mutate artifacts.

## Task Table

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| Add TestKnowledgeCard prompt context audit summary task plan | done | `test -f docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md && rg -n "TestKnowledgeCard Prompt Context Audit Summary|prompt context consumption|used_knowledge|output citations|skipped evidence|PromptVersion|SkillVersion|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md NEXT_AI_TASK.md && git diff --check` | `24f05c3` | planning-only scope |
| Define TestKnowledgeCard prompt context audit summary contracts | done | `rg -n "TestKnowledgeCard Prompt Context Audit Summary|prompt_context_audit_summary|summarize_prompt_context_consumption|used_knowledge|output citations|skipped evidence|unsupported claims|PromptVersion|SkillVersion|ReviewHistory|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md && git diff --check` | pending | contract-only |
| Add TestKnowledgeCard prompt context audit summary golden smoke | done | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_summary_contract_golden.py -q && git diff --check` | pending | no frontend/report runtime |
| Slice 43 completion gate | planned | `backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_summary_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_consumption_contract_golden.py -q && git diff --check` | pending | docs and handoff |

## Task 1: Add TestKnowledgeCard Prompt Context Audit Summary Task Plan

Goal: Create a narrow plan for prompt context audit summary before contract
edits, frontend/report changes, or runtime implementation.

Expected files:

- `docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
test -f docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md
rg -n "TestKnowledgeCard Prompt Context Audit Summary|prompt context consumption|used_knowledge|output citations|skipped evidence|PromptVersion|SkillVersion|ReviewHistory|Product Value Answer|Non-goals|Task Table" docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md NEXT_AI_TASK.md
git diff --check
```

Acceptance:

- Slice 43 plan exists with product value, non-goals, task table, expected
  files, verification commands, and commit messages.
- The plan names audit summary inputs, cited/skipped evidence summaries,
  unsupported claim handling, `used_knowledge`, PromptVersion/SkillVersion,
  source hash/context manifest links, ReviewHistory, failure behavior, and
  non-goals.
- The plan excludes frontend page, report generation behavior, prompt assembly
  implementation, prompt runtime execution, provider calls, retrieval ranking
  changes, vector indexes, embeddings, reranking, graph jobs, MCP runtime,
  broad CRUD, automatic eligibility, and historical evidence mutation.
- `NEXT_AI_TASK.md` points to Task 2.

Commit message:

```text
docs(v2): add test knowledge card prompt context audit summary plan
```

## Task 2: Define TestKnowledgeCard Prompt Context Audit Summary Contracts

Goal: Update data, API, state-machine, artifact, and prompt/skill contracts
with the read-only audit summary boundary for future review or report surfaces
that summarize TestKnowledgeCard prompt context consumption evidence.

Expected files:

- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
rg -n "TestKnowledgeCard Prompt Context Audit Summary|prompt_context_audit_summary|summarize_prompt_context_consumption|used_knowledge|output citations|skipped evidence|unsupported claims|PromptVersion|SkillVersion|ReviewHistory|source hash|context manifest" docs/contracts/01-data-model-contract.md docs/contracts/02-api-contract.md docs/contracts/03-state-machines.md docs/contracts/04-artifact-contract.md docs/contracts/05-prompt-skill-contract.md docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md
git diff --check
```

Acceptance:

- Contracts define audit summary inputs, prompt context consumption artifact
  references, context manifest links, cited TestKnowledgeCard ids, source
  hashes, output citations, skipped evidence, unsupported claims,
  PromptVersion/SkillVersion trace, ReviewHistory ids, usage status, failure
  behavior, and forbidden side effects.
- Contracts require audit summaries to be read-only and to preserve
  `used_knowledge` and citation evidence without inventing or mutating
  evidence.
- Contracts keep frontend page, report generation behavior, prompt assembly
  implementation, prompt runtime execution, provider calls, retrieval ranking
  changes, vector indexes, embeddings, reranking, graph jobs, MCP runtime,
  broad CRUD, automatic eligibility, and historical evidence mutation out of
  scope.

Commit message:

```text
docs(v2): define test knowledge card prompt context audit summary contracts
```

## Task 3: Add TestKnowledgeCard Prompt Context Audit Summary Golden Smoke

Goal: Add a contract-level fixture and golden smoke proving prompt context
audit summaries cannot invent citations, rewrite `used_knowledge`, mutate
evidence, or imply frontend/report behavior.

Expected files:

- `backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_summary_contract_golden.py`
- `docs/fixtures/31-test-knowledge-card-prompt-context-audit-summary-golden.md`
- `docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_summary_contract_golden.py -q
git diff --check
```

Acceptance:

- Golden names prompt context consumption artifact id, prompt context evidence
  artifact id, `used_knowledge`, output citations, skipped evidence,
  unsupported claims, source hash, context manifest, PromptVersion,
  SkillVersion, ReviewHistory, failure behavior, and forbidden side effects.
- Golden proves no frontend page, report generation behavior, prompt assembly
  implementation, prompt runtime execution, provider call, retrieval ranking
  change, vector index, embedding, reranking, graph job, MCP runtime, broad
  CRUD, automatic eligibility, historical evidence mutation, RBAC, tenants, or
  permissions is created by the contract.

Commit message:

```text
test(golden): add test knowledge card prompt context audit summary smoke
```

## Slice 43 Completion Gate

Goal: Validate Slice 43 and hand off the next narrow V2 task.

Expected files:

- `docs/implementation/slices/slice-43-test-knowledge-card-prompt-context-audit-summary-contract.md`
- `docs/implementation/10-v2-scope-options.md`
- `NEXT_AI_TASK.md`
- `memory/07-dev-log.md`
- `memory/08-session-handoff.md`

Verification Command:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_test_knowledge_card_prompt_context_audit_summary_contract_golden.py backend/app/tests/golden/test_test_knowledge_card_prompt_context_consumption_contract_golden.py -q
git diff --check
```

Acceptance:

- Slice 43 task table records Task 1-3 commits.
- Focused golden verification passes.
- V2 scope options and handoff memory recommend the next narrow slice.

Commit message:

```text
docs(v2): complete test knowledge card prompt context audit summary slice
```
