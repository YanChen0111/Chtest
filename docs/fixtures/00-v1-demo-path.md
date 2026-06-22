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
- ContextArtifact: `coupon-api-notes.md`, stored as `context_markdown`, owner `Project`.
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
6. Create ContextArtifact `coupon-api-notes.md`.
7. Input coupon requirement.
8. Mock RequirementReviewAgent generates requirement review using `context_artifact_ids`.
9. Mock CaseGenerationAgent generates candidate cases using the same ContextArtifact.
10. User approves at least one candidate case.
11. Mock AutomationDraftAgent generates pytest AutomationDraft.
12. User approves AutomationDraft.
13. TestRunnerTool runs pytest.
14. Chtest saves TestRun, TestResult, and Artifact.
15. ReportAgent generates `automation_execution` report.

## 4. Success Criteria

- At least one `TestCase` has `review_status=approved`.
- At least one `AutomationDraft` has `status=approved`.
- At least one `TestRun` has `status=passed`.
- At least one `Report` has `status=ready` and `report_type=automation_execution`.
- All related AITask records can trace PromptVersion, SkillVersion, model, input artifact, and output artifact.
- RequirementReview and CaseGeneration AITask records include `context_artifact_ids`.
- AI task artifact directory includes `context_manifest.json` with the exact ContextArtifact id, sha256, title, MIME type, and redaction flag.
- ToolInvocation is linked to TestRun and captures stdout/stderr/JUnit artifacts.

## 5. Minimum Evidence

The demo must show:

- Project Settings payload.
- ContextArtifact list with `coupon-api-notes.md`, `safe_to_show`, and `redaction_applied`.
- RequirementReview result.
- RequirementReview context usage: `used_knowledge=false` and `used_context_artifact_ids=[coupon-api-notes.md id]`.
- GeneratedCaseCandidate list.
- Approved TestCase.
- Approved AutomationDraft.
- TestRun detail with parsed result.
- Report detail with evidence/artifact references.

## 6. Out Of Scope For This Demo

- Real LLM provider.
- External RAG/KnowledgeAdapter evidence retrieval.
- Playwright execution.
- Git Quality workflow.
- Newman/JMeter/Appium/traffic capture.
- Multi-user collaboration.
