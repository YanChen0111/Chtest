# Chtest AI Quality Metrics

## 1. 文档目的

Chtest 的核心价值不是“能调用大模型”，而是能证明 AI 在测试流程中提高了效率和质量。本文定义第一版必须采集、展示和复盘的 AI 质量指标。

如果没有质量指标，AI 生成用例、生成脚本、失败归因都只是不可控的文本输出。Chtest 必须把 AI 输出变成可评审、可执行、可度量、可优化的测试资产。

## 2. 指标设计原则

- 每个 AI 结果必须绑定 Prompt、Skill、模型、输入、输出、artifact。
- 指标必须能按项目、模块、需求、批次、Prompt、Skill、模型聚合。
- 指标必须覆盖“生成质量”和“执行效果”，不能只统计生成数量。
- 指标必须支持人工反馈，因为第一版最可靠的质量判断来自评审动作。
- 指标必须能指导 Prompt/Skill 迭代，而不是只做展示。

## 3. 指标分层

```text
效率指标：节省多少时间，减少多少重复劳动
质量指标：AI 产物是否完整、准确、可执行、可维护
风险指标：AI 是否遗漏关键场景，是否生成危险操作
执行指标：生成脚本和测试是否能跑通，是否能发现问题
反馈指标：用户最终接受、修改、驳回了什么
```

## 4. 需求评审指标

| 指标 | 公式/来源 | 用途 |
|---|---|---|
| requirement_review_count | 需求评审任务数 | 使用频次 |
| average_requirement_score | 六维评分平均值 | 需求质量趋势 |
| clarification_question_count | AI 生成澄清问题数 | 需求不清晰程度 |
| accepted_issue_rate | 用户保留的问题数 / AI 提出问题数 | 需求评审有效性 |
| edited_issue_rate | 用户编辑的问题数 / AI 提出问题数 | AI 表达质量 |
| risk_item_count | 风险项数量 | 测试风险规模 |
| risk_acceptance_rate | 用户确认风险数 / AI 风险数 | 风险识别准确度 |

第一版可先通过用户保存、删除、编辑需求评审项来计算接受率和修改率。

## 5. 用例生成指标

| 指标 | 公式/来源 | 用途 |
|---|---|---|
| generated_count | 候选用例总数 | 产出规模 |
| schema_valid_rate | schema 校验通过数 / AI 输出用例数 | 输出稳定性 |
| field_complete_rate | 必填字段完整用例数 / 候选用例数 | 用例完整性 |
| duplicate_rate | 重复候选数 / 候选用例数 | 冗余程度 |
| acceptance_rate | 接受数 / 候选用例数 | 直接可用性 |
| edited_acceptance_rate | 编辑后接受数 / 候选用例数 | 半成品可用性 |
| rejection_rate | 驳回数 / 候选用例数 | 无效产出比例 |
| optimization_rate | 要求优化数 / 候选用例数 | 需要二次生成比例 |
| average_review_time | 评审完成耗时 / 候选用例数 | 人工成本 |
| execution_pass_rate | 后续执行通过用例数 / 已执行 AI 用例数 | 运行质量 |
| defect_detection_count | AI 用例发现缺陷数 | 测试价值 |
| requirement_trace_rate | 有需求引用用例数 / 候选用例数 | 可追溯性 |

### 5.1 用例质量分级

| 等级 | 条件 | 解释 |
|---|---|---|
| A | 接受率高、编辑率低、执行通过率高、重复率低 | Prompt/Skill 可稳定复用 |
| B | 接受率中等、编辑率较高 | 可用但需要优化输出格式或测试深度 |
| C | 驳回率高或重复率高 | 需要重写 Prompt/Skill |
| D | schema 经常失败或不可执行 | 禁止作为默认版本 |

### 5.2 第一版建议阈值

这些阈值不是上线硬阻塞，但用于评审 AI 效果：

| 指标 | 建议目标 |
|---|---|
| schema_valid_rate | >= 95% |
| field_complete_rate | >= 90% |
| duplicate_rate | <= 20% |
| acceptance_rate + edited_acceptance_rate | >= 60% |
| rejection_rate | <= 30% |
| requirement_trace_rate | >= 90% |

## 6. 单测生成指标

| 指标 | 公式/来源 | 用途 |
|---|---|---|
| patch_generated_count | 生成 patch 数 | 产出规模 |
| patch_scope_pass_rate | 通过路径门禁 patch 数 / patch 数 | 安全性 |
| patch_apply_rate | 成功应用 patch 数 / 通过门禁 patch 数 | 可应用性 |
| syntax_pass_rate | 语法检查通过 patch 数 / 应用 patch 数 | 基础质量 |
| new_test_pass_rate | 新增测试通过数 / 新增测试总数 | 单测质量 |
| regression_pass_rate | 回归通过数 / 回归执行数 | 变更安全 |
| coverage_delta | 新覆盖率 - 基线覆盖率 | 覆盖改善 |
| human_patch_edit_rate | 人工编辑 patch 数 / patch 数 | 生成可用性 |
| patch_rejection_rate | 拒绝 patch 数 / patch 数 | 无效产出比例 |

第一版如果覆盖率工具未配置，可以把 coverage_delta 标记为 `not_collected`，不能伪造。

