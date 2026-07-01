# V1 Manual Walkthrough

Date: 2026-06-30

## Purpose

This walkthrough is the human-readable release companion for the automated V1
golden suite. It follows the same product proof as
`docs/fixtures/00-v1-demo-path.md` without replacing automated acceptance.

## Walkthrough Outline

### 1. Project And Context Setup

Goal:

- Confirm the workbench has enough local project context to make AI output
  traceable.

Checklist:

- Create or open the local project.
- Confirm the module is present for the checkout/coupon domain.
- Confirm repository, environment, and TestCommand configuration.
- Confirm ContextArtifact inventory includes project context such as
  `coupon-api-notes.md`.

Expected evidence:

- Project settings are visible.
- ContextArtifact metadata includes title, MIME type, hash/safety metadata, and
  prompt eligibility.

### 2. Requirement Review And Context Usage

Goal:

- Confirm requirement analysis is evidence-backed and context-aware.

Checklist:

- Submit the coupon requirement.
- Review RequirementReview output.
- Confirm risk items and scoring are visible.
- Confirm context usage is traceable through `context_artifact_ids`.
- Confirm `used_knowledge=false` unless KnowledgeAdapter is explicitly
  configured in a later release.

Expected evidence:

- RequirementReview references PromptVersion, SkillVersion, model provider, and
  model name.
- Related AITask has succeeded status and context references.

### 3. Candidate Case Generation And Human Approval

Goal:

- Confirm AI-generated cases cannot bypass human review.

Checklist:

- Generate case candidates from the reviewed requirement.
- Review candidate details, risks, expected results, and coverage.
- Approve at least one candidate into the TestCase library.
- Check rejected or edited cases remain review-visible.

Expected evidence:

- Approved TestCase exists in the library.
- Case quality metrics can report acceptance/edit/rejection signals.

### 4. AutomationDraft Review And Approval

Goal:

- Confirm generated automation remains review-gated before execution.

Checklist:

- Generate an AutomationDraft from an approved TestCase.
- Review draft code, suggested file path, execution notes, and risk notes.
- Edit notes or code when needed.
- Approve the draft before any execution.

Expected evidence:

- AutomationDraft status moves from generated/edited to approved.
- Runtime artifact fields remain empty until execution.

### 5. pytest Execution Evidence

Goal:

- Confirm approved automation produces controlled runner evidence.

Checklist:

- Execute the approved pytest draft through the controlled runner path.
- Confirm TestRun status, parsed result, TestResult, stdout/stderr, and runtime
  manifest evidence.
- Confirm repository readonly and network-disabled sandbox metadata.
- Confirm execution artifacts are linked to the TestRun.

Expected evidence:

- TestRun status is passed or failed with parsed result.
- Runtime manifest and stdout/stderr artifacts are present.
- Runner mode, readonly setting, and network setting are visible.

### 6. Failure Analysis And Report Evidence

Goal:

- Confirm reports do not make unsupported claims.

Checklist:

- Review failure analysis when a failed TestRun exists.
- Generate an automation execution report.
- Confirm the report includes evidence manifest, artifact references, and a
  conclusion backed by evidence.
- Confirm missing evidence is explicit when evidence is unavailable.

Expected evidence:

- FailureAnalysis links to TestRun/TestResult and evidence artifacts.
- Report status is ready only when evidence manifest exists.
- Report conclusion matches evidence.

### 7. CI/CD Quality Center Support Workflow

Goal:

- Confirm local code-change support can produce reviewable quality evidence
  without acting as a remote CI/CD platform.

Checklist:

- Create a local diff CICDRun.
- Review changed file risk analysis.
- Generate and review UnitTestPatch.
- Confirm PatchScopeGate blocks business-source patch application.
- Run new-test and regression evidence.
- Review QualityGateDecision and CI/CD quality report.

Expected evidence:

- CICDRun has changed files and risk analysis artifacts.
- UnitTestPatch is reviewed before application.
- QualityGateDecision links to test/regression evidence.

### 8. Extension Surfaces

Goal:

- Confirm extension points are visible without expanding V1 runtime scope.

Checklist:

- Open RAG 知识库 and confirm it is a ContextArtifact and KnowledgeAdapter
  management surface.
- Review MCP-ready ToolDefinition metadata.
- Confirm there is no RAG runtime, vector index, MCP runtime, RBAC, tenants, or
  permissions behavior in V1.

Expected evidence:

- KnowledgeAdapter state is explicit.
- ToolDefinition readiness/schema metadata is visible.
- No vector/RAG/MCP runtime behavior is required for acceptance.

## Release Acceptance Cross-Check

Before publishing release notes, run or reference:

```bash
backend/.venv/bin/python -m pytest backend/app/tests/golden/test_requirement_to_case.py backend/app/tests/golden/test_requirement_to_case_metrics.py backend/app/tests/golden/test_test_case_library_golden.py backend/app/tests/golden/test_automation_draft_golden.py backend/app/tests/golden/test_testrunner_pytest_golden.py backend/app/tests/golden/test_playwright_minimal_loop_golden.py backend/app/tests/golden/test_report_failure_analysis_golden.py backend/app/tests/golden/test_cicd_quality_center_golden.py backend/app/tests/golden/test_unit_test_patch_regression_golden.py backend/app/tests/golden/test_extension_surface_golden.py -q
npm --prefix frontend run test -- --run
git diff --check
```

Expected recorded release result:

- Backend golden suite: `10 passed`.
- Frontend suite: `14` test files passed, `17` tests passed.
- Diff check: clean.

## Optional Screenshots

Store optional screenshots under `docs/release/v1/screenshots/`.

Suggested pages:

- AI 工作台.
- 需求评审.
- 用例库.
- 执行中心.
- CI/CD 质量中心.
- 报告中心.
- RAG 知识库.
