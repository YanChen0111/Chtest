# Chtest V1 Product PRD

## 1. Product Definition

Chtest V1 is an AI Testing Workbench for individual test engineers and automation test engineers. It helps a single user complete the core testing workflow from requirement analysis, requirement review, test case generation, human review, automation draft generation, test execution, failure analysis, and report generation.

Chtest V1 is not a team collaboration platform, defect management system, enterprise quality portal, or general project management system. The first version must stay focused on personal productivity, reviewable AI output, executable tests, and measurable quality improvement.

## 2. Target Users

Primary users:

- Test engineers who need to turn requirement documents into structured test cases quickly.
- Automation test engineers who need AI assistance to draft pytest and Playwright scripts.
- Engineers who want a local-first personal tool to review AI output before using it in real projects.

Non-target users for V1:

- Multi-team QA management organizations.
- Enterprise administrators who need role, permission, audit, SSO, and organization hierarchy.
- Users expecting a complete replacement for MeterSphere, TestRail, Jira, Postman, JMeter, or Fiddler.

## 3. V1 Success Criteria

Chtest V1 is successful when it can repeatedly complete these loops in a real project:

1. Requirement to reviewed test cases.
2. Reviewed test cases to approved automation drafts.
3. Approved automation drafts to executable pytest or Playwright test runs.
4. Test runs to failure analysis and reports.
5. Local Git diff to AI-generated unit test patch, approval, execution, and regression conclusion.

The product must measure AI output quality instead of only showing generated content. Every AI result needs review status, acceptance data, edit data, failure data, and traceable artifacts.

## 4. Core User Scenarios

### 4.1 Requirement Review

User uploads or pastes a requirement. Chtest asks AI to analyze the requirement on six dimensions:

- Completeness.
- Clarity.
- Consistency.
- Testability.
- Feasibility.
- Logic.

The output includes score, issue list, clarification questions, risk items, and test design notes. The user can confirm the review result before generating cases.

### 4.2 AI Test Case Generation

User selects a requirement, target test types, and optional context. Chtest generates structured candidate cases.

Each candidate case must include:

- Title.
- Priority.
- Test type.
- Preconditions.
- Steps.
- Input data.
- Expected results.
- Requirement references.
- Risk references.
- AI generation reason.

Candidates cannot directly become official test cases. They enter a review queue first.

### 4.3 Test Case Review

The user reviews generated cases in a dedicated review screen. Supported decisions:

- Approve.
- Edit then approve.
- Reject.
- Request optimization.
- Mark unavailable.

The product records acceptance rate, edit rate, rejection reason, optimization result, and final approved case quality.

### 4.4 Automation Draft Generation

The user selects a requirement or approved test case and asks AI to generate an automation draft.

V1 supported frameworks:

- pytest for unit/API/service-style tests.
- Playwright for UI automation draft and smoke execution.

AutomationDraft must include:

- Target framework.
- Suggested file path.
- Draft code.
- Execution notes.
- Risk notes.
- Required fixtures or test data notes.

AutomationDraft is not written into the business project automatically. It must enter human review and approval.

### 4.5 Test Execution

The user can run approved TestCommand or AutomationDraft through controlled tool adapters.

V1 execution focus:

- pytest command execution.
- JUnit parsing.
- Basic coverage parsing when configured.
- Playwright smoke execution with screenshot/trace artifacts.

Every execution creates TestRun, TestResult, ToolInvocation, Artifact, and Report data.

### 4.6 Failure Analysis

When execution fails, Chtest analyzes stdout, stderr, JUnit, screenshots, traces, and related artifacts. The output must classify failure type, list evidence, and suggest next actions.

Allowed failure classifications:

- product_defect.
- test_script_issue.
- environment_issue.
- test_data_issue.
- dependency_issue.
- flaky_test.
- insufficient_evidence.

AI must not invent a root cause without evidence.

### 4.7 Git Quality Support