## 7. 回归选择指标

| 指标 | 公式/来源 | 用途 |
|---|---|---|
| selected_test_count | 推荐测试数量 | 回归规模 |
| selection_reason_coverage | 有明确选择原因的测试数 / 推荐测试数 | 可解释性 |
| regression_runtime | 回归执行耗时 | 效率 |
| failure_hit_count | 推荐回归中发现失败数量 | 有效性 |
| manual_added_test_count | 用户额外添加测试数 | AI 遗漏程度 |
| full_regression_fallback_count | 触发全量回归次数 | 风险兜底频率 |

V1 不强求自动计算“遗漏率”，但必须记录用户手动追加的测试命令和原因。

## 8. 工具执行指标

| 指标 | 来源 | 用途 |
|---|---|---|
| tool_invocation_count | ToolInvocation | 工具使用量 |
| tool_success_rate | 成功调用数 / 总调用数 | 稳定性 |
| tool_timeout_rate | 超时数 / 总调用数 | 配置合理性 |
| artifact_parse_rate | 成功解析 artifact 数 / artifact 总数 | 报告能力 |
| approval_block_count | 被审批拒绝的高风险调用数 | 安全风险 |

按工具拆分：TestRunner、Playwright、ChangeSetTool、ArtifactTool。Newman 和 JMeter 接入后复用同一指标。

## 9. 失败归因指标

| 指标 | 公式/来源 | 用途 |
|---|---|---|
| analyzed_failure_count | 失败归因任务数 | 使用量 |
| evidence_complete_rate | 有 stdout/stderr/JUnit/trace 等证据的归因数 / 归因数 | 证据完整性 |
| classification_accuracy | 用户确认正确分类数 / 已反馈归因数 | 归因准确性 |
| unresolved_failure_rate | 未能归因失败数 / 失败数 | Agent 能力缺口 |
| fix_suggestion_acceptance_rate | 用户采纳建议数 / 建议数 | 建议价值 |

第一版用人工反馈按钮记录：准确、不准确、部分准确、无证据。

## 10. 报告质量指标

| 指标 | 来源 | 用途 |
|---|---|---|
| report_generated_count | Report | 报告产出量 |
| report_regeneration_rate | 重新生成次数 / 报告数 | 首次报告质量 |
| evidence_link_rate | 有证据链接结论数 / 总结论数 | 可追溯性 |
| manual_report_edit_rate | 人工编辑报告数 / 报告数 | 报告可用性 |
| decision_clear_rate | 有明确通过/不通过/需人工判断结论报告数 / 报告数 | 决策价值 |

## 11. 数据事件模型

建议第一版保留事件表或指标表，至少记录以下事件：

```text
ai_task_created
ai_task_succeeded
ai_task_failed
requirement_issue_accepted
requirement_issue_edited
case_candidate_generated
case_candidate_approved
case_candidate_approved_after_edit
case_candidate_rejected
case_candidate_optimization_requested
unit_test_patch_generated
unit_test_patch_approved
unit_test_patch_rejected
tool_invocation_started
tool_invocation_finished
failure_analysis_feedback_submitted
report_generated
report_edited
```

事件字段：

```text
event_type
project_id
entity_type
entity_id
batch_id
agent_name
prompt_version
skill_version
model_name
created_at
payload_json
```

## 12. 指标展示页面

V1 在主证据闭环可运行后至少提供三个视图。V0.1 和早期 Slice
只需要先把指标事件和字段持久化，不要为了完整指标看板阻塞
Project -> ContextArtifact -> Mock AITask -> artifacts -> pytest -> report
证据闭环。

### 12.1 用例生成批次指标

- 生成数量。
- 采纳率。
- 编辑后采纳率。
- 驳回率。
- 重复率。
- 字段完整率。
- 评审进度。

### 12.2 Prompt/Skill 效果视图

- 按 Prompt 版本比较采纳率。
- 按 Skill 版本比较 schema 通过率。
- 按模型比较平均耗时、token、失败率。

### 12.3 CI/CD 质量中心指标

- patch 生成数。
- patch 应用成功率。
- 新增测试通过率。
- 回归通过率。
- 失败归因准确反馈。

## 13. 指标驱动优化规则

- schema_valid_rate 低：优先修 Prompt 输出 schema 和解析器。
- duplicate_rate 高：增加已有用例检索和重复检测策略。
- acceptance_rate 低：优化测试设计 Skill，而不是只换模型。
- patch_scope_pass_rate 低：收紧 UnitTestAgent 的禁止事项。
- new_test_pass_rate 低：加强测试框架识别和 fixture 学习。
- failure_analysis_accuracy 低：补充 artifact 解析和分类规则。

## 14. 第一版验收标准

- 每个 AI Task 都记录 prompt_version、skill_version、model、输入输出 artifact。
- 用例生成批次能展示采纳率、驳回率、修改率、重复率、字段完整率；在完整页面完成前，后端必须已记录可计算这些指标的事件。
- CI/CD 质量中心能展示 patch 应用率、新增测试通过率、回归通过率；CI/CD 质量中心未进入主线前，不阻塞 V0.1 或需求到自动化主闭环。
- 失败归因支持用户反馈准确性。
- Report Center 能展示报告是否有证据链。
