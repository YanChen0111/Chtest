# Golden Path: Requirement To Case

## 1. 目的

本 fixture 用于验证 Chtest V1 主线 A：需求到用例。后续实现 RequirementReviewAgent、CaseGenerationAgent、Case Review 页面和 API 时，必须能跑通本示例。

## 2. 输入需求

```markdown
# 优惠券结算规则

用户在提交订单时，可以选择一张可用优惠券。优惠券不可与积分同时使用。过期优惠券不可使用。优惠券金额不能超过订单应付金额。提交订单后，系统需要展示优惠后的最终支付金额。
```

项目信息：

```json
{
  "project": "Checkout System",
  "module": "订单结算",
  "target_test_types": ["functional", "ui"]
}
```

## 3. 期望需求评审输出

```json
{
  "overall_score": 82,
  "scores": {
    "completeness": 78,
    "clarity": 85,
    "consistency": 88,
    "testability": 84,
    "feasibility": 82,
    "logic": 75
  },
  "issues": [
    {
      "type": "missing_boundary",
      "severity": "medium",
      "text": "未说明优惠券金额等于订单应付金额时是否允许支付金额为 0"
    },
    {
      "type": "missing_rule",
      "severity": "medium",
      "text": "未说明优惠券最低消费门槛和适用商品范围"
    }
  ],
  "clarification_questions": [
    "优惠券是否可以与平台活动叠加？",
    "优惠券金额等于订单应付金额时是否允许提交？"
  ],
  "risk_items": [
    {
      "title": "优惠券与积分互斥规则",
      "risk_level": "high",
      "suggestion": "覆盖同时选择优惠券和积分时的提交阻断"
    },
    {
      "title": "优惠券金额超过应付金额",
      "risk_level": "high",
      "suggestion": "覆盖优惠券金额大于订单金额时的金额计算和错误提示"
    }
  ]
}
```

## 4. 期望候选用例

至少生成以下 5 条候选用例：

```json
{
  "cases": [
    {
      "title": "可用优惠券可成功抵扣订单金额",
      "priority": "P0",
      "test_type": "functional",
      "precondition": "用户存在一张未过期且满足使用条件的优惠券",
      "steps": ["登录用户账号", "创建包含可用商品的订单", "进入结算页", "选择可用优惠券", "提交订单"],
      "expected_results": ["订单提交成功", "最终支付金额等于订单应付金额减优惠券金额"],
      "requirement_refs": ["用户在提交订单时，可以选择一张可用优惠券"],
      "ai_reason": "覆盖优惠券主流程"
    },
    {
      "title": "优惠券不可与积分同时使用",
      "priority": "P0",
      "test_type": "functional",
      "precondition": "用户同时拥有可用优惠券和可用积分",
      "steps": ["进入结算页", "选择优惠券", "选择积分抵扣", "提交订单"],
      "expected_results": ["系统阻止同时使用", "页面提示优惠券不可与积分同时使用"],
      "requirement_refs": ["优惠券不可与积分同时使用"],
      "ai_reason": "覆盖互斥规则"
    },
    {
      "title": "过期优惠券不可用于结算",
      "priority": "P0",
      "test_type": "functional",
      "precondition": "用户存在一张已过期优惠券",
      "steps": ["进入结算页", "查看优惠券列表", "尝试选择已过期优惠券", "提交订单"],
      "expected_results": ["已过期优惠券不可选或提交失败", "页面提示优惠券已过期"],
      "requirement_refs": ["过期优惠券不可使用"],
      "ai_reason": "覆盖有效期边界"
    },
    {
      "title": "优惠券金额不能超过订单应付金额",
      "priority": "P1",
      "test_type": "functional",
      "precondition": "订单应付金额小于优惠券金额",
      "steps": ["进入结算页", "选择金额大于订单应付金额的优惠券", "提交订单"],
      "expected_results": ["系统按规则阻断或限制抵扣", "最终支付金额不会为负数"],
      "requirement_refs": ["优惠券金额不能超过订单应付金额"],
      "ai_reason": "覆盖金额边界"
    },
    {
      "title": "提交订单后展示优惠后的最终支付金额",
      "priority": "P1",
      "test_type": "ui",
      "precondition": "用户选择一张可用优惠券",
      "steps": ["进入结算页", "选择优惠券", "提交订单", "查看订单确认页"],
      "expected_results": ["订单确认页展示优惠后的最终支付金额", "金额与结算页一致"],
      "requirement_refs": ["系统需要展示优惠后的最终支付金额"],
      "ai_reason": "覆盖 UI 展示一致性"
    }
  ]
}
```

## 5. 人工评审期望

评审动作：

| 用例 | 动作 | 原因 |
|---|---|---|
| 可用优惠券可成功抵扣订单金额 | approve | 主流程完整 |
| 优惠券不可与积分同时使用 | approve | 高风险互斥规则 |
| 过期优惠券不可用于结算 | approve_after_edit | 补充测试数据准备 |
| 优惠券金额不能超过订单应付金额 | needs_optimization | 需求未明确阻断或限制抵扣策略 |
| 展示优惠后的最终支付金额 | approve | UI 展示可测 |

## 6. 验收标准

- RequirementReview 六维评分存在。
- RiskItem 至少 2 条。
- GeneratedCaseCandidate 至少 5 条。
- 每条候选用例都有 steps、expected_results、requirement_refs、ai_reason。
- 评审后至少 4 条进入 TestCase 或优化流程。
- 批次指标能计算 generated_count、approved_count、edited_count、optimization_count、acceptance_rate。
