# Chtest State Machines

## 1. 文档目的

本文定义 Chtest V1 核心状态机。任何后端 service、worker、前端操作按钮和测试 fixture 都必须遵循本文的允许迁移。

## 2. AITask 状态机

```text
created -> pending -> running -> succeeded
created -> pending -> running -> waiting_review -> succeeded
created -> pending -> running -> waiting_approval -> running -> succeeded
created -> pending -> running -> failed
pending/running/waiting_review/waiting_approval -> cancelled
```

| 当前状态 | 动作 | 目标状态 | 触发者 |
|---|---|---|---|
| created | enqueue | pending | API |
| pending | worker_start | running | Worker |
| running | llm_success_no_review | succeeded | Worker |
| running | llm_success_needs_review | waiting_review | Worker |
| running | tool_needs_approval | waiting_approval | Worker |
| waiting_approval | approve | running | User/API |
| waiting_approval | reject | failed | User/API |
| running | llm_or_schema_error | failed | Worker |
| pending/running/waiting_review/waiting_approval | cancel | cancelled | User/API |

规则：schema 校验失败不能写业务主表，必须保存 raw output artifact。

Deterministic retrieval 规则：

- `use_knowledge=true` may run deterministic local retrieval before or during
  `pending -> running`.
- Retrieval success does not add a new AITask status; it is recorded as
  `knowledge_retrieval` artifact evidence and AITask output metadata.
- Retrieval failure may continue with `used_knowledge=false` only when the
  workflow explicitly allows fallback and records the retrieval error evidence.
- `used_knowledge=true` is invalid without retrieved snippets and exact
  `used_context_artifact_ids`.
- Deterministic retrieval must not enqueue background indexing, embedding,
  reranking, external provider, MCP runtime, RBAC, tenant, or permission
  behavior.

## 3. GeneratedCaseCandidate 状态机

```text
generated -> under_review -> approved -> TestCase created
generated -> under_review -> approved_after_edit -> TestCase created
generated -> under_review -> rejected
generated -> under_review -> needs_optimization -> optimization_pending_review -> under_review
any non-final -> archived
```

| 当前状态 | 动作 | 目标状态 | 结果 |
|---|---|---|---|
| generated | open_review | under_review | 进入评审窗口 |
| under_review | approve | approved | 创建 TestCase |
| under_review | approve_after_edit | approved_after_edit | 保存编辑差异，创建 TestCase |
| under_review | reject | rejected | 记录原因，不入库 |
| under_review | request_optimization | needs_optimization | 触发 CaseReviewAgent |
| needs_optimization | optimization_generated | optimization_pending_review | 生成优化版本 |
| optimization_pending_review | reopen_review | under_review | 用户再次评审 |
| generated/under_review/needs_optimization/optimization_pending_review | archive | archived | 归档 |

规则：approved/approved_after_edit/rejected 是最终评审状态，不允许再次修改为 generated。

ReviewHistory side effect:

- `approve`, `approve_after_edit`, and `reject` append a ReviewHistory record
  after the state transition succeeds.
- The primary history entity is the GeneratedCaseCandidate. The created
  TestCase may display this source history through `source_candidate_id`
  without duplicating the same approval event.
- Invalid transitions must not append successful review history.

TestKnowledgeCard / KnowledgeEvidence rules:

- KnowledgeEvidence can support `generated -> under_review` review decisions,
  but it does not add new GeneratedCaseCandidate states.
- `source_knowledge_evidence_ids`, `quality_score`, `review_findings_json`, and
  `coverage_gap_notes` are review evidence only. They must not auto-approve a
  candidate or create a TestCase.
- Missing or weak KnowledgeEvidence may lead a reviewer or CaseReviewAgent to
  choose `needs_optimization` or `rejected`, but that decision still follows the
  existing review transition.
- Updating KnowledgeEvidence display fields must not trigger retrieval jobs,
  vector indexing, embeddings, reranking, graph extraction, external provider
  calls, MCP runtime calls, artifact mutation, runner execution, report
  generation, RBAC, tenant, permission, or remote CI provider behavior.

## 7.3 KnowledgeFeedbackDraft State Contract

KnowledgeFeedbackAgent output is draft feedback evidence. It is not a
TestKnowledgeCard state and does not change TestKnowledgeCard prompt
eligibility by itself.

```text
draft -> needs_review -> approved_by_human
draft -> needs_review -> rejected
draft -> rejected
needs_review -> draft
approved_by_human -> prompt_eligible
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| draft | submit_for_review | needs_review | AITask worker or API | Draft feedback is visible for human review |
| draft | reject_invalid_source | rejected | AITask worker or reviewer | Source evidence is insufficient or unsafe |
| needs_review | approve_feedback | approved_by_human | User/API | May later feed a separate TestKnowledgeCard workflow |
| needs_review | reject_feedback | rejected | User/API | Feedback is retained as rejected evidence |
| needs_review | request_revision | draft | User/API | Feedback needs more source evidence |
| approved_by_human | mark_prompt_eligible | prompt_eligible | User/API | Requires explicit human prompt-eligibility decision |

Knowledge feedback state rules:

- KnowledgeFeedbackAgent may create only draft feedback artifacts or payloads.
  It must not create, approve, archive, delete, or mutate TestKnowledgeCard
  rows.
- `approved_by_human` in this draft contract is not the same as
  `TestKnowledgeCard.active` and must not mark a card `allowed_for_prompt=true`
  without a later explicit knowledge-card review workflow.
- `prompt_eligible` means a human reviewer explicitly marked the feedback as
  eligible for future prompt use. It still does not create a TestKnowledgeCard
  row in this contract.
- Every state transition must preserve source evidence ids, prompt_version,
  skill_version, schema validation status, and unsupported claims.
- `UNABLE_TO_CREATE_KNOWLEDGE_FEEDBACK` leaves the feedback output empty and
  records unsupported claims; it must not create fallback knowledge.
- Knowledge feedback must not mutate ReviewHistory, FailureAnalysis, Report,
  TestRun, TestResult, TestCase, GeneratedCaseCandidate, Artifact, or
  TestKnowledgeCard rows; approve generated cases; promote TestCase rows;
  generate reports; start retrieval; index vectors; create embeddings; rerank;
  run graph jobs; call external providers; invoke MCP runtime; call remote CI
  providers; add RBAC; create tenants; or change permissions.
- Slice 31 persistence of KnowledgeEvidence display fields happens when a
  GeneratedCaseCandidate is created from validated AI output. It does not add a
  new review state, does not count as `open_review`, and does not append
  ReviewHistory by itself.

Knowledge feedback review gate rules:

- `approve_feedback`, `reject_feedback`, `request_revision`, and
  `mark_prompt_eligible` are human review actions. Model confidence, schema
  validity, quality score, or missing unsupported claims must not execute them
  automatically.
- `mark_prompt_eligible` is allowed only after `approved_by_human`, with
  safe-to-show evidence, reviewed source citations, and a reviewer reason.
- `request_revision` preserves the previous draft, source evidence, and
  unsupported claims as audit evidence; it must not mutate historical source
  entities.
- `reject_feedback` is terminal for that draft unless a separate new draft is
  created; rejected feedback must not be reused as positive knowledge.
- Successful review gate actions append or reference ReviewHistory and may
  write a feedback review artifact. Invalid transitions and validation failures
  must not append successful ReviewHistory.
- Future TestKnowledgeCard handoff is a payload boundary only in this slice;
  it must not create, approve, archive, delete, or mutate TestKnowledgeCard
  rows.
- The review gate must not add a runtime review API, frontend review page,
  TestKnowledgeCard CRUD, automatic prompt eligibility, provider calls, MCP
  runtime, vector/graph runtime, artifact mutation, historical evidence
  mutation, generated-case auto-approval, runner behavior changes, report
  generation behavior changes, RBAC, tenants, permissions, or remote CI
  provider behavior.

## 7.4 TestKnowledgeCard Handoff Candidate State Contract

The TestKnowledgeCard handoff candidate state is a payload boundary layered on
top of `approved_by_human` KnowledgeFeedbackDraft review. It is not a
TestKnowledgeCard lifecycle and must not create TestKnowledgeCard rows.

```text
approved_by_human -> handoff_payload_prepared -> card_review_required
approved_by_human -> handoff_rejected
card_review_required -> duplicate_review_required
card_review_required -> merge_requested
card_review_required -> ready_for_future_card_creation
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| approved_by_human | create_knowledge_card_candidate | handoff_payload_prepared | Human reviewer/API | Prepares payload only |
| approved_by_human | reject_handoff_source | handoff_rejected | Human reviewer/API | Source evidence is unsafe, missing, cross-project, or unbounded |
| handoff_payload_prepared | require_card_review | card_review_required | System/API | Future card creation needs explicit review |
| card_review_required | flag_duplicate | duplicate_review_required | Human reviewer/API | Duplicate candidates need review |
| card_review_required | request_merge_review | merge_requested | Human reviewer/API | Merge hint needs explicit review |
| card_review_required | mark_ready_for_future_card_creation | ready_for_future_card_creation | Human reviewer/API | Still not CRUD in this contract |

TestKnowledgeCard handoff state rules:

- `create_knowledge_card_candidate` requires an approved KnowledgeFeedbackDraft,
  same-project source artifacts, ReviewHistory, a feedback review artifact,
  source quote/hash, visible unsupported claims, and safe-to-show evidence.
- `handoff_payload_prepared`, `card_review_required`,
  `duplicate_review_required`, `merge_requested`, and
  `ready_for_future_card_creation` are payload states only. They must not be
  persisted as TestKnowledgeCard status values in this slice.
- Every candidate keeps `allowed_for_prompt=false`. Prompt eligibility requires
  a later human card review after a TestKnowledgeCard row exists.
- Duplicate/merge states preserve reviewer work. They must not automatically
  merge, archive, delete, replace, or relabel existing TestKnowledgeCard rows.
- `handoff_rejected` remains auditable and must preserve rejection reason,
  source evidence ids, unsupported claims, ReviewHistory id when present, and
  failure code. It must not append successful ReviewHistory for invalid
  transitions.
- Model confidence, schema validity, quality score, and absence of unsupported
  claims must not move a candidate to any handoff state without a human
  reviewer action.
