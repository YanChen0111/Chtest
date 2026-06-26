# Chtest Mock Provider Contract

## 1. Purpose

This document defines deterministic Mock Provider behavior for Chtest V1 tests and Golden Path verification.

The Mock Provider lets Slice development validate AI workflows without a real LLM, external network, RAG, or paid API key.

## 2. Provider Identity

| Field | Value |
|---|---|
| provider | mock |
| default_model | mock-model |
| network_required | false |
| deterministic | true |

## 3. Mock Model Outputs

| Model Name | Task Type | Required Output |
|---|---|---|
| mock-requirement-review | requirement_review | Golden requirement review with six scores, issues, questions, and risks |
| mock-case-generator | case_generation | Golden case candidates matching `docs/fixtures/01-golden-requirement-to-case.md` |
| mock-automation-draft | automation_draft | Golden pytest or Playwright AutomationDraft matching `docs/fixtures/02-golden-case-to-playwright.md` |
| mock-cicd-analysis | cicd_change_analysis | Golden CI/CD change risk analysis matching `docs/fixtures/03-golden-cicd-quality.md` |
| mock-unit-test-generator | unit_test_generation | Golden UnitTestPatch matching `docs/fixtures/03-golden-cicd-quality.md` |
| mock-failure-analysis | failure_analysis | Evidence-based FailureAnalysis with deterministic classification |
| mock-report-generator | report_generation | Report JSON/Markdown summary based on provided TestRun or workflow data |

## 4. Behavior Rules

- Mock outputs must pass the same schema validators as real provider outputs.
- Mock outputs must create AITask artifacts the same way real provider outputs do.
- Mock outputs must echo `used_context_artifact_ids` when context is provided.
- Mock outputs must create `context_manifest.json` when context is provided.
- Mock Provider must support forced failure mode for tests.
- Mock Provider must support schema-invalid output mode for parser tests.
- Mock Provider must never call external network.
- Mock Provider must never read secrets.

## 5. Suggested Test Modes

| Mode | Behavior | Use |
|---|---|---|
| success | Return valid deterministic output | Golden Path and happy-path tests |
| provider_error | Raise provider error | AITask failed state tests |
| schema_invalid | Return invalid JSON/schema | Schema validation tests |
| timeout | Simulate timeout | Worker timeout handling |

## 6. Golden Path Mapping

- V1 Minimum Demo uses `mock-requirement-review`, `mock-case-generator`, and `mock-automation-draft`.
- V1 Minimum Demo requirement review and case generation must reference seed ContextArtifact `coupon-api-notes.md`.
- CI/CD Quality Golden Path uses `mock-cicd-analysis` and `mock-unit-test-generator`.
- Failure analysis tests use `mock-failure-analysis` with deterministic artifacts.
