# Golden Path: Case To Playwright And Pytest

## 1. Purpose

This fixture verifies Chtest V1 Mainline B: reviewed case to automation execution. V1 does not build a complete low-code UI automation platform. It must prove that AI can generate an AutomationDraft, the user can review and approve it, and the approved draft can be executed through pytest or Playwright with artifacts and reports.

## 2. Input Test Case

```json
{
  "test_case_id": "00000000-0000-0000-0000-000000000901",
  "title": "Expired coupon cannot be used during checkout",
  "priority": "P0",
  "test_type": "ui",
  "precondition": "The user has one expired coupon",
  "steps": ["Login", "Open checkout", "Open coupon list", "Try selecting expired coupon", "Submit order"],
  "expected_results": ["Expired coupon is unavailable or submit fails", "The page shows coupon expired message"],
  "input_data": {"coupon_status": "expired"}
}
```

## 3. Expected Playwright AutomationDraft

```json
{
  "target_framework": "playwright",
  "title": "expired coupon cannot be used at checkout",
  "suggested_file_path": "tests/e2e/checkout-expired-coupon.spec.ts",
  "draft_language": "typescript",
  "draft_code": "import { test, expect } from '@playwright/test';

test('expired coupon cannot be used at checkout', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Username').fill('coupon_user');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Login' }).click();
  await page.goto('/checkout');
  await expect(page.getByText('Expired coupon')).toBeVisible();
  await page.getByText('Expired coupon').click();
  await expect(page.getByText('Coupon expired')).toBeVisible();
});
",
  "execution_notes": ["Test environment must provide coupon_user and an expired coupon", "baseURL is read from Playwright config"],
  "risk_notes": ["The user must verify locators against the real page"]
}
```

## 4. Expected Pytest AutomationDraft

```json
{
  "target_framework": "pytest",
  "title": "test_expired_coupon_cannot_be_applied",
  "suggested_file_path": "tests/test_coupon_checkout.py",
  "draft_language": "python",
  "draft_code": "def test_expired_coupon_cannot_be_applied(coupon_service, order_factory):
    order = order_factory(total_amount=100)
    expired_coupon = coupon_service.create_coupon(amount=20, status='expired')

    result = coupon_service.apply_coupon(order_id=order.id, coupon_id=expired_coupon.id)

    assert result.success is False
    assert result.error_code == 'COUPON_EXPIRED'
",
  "execution_notes": ["coupon_service and order_factory are example fixtures and must be mapped by the user"],
  "risk_notes": ["AI generates a draft only and does not write into the target repository"]
}
```

## 5. Human Review Expectation

| Draft | Required action | Expected state flow | Reason |
|---|---|---|---|
| Playwright draft | edit then approve | draft_generated -> under_review -> edited -> approved | Locators usually need real page adjustment |
| Pytest draft | approve | draft_generated -> under_review -> approved | Service-level fixtures can be clear enough to run |

AutomationDraft does not use `approve_after_edit`. That action is reserved for GeneratedCaseCandidate review.

## 6. Execution Input

`POST /api/test-runs`

```json
{
  "project_id": "00000000-0000-0000-0000-000000000101",
  "automation_draft_id": "00000000-0000-0000-0000-000000001001",
  "test_command_id": "00000000-0000-0000-0000-000000000302",
  "reason": "execute approved pytest automation draft"
}
```

## 7. Expected Execution Result

```json
{
  "status": "passed",
  "exit_code": 0,
  "parsed_result": {
    "total": 1,
    "passed": 1,
    "failed": 0,
    "skipped": 0,
    "error": 0
  },
  "artifacts": [
    {"artifact_type": "stdout"},
    {"artifact_type": "junit"}
  ]
}
```

If execution fails, Chtest must create FailureAnalysis:

```json
{
  "classification": "test_script_issue",
  "evidence_artifact_ids": ["stderr.log", "junit.xml"],
  "summary": "pytest fixture coupon_service is not defined.",
  "root_cause": "The draft references a fixture that is not available in the target project.",
  "suggested_actions": ["Map coupon_service to an existing fixture", "Edit AutomationDraft before rerun"]
}
```

## 8. Acceptance Criteria

- AutomationDraft generation creates `draft_generated` state.
- Unapproved AutomationDraft cannot create TestRun.
- `edit -> edited -> approve -> approved` is supported.
- Approved AutomationDraft can create TestRun.
- TestRun saves stdout/stderr/JUnit or Playwright trace/screenshot.
- Passed and failed runs can both generate `automation_execution` reports.
- AI does not directly write business source files.
