# Minimal Prompt And Skill Seeds

## 1. Purpose

This fixture turns the Prompt/Skill contract into concrete seed files that Slice
5 can load into PromptVersion and SkillVersion records. The seeds are small by
design and can run against the mock provider before real LLM integration exists.

The source contract remains `docs/contracts/05-prompt-skill-contract.md`.

## 2. Seed Directory

```text
docs/fixtures/prompt-skill-seeds/
  prompts/
    requirement_review/v1.md
    risk_matrix/v1.md
    case_generation/v1.md
    case_review/v1.md
    automation_draft_generation/v1.md
    cicd_change_analysis/v1.md
    unit_test_generation/v1.md
    regression_selection/v1.md
    tool_execution/v1.md
    failure_analysis/v1.md
    report_generation/v1.md
    knowledge_card_extraction/v1.md
    requirement_understanding/v1.md
    risk_analysis/v1.md
    coverage_analysis/v1.md
    test_design/v1.md
    evidence_case_generation/v1.md
    evidence_case_review/v1.md
    case_dedup/v1.md
    automation_readiness/v1.md
    knowledge_feedback/v1.md
  skills/
    requirement-review-skill/v1.md
    test-case-generation-skill/v1.md
    testcase-review-skill/v1.md
    automation-draft-skill/v1.md
    unit-test-generation-skill/v1.md
    regression-selection-skill/v1.md
    tool-execution-skill/v1.md
    failure-analysis-skill/v1.md
    report-generation-skill/v1.md
    knowledge-ingestion-skill/v1.md
    risk-analysis-skill/v1.md
    coverage-analysis-skill/v1.md
    test-design-skill/v1.md
    knowledge-feedback-skill/v1.md
```

Slice 5 may copy or import these files into the runtime `prompts/` and `skills/`
directories. Do not edit published runtime versions in place after activation;
create a new version instead.

## 3. Seed Set

| Agent | Prompt Seed | Skill Seed | Mock Provider Use |
|---|---|---|---|
| RequirementReviewAgent | `prompts/requirement_review/v1.md` | `skills/requirement-review-skill/v1.md` | Generate six-dimensional requirement review JSON |
| RequirementReviewAgent | `prompts/risk_matrix/v1.md` | `skills/requirement-review-skill/v1.md` | Generate structured risk matrix JSON |
| CaseGenerationAgent | `prompts/case_generation/v1.md` | `skills/test-case-generation-skill/v1.md` | Generate structured candidate cases |
| CaseReviewAgent | `prompts/case_review/v1.md` | `skills/testcase-review-skill/v1.md` | Review generated case candidate quality |
| AutomationDraftAgent | `prompts/automation_draft_generation/v1.md` | `skills/automation-draft-skill/v1.md` | Generate pytest or Playwright draft code |
| CICDChangeAnalysisAgent | `prompts/cicd_change_analysis/v1.md` | `skills/regression-selection-skill/v1.md` | Generate CI/CD change risk evidence |
| UnitTestAgent | `prompts/unit_test_generation/v1.md` | `skills/unit-test-generation-skill/v1.md` | Generate scoped UnitTestPatch candidates |
| RegressionAgent | `prompts/regression_selection/v1.md` | `skills/regression-selection-skill/v1.md` | Select pytest regression commands |
| ToolExecutionAgent | `prompts/tool_execution/v1.md` | `skills/tool-execution-skill/v1.md` | Plan allowlisted pytest or Playwright execution |
| FailureAnalysisAgent | `prompts/failure_analysis/v1.md` | `skills/failure-analysis-skill/v1.md` | Classify failed execution with evidence references |
| ReportAgent | `prompts/report_generation/v1.md` | `skills/report-generation-skill/v1.md` | Generate evidence-backed reports |
| KnowledgeIngestionAgent | `prompts/knowledge_card_extraction/v1.md` | `skills/knowledge-ingestion-skill/v1.md` | Extract draft TestKnowledgeCard candidates |
| RequirementUnderstandingAgent | `prompts/requirement_understanding/v1.md` | `skills/requirement-review-skill/v1.md` | Extract acceptance points and testability issues |
| RiskAnalysisAgent | `prompts/risk_analysis/v1.md` | `skills/risk-analysis-skill/v1.md` | Identify evidence-backed testing risks |
| CoverageAnalysisAgent | `prompts/coverage_analysis/v1.md` | `skills/coverage-analysis-skill/v1.md` | Identify coverage gaps over supplied evidence |
| TestDesignAgent | `prompts/test_design/v1.md` | `skills/test-design-skill/v1.md` | Define evidence-backed test design notes |
| CaseGenerationAgent | `prompts/evidence_case_generation/v1.md` | `skills/test-case-generation-skill/v1.md` | Generate evidence-backed case candidates |
| CaseReviewAgent | `prompts/evidence_case_review/v1.md` | `skills/testcase-review-skill/v1.md` | Review evidence-backed case candidates |
| DedupAgent | `prompts/case_dedup/v1.md` | `skills/testcase-review-skill/v1.md` | Deduplicate case candidates while preserving distinct coverage |
| AutomationReadinessAgent | `prompts/automation_readiness/v1.md` | `skills/automation-draft-skill/v1.md` | Classify automation readiness without generating code |
| KnowledgeFeedbackAgent | `prompts/knowledge_feedback/v1.md` | `skills/knowledge-feedback-skill/v1.md` | Convert reviewed evidence into draft knowledge feedback |

## 4. Minimum Loader Acceptance

Slice 5 is accepted when a loader or smoke test can prove:

- all seed files listed in this fixture exist;
- every Prompt seed includes `Agent`, `Purpose`, `Input Schema`, `Output Schema`,
  `Instructions`, and `Failure Output`;
- every Skill seed includes `Applies To`, `Methodology`, `Input Contract`,
  `Output Contract`, `Quality Gates`, `Forbidden Actions`, and `Tool Permissions`;
- each loaded PromptVersion and SkillVersion records a content hash;
- mock provider outputs can be validated against the prompt output schema.

## 5. Mock Output Rule

The mock provider should use deterministic outputs aligned with these seeds.
Mock output does not need model quality, but it must prove:

- schema validation;
- context artifact traceability;
- review-gated assets;
- artifact writing;
- evidence-backed report input.

## 6. Vibe Coding Instruction

When implementing Slice 5, use these seeds before designing a prompt management
UI. The product value is traceable, versioned AI behavior, not prompt editing
surface area.
