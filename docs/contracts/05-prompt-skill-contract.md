# Chtest Prompt And Skill Contract

## 1. 文档目的

本文定义 PromptVersion 和 SkillVersion 的文件格式、版本规则、输出约束和质量门禁。Chtest 的 AI 能力必须可追溯、可复盘、可比较，不能依赖临时口头提示词。

## 2. Prompt 目录

```text
prompts/
  requirement_review/v1.md
  risk_matrix/v1.md
  case_generation/v1.md
  case_review/v1.md
  automation_draft_generation/v1.md
  cicd_change_analysis/v1.md
  unit_test_generation/v1.md
  regression_selection/v1.md
  tool_execution/v1.md
  failure_analysis/v1.md
  report_generation/v1.md
```

## 3. Skill 目录

```text
skills/
  requirement-review-skill/v1.md
  test-case-generation-skill/v1.md
  testcase-review-skill/v1.md
  automation-draft-skill/v1.md
  unit-test-generation-skill/v1.md
  regression-selection-skill/v1.md
  tool-execution-skill/v1.md
  failure-analysis-skill/v1.md
  report-generation-skill/v1.md
```

## 4. Prompt 文件格式

每个 Prompt 文件必须包含以下段落：

```markdown
# Prompt: requirement_review v1

## Agent
RequirementReviewAgent

## Purpose
Generate six-dimensional requirement review output.

## Input Schema
```json
{"type":"object","required":["requirement"],"properties":{"requirement":{"type":"string"}}}
```

## Output Schema
```json
{"type":"object","required":["scores","issues"],"properties":{"scores":{"type":"object"},"issues":{"type":"array"}}}
```

## Instructions
Return JSON only. Do not include markdown fences in the model output.

## Failure Output
{"error_code":"UNABLE_TO_REVIEW","message":"reason","recoverable":true}
```

规则：

- 主输出必须是 JSON。
- 不允许把自由散文作为主结果。
- 输出 schema 必须能被后端校验。
- Prompt 内容变化必须生成新 hash。
- 已发布版本不能覆盖。

## 4.1 Context Input Contract

RequirementReviewAgent and CaseGenerationAgent may receive local ContextArtifacts.

Prompt input must include:

```json
{
  "use_knowledge": false,
  "context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
  "context_manifest": [
    {
      "artifact_id": "00000000-0000-0000-0000-000000000371",
      "title": "coupon-api-notes.md",
      "mime_type": "text/markdown",
      "sha256": "sha256:example",
      "redaction_applied": false
    }
  ]
}
```

Rules:

- `use_knowledge=false` means external RAG/KnowledgeAdapter is disabled.
- ContextArtifact content is still available to the prompt when `context_artifact_ids` is non-empty.
- Prompt input artifacts must save `context_manifest.json`.
- Model output or parsed AITask output must expose `used_context_artifact_ids`.
- Model output must not claim external evidence when `used_knowledge=false`.

## 5. Skill 文件格式

每个 Skill 文件必须包含以下段落：

```markdown
# Skill: test-case-generation-skill v1

## Applies To
- CaseGenerationAgent

## Methodology
- Equivalence partitioning
- Boundary value analysis
- State transition testing
- Error guessing

## Input Contract
Describe accepted input fields.

## Output Contract
Describe required output fields.

## Quality Gates
- Every case must have explicit expected result.
- Every case must reference requirement text.

## Forbidden Actions
- Do not create vague cases like "verify it works".
- Do not skip negative scenarios for P0/P1 flows.

## Tool Permissions
- KnowledgeAdapter.search_context optional.
```

## 6. V1 Prompt/Skill 映射

