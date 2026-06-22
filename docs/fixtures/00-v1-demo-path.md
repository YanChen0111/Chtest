# Golden Path: V1 Minimum Demo

## 1. Purpose

This fixture defines the shortest demonstrable V1 loop. It is the first end-to-end acceptance path after Slice 1-14 are implemented.

The goal is not to cover every feature. The goal is to prove that Chtest can create a project, run AI-assisted requirement/case/automation workflows through mock providers, execute pytest through Tool Adapter, store evidence, and generate a report.

## 2. Seed Data

Required seed data:

- Default workspace.
- Default user.
- Project: `Checkout System`.
- Module: `订单结算`.
- Repository: local sample repository under an allowlisted path.
- Environment: `local`.
- TestCommand: `pytest tests -q --junitxml=artifacts/junit.xml`.
- Mock Provider enabled.
- Built-in PromptVersion loaded.
- Built-in SkillVersion loaded.
- Built-in ToolDefinition: `TestRunnerTool`.

## 3. Minimum Flow

1. Create Project.
2. Create Module.
3. Create Repository.
4. Create Environment.
5. Create TestCommand.
6. Input coupon requirement.
7. Mock RequirementReviewAgent generates requirement review.
8. Mock CaseGenerationAgent generates candidate cases.
9. User approves at least one candidate case.
10. Mock AutomationDraftAgent generates pytest AutomationDraft.
11. User approves AutomationDraft.
12. TestRunnerTool runs pytest.
13. Chtest saves TestRun, TestResult, and Artifact.
14. ReportAgent generates `automation_execution` report.

## 4. Success Criteria

- At least one `TestCase` has `review_status=approved`.
- At least one `AutomationDraft` has `status=approved`.
- At least one `TestRun` has `status=passed`.
- TestRun records `runtime_artifact_ids`, `runtime_manifest.json`, `dependency_snapshot.json`, and `environment_snapshot.json`.
- TestRun records runner sandbox metadata: runner mode, isolated run workspace, repository readonly setting, and network setting.
- At least one `Report` has `status=ready` and `report_type=automation_execution`.
- All related AITask records can trace PromptVersion, SkillVersion, model, input artifact, and output artifact.
- ToolInvocation is linked to TestRun and captures stdout/stderr/JUnit artifacts.

## 5. Product Value Acceptance

The demo is acceptable only when the user can answer these questions from the UI or generated report:

- What requirement did AI analyze?
- Which generated cases were approved or edited?
- Which AutomationDraft was approved and what exact runtime file was executed?
- Did the approved draft run successfully on the first execution?
- What evidence supports the execution conclusion?
- Which Prompt, Skill, model, and mock provider output produced the result?
- What would the user do next if the TestRun failed?

## 6. Minimum Evidence

The demo must show:

- Project Settings payload.
- RequirementReview result.
- GeneratedCaseCandidate list.
- Approved TestCase.
- Approved AutomationDraft.
- TestRun detail with parsed result.
- Runtime manifest, dependency snapshot, and environment snapshot.
- Report detail with evidence/artifact references.

## 7. Out Of Scope For This Demo

- Real LLM provider.
- RAG evidence retrieval.
- Playwright execution.
- Git Quality workflow.
- Newman/JMeter/Appium/traffic capture.
- Multi-user collaboration.
