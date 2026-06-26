# Golden Path: CI/CD Quality

## 1. 目的

本 fixture 用于验证 Chtest V1 支线 C：CI/CD 到质量。CI/CD Quality Center 在 V1 是支线能力，但必须满足用户“push/diff 后补单测和回归”的明确诉求。

## 2. 输入 diff

```diff
diff --git a/src/coupon.py b/src/coupon.py
index 1111111..2222222 100644
--- a/src/coupon.py
+++ b/src/coupon.py
@@ -10,6 +10,8 @@ def apply_coupon(order_total, coupon):
     if coupon.status == 'expired':
         return ApplyResult(False, 'COUPON_EXPIRED', order_total)
+    if coupon.amount > order_total:
+        return ApplyResult(False, 'COUPON_AMOUNT_EXCEEDS_ORDER_TOTAL', order_total)
     return ApplyResult(True, None, order_total - coupon.amount)
```

项目信息：

```json
{
  "repository": "/Users/yanchen/VscodeProject/sample-checkout",
  "base_ref": "main",
  "head_ref": "HEAD",
  "test_command": "pytest tests -q --junitxml=artifacts/junit.xml"
}
```

## 3. 期望 CICDChangeAnalysisAgent 输出

```json
{
  "summary": "优惠券应用逻辑新增金额超过订单总额时的阻断分支。",
  "overall_risk": "medium",
  "impacted_modules": ["coupon", "checkout"],
  "changed_files": [
    {
      "path": "src/coupon.py",
      "file_role": "source",
      "risk_level": "medium",
      "risk_reasons": ["新增业务分支", "需要补充分支覆盖"]
    }
  ],
  "test_recommendations": [
    {
      "type": "unit",
      "target": "tests/test_coupon.py",
      "reason": "新增 coupon.amount > order_total 分支需要单测覆盖"
    }
  ]
}
```

## 4. 期望 UnitTestPatch

```diff
diff --git a/tests/test_coupon.py b/tests/test_coupon.py
index 3333333..4444444 100644
--- a/tests/test_coupon.py
+++ b/tests/test_coupon.py
@@ -20,3 +20,12 @@ def test_expired_coupon_is_rejected():
     assert result.success is False
     assert result.error_code == 'COUPON_EXPIRED'
+
+
+def test_coupon_amount_cannot_exceed_order_total():
+    coupon = Coupon(status='active', amount=120)
+
+    result = apply_coupon(order_total=100, coupon=coupon)
+
+    assert result.success is False
+    assert result.error_code == 'COUPON_AMOUNT_EXCEEDS_ORDER_TOTAL'
+    assert result.final_total == 100
```

Patch 说明：

```json
{
  "target_framework": "pytest",
  "test_intent": "覆盖优惠券金额大于订单总额的新分支",
  "coverage_target": ["src/coupon.py apply_coupon coupon.amount > order_total"],
  "risk_notes": ["patch 只修改 tests/test_coupon.py"]
}
```

## 5. PatchScopeGate 期望

```json
{
  "allowed": true,
  "checked_paths": ["tests/test_coupon.py"],
  "blocked_paths": [],
  "forbidden_patterns": [],
  "risk_level": "low"
}
```

如果 patch 修改 `src/coupon.py`，期望：

```json
{
  "allowed": false,
  "blocked_paths": ["src/coupon.py"],
  "reason": "V1 UnitTestPatch may only modify test directories"
}
```

## 6. 期望测试执行

新增测试命令：

```text
pytest tests/test_coupon.py -q --junitxml=artifacts/junit.xml
```

回归命令：

```text
pytest tests -q --junitxml=artifacts/junit.xml
```

期望 TestRun：

```json
{
  "status": "passed",
  "exit_code": 0,
  "parsed_result": {
    "total": 8,
    "passed": 8,
    "failed": 0
  }
}
```

## 7. 期望 CI/CD Quality Report

```json
{
  "report_type": "cicd_quality",
  "conclusion": "passed",
  "summary": "本次变更新增优惠券金额边界分支，已生成并执行对应 pytest 单测，相关回归通过。",
  "metrics": {
    "changed_files": 1,
    "unit_test_patch_generated": true,
    "patch_scope_passed": true,
    "new_tests_passed": true,
    "regression_passed": true
  },
  "risks": [],
  "evidence": ["diff.patch", "unit_test.patch", "junit.xml", "stdout.log"]
}
```

## 8. 验收标准

- CICDRun 能保存 diff 和 changed files。
- CICDChangeAnalysisAgent 能识别 source 文件和新增分支风险。
- UnitTestPatch 只修改测试目录。
- PatchScopeGate 能阻止业务源码修改。
- 用户审批后才能应用 patch。
- 新增测试和回归测试都能生成 TestRun。
- CICDQualityReport 结论引用 evidence。