- The handoff state contract must not add a runtime review API, frontend page,
  TestKnowledgeCard CRUD, automatic card creation, automatic prompt
  eligibility, provider calls, MCP runtime, vector/graph runtime, artifact
  mutation outside declared handoff outputs, historical evidence mutation,
  generated-case auto-approval, runner behavior changes, report generation
  behavior changes, RBAC, tenants, permissions, or remote CI provider behavior.

## 7.5 TestKnowledgeCard Candidate Review State Contract

The TestKnowledgeCard Candidate Review state contract is a human review layer
for handoff candidates. It is not a TestKnowledgeCard lifecycle and must not
create, merge, archive, delete, relabel, or make prompt-eligible
TestKnowledgeCard rows.

```text
card_review_required -> candidate_approved_for_future_creation
card_review_required -> candidate_rejected
card_review_required -> candidate_revision_requested
card_review_required -> duplicate_review_required
duplicate_review_required -> merge_review_requested
candidate_approved_for_future_creation -> prompt_eligibility_deferred
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| card_review_required | approve_candidate_for_creation | candidate_approved_for_future_creation | Human reviewer/API | Future card creation only |
| card_review_required | reject_candidate | candidate_rejected | Human reviewer/API | Candidate remains auditable |
| card_review_required | request_candidate_revision | candidate_revision_requested | Human reviewer/API | Better evidence or mapping required |
| card_review_required | flag_duplicate | duplicate_review_required | Human reviewer/API | Duplicate routing only |
| duplicate_review_required | request_merge_review | merge_review_requested | Human reviewer/API | Merge review only |
| candidate_approved_for_future_creation | defer_prompt_eligibility | prompt_eligibility_deferred | Human reviewer/API | Keeps allowed_for_prompt=false |

TestKnowledgeCard Candidate Review state rules:

- Candidate review requires a TestKnowledgeCard handoff candidate, candidate
  card JSON, same-project source artifacts, ReviewHistory or prior review
  artifact references, source quote/hash, duplicate/merge hints, and visible
  unsupported claims.
- Candidate review actions are human reviewer actions. Model confidence,
  schema validity, safe_to_show, duplicate similarity, or absence of
  unsupported claims must not execute them automatically.
- `candidate_approved_for_future_creation` is not `TestKnowledgeCard.active`.
  It must not create a row, produce a TestKnowledgeCard id, or mark a card
  prompt-eligible.
- `prompt_eligibility_deferred` is the default after candidate review.
  Candidates keep `allowed_for_prompt=false` until a later explicitly scoped
  card workflow grants eligibility.
- `duplicate_review_required` and `merge_review_requested` must not
  automatically merge, archive, replace, delete, relabel, or create
  TestKnowledgeCard rows.
- Successful candidate review actions append or reference ReviewHistory and may
  write a candidate review artifact. Invalid transitions, unsafe evidence, or
  validation failures must not append successful ReviewHistory.
- Rejected and revision-requested candidates remain auditable and must preserve
  source evidence ids, unsupported claims, reviewer reason, and failure code.
- The candidate review state contract must not add a runtime review API,
  frontend page, TestKnowledgeCard CRUD, automatic card creation, automatic
  prompt eligibility, provider calls, MCP runtime, vector/graph runtime,
  artifact mutation outside declared candidate review outputs, historical
  evidence mutation, generated-case auto-approval, runner behavior changes,
  report generation behavior changes, RBAC, tenants, permissions, or remote CI
  provider behavior.

## 7.6 Reviewed TestKnowledgeCard Creation State Contract

Reviewed TestKnowledgeCard Creation is a future scoped creation boundary from
an approved candidate review into a TestKnowledgeCard record. It is not broad
TestKnowledgeCard CRUD and must not grant prompt eligibility by itself.

```text
candidate_approved_for_future_creation -> creation_preflight_required
creation_preflight_required -> creation_blocked
creation_preflight_required -> ready_for_reviewed_creation
ready_for_reviewed_creation -> reviewed_card_creation_deferred
ready_for_reviewed_creation -> reviewed_card_created
reviewed_card_created -> prompt_eligibility_deferred
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| candidate_approved_for_future_creation | require_creation_preflight | creation_preflight_required | System/API | Checks source evidence and duplicate/merge preconditions |
| creation_preflight_required | block_creation | creation_blocked | System/API | Unsafe, stale, unresolved duplicate, or unsupported evidence |
| creation_preflight_required | mark_ready_for_reviewed_creation | ready_for_reviewed_creation | Human reviewer/API | Creation remains future scoped |
| ready_for_reviewed_creation | defer_creation | reviewed_card_creation_deferred | Human reviewer/API | No row is created |
| ready_for_reviewed_creation | create_reviewed_test_knowledge_card | reviewed_card_created | Future scoped implementation | Creates only after explicit scope exists |
| reviewed_card_created | defer_prompt_eligibility | prompt_eligibility_deferred | Human reviewer/API | Keeps allowed_for_prompt=false |

Reviewed TestKnowledgeCard Creation state rules:

- Creation requires an approved candidate review, candidate review artifact,
  handoff artifact, candidate_card_json, same-project source artifacts, source
  manifest, ReviewHistory ids, duplicate/merge precondition result, and visible
  unsupported claims.
- `reviewed_card_created` is a future scoped implementation state only. This
  contract must not add an endpoint, migration, backend service, frontend page,
  or broad CRUD behavior by itself.
- Creation preflight must block stale, rejected, revision-requested,
  duplicate-conflicted, cross-project, unsafe, unbounded, or unsupported source
  evidence. Blocked creation must preserve a failure code and must not create
  fallback cards.
- Reviewed creation must default to `allowed_for_prompt=false`.
  `prompt_eligibility_deferred` remains separate from card creation and must
  not be inferred from safe_to_show, model confidence, or schema validity.
- Duplicate/merge preconditions must not automatically merge, archive, replace,
  delete, relabel, or create TestKnowledgeCard rows.
- Successful future creation may append or reference ReviewHistory and may
  write a creation artifact. Invalid transitions or failed preflight must not
  append successful ReviewHistory.
- The reviewed creation state contract must not add a runtime API, frontend
  page, broad TestKnowledgeCard CRUD, automatic card creation from model
  output, automatic prompt eligibility, provider calls, MCP runtime,
  vector/graph runtime, artifact mutation outside declared creation outputs,
  historical evidence mutation, generated-case auto-approval, runner behavior
  changes, report generation behavior changes, RBAC, tenants, permissions, or
  remote CI provider behavior.

## 7.7 TestKnowledgeCard Prompt Eligibility State Contract

TestKnowledgeCard Prompt Eligibility is a human review state boundary for
whether an existing reviewed card may enter future prompt context. It is not
retrieval runtime, card creation, or broad TestKnowledgeCard CRUD.

```text
reviewed_card_created -> prompt_eligibility_pending
prompt_eligibility_pending -> prompt_eligible
prompt_eligibility_pending -> prompt_eligibility_denied
prompt_eligibility_pending -> prompt_eligibility_revision_requested
prompt_eligible -> prompt_eligibility_revoked
prompt_eligibility_revoked -> prompt_eligibility_pending
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| reviewed_card_created | request_prompt_eligibility_review | prompt_eligibility_pending | Human reviewer/API | Starts eligibility review |
| prompt_eligibility_pending | mark_card_prompt_eligible | prompt_eligible | Human reviewer/API | Requires safe_to_show, redaction, source evidence, and reason |
| prompt_eligibility_pending | deny_card_prompt_eligibility | prompt_eligibility_denied | Human reviewer/API | Keeps allowed_for_prompt=false |
| prompt_eligibility_pending | request_prompt_eligibility_revision | prompt_eligibility_revision_requested | Human reviewer/API | Source/redaction fixes required |
| prompt_eligible | revoke_card_prompt_eligibility | prompt_eligibility_revoked | Human reviewer/API | Removes future prompt eligibility |
| prompt_eligibility_revoked | request_prompt_eligibility_review | prompt_eligibility_pending | Human reviewer/API | Requires fresh review |

TestKnowledgeCard Prompt Eligibility state rules:

- `mark_card_prompt_eligible` requires `safe_to_show=true`, reviewed redaction
  status, same-project source artifacts, source manifest, reviewed source
  citations, prompt eligibility reason, ReviewHistory, and prompt eligibility
  artifact evidence.
- `allowed_for_prompt=true` must not be inferred from reviewed creation,
  safe_to_show alone, model confidence, schema validity, absence of unsupported
  claims, retrieval score, vector match, or prompt runtime need.
- Denied, revision-requested, and revoked states keep or set
  `allowed_for_prompt=false` and must preserve reviewer reason, failure code,
  source evidence ids, and unsupported claims.
- Successful prompt eligibility actions append or reference ReviewHistory and
  may write prompt eligibility artifacts. Invalid transitions, unsafe evidence,
  missing redaction, or validation failures must not append successful
  ReviewHistory.
- Revocation must not delete TestKnowledgeCard rows, mutate source artifacts,
  rewrite creation artifacts, or rewrite historical ReviewHistory.
- The prompt eligibility state contract must not add retrieval runtime changes,
  vector indexes, embeddings, reranking, graph jobs, MCP runtime, provider
  calls, broad TestKnowledgeCard CRUD, automatic eligibility, artifact mutation
  outside declared prompt eligibility outputs, historical evidence mutation,
  generated-case auto-approval, runner behavior changes, report generation
  behavior changes, RBAC, tenants, permissions, or remote CI provider behavior.

## 7.8 TestKnowledgeCard Retrieval Boundary State Contract

TestKnowledgeCard Retrieval Boundary is a read-only selection state boundary
for future prompt-context consideration. It starts only from current
`prompt_eligible` evidence and does not implement retrieval runtime, prompt
assembly, card creation, or broad TestKnowledgeCard CRUD.

```text
prompt_eligible -> retrieval_boundary_candidate
retrieval_boundary_candidate -> retrieval_selected
retrieval_boundary_candidate -> retrieval_excluded
prompt_eligibility_denied -> retrieval_excluded
prompt_eligibility_revision_requested -> retrieval_excluded
prompt_eligibility_revoked -> retrieval_excluded
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| prompt_eligible | request_retrieval_boundary_selection | retrieval_boundary_candidate | Future workflow/API | Starts read-only selection evaluation |
| retrieval_boundary_candidate | select_prompt_eligible_cards | retrieval_selected | Future workflow/API | Requires allowed_for_prompt, safe_to_show, source evidence, and ReviewHistory |
| retrieval_boundary_candidate | exclude_prompt_context_card | retrieval_excluded | Future workflow/API | Records excluded_card_reason |
| prompt_eligibility_denied | select_prompt_eligible_cards | retrieval_excluded | Future workflow/API | Must not select denied cards |
| prompt_eligibility_revision_requested | select_prompt_eligible_cards | retrieval_excluded | Future workflow/API | Must not select revision-requested cards |
| prompt_eligibility_revoked | select_prompt_eligible_cards | retrieval_excluded | Future workflow/API | Must not select revoked cards |

