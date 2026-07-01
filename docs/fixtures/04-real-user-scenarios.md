# Real User Scenario Samples

## 1. Purpose

This fixture keeps V1 grounded in real tester work instead of only internal
product loops. Each scenario names the input material, the user's goal, and the
evidence Chtest must produce.

These scenarios do not replace `00-v1-demo-path.md`. They make the Golden Path
more realistic by showing how different users recognize value.

## 2. Scenario A: API Test Engineer

### User

API test engineer responsible for checkout and coupon interfaces.

### Input Material

- Requirement text: "Users can apply a coupon on the checkout page. Expired,
  disabled, or already-used coupons cannot reduce the payable amount."
- ContextArtifact: `coupon-api-notes.md` with endpoint notes for
  `POST /api/coupons/validate`.
- OpenAPI snippet for request and response fields.
- Existing pytest command: `pytest tests/api -q --junitxml=artifacts/junit.xml`.
- Local sample repository under an allowlisted path.

### User Goal

Turn an ambiguous coupon requirement into reviewable API cases and one approved
pytest automation draft, then run the draft and understand whether the evidence
supports the result.

### Chtest Evidence Output

- RequirementReview with six-dimension scores and explicit ambiguity questions.
- RiskItem records for expired, disabled, reused, missing, and boundary-value
  coupon scenarios.
- GeneratedCaseCandidate records with steps, expected results, input data, and
  requirement/risk references.
- CaseReviewSession decisions showing at least one approved or edited-approved
  case.
- AutomationDraft for pytest with suggested file path, draft code, execution
  notes, and risk notes.
- TestRun with stdout, stderr, JUnit or parsed result artifact, runner mode,
  runtime manifest, dependency snapshot, and environment snapshot.
- Report with `evidence_manifest.json` linking the conclusion to artifacts.

### Related V1 Mainline

Requirement -> AI requirement review -> AI case generation -> human review ->
AutomationDraft -> approved execution -> evidence report.

## 3. Scenario B: Web Automation Engineer

### User

Web automation engineer maintaining checkout smoke tests.

### Input Material

- Approved TestCase: "Expired coupon cannot submit checkout order."
- ContextArtifact: checkout page selectors and test account notes.
- Playwright smoke command: `npx playwright test tests/checkout --reporter=junit`.
- Existing UI screenshots or trace artifacts from a failed manual run.

### User Goal

Generate a Playwright automation draft from an approved case, review it before
execution, and collect evidence that explains whether the browser flow passed or
failed.

### Chtest Evidence Output

- AutomationDraft with target framework `playwright`, TypeScript draft code,
  suggested path, dependency assumptions, selector assumptions, and risk notes.
- Human approval record before execution.
- ToolInvocation linked to the approved draft and the configured Playwright
  command.
- TestRun with parsed result, stdout, stderr, trace zip, screenshot, runtime
  manifest, dependency snapshot, and environment snapshot when available.
- FailureAnalysis with classification `test_script_issue`,
  `environment_issue`, `product_defect`, or `insufficient_evidence`.
- Report that shows browser evidence before AI explanation.

### Related V1 Mainline

Reviewed case -> AutomationDraft -> approval -> Playwright smoke execution ->
failure analysis -> evidence report.

## 4. Scenario C: Backend Engineer Adding Unit Tests

### User

Backend engineer who changed coupon validation logic and wants fast regression
confidence before opening a pull request.

### Input Material

- Local Git diff for files such as `src/coupons/validator.py`.
- Existing unit tests under `tests/unit/`.
- Test command: `pytest tests/unit -q --junitxml=artifacts/junit.xml`.
- ContextArtifact: short business rule note for coupon expiration and reuse.

### User Goal

Ask Chtest to analyze the local change, propose a unit test patch only under the
test directory, review the patch, apply it after approval, and run regression
with evidence.

### Chtest Evidence Output

- CICDRun and CICDChangedFile records with changed file summary.
- CI/CD risk analysis naming affected coupon validation behavior.
- UnitTestPatch with test intent, coverage target, unified diff, and risk notes.
- PatchScopeGate result proving only test files are modified.
- Human approval record before patch application.
- TestRun with pytest result artifacts and parsed pass/fail status.
- CI/CD quality report that links diff, patch, scope gate, and regression result.

### Related V1 Mainline

Local Git diff -> AI risk analysis -> UnitTestPatch -> review -> pytest
regression -> CI/CD quality report.

## 5. How To Use These Scenarios

- Use Scenario A as the default V1 product demo input.
- Use Scenario B after the pytest loop is stable and Playwright execution starts.
- Use Scenario C only after the requirement-to-automation mainlines are already
  moving; CI/CD Quality remains a support workflow in V1.
