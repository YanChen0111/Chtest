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

## 5. AutomationRepairTask 状态机

```text
created -> running -> generated -> under_review -> approved
created -> running -> generated -> under_review -> rejected
created -> running -> failed
generated/under_review -> superseded
```

| 当前状态 | 动作 | 目标状态 | 说明 |
|---|---|---|---|
| created | enqueue | running | Worker 开始基于失败证据生成修复候选 |
| running | repair_generated | generated | 生成修复候选和 artifact |
| running | repair_failed | failed | 证据不足、schema 失败或 provider 失败 |
| generated | open_review | under_review | 用户评审修复候选 |
| under_review | approve | approved | 用户接受修复候选，可更新 AutomationDraft 或创建新 draft revision |
| under_review | reject | rejected | 用户拒绝修复候选 |
| generated/under_review | regenerate | superseded | 被新的 repair attempt 替代 |

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

规则：scope_rejected 不能进入 approved。UnitTestPatch 只允许写测试目录。

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

## 9. Report 状态机

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

## 10. PromptVersion 和 SkillVersion 状态机

```text
draft -> active -> deprecated
active -> deprecated
```

规则：

- active 版本可被新任务使用。
- deprecated 版本不可作为默认新任务版本。
- 已完成 AITask 必须仍能查看 deprecated 版本内容和 hash。
- 禁止覆盖已发布版本内容。