TestKnowledgeCard Retrieval Boundary state rules:

- `select_prompt_eligible_cards` requires `allowed_for_prompt=true`,
  `prompt_eligible`, `safe_to_show=true`, reviewed redaction status,
  same-project source artifacts, source manifest, reviewed source citations,
  ReviewHistory, and prompt eligibility artifact evidence.
- `allowed_for_prompt=true` is necessary but not sufficient. It must not bypass
  stale evidence, cross-project evidence, unsafe evidence, unsupported claims,
  missing source evidence, unbounded evidence, redaction failure, source
  manifest mismatch, missing ReviewHistory, or missing prompt eligibility
  artifact evidence.
- Retrieval-excluded states record `excluded_card_reason`, failure code,
  source evidence ids, and unsupported claims when applicable.
- Retrieval boundary selection may write retrieval evidence artifacts in a
  later scoped workflow. It must not mutate TestKnowledgeCard rows, source
  artifacts, prompt eligibility artifacts, ReviewHistory, KnowledgeEvidence, or
  historical evidence.
- The retrieval boundary state contract must not add prompt runtime retrieval,
  deterministic retrieval ranking changes, vector indexes, embeddings,
  reranking, graph jobs, MCP runtime, provider calls, broad TestKnowledgeCard
  CRUD, automatic eligibility, artifact mutation outside declared retrieval
  evidence, historical evidence mutation, generated-case auto-approval, runner
  behavior changes, report generation behavior changes, RBAC, tenants,
  permissions, or remote CI provider behavior.

## 7.9 TestKnowledgeCard Prompt Context Evidence State Contract

TestKnowledgeCard Prompt Context Evidence is an evidence-building boundary for
future prompt context. It starts only from retrieval boundary selection
evidence and does not implement prompt assembly, prompt runtime execution,
provider calls, retrieval ranking, card creation, or broad TestKnowledgeCard
CRUD.

```text
retrieval_selected -> prompt_context_evidence_pending
prompt_context_evidence_pending -> prompt_context_evidence_ready
prompt_context_evidence_pending -> prompt_context_evidence_omitted
prompt_context_evidence_pending -> prompt_context_evidence_failed
retrieval_excluded -> prompt_context_evidence_omitted
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| retrieval_selected | request_prompt_context_evidence | prompt_context_evidence_pending | Future workflow/API | Starts evidence shaping only |
| prompt_context_evidence_pending | build_prompt_context_evidence | prompt_context_evidence_ready | Future workflow/API | Requires bounded snippet or source hash |
| prompt_context_evidence_pending | omit_prompt_context_card | prompt_context_evidence_omitted | Future workflow/API | Records omission reason |
| prompt_context_evidence_pending | fail_prompt_context_evidence | prompt_context_evidence_failed | Future workflow/API | Records failure code |
| retrieval_excluded | build_prompt_context_evidence | prompt_context_evidence_omitted | Future workflow/API | Excluded cards cannot enter context |

TestKnowledgeCard Prompt Context Evidence state rules:

- `build_prompt_context_evidence` requires retrieval boundary artifact
  evidence, selected TestKnowledgeCard ids, PromptVersion, SkillVersion,
  source manifest, same-project source artifacts, prompt eligibility artifact
  evidence, ReviewHistory, `safe_to_show=true`, and reviewed redaction.
- Prompt context entries must use a bounded snippet or source hash. Raw large
  source text, unsafe provider payloads, vector store payloads, embedding
  vectors, reranker traces, graph runtime payloads, and executable prompt
  assembly payloads are not valid prompt context evidence.
- `safe_to_show=false`, missing redaction, missing source evidence, missing
  retrieval boundary artifact, missing prompt eligibility artifact, stale,
  revoked, cross-project, unsupported, unbounded, or evidence-mismatched input
  must produce `prompt_context_evidence_omitted` or
  `prompt_context_evidence_failed` with omission reason or failure code.
- Prompt context evidence may write prompt context evidence artifacts in a
  later scoped workflow. It must not mutate TestKnowledgeCard rows, source
  artifacts, retrieval boundary artifacts, prompt eligibility artifacts,
  ReviewHistory, KnowledgeEvidence, or historical evidence.
- The prompt context evidence state contract must not add prompt assembly
  implementation, prompt runtime execution, provider calls, retrieval ranking
  changes, vector indexes, embeddings, reranking, graph jobs, MCP runtime,
  broad TestKnowledgeCard CRUD, automatic eligibility, artifact mutation
  outside declared prompt context evidence, historical evidence mutation,
  generated-case auto-approval, runner behavior changes, report generation
  behavior changes, RBAC, tenants, permissions, or remote CI provider behavior.

## 7.10 TestKnowledgeCard Prompt Context Consumption State Contract

TestKnowledgeCard Prompt Context Consumption is a citation state boundary for
future AI outputs that reference prompt context evidence. It starts only from
prompt context evidence and does not implement prompt assembly, prompt runtime
execution, provider calls, retrieval ranking, model citation generation, card
creation, or broad TestKnowledgeCard CRUD.

```text
prompt_context_evidence_ready -> prompt_context_consumption_pending
prompt_context_consumption_pending -> prompt_context_consumed
prompt_context_consumption_pending -> prompt_context_consumption_skipped
prompt_context_consumption_pending -> prompt_context_consumption_failed
prompt_context_evidence_omitted -> prompt_context_consumption_skipped
prompt_context_evidence_failed -> prompt_context_consumption_failed
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| prompt_context_evidence_ready | request_prompt_context_consumption | prompt_context_consumption_pending | Future workflow/API | Starts citation evaluation only |
| prompt_context_consumption_pending | consume_prompt_context_evidence | prompt_context_consumed | Future workflow/API | Requires valid consumed citation |
| prompt_context_consumption_pending | skip_prompt_context_evidence | prompt_context_consumption_skipped | Future workflow/API | Records skip reason |
| prompt_context_consumption_pending | fail_prompt_context_consumption | prompt_context_consumption_failed | Future workflow/API | Records failure code |
| prompt_context_evidence_omitted | consume_prompt_context_evidence | prompt_context_consumption_skipped | Future workflow/API | Omitted evidence cannot be cited |
| prompt_context_evidence_failed | consume_prompt_context_evidence | prompt_context_consumption_failed | Future workflow/API | Failed evidence cannot be cited |

TestKnowledgeCard Prompt Context Consumption state rules:

- `consume_prompt_context_evidence` requires a prompt context evidence artifact,
  context manifest, consumed context entry ids, consumed TestKnowledgeCard ids,
  consumed source hashes or source quote/hash pointers, PromptVersion,
  SkillVersion, ReviewHistory, and intended output artifact type.
- `used_knowledge=true` is valid only in `prompt_context_consumed` when at
  least one output citation points to consumed prompt context evidence. Missing
  or invalid citations must keep `used_knowledge=false` or fail the
  consumption contract.
- Skipped evidence records skip reason, unsupported claims, stale evidence,
  unsafe evidence, revoked evidence, cross-project evidence, unbounded snippet,
  redaction failure, citation mismatch, context mismatch, prompt-version
  mismatch, skill-version mismatch, or evidence mismatch when applicable.
- Prompt context consumption may write prompt context consumption artifacts in
  a later scoped workflow. It must not mutate TestKnowledgeCard rows, source
  artifacts, prompt context evidence artifacts, retrieval boundary artifacts,
  prompt eligibility artifacts, ReviewHistory, KnowledgeEvidence, or historical
  evidence.
- The prompt context consumption state contract must not add prompt assembly
  implementation, prompt runtime execution, provider calls, retrieval ranking
  changes, vector indexes, embeddings, reranking, graph jobs, MCP runtime,
  broad TestKnowledgeCard CRUD, automatic eligibility, automatic
  `used_knowledge=true` marking, artifact mutation outside declared prompt
  context consumption, historical evidence mutation, generated-case
  auto-approval, runner behavior changes, report generation behavior changes,
  RBAC, tenants, permissions, or remote CI provider behavior.

## 7.11 TestKnowledgeCard Prompt Context Audit Summary State Contract

TestKnowledgeCard Prompt Context Audit Summary is a read-only summary state
boundary for future review/report surfaces that explain prompt context
consumption evidence. It starts only from prompt context consumption evidence
and does not implement frontend rendering, report generation behavior, prompt
assembly, prompt runtime execution, provider calls, retrieval ranking, model
citation generation, card creation, or broad TestKnowledgeCard CRUD.

