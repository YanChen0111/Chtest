# V1 Manual Walkthrough

Date: 2026-06-30

## Purpose

This walkthrough is the human-readable release companion for the automated V1
golden suite. It follows the same product proof as
`docs/fixtures/00-v1-demo-path.md` without replacing automated acceptance.

## Walkthrough Outline

### 1. Project And Context Setup

- Create or open the local project.
- Confirm module, repository, environment, and test command configuration.
- Confirm ContextArtifact inventory includes project context such as
  `coupon-api-notes.md`.

### 2. Requirement Review And Context Usage

- Submit the coupon requirement.
- Review RequirementReview output.
- Confirm context usage is traceable through `context_artifact_ids`.
- Confirm `used_knowledge=false` unless KnowledgeAdapter is explicitly
  configured in a later release.

### 3. Candidate Case Generation And Human Approval

- Generate case candidates from the reviewed requirement.
- Review candidate details, risks, and coverage.
- Approve at least one candidate into the TestCase library.

### 4. AutomationDraft Review And Approval

- Generate an AutomationDraft from an approved TestCase.
- Review draft code, suggested file path, execution notes, and risk notes.
- Approve the draft before any execution.

### 5. pytest Execution Evidence

- Execute the approved pytest draft through the controlled runner path.
- Confirm TestRun status, parsed result, TestResult, stdout/stderr, and runtime
  manifest evidence.
- Confirm repository readonly and network-disabled sandbox metadata.

### 6. Failure Analysis And Report Evidence

- Review failure analysis when a failed TestRun exists.
- Generate an automation execution report.
- Confirm the report includes evidence manifest, artifact references, and a
  conclusion backed by evidence.

### 7. CI/CD Quality Center Support Workflow

- Create a local diff CICDRun.
- Review changed file risk analysis.
- Generate and review UnitTestPatch.
- Run new-test and regression evidence.
- Review QualityGateDecision and CI/CD quality report.

### 8. Extension Surfaces

- Open RAG 知识库 and confirm it is a ContextArtifact and KnowledgeAdapter
  management surface.
- Review MCP-ready ToolDefinition metadata.
- Confirm there is no RAG runtime, vector index, MCP runtime, RBAC, tenants, or
  permissions behavior in V1.

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
