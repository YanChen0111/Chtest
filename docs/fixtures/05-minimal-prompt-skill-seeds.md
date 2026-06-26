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
    case_generation/v1.md
    automation_draft_generation/v1.md
    cicd_change_analysis/v1.md
    failure_analysis/v1.md
  skills/
    requirement-review-skill/v1.md
    test-case-generation-skill/v1.md
    automation-draft-skill/v1.md
    regression-selection-skill/v1.md
    failure-analysis-skill/v1.md
```

Slice 5 may copy or import these files into the runtime `prompts/` and `skills/`
directories. Do not edit published runtime versions in place after activation;
create a new version instead.

## 3. Seed Set

| Agent | Prompt Seed | Skill Seed | Mock Provider Use |
|---|---|---|---|
| RequirementReviewAgent | `prompts/requirement_review/v1.md` | `skills/requirement-review-skill/v1.md` | Generate six-dimensional requirement review JSON |
| CaseGenerationAgent | `prompts/case_generation/v1.md` | `skills/test-case-generation-skill/v1.md` | Generate structured candidate cases |
| AutomationDraftAgent | `prompts/automation_draft_generation/v1.md` | `skills/automation-draft-skill/v1.md` | Generate pytest or Playwright draft code |
| CICDChangeAnalysisAgent | `prompts/cicd_change_analysis/v1.md` | `skills/regression-selection-skill/v1.md` | Generate CI/CD change risk evidence |
| FailureAnalysisAgent | `prompts/failure_analysis/v1.md` | `skills/failure-analysis-skill/v1.md` | Classify failed execution with evidence references |

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