```text
prompt_context_consumed -> prompt_context_audit_summary_pending
prompt_context_consumption_skipped -> prompt_context_audit_summary_pending
prompt_context_consumption_failed -> prompt_context_audit_summary_pending
prompt_context_audit_summary_pending -> prompt_context_audit_summary_ready
prompt_context_audit_summary_pending -> prompt_context_audit_summary_failed
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| prompt_context_consumed | request_prompt_context_audit_summary | prompt_context_audit_summary_pending | Future workflow/API | Starts read-only summary only |
| prompt_context_consumption_skipped | request_prompt_context_audit_summary | prompt_context_audit_summary_pending | Future workflow/API | Summarizes skipped evidence |
| prompt_context_consumption_failed | request_prompt_context_audit_summary | prompt_context_audit_summary_pending | Future workflow/API | Summarizes failure evidence |
| prompt_context_audit_summary_pending | summarize_prompt_context_consumption | prompt_context_audit_summary_ready | Future workflow/API | Requires consumption evidence |
| prompt_context_audit_summary_pending | fail_prompt_context_audit_summary | prompt_context_audit_summary_failed | Future workflow/API | Records failure code |

TestKnowledgeCard Prompt Context Audit Summary state rules:

- `summarize_prompt_context_consumption` requires prompt context consumption
  artifact id, prompt context evidence artifact id, context manifest,
  `used_knowledge` decision, output citations, skipped evidence, unsupported
  claims, PromptVersion, SkillVersion, source hash, ReviewHistory, and failure
  code when applicable.
- Audit summaries are read-only. They may produce usage status, cited entries,
  skipped entries, unsupported claim summaries, review flags, and failure
  reasons, but they must not invent citations, rewrite `used_knowledge`, or
  mutate consumption evidence.
- Missing, stale, unsafe, revoked, cross-project, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, or evidence-mismatched input must
  produce `prompt_context_audit_summary_failed` or a summary with failure flags.
- Prompt context audit summary may write audit summary artifacts in a later
  scoped workflow. It must not mutate TestKnowledgeCard rows, source artifacts,
  prompt context consumption artifacts, prompt context evidence artifacts,
  retrieval boundary artifacts, prompt eligibility artifacts, ReviewHistory,
  KnowledgeEvidence, or historical evidence.
- The prompt context audit summary state contract must not add frontend page,
  report generation behavior, prompt assembly implementation, prompt runtime
  execution, provider calls, retrieval ranking changes, vector indexes,
  embeddings, reranking, graph jobs, MCP runtime, broad TestKnowledgeCard CRUD,
  automatic eligibility, artifact mutation outside declared audit summary
  output, historical evidence mutation, generated-case auto-approval, runner
  behavior changes, RBAC, tenants, permissions, or remote CI provider behavior.

## 7.12 TestKnowledgeCard Prompt Context Audit Review Decision State Contract

TestKnowledgeCard Prompt Context Audit Review Decision is a human review
decision state boundary for future workflows that accept, question, or reject
prompt context audit summaries. It starts only from prompt context audit summary
evidence and does not implement frontend rendering, report generation behavior,
prompt assembly, prompt runtime execution, provider calls, retrieval ranking,
model citation generation, prompt eligibility, card creation, or broad
TestKnowledgeCard CRUD.

```text
prompt_context_audit_summary_ready -> prompt_context_audit_review_pending
prompt_context_audit_review_pending -> prompt_context_audit_review_accepted
prompt_context_audit_review_pending -> prompt_context_audit_review_needs_clarification
prompt_context_audit_review_pending -> prompt_context_audit_review_rejected_for_missing_evidence
prompt_context_audit_review_pending -> prompt_context_audit_review_rejected_for_unsupported_claim
prompt_context_audit_review_pending -> prompt_context_audit_review_rejected_for_citation_mismatch
prompt_context_audit_review_pending -> prompt_context_audit_review_failed
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| prompt_context_audit_summary_ready | request_prompt_context_audit_review | prompt_context_audit_review_pending | Future workflow/API | Starts human review decision only |
| prompt_context_audit_review_pending | review_prompt_context_audit_summary | prompt_context_audit_review_accepted | Future human reviewer | Uses `review_action=accepted` |
| prompt_context_audit_review_pending | review_prompt_context_audit_summary | prompt_context_audit_review_needs_clarification | Future human reviewer | Uses `review_action=needs_clarification` |
| prompt_context_audit_review_pending | review_prompt_context_audit_summary | prompt_context_audit_review_rejected_for_missing_evidence | Future human reviewer | Uses `review_action=rejected_for_missing_evidence` |
| prompt_context_audit_review_pending | review_prompt_context_audit_summary | prompt_context_audit_review_rejected_for_unsupported_claim | Future human reviewer | Uses `review_action=rejected_for_unsupported_claim` |
| prompt_context_audit_review_pending | review_prompt_context_audit_summary | prompt_context_audit_review_rejected_for_citation_mismatch | Future human reviewer | Uses `review_action=rejected_for_citation_mismatch` |
| prompt_context_audit_review_pending | fail_prompt_context_audit_review_decision | prompt_context_audit_review_failed | Future workflow/API | Records invalid input or failure code |

TestKnowledgeCard Prompt Context Audit Review Decision state rules:

- `review_prompt_context_audit_summary` requires prompt context audit summary
  artifact id, prompt context consumption artifact id, prompt context evidence
  artifact id, context manifest, `used_knowledge` decision, usage status,
  output citations, skipped evidence, unsupported claims, PromptVersion,
  SkillVersion, source hash, ReviewHistory, review action, and failure code
  when applicable.
- Review decision states are human review evidence. They may produce review
  action, reviewer comment, accepted/questioned/rejected citation ids,
  follow-up flags, requested clarification, ReviewHistory link, and failure
  reasons, but they must not invent citations, rewrite `used_knowledge`, or
  mutate audit summary evidence.
- `accepted` does not create prompt eligibility, approve TestKnowledgeCard
  content, approve generated cases, mutate prompt context consumption evidence,
  or change `used_knowledge`.
- `needs_clarification`,
  `rejected_for_missing_evidence`, `rejected_for_unsupported_claim`,
  `rejected_for_citation_mismatch`, `rejected_for_stale_evidence`, and
  `rejected_for_cross_project_evidence` must preserve cited evidence, skipped
  evidence, unsupported claims, source hashes, PromptVersion, SkillVersion,
  context manifest links, and ReviewHistory.
- Missing, stale, unsafe, revoked, cross-project, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched, or audit
  summary-mismatched input must produce `prompt_context_audit_review_failed`
  and must not append a successful ReviewHistory decision.
- Prompt context audit review decision may write review decision artifacts in a
  later scoped workflow. It must not mutate TestKnowledgeCard rows, source
  artifacts, prompt context audit summary artifacts, prompt context consumption
  artifacts, prompt context evidence artifacts, retrieval boundary artifacts,
  prompt eligibility artifacts, ReviewHistory, KnowledgeEvidence, or historical
  evidence.
- The prompt context audit review decision state contract must not add
  frontend page, report generation behavior, prompt assembly implementation,
  prompt runtime execution, provider calls, retrieval ranking changes, vector
  indexes, embeddings, reranking, graph jobs, MCP runtime, broad
  TestKnowledgeCard CRUD, automatic eligibility, artifact mutation outside
  declared review decision output, historical evidence mutation,
  generated-case auto-approval, runner behavior changes, RBAC, tenants,
  permissions, or remote CI provider behavior.

## 7.13 TestKnowledgeCard Prompt Context Audit Review Summary Export State Contract

TestKnowledgeCard Prompt Context Audit Review Summary Export is a contract-only
state boundary for future workflows that package prompt context audit review
decision evidence into an exportable summary. It starts only from prompt
context audit review decision evidence and does not implement frontend
rendering, report generation behavior, export/download endpoints, prompt
assembly, prompt runtime execution, provider calls, retrieval ranking, model
citation generation, prompt eligibility, card creation, or broad
TestKnowledgeCard CRUD.

