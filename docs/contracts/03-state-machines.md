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
