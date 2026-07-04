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