```text
prompt_context_audit_review_accepted -> prompt_context_audit_review_summary_export_pending
prompt_context_audit_review_needs_clarification -> prompt_context_audit_review_summary_export_pending
prompt_context_audit_review_rejected_for_missing_evidence -> prompt_context_audit_review_summary_export_pending
prompt_context_audit_review_rejected_for_unsupported_claim -> prompt_context_audit_review_summary_export_pending
prompt_context_audit_review_rejected_for_citation_mismatch -> prompt_context_audit_review_summary_export_pending
prompt_context_audit_review_summary_export_pending -> prompt_context_audit_review_summary_export_ready
prompt_context_audit_review_summary_export_pending -> prompt_context_audit_review_summary_export_failed
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| prompt_context_audit_review_accepted | request_prompt_context_audit_review_summary_export | prompt_context_audit_review_summary_export_pending | Future workflow/API | Starts summary export only |
| prompt_context_audit_review_needs_clarification | request_prompt_context_audit_review_summary_export | prompt_context_audit_review_summary_export_pending | Future workflow/API | Keeps unresolved follow-up visible |
| prompt_context_audit_review_rejected_for_missing_evidence | request_prompt_context_audit_review_summary_export | prompt_context_audit_review_summary_export_pending | Future workflow/API | Packages rejection evidence |
| prompt_context_audit_review_rejected_for_unsupported_claim | request_prompt_context_audit_review_summary_export | prompt_context_audit_review_summary_export_pending | Future workflow/API | Packages unsupported claims |
| prompt_context_audit_review_rejected_for_citation_mismatch | request_prompt_context_audit_review_summary_export | prompt_context_audit_review_summary_export_pending | Future workflow/API | Packages citation mismatch |
| prompt_context_audit_review_summary_export_pending | export_prompt_context_audit_review_summary | prompt_context_audit_review_summary_export_ready | Future workflow/API | Requires review decision evidence |
| prompt_context_audit_review_summary_export_pending | fail_prompt_context_audit_review_summary_export | prompt_context_audit_review_summary_export_failed | Future workflow/API | Records invalid input or failure code |

TestKnowledgeCard Prompt Context Audit Review Summary Export state rules:

- `export_prompt_context_audit_review_summary` requires prompt context audit
  review decision artifact id, prompt context audit summary artifact id, prompt
  context consumption artifact id, prompt context evidence artifact id, context
  manifest, `used_knowledge` decision, usage status, review action, accepted/
  questioned/rejected citations, unresolved follow-up flags, unsupported
  claims, PromptVersion, SkillVersion, source hash, ReviewHistory, and failure
  code when applicable.
- Summary export states are evidence packaging only. They may produce review
  outcome summary, accepted/questioned/rejected citation groups, unresolved
  follow-up flags, unsupported claim references, reviewer comment summary,
  ReviewHistory links, and failure reasons, but they must not invent citations,
  rewrite `used_knowledge`, or mutate audit review decision evidence.
- Accepted citation groups do not create prompt eligibility, approve
  TestKnowledgeCard content, approve generated cases, mutate prompt context
  consumption evidence, or change `used_knowledge`.
- Questioned citation groups, rejected citation groups,
  `needs_clarification`, unresolved follow-up flags, skipped evidence, and
  unsupported claims must preserve source hashes, PromptVersion, SkillVersion,
  context manifest links, and ReviewHistory.
- Missing, stale, unsafe, revoked, cross-project, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched,
  audit-summary-mismatched, or review-decision-mismatched input must produce
  `prompt_context_audit_review_summary_export_failed` and must not append a
  successful summary export.
- Prompt context audit review summary export may write summary export artifacts
  in a later scoped workflow. It must not mutate TestKnowledgeCard rows, source
  artifacts, prompt context audit review decision artifacts, prompt context
  audit summary artifacts, prompt context consumption artifacts, prompt context
  evidence artifacts, retrieval boundary artifacts, prompt eligibility
  artifacts, ReviewHistory, KnowledgeEvidence, or historical evidence.
- The prompt context audit review summary export state contract must not add
  frontend page, report generation behavior, export/download endpoint, prompt
  assembly implementation, prompt runtime execution, provider calls, retrieval
  ranking changes, vector indexes, embeddings, reranking, graph jobs, MCP
  runtime, broad TestKnowledgeCard CRUD, automatic eligibility, artifact
  mutation outside declared summary export output, historical evidence
  mutation, generated-case auto-approval, runner behavior changes, RBAC,
  tenants, permissions, or remote CI provider behavior.

## 7.14 TestKnowledgeCard Prompt Context Review Discrepancy Tracking State Contract

TestKnowledgeCard Prompt Context Review Discrepancy Tracking is a
contract-only state boundary for future workflows that record reviewable
discrepancies between prompt context consumption, audit summaries, review
decisions, and summary exports. It starts only from persisted review evidence
and does not implement frontend rendering, report generation behavior,
export/download endpoints, prompt assembly, prompt runtime execution, provider
calls, retrieval ranking, model citation generation, prompt eligibility, card
creation, or broad TestKnowledgeCard CRUD.

```text
prompt_context_audit_review_summary_export_ready -> prompt_context_review_discrepancy_pending
prompt_context_review_discrepancy_pending -> prompt_context_review_discrepancy_recorded
prompt_context_review_discrepancy_pending -> prompt_context_review_discrepancy_failed
prompt_context_review_discrepancy_recorded -> prompt_context_review_discrepancy_open
prompt_context_review_discrepancy_recorded -> prompt_context_review_discrepancy_acknowledged
prompt_context_review_discrepancy_recorded -> prompt_context_review_discrepancy_needs_clarification
prompt_context_review_discrepancy_recorded -> prompt_context_review_discrepancy_resolved_by_later_review
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| prompt_context_audit_review_summary_export_ready | request_prompt_context_review_discrepancy_tracking | prompt_context_review_discrepancy_pending | Future workflow/API | Starts discrepancy tracking only |
| prompt_context_review_discrepancy_pending | track_prompt_context_review_discrepancy | prompt_context_review_discrepancy_recorded | Future workflow/API | Requires review evidence |
| prompt_context_review_discrepancy_pending | fail_prompt_context_review_discrepancy | prompt_context_review_discrepancy_failed | Future workflow/API | Records invalid input or failure code |
| prompt_context_review_discrepancy_recorded | mark_discrepancy_open | prompt_context_review_discrepancy_open | Future human reviewer | Status label only |
| prompt_context_review_discrepancy_recorded | acknowledge_discrepancy | prompt_context_review_discrepancy_acknowledged | Future human reviewer | Status label only |
| prompt_context_review_discrepancy_recorded | request_discrepancy_clarification | prompt_context_review_discrepancy_needs_clarification | Future human reviewer | Status label only |
| prompt_context_review_discrepancy_recorded | mark_resolved_by_later_review | prompt_context_review_discrepancy_resolved_by_later_review | Future human reviewer | References later ReviewHistory |

TestKnowledgeCard Prompt Context Review Discrepancy Tracking state rules:

- `track_prompt_context_review_discrepancy` requires prompt context audit
  review summary export artifact id, audit review decision artifact id, audit
  summary artifact id, prompt context consumption artifact id, prompt context
  evidence artifact id, context manifest, `used_knowledge` decision, usage
  status, affected citation ids, discrepancy type, evidence gap summary,
  mismatch reason, severity, resolution status, unresolved follow-up flags,
  unsupported claim references, PromptVersion, SkillVersion, source hash,
  ReviewHistory, and failure code when applicable.
- Discrepancy states are mismatch evidence only. They may produce discrepancy
  type, affected citation ids, evidence gap summary, mismatch reason, reviewer
  note, severity, resolution status, unresolved follow-up flags, unsupported
  claim references, ReviewHistory links, and failure reasons, but they must not
  invent citations, rewrite `used_knowledge`, auto-resolve discrepancies, or
  mutate review summary export evidence.
- Resolution statuses are audit labels only. They do not create prompt
  eligibility, approve TestKnowledgeCard content, approve generated cases,
  mutate prompt context consumption evidence, or change `used_knowledge`.
- Affected citation ids, questioned/rejected citation groups, unresolved
  follow-up flags, skipped evidence, unsupported claims, source hashes,
  PromptVersion, SkillVersion, context manifest links, and ReviewHistory must
  remain visible.
- Missing, stale, unsafe, revoked, cross-project, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched,
  audit-summary-mismatched, review-decision-mismatched, or
  summary-export-mismatched input must produce
  `prompt_context_review_discrepancy_failed` and must not append a successful
  discrepancy record.
- Prompt context review discrepancy tracking may write discrepancy artifacts in
  a later scoped workflow. It must not mutate TestKnowledgeCard rows, source
  artifacts, review summary export artifacts, audit review decision artifacts,
  audit summary artifacts, prompt context consumption artifacts, prompt context
  evidence artifacts, retrieval boundary artifacts, prompt eligibility
  artifacts, ReviewHistory, KnowledgeEvidence, or historical evidence.
- The prompt context review discrepancy tracking state contract must not add
  frontend page, report generation behavior, export/download endpoint, prompt
  assembly implementation, prompt runtime execution, provider calls, retrieval
  ranking changes, vector indexes, embeddings, reranking, graph jobs, MCP
  runtime, broad TestKnowledgeCard CRUD, automatic eligibility, artifact
  mutation outside declared discrepancy output, historical evidence mutation,
  generated-case auto-approval, runner behavior changes, RBAC, tenants,
  permissions, or remote CI provider behavior.

## 7.15 TestKnowledgeCard Prompt Context Discrepancy Resolution Review State Contract

TestKnowledgeCard Prompt Context Discrepancy Resolution Review is a
contract-only state boundary for future workflows that record human review of
prompt context discrepancy records. It starts only from persisted discrepancy
tracking evidence and does not implement frontend rendering, report generation
behavior, export/download endpoints, prompt assembly, prompt runtime
execution, provider calls, retrieval ranking, model citation generation,
prompt eligibility, card creation, or broad TestKnowledgeCard CRUD.