| 流程 | Agent | Prompt | Skill |
|---|---|---|---|
| 需求评审 | RequirementReviewAgent | requirement_review:v1 | requirement-review-skill:v1 |
| 风险矩阵 | RequirementReviewAgent | risk_matrix:v1 | requirement-review-skill:v1 |
| 用例生成 | CaseGenerationAgent | case_generation:v1 | test-case-generation-skill:v1 |
| 用例评审 | CaseReviewAgent | case_review:v1 | testcase-review-skill:v1 |
| 自动化草稿 | AutomationDraftAgent | automation_draft_generation:v1 | automation-draft-skill:v1 |
| CI/CD 变更分析 | CICDChangeAnalysisAgent | cicd_change_analysis:v1 | regression-selection-skill:v1 |
| 单测 patch | UnitTestAgent | unit_test_generation:v1 | unit-test-generation-skill:v1 |
| 回归选择 | RegressionAgent | regression_selection:v1 | regression-selection-skill:v1 |
| 工具执行计划 | ToolExecutionAgent | tool_execution:v1 | tool-execution-skill:v1 |
| 失败归因 | FailureAnalysisAgent | failure_analysis:v1 | failure-analysis-skill:v1 |
| 报告生成 | ReportAgent | report_generation:v1 | report-generation-skill:v1 |

## 7. 输出 JSON 约束

### 7.1 用例生成输出

```json
{
  "cases": [
    {
      "title": "过期优惠券不可提交订单",
      "priority": "P0",
      "test_type": "functional",
      "precondition": "存在一张已过期优惠券",
      "steps": ["登录", "进入结算页", "选择过期优惠券", "提交订单"],
      "expected_results": ["系统阻止提交", "展示错误提示"],
      "input_data": {"coupon_status": "expired"},
      "requirement_refs": ["过期优惠券不可使用"],
      "risk_refs": ["RISK-001"],
      "ai_reason": "覆盖优惠券有效期边界"
    }
  ]
}
```

### 7.2 AutomationDraft 输出

```json
{
  "drafts": [
    {
      "target_framework": "pytest",
      "title": "test_expired_coupon_cannot_checkout",
      "suggested_file_path": "tests/test_coupon_checkout.py",
      "draft_language": "python",
      "draft_code": "def test_expired_coupon_cannot_checkout():\n    assert True",
      "execution_notes": ["需要替换为真实 fixture"],
      "risk_notes": ["草稿不能直接写入业务仓库"]
    }
  ]
}
```

### 7.3 UnitTestPatch 输出

```json
{
  "patch": "diff --git a/tests/test_coupon.py b/tests/test_coupon.py\n...",
  "target_framework": "pytest",
  "test_intent": "cover expired coupon rejection",
  "coverage_target": ["coupon validation branch"],
  "risk_notes": ["patch only modifies tests/"]
}
```

### 7.4 RegressionPlan 输出

```json
{
  "recommended_test_command_ids": ["00000000-0000-0000-0000-000000000302"],
  "reasons": ["Changed source branch is covered by pytest unit command."],
  "risk_coverage": ["src/coupon.py coupon.amount > order_total"],
  "needs_review": false
}
```

### 7.5 Report 输出

```json
{
  "conclusion": "passed",
  "summary": "Patch scope, new tests, and regression passed with evidence.",
  "metrics": {"new_tests_passed": true, "regression_passed": true},
  "evidence_artifact_ids": ["00000000-0000-0000-0000-000000001601"],
  "next_actions": []
}
```

## 8. 质量门禁

| 输出 | 门禁 |
|---|---|
| RequirementReview | 必须包含六维评分和至少一个测试设计建议 |
| GeneratedCaseCandidate | 必须有步骤、预期、需求引用、AI 理由 |
| AutomationDraft | 必须标明 target_framework、suggested_file_path、draft_code |
| UnitTestPatch | 必须通过 PatchScopeGate，不能修改业务源码 |
| RegressionPlan | 每个推荐命令必须有 reason |
| FailureAnalysis | 无证据时必须返回 insufficient_evidence |
| Report | 每个结论必须引用 artifact 或结构化指标 |

## 9. 版本与指标

每次 AI Task 必须记录：

- prompt_name。
- prompt_version。
- prompt_hash。
- skill_name。
- skill_version。
- skill_hash。
- model_provider。
- model_name。
- schema_valid。
- quality_gate_result。

指标按 PromptVersion 和 SkillVersion 聚合：采纳率、编辑率、驳回率、schema 通过率、执行通过率、失败率、平均 token、平均耗时。
