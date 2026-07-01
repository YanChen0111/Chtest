# Knowledge Prompt/Skill Seeds Golden

## Purpose

This fixture records the first knowledge-driven prompt and skill seeds for the
final Chtest agent workflow. The seeds are draftable and loadable artifacts, not
runtime behavior.

## Seed Set

| Agent | Prompt | Skill | Purpose |
|---|---|---|---|
| KnowledgeIngestionAgent | `prompts/knowledge_card_extraction/v1.md` | `skills/knowledge-ingestion-skill/v1.md` | Extract draft TestKnowledgeCard candidates from local evidence |
| CaseGenerationAgent | `prompts/evidence_case_generation/v1.md` | `skills/test-case-generation-skill/v1.md` | Generate evidence-backed case candidates |
| CaseReviewAgent | `prompts/evidence_case_review/v1.md` | `skills/testcase-review-skill/v1.md` | Review generated cases for evidence, coverage, duplicates, and hallucination risk |
| AutomationReadinessAgent | `prompts/automation_readiness/v1.md` | `skills/automation-draft-skill/v1.md` | Classify reviewed cases for automation fit without generating code |
| KnowledgeFeedbackAgent | `prompts/knowledge_feedback/v1.md` | `skills/knowledge-feedback-skill/v1.md` | Convert accepted cases, rejected cases, reviews, failures, and reports into draft knowledge feedback |
| CoverageAnalysisAgent | no prompt in this slice | `skills/coverage-analysis-skill/v1.md` | Define methodology for coverage gap analysis over supplied local evidence |
| TestDesignAgent | no prompt in this slice | `skills/test-design-skill/v1.md` | Define testing-method guidance for future evidence-backed design agents |

## Reference Use

- Awesome LLM Apps is used as a pattern reference for focused agent apps and
  reusable skill-style instructions.
- PageIndex-style tree and section navigation is used as a pattern reference
  for source spans in `knowledge_card_extraction`.
- Microsoft GraphRAG-style relationship reasoning is used as a later review
  concept only. This fixture does not introduce graph extraction, indexing, or
  graph runtime behavior.

## Required Boundary

Each seed must preserve this boundary:

```text
Do not call external providers.
Do not create vector indexes.
Do not trigger MCP runtime.
Do not promote generated cases.
```

## Expected Smoke

The smoke test proves:

- all seed files exist;
- prompt files have required prompt sections;
- skill files have required skill sections;
- prompt/skill text references `TestKnowledgeCard` and `KnowledgeEvidence`;
- prompt/skill text keeps runtime non-goals explicit.