```text
prompt_context_review_discrepancy_open -> prompt_context_discrepancy_resolution_review_pending
prompt_context_review_discrepancy_needs_clarification -> prompt_context_discrepancy_resolution_review_pending
prompt_context_review_discrepancy_acknowledged -> prompt_context_discrepancy_resolution_review_pending
prompt_context_discrepancy_resolution_review_pending -> prompt_context_discrepancy_resolution_review_recorded
prompt_context_discrepancy_resolution_review_pending -> prompt_context_discrepancy_resolution_review_failed
prompt_context_discrepancy_resolution_review_recorded -> prompt_context_discrepancy_resolution_acknowledged
prompt_context_discrepancy_resolution_review_recorded -> prompt_context_discrepancy_resolution_rejected
prompt_context_discrepancy_resolution_review_recorded -> prompt_context_discrepancy_resolution_needs_clarification
prompt_context_discrepancy_resolution_review_recorded -> prompt_context_discrepancy_resolution_resolved_by_later_review
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| prompt_context_review_discrepancy_open | request_prompt_context_discrepancy_resolution_review | prompt_context_discrepancy_resolution_review_pending | Future human reviewer | Starts resolution review only |
| prompt_context_review_discrepancy_needs_clarification | request_prompt_context_discrepancy_resolution_review | prompt_context_discrepancy_resolution_review_pending | Future human reviewer | Preserves clarification request |
| prompt_context_review_discrepancy_acknowledged | request_prompt_context_discrepancy_resolution_review | prompt_context_discrepancy_resolution_review_pending | Future human reviewer | Adds review evidence without mutating history |
| prompt_context_discrepancy_resolution_review_pending | review_prompt_context_discrepancy_resolution | prompt_context_discrepancy_resolution_review_recorded | Future workflow/API | Requires discrepancy evidence |
| prompt_context_discrepancy_resolution_review_pending | fail_prompt_context_discrepancy_resolution_review | prompt_context_discrepancy_resolution_review_failed | Future workflow/API | Records invalid input or failure code |
| prompt_context_discrepancy_resolution_review_recorded | acknowledge_discrepancy | prompt_context_discrepancy_resolution_acknowledged | Future human reviewer | Status label only |
| prompt_context_discrepancy_resolution_review_recorded | reject_discrepancy_resolution | prompt_context_discrepancy_resolution_rejected | Future human reviewer | Status label only |
| prompt_context_discrepancy_resolution_review_recorded | request_discrepancy_clarification | prompt_context_discrepancy_resolution_needs_clarification | Future human reviewer | Preserves requested fields |
| prompt_context_discrepancy_resolution_review_recorded | mark_resolved_by_later_review | prompt_context_discrepancy_resolution_resolved_by_later_review | Future human reviewer | References later ReviewHistory |

TestKnowledgeCard Prompt Context Discrepancy Resolution Review state rules:

- `review_prompt_context_discrepancy_resolution` requires prompt context review
  discrepancy artifact id, prompt context audit review summary export artifact
  id, audit review decision artifact id, audit summary artifact id, prompt
  context consumption artifact id, prompt context evidence artifact id, context
  manifest, `used_knowledge` decision, usage status, discrepancy type,
  affected citation ids, evidence gap summary, mismatch reason, severity,
  current resolution status, resolution action, accepted discrepancy ids,
  rejected discrepancy ids, acknowledged discrepancy ids, unresolved follow-up
  flags, unsupported claim references, PromptVersion, SkillVersion, source
  hash, ReviewHistory, and failure code when applicable.
- Resolution review states are human review evidence only. They may produce
  resolution action, resulting resolution status, accepted discrepancy ids,
  rejected discrepancy ids, acknowledged discrepancy ids, clarification
  requested fields, reviewer note, follow-up flags, ReviewHistory links,
  failure reasons, and visible reason, but they must not invent citations, rewrite
  `used_knowledge`, auto-resolve discrepancies, or mutate discrepancy tracking
  evidence.
- Resolution statuses are audit labels only. They do not create prompt
  eligibility, approve TestKnowledgeCard content, approve generated cases,
  mutate prompt context consumption evidence, or change `used_knowledge`.
- Affected citation ids, accepted/rejected/acknowledged discrepancy ids,
  questioned/rejected citation groups, unresolved follow-up flags, skipped
  evidence, unsupported claims, source hashes, PromptVersion, SkillVersion,
  context manifest links, and ReviewHistory must remain visible.
- Missing, stale, unsafe, revoked, cross-project, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, discrepancy-mismatched,
  evidence-mismatched, audit-summary-mismatched, review-decision-mismatched, or
  summary-export-mismatched input must produce
  `prompt_context_discrepancy_resolution_review_failed` with a visible reason
  and must not append a successful resolution review.
- Prompt context discrepancy resolution review may write resolution review
  artifacts in a later scoped workflow. It must not mutate TestKnowledgeCard
  rows, source artifacts, prompt context review discrepancy artifacts, review
  summary export artifacts, audit review decision artifacts, audit summary
  artifacts, prompt context consumption artifacts, prompt context evidence
  artifacts, retrieval boundary artifacts, prompt eligibility artifacts,
  ReviewHistory, KnowledgeEvidence, or historical evidence.
- The prompt context discrepancy resolution review state contract must not add
  frontend page, report generation behavior, export/download endpoint, prompt
  assembly implementation, prompt runtime execution, provider calls, retrieval
  ranking changes, vector indexes, embeddings, reranking, graph jobs, MCP
  runtime, broad TestKnowledgeCard CRUD, automatic eligibility, artifact
  mutation outside declared resolution review output, historical evidence
  mutation, generated-case auto-approval, runner behavior changes, RBAC,
  tenants, permissions, or remote CI provider behavior.

## 7.16 TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export State Contract

TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export is a
contract-only state boundary for future workflows that package prompt context
discrepancy resolution review evidence into a summary export. It starts only
from persisted resolution review evidence and does not implement frontend
rendering, report generation behavior, export/download endpoints, prompt
assembly, prompt runtime execution, provider calls, retrieval ranking, model
citation generation, prompt eligibility, card creation, or broad
TestKnowledgeCard CRUD.

```text
prompt_context_discrepancy_resolution_acknowledged -> prompt_context_discrepancy_resolution_summary_export_pending
prompt_context_discrepancy_resolution_rejected -> prompt_context_discrepancy_resolution_summary_export_pending
prompt_context_discrepancy_resolution_needs_clarification -> prompt_context_discrepancy_resolution_summary_export_pending
prompt_context_discrepancy_resolution_resolved_by_later_review -> prompt_context_discrepancy_resolution_summary_export_pending
prompt_context_discrepancy_resolution_summary_export_pending -> prompt_context_discrepancy_resolution_summary_export_ready
prompt_context_discrepancy_resolution_summary_export_pending -> prompt_context_discrepancy_resolution_summary_export_failed
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| prompt_context_discrepancy_resolution_acknowledged | request_prompt_context_discrepancy_resolution_summary_export | prompt_context_discrepancy_resolution_summary_export_pending | Future workflow/API | Packages acknowledged discrepancy evidence |
| prompt_context_discrepancy_resolution_rejected | request_prompt_context_discrepancy_resolution_summary_export | prompt_context_discrepancy_resolution_summary_export_pending | Future workflow/API | Packages rejected discrepancy evidence |
| prompt_context_discrepancy_resolution_needs_clarification | request_prompt_context_discrepancy_resolution_summary_export | prompt_context_discrepancy_resolution_summary_export_pending | Future workflow/API | Keeps clarification fields visible |
| prompt_context_discrepancy_resolution_resolved_by_later_review | request_prompt_context_discrepancy_resolution_summary_export | prompt_context_discrepancy_resolution_summary_export_pending | Future workflow/API | References later ReviewHistory |
| prompt_context_discrepancy_resolution_summary_export_pending | export_prompt_context_discrepancy_resolution_summary | prompt_context_discrepancy_resolution_summary_export_ready | Future workflow/API | Requires resolution review evidence |
| prompt_context_discrepancy_resolution_summary_export_pending | fail_prompt_context_discrepancy_resolution_summary_export | prompt_context_discrepancy_resolution_summary_export_failed | Future workflow/API | Records invalid input or failure code |

TestKnowledgeCard Prompt Context Discrepancy Resolution Summary Export state
rules:

- `export_prompt_context_discrepancy_resolution_summary` requires prompt
  context discrepancy resolution review artifact id, prompt context review
  discrepancy artifact id, prompt context audit review summary export artifact
  id, audit review decision artifact id, audit summary artifact id, prompt
  context consumption artifact id, prompt context evidence artifact id,
  context manifest, `used_knowledge` decision, usage status, resolution
  action, resulting resolution status, accepted discrepancy ids, rejected
  discrepancy ids, acknowledged discrepancy ids, clarification requested
  fields, affected citation ids, evidence gap summary, mismatch reason,
  unresolved follow-up flags, unsupported claim references, PromptVersion,
  SkillVersion, source hash, ReviewHistory, and failure code when applicable.
- Resolution summary export states are evidence packaging only. They may
  produce resolution outcome summary, accepted discrepancy group, rejected
  discrepancy group, acknowledged discrepancy group, clarification requested
  field group, unresolved follow-up flag group, reviewer comment summary,
  resulting resolution status group, ReviewHistory links, failure reasons, and
  visible reason, but they must not invent citations, rewrite `used_knowledge`,
  auto-resolve discrepancies, or mutate resolution review evidence.
- Resolution outcome groups and resulting resolution status group are audit
  labels only. They do not create prompt eligibility, approve TestKnowledgeCard
  content, approve generated cases, mutate prompt context consumption evidence,
  or change `used_knowledge`.
- Accepted/rejected/acknowledged discrepancy groups, clarification requested
  fields, affected citation ids, unresolved follow-up flags, skipped evidence,
  unsupported claims, source hashes, PromptVersion, SkillVersion, context
  manifest links, and ReviewHistory must remain visible.
- Missing, stale, unsafe, revoked, cross-project, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, discrepancy-mismatched,
  resolution-review-mismatched, evidence-mismatched, audit-summary-mismatched,
  review-decision-mismatched, or summary-export-mismatched input must produce
  `prompt_context_discrepancy_resolution_summary_export_failed` with a visible
  reason and must not append a successful resolution summary export.
- Prompt context discrepancy resolution summary export may write summary export
  artifacts in a later scoped workflow. It must not mutate TestKnowledgeCard
  rows, source artifacts, prompt context discrepancy resolution review
  artifacts, prompt context review discrepancy artifacts, review summary export
  artifacts, audit review decision artifacts, audit summary artifacts, prompt
  context consumption artifacts, prompt context evidence artifacts, retrieval
  boundary artifacts, prompt eligibility artifacts, ReviewHistory,
  KnowledgeEvidence, or historical evidence.
- The prompt context discrepancy resolution summary export state contract must
  not add frontend page, report generation behavior, export/download endpoint,
  prompt assembly implementation, prompt runtime execution, provider calls,
  retrieval ranking changes, vector indexes, embeddings, reranking, graph jobs,
  MCP runtime, broad TestKnowledgeCard CRUD, automatic eligibility, artifact
  mutation outside declared summary export output, historical evidence
  mutation, generated-case auto-approval, runner behavior changes, RBAC,
  tenants, permissions, or remote CI provider behavior.

### 3.1 Requirement To Reviewed Case Agent Workflow State Contract

The requirement-to-reviewed-case agent workflow is a state contract layered on
top of existing AITask, GeneratedCaseCandidate, TestCase, and ReviewHistory
behavior. It must not introduce a new orchestrator runtime, API endpoint,
runtime graph executor, provider runtime, RAG runtime, MCP runtime, vector
index, embedding job, reranking job, graph extraction job, RBAC, tenant, or
permission behavior.

```text
created
  -> requirement_understanding_running -> requirement_understanding_ready
  -> risk_analysis_running -> risk_analysis_ready
  -> coverage_analysis_running -> coverage_analysis_ready
  -> test_design_running -> test_design_ready
  -> case_generation_running -> candidates_generated
  -> case_review_running -> case_review_ready
  -> dedup_running -> dedup_ready
  -> automation_readiness_running -> waiting_human_review
waiting_human_review -> reviewed_case_created
waiting_human_review -> rejected
waiting_human_review -> needs_optimization -> test_design_running
any *_running -> failed
failed -> fallback_ready
fallback_ready -> waiting_human_review
created/running/ready/waiting_human_review -> cancelled
```