The user connects a local repository and creates a change set from a local diff. Chtest analyzes changed files, risk, and affected tests. It can generate a unit test patch for test directories only.

UnitTestPatch rules:

- Must modify test files only.
- Must not modify business source files.
- Must not add skip or xfail to hide failures.
- Must be reviewed before application.
- Must be followed by test execution and a report.

Git Quality is a support workflow in V1. The main product value remains requirement review, case generation, automation draft, execution, failure analysis, and reports.

## 5. Functional Scope

### 5.1 Project Settings

Project Settings must support:

- Project creation.
- Module tree up to five levels.
- Repository configuration.
- Environment configuration.
- Test command configuration.
- Command validation.

### 5.2 Case Library

Case Library must support:

- Module tree filter.
- Test type filter.
- Priority filter.
- Status filter.
- Case detail view.
- Manual creation and editing.
- Cases generated by AI after approval.

### 5.3 Automation Center

Automation Center must support:

- Generate automation draft from TestCase or Requirement.
- Review draft.
- Edit draft metadata.
- Approve or reject draft.
- Run approved draft through configured command.
- View run result and artifacts.

### 5.4 Execution Center

Execution Center must support:

- TestRun list.
- Running status refresh.
- Parsed pass/fail/skipped/error counts.
- Artifact links.
- Failure analysis entry.
- Report generation entry.

### 5.5 Report Center

Report Center must support:

- Requirement review report.
- Case quality report.
- Automation execution report.
- Git quality report.
- AI effectiveness report.

Reports must include raw data references and artifact ids.

## 6. Tool Scope

V1 tool scope:

- TestRunner for pytest.
- Playwright smoke execution.
- Git diff reader.
- Patch scope validator.
- Artifact parser for stdout, stderr, JUnit, coverage, screenshot, trace.
- Markdown/HTML/JSON report generator.

Postman-compatible execution is introduced through Newman after V1 proves the execution model. JMeter is introduced after execution artifact parsing and report aggregation are stable. Appium, Fiddler-style capture, and advanced performance analysis are roadmap capabilities.

## 7. AI Scope

AI can:

- Review requirements.
- Generate structured candidate cases.
- Optimize rejected or weak cases.
- Generate automation draft code.
- Analyze Git diff risk.
- Generate unit test patches under test directories.
- Select regression commands with explanation.
- Analyze failure evidence.
- Generate reports.

AI cannot:

- Write directly into business source files.
- Apply patches without approval.
- Execute high-risk tools without approval.
- Convert candidates into official cases without user review.
- Claim a defect without evidence.
- Depend on RAG being available.

## 8. Knowledge/RAG Boundary

V1 does not build a RAG system. It provides a KnowledgeAdapter interface so a later RAG service can be connected.

When no knowledge provider is configured, AI workflows must still run with `used_knowledge=false` and an empty evidence list.

## 9. Quality Metrics

Chtest must track:

- Requirement review score distribution.
- Generated case acceptance rate.
- Generated case edit rate.
- Generated case rejection reasons.
- Automation draft approval rate.
- Automation draft first-run pass rate.
- TestRun pass rate.
- Failure classification distribution.
- AI task schema validation pass rate.
- Prompt and skill version effectiveness.

## 10. V1 Acceptance Criteria

V1 can be accepted when:

- A user can create a project and configure repository, environment, and test commands.
- A user can create a requirement, run AI review, and view six-dimension results.
- A user can generate candidate cases and complete review decisions.
- Approved candidates become TestCase records.
- A user can generate AutomationDraft from TestCase.
- AutomationDraft requires approval before execution.
- A user can run pytest through TestCommand and view TestRun/TestResult.
- A failed run can trigger FailureAnalysis.
- A report can be generated for execution and case quality.
- A local Git diff can generate a scoped UnitTestPatch and run tests after approval.
- All AI outputs are stored with prompt, skill, model, schema validation, artifacts, and quality metrics.