| Current state | Action | Target state | Actor | Notes |
|---|---|---|---|---|
| created | start_requirement_understanding | requirement_understanding_running | AITask worker | Reads Requirement and context manifest only |
| requirement_understanding_running | understanding_valid | requirement_understanding_ready | AITask worker | Writes `requirement_understanding` artifact |
| requirement_understanding_ready | start_risk_analysis | risk_analysis_running | AITask worker | Reads understanding artifact |
| risk_analysis_running | risk_valid | risk_analysis_ready | AITask worker | Writes `risk_analysis` artifact |
| risk_analysis_ready | start_coverage_analysis | coverage_analysis_running | AITask worker | Reads risk and requirement trace refs |
| coverage_analysis_running | coverage_valid | coverage_analysis_ready | AITask worker | Writes `coverage_analysis` artifact |
| coverage_analysis_ready | start_test_design | test_design_running | AITask worker | Reads coverage gaps and target test types |
| test_design_running | design_valid | test_design_ready | AITask worker | Writes `test_design` artifact |
| test_design_ready | start_case_generation | case_generation_running | AITask worker | Uses existing case generation task |
| case_generation_running | candidates_validated | candidates_generated | AITask worker | Creates GeneratedCaseCandidate rows with `status=generated` |
| candidates_generated | start_case_review | case_review_running | AITask worker | Reads persisted candidates and evidence |
| case_review_running | review_valid | case_review_ready | AITask worker | Writes review findings only |
| case_review_ready | start_dedup | dedup_running | AITask worker | Reads candidates and approved TestCase summaries |
| dedup_running | dedup_valid | dedup_ready | AITask worker | Writes dedup findings only |
| dedup_ready | start_automation_readiness | automation_readiness_running | AITask worker | Reads ToolDefinition/TestCommand metadata only |
| automation_readiness_running | readiness_valid | waiting_human_review | AITask worker | Writes readiness findings only |
| waiting_human_review | approve | reviewed_case_created | User/API | Existing candidate review approval creates TestCase |
| waiting_human_review | approve_after_edit | reviewed_case_created | User/API | Existing candidate review approval creates edited TestCase |
| waiting_human_review | reject | rejected | User/API | Existing candidate rejection; no TestCase |
| waiting_human_review | request_optimization | needs_optimization | User/API | Existing optimization path |
| needs_optimization | regenerate_from_feedback | test_design_running | AITask worker | Reuses design/generation path with reviewer feedback |
| any *_running | schema_or_agent_error | failed | AITask worker | Persists raw/error artifacts |
| failed | fallback_available | fallback_ready | AITask worker | Only when a valid partial output can be safely reviewed |
| fallback_ready | submit_partial_for_review | waiting_human_review | AITask worker | Human gate remains required |
| created/running/ready/waiting_human_review | cancel | cancelled | User/API | Must not create or approve TestCase |

Agent state rules:

| Agent | Success state | write permission | human gate | failure behavior |
|---|---|---|---|---|
| RequirementUnderstandingAgent | `requirement_understanding_ready` | AITask artifacts and parsed requirement-understanding payload only | None inside the step | Schema failure stops the workflow in `failed`; fallback may record ambiguity findings but must not generate cases |
| RiskAnalysisAgent | `risk_analysis_ready` | AITask artifacts and derived risk evidence only | None inside the step | Failure may fallback to `risk_level=unknown` and continue only with visible risk warning evidence |
| CoverageAnalysisAgent | `coverage_analysis_ready` | AITask artifacts and coverage/gap evidence only | None inside the step | Failure may fallback to `coverage_status=unknown`; no candidate may be auto-approved |
| TestDesignAgent | `test_design_ready` | AITask artifacts and transient design payloads only | None inside the step | Invalid design stops generation unless valid scenario subsets are explicitly recorded as partial fallback |
| CaseGenerationAgent | `candidates_generated` | AITask artifacts and GeneratedCaseCandidate creation with `status=generated` | Required after generation | Invalid candidates are not persisted; zero valid candidates leaves the workflow `failed` or reviewable only as an error artifact |
| CaseReviewAgent | `case_review_ready` | AITask artifacts and candidate review evidence fields only | Required for any approve/reject/optimization action | Failure leaves candidate status unchanged and records `case_review_unavailable` |
| DedupAgent | `dedup_ready` | AITask artifacts and duplicate review findings only | Required for any duplicate resolution | Failure records `dedup_status=unknown`; candidates remain unapproved until human review |
| AutomationReadinessAgent | `waiting_human_review` | AITask artifacts and readiness review findings only | Required before TestCase creation | Failure records `automation_readiness=unknown`; must not create AutomationDraft, ToolInvocation, or TestRun |

Hard rules:

- `waiting_human_review` is the only state from which a generated candidate may
  become a reviewed TestCase, and only through the existing human review action.
- Agent states do not replace AITask statuses. They are trace fields and
  artifact metadata for the existing AITask/case generation surfaces.
- Agent outputs are evidence. Quality scores, coverage gaps, dedup clusters,
  risk scores, and automation readiness must not auto promote TestCase,
  approve candidates, reject candidates, archive candidates, mutate TestCase
  rows, execute automation, create reports, or update CI/CD state.
- Failure fallback must be explicit in trace fields: `fallback_applied=true`,
  a stable `failure_code`, and output artifacts explaining what was omitted.
- Schema validation failure may write raw/error artifacts but must not write
  business rows except for already validated candidates created before the
  failure. Partial candidate persistence must preserve validation evidence.
- The workflow must not start background indexing, provider calls, external RAG
  retrieval, MCP calls, vector search, embedding creation, reranking, graph
  extraction, remote CI provider calls, RBAC, tenants, permissions,
  marketplace, cloud sync, merge, deploy, or release behavior.

## 4. AutomationDraft 状态机

```text
draft_generated -> under_review -> approved -> execution_pending -> executed -> promoted
draft_generated -> under_review -> edited -> approved
draft_generated -> under_review -> rejected
authorized execution failure: execution_pending -> execution_failed -> under_review
```

| 当前状态 | 动作 | 目标状态 | 说明 |
|---|---|---|---|
| draft_generated | open_review | under_review | 用户查看草稿 |
| under_review | edit | edited | 用户修改草稿 |
| under_review/edited | approve | approved | 允许执行 |
| under_review/edited | reject | rejected | 不执行 |
| approved | create_test_run | execution_pending | 创建 TestRun |
| execution_pending | test_passed | executed | 执行成功 |
| execution_pending | test_failed | execution_failed | 执行失败 |
| execution_failed | revise | under_review | 重新评审草稿 |
| executed | promote | promoted | 可转为正式自动化资产或 artifact |

规则：AutomationDraft 未 approved 前不能执行。V1 不允许自动写业务源码。

ReviewHistory side effect:

- `edit`, `approve`, and `reject` append ReviewHistory after successful
  transitions where the workflow implements the action.
- ReviewHistory does not make a draft executable. Only the existing
  `status=approved` rule authorizes execution.
- Invalid transitions and validation failures must not append successful review
  history.

## 5. AutomationRepairTask 状态机

```text
created -> running -> candidate_generated -> waiting_review -> approved
created -> running -> failed
candidate_generated -> waiting_review -> rejected
waiting_review -> rejected
```

| 当前状态 | 动作 | 目标状态 | 说明 |
|---|---|---|---|
| created | enqueue | running | 基于失败证据触发修复 |
| running | repair_generated | candidate_generated | 生成修复候选 |
| running | repair_failed | failed | 修复生成失败 |
| candidate_generated | submit_review | waiting_review | 等待人工评审 |
| waiting_review | approve | approved | 用户批准修复候选 |
| waiting_review | reject | rejected | 用户拒绝修复候选 |

规则：AutomationRepairTask 不能自动覆盖已 approved 的 AutomationDraft，不能绕过 AutomationDraft 审批，不能在证据不足时编造 root cause 或 fixture。

## 6. UnitTestPatch 状态机

```text
generated -> scope_validated -> awaiting_review -> approved -> applied
generated -> scope_rejected
generated/scope_validated/awaiting_review -> rejected
generated/scope_validated/awaiting_review -> edited -> scope_validated
awaiting_review/approved -> replaced
approved -> apply_failed
```

| 当前状态 | 动作 | 目标状态 | 说明 |
|---|---|---|---|
| generated | validate_scope_pass | scope_validated | 路径门禁通过 |
| generated | validate_scope_fail | scope_rejected | 包含禁止路径或危险操作 |
| scope_validated | submit_review | awaiting_review | 等待用户审批 |
| awaiting_review | approve | approved | 用户批准 |
| awaiting_review | reject | rejected | 用户拒绝 |
| awaiting_review | edit | edited | 用户编辑 patch |
| edited | validate_scope_pass | scope_validated | 编辑后重新校验 |
| approved | apply_patch_success | applied | 应用成功 |
| approved | apply_patch_failed | apply_failed | 应用失败 |
| awaiting_review/approved | regenerate | replaced | 被新 patch 替代 |

规则：

- `scope_rejected` 不能进入 `approved`。
- UnitTestPatch 只允许写测试目录。
- `approved` 之前不能 apply。
- PatchScopeGate must pass before `approved -> applied`.
- Apply failure must preserve the original patch and error evidence.
- `approve` and `reject` append ReviewHistory after successful review
  transitions. `apply_patch_success` is execution evidence, not a review
  approval event in Slice 21.
- ReviewHistory must not weaken PatchScopeGate or allow a `scope_rejected`
  patch to become approved.

## 7. ToolInvocation 状态机

```text
created -> waiting_approval -> approved -> running -> succeeded
created -> waiting_approval -> rejected
created -> running -> succeeded
running -> failed / timeout / cancelled
```

| 当前状态 | 动作 | 目标状态 | 说明 |
|---|---|---|---|
| created | require_approval | waiting_approval | medium/high 风险 |
| created | auto_approve_low_risk | running | low 风险 |
| waiting_approval | approve | approved | 用户确认 |
| waiting_approval | reject | rejected | 用户拒绝 |
| approved | start | running | 开始执行 |
| running | exit_zero | succeeded | 成功 |
| running | exit_nonzero | failed | 失败 |
| running | timeout | timeout | 超时 |
| running | cancel | cancelled | 取消 |

规则：ToolInvocation 必须来自 ToolDefinition allowlist，禁止任意 shell。

Newman 规则：

ToolDefinition safety state rules:

- ToolInvocation creation snapshots ToolDefinition `input_schema_json`,
  `output_schema_json`, `risk_level`, `approval_required`, `timeout_seconds`,
  `artifact_policy_json`, and MCP-ready metadata before execution.
- `approval_required=true` with medium/high risk must transition through
  `waiting_approval`; it cannot use `auto_approve_low_risk`.
- `waiting_approval -> approved` is the only human gate that allows a
  pending medium/high-risk invocation to reach `running`.
- `waiting_approval -> rejected` is terminal for that invocation and must not
  execute the tool later under the same id.
- `running` requires allowlist validation, working-directory validation,
  timeout validation, approval validation, and artifact policy validation.

ToolInvocation artifact/failure rules:

- `failed`, `timeout`, `cancelled`, and `rejected` must preserve bounded
  stdout, stderr, structured error, and validation artifacts when available.
- A failed or timed-out invocation must not rewrite previous successful
  artifacts and must not create report conclusions by itself.
- ToolInvocation output is execution evidence only. It must not approve
  GeneratedCaseCandidate rows, promote TestCase rows, bypass AutomationDraft
  approval, bypass QualityGateDecision evidence, mutate unrelated artifacts,
  start MCP runtime, call provider SDKs, call external providers, or update
  remote CI provider state.
- `mcp_metadata_json.provider_state` values such as `disabled`, `configured`,
  and `unhealthy` are display readiness only; they do not add ToolInvocation
  states and do not start MCP server/client transport.

Newman execution rules:

- Newman execution uses a ToolInvocation created from the
  `newman_collection_run` ToolDefinition or equivalent built-in allowlisted
  tool.
- The ToolInvocation input must reference an approved `TestCommand` with
  `command_type=newman`; it must not carry arbitrary shell text from the client.
- Shell chaining, redirection, command substitution, and pipes remain forbidden
  even when the underlying executable is Newman.

## 7.1 KnowledgeAdapterConfig 状态机

```text
not_configured -> configured_stub
not_configured -> disabled
configured_stub -> disabled
disabled -> configured_stub
configured_stub -> not_configured
disabled -> not_configured
```

| 当前状态 | 动作 | 目标状态 | 说明 |
|---|---|---|---|
| not_configured | save_stub_config | configured_stub | 只保存 V1 占位配置 |
| not_configured | disable | disabled | 显式禁用 |
| configured_stub | disable | disabled | 禁用占位配置 |
| disabled | enable_stub | configured_stub | 重新启用占位配置 |
| configured_stub | clear | not_configured | 清空配置 |
| disabled | clear | not_configured | 清空配置 |

规则：

- KnowledgeAdapterConfig 状态变化只影响配置展示，不触发 retrieval。
- V1 `configured_stub` 仍然必须返回 `used_knowledge=false`。
- 状态机不得创建 vector index、embedding、reranking job、external provider
  call、MCP runtime call、RBAC、tenant 或 permission 行为。

V2 deterministic retrieval 规则：

- Slice 19 may use `configured_stub` with `provider_type=deterministic_local`
  as a local retrieval stub.
- Configuration changes still do not trigger retrieval by themselves.
- Retrieval is scoped to an AI task invocation and writes evidence artifacts;
  it does not create a long-running adapter state transition.
- `disabled` and `not_configured` always force `used_knowledge=false`.

KnowledgeAdapter safety state rules:

- `provider_state` may appear only as display/health metadata in config or
  safety policy. It is not a persisted state-machine node.
- `provider_state=disabled` behaves like `disabled`: it forces
  `used_knowledge=false` and local/no-knowledge fallback.
- `provider_state=unhealthy` records provider health failure and fallback
  evidence. Core requirement review, case generation, and human review flows
  may continue with `used_knowledge=false` unless the caller explicitly marks
  knowledge evidence as required.
- `configured_stub` and `provider_state=configured` must not create retrieval
  results by themselves. Retrieval evidence exists only after an AI task writes
  a bounded `knowledge_retrieval` artifact with exact source ids.
- Future provider output must normalize into Chtest `KnowledgeEvidence` before
  any prompt, GeneratedCaseCandidate, or review surface cites it.
- KnowledgeAdapter state changes must not create TestKnowledgeCard rows, mutate
  Artifact rows, create ToolInvocation rows, approve/reject/generated-case
  review actions, promote TestCase rows, generate Reports, start MCP runtime,
  call provider SDKs, create vector indexes, create embeddings, rerank, run
  graph jobs, or update remote CI provider state.

## 7.2 TestKnowledgeCard 状态规则

TestKnowledgeCard uses `EntityStatus` only:

```text
active -> archived
active -> deleted
archived -> active
archived -> deleted
```

| 当前状态 | 动作 | 目标状态 | 说明 |
|---|---|---|---|
| active | archive | archived | 从默认知识卡列表隐藏 |
| active | delete | deleted | 软删除，不再用于 prompt 或证据选择 |
| archived | restore | active | 恢复为可见知识卡 |
| archived | delete | deleted | 软删除 |

规则：

- `active` only means the card may be shown or selected when its safety fields
  allow it. It does not mean the card is automatically injected into prompts.
- `deleted` cards must not be cited by new generated cases, but existing
  generated candidates and artifacts may keep historical ids as immutable
  evidence references.
- Status changes must not trigger retrieval, indexing, embeddings, reranking,
  graph extraction, external provider calls, MCP runtime calls, generated-case
  approval, TestCase creation, artifact mutation, runner execution, report
  generation, RBAC, tenant, permission, or remote CI provider behavior.

## 8. TestRun 状态机

```text
created -> queued -> running -> passed
created -> queued -> running -> failed
created -> queued -> running -> error
created/queued/running -> cancelled
running -> timeout
```

| 当前状态 | 动作 | 目标状态 | 说明 |
|---|---|---|---|
| created | enqueue | queued | 入队 |
| queued | worker_start | running | Worker 开始 |
| running | all_tests_pass | passed | 全部通过 |
| running | tests_failed | failed | 有用例失败 |
| running | runner_error | error | 执行器错误 |
| running | timeout | timeout | 超时 |
| created/queued/running | cancel | cancelled | 用户取消 |

规则：failed 与 error 不等价。failed 是测试断言失败，error 是环境、命令、解析器或执行器异常。

Newman 规则：

- Newman follows the same TestRun statuses.
- Newman assertion failures produce `failed`.
- Newman process launch failure, timeout, allowlist rejection, missing
  collection, malformed output, or parser failure produces `error` unless the
  run was cancelled or timed out by the user/runtime.
- Newman `parsed_result_json` and `newman_json` artifacts must be written before
  marking the run `passed` or `failed` when the runner produced parseable
  output.

JMeter 规则：

- JMeter follows the same TestRun statuses.
- JMeter sampler/assertion failures produce `failed`.
- JMeter process launch failure, timeout, allowlist rejection, missing JMX/JTL,
  malformed JTL output, or parser failure produces `error` unless the run was
  cancelled or timed out by the user/runtime.
- JMeter `parsed_result_json` and `jmeter_jtl` artifacts must be written before
  marking the run `passed` or `failed` when the runner produced parseable
  output.
- JMeter execution must stay under ToolDefinition/TestCommand allowlists and
  must not add distributed load agents, cloud load testing controls,
  performance dashboards, RAG runtime calls, MCP runtime dependencies, RBAC,
  tenants, or permissions behavior.

## 8.1 CICDRun Import 状态规则

Slice 20 `ci_import` is an evidence import state, not a remote CI provider
execution state.

```text
created -> imported
created -> import_failed
imported -> analyzed
imported -> archived
```

规则：

- `POST /api/cicd/runs/import` may create a CICDRun directly in `imported`
  status after `ci_run_metadata.json` and changed-file evidence are persisted.
- `import_failed` means the local import payload could not be validated or
  persisted. It does not mean a remote CI job failed.
- Imported CI conclusion values (`success`, `failure`, `cancelled`, `skipped`,
  `timed_out`, `unknown`) are evidence fields, not CICDRun state transitions.
- Imported CI success must not automatically transition
  `CICDRun.quality_gate_status` to `passed`.
- Imported CI failure must not automatically transition
  `CICDRun.quality_gate_status` to `failed`.
- `quality_gate_status` remains `pending` until
  `POST /api/cicd/runs/{id}/quality-gate` or an equivalent explicit gate
  recompute creates a QualityGateDecision.
- Import must not trigger remote CI provider API calls, webhooks, reruns,
  cancellation, scheduling, PR comments, commit status updates, merge, deploy,
  release, credentials, RBAC, tenants, or permissions behavior.

## 9. QualityGateDecision 状态机

```text
CICDRun.quality_gate_status pending -> passed
CICDRun.quality_gate_status pending -> failed
CICDRun.quality_gate_status pending -> needs_review
passed/failed/needs_review -> new QualityGateDecision record on recompute, then update CICDRun.quality_gate_status
```

| 当前状态 | 动作 | 目标状态 | 说明 |
|---|---|---|---|
| pending | compute_gate_pass | passed | PatchScopeGate、新增测试、回归和失败证据均通过 |
| pending | compute_gate_fail | failed | 存在阻塞原因，例如 patch 越界、测试失败或高风险未覆盖 |
| pending | compute_gate_needs_review | needs_review | 证据不足、风险中等或需要人工判断 |
| passed/failed/needs_review | recompute | passed/failed/needs_review | V1 保留旧决定，新建 QualityGateDecision 记录，并更新 CICDRun.quality_gate_status |

规则：

- `pending` 只存在于 `CICDRun.quality_gate_status`，表示尚未产生
  QualityGateDecision。
- QualityGateDecision 记录本身只能是 `passed`、`failed` 或
  `needs_review`。
- QualityGateDecision 不触发 merge、push、release、deployment、remote CI
  status update 或 PR comment。
- Imported CI conclusion may be cited as evidence, but success alone is never
  enough for `passed` and failure alone is not automatically `failed`. Missing
  required local evidence keeps the gate at `needs_review`.
- 每个结论必须引用 evidence artifacts；证据缺失时只能是
  `needs_review`，不能写成 `passed`。
- A successful compute or recompute appends ReviewHistory with
  `entity_type=QualityGateDecision`. `from_status` and `to_status` describe the
  `CICDRun.quality_gate_status` before and after recompute, and
  `related_entity_type=CICDRun` may be used for CI/CD quality page display.
- ReviewHistory does not authorize merge, push, release, deployment, remote CI
  status update, PR comment, RBAC, tenants, or permissions behavior.

## 10. Report 状态机

```text
draft -> generating -> ready
draft -> generating -> failed
ready -> archived
failed -> generating
```

| 当前状态 | 动作 | 目标状态 | 说明 |
|---|---|---|---|
| draft | generate | generating | 开始生成 |
| generating | success | ready | 报告可读 |
| generating | failure | failed | 生成失败 |
| failed | retry | generating | 重试 |
| ready | archive | archived | 归档 |

规则：报告结论必须引用 evidence/artifact。无证据时 conclusion 必须是 `insufficient_evidence` 或 `needs_attention`。

## 11. PromptVersion 和 SkillVersion 状态机

```text
draft -> active -> deprecated
active -> deprecated
```

规则：

- active 版本可被新任务使用。
- deprecated 版本不可作为默认新任务版本。
- 已完成 AITask 必须仍能查看 deprecated 版本内容和 hash。
- 禁止覆盖已发布版本内容。
