# Agent Workflow Contract Golden

This fixture proves Slice 32 remains a contract-only requirement-to-reviewed-case
workflow definition. It is not a runtime workflow, not an agent executor, and
not a provider integration.

## Workflow Steps

| Order | Agent | PromptVersion | SkillVersion | Input evidence | Output | Write permission | Human gate | Failure behavior | Trace requirement |
|---|---|---|---|---|---|---|---|---|---|
| 1 | RequirementUnderstandingAgent | requirement_understanding:v1 | requirement-review-skill:v1 | Requirement text, requirement artifact ids, ContextArtifact manifest | requirement_understanding artifact | AITask artifacts only | Human clarification for ambiguity/conflict | UNABLE_TO_UNDERSTAND_REQUIREMENT | workflow_run_id, agent_step, requirement_id, prompt_version, skill_version, input_artifact_ids, output_artifact_ids |
| 2 | RiskAnalysisAgent | risk_analysis:v1 | risk-analysis-skill:v1 | RequirementUnderstandingAgent output, local risk evidence | risk_analysis artifact | AITask artifacts only | Test lead review for P0/P1 risk gaps | UNABLE_TO_ANALYZE_RISK | workflow_run_id, agent_step, risk_item_count, max_risk_level, fallback_applied |
| 3 | CoverageAnalysisAgent | coverage_analysis:v1 | coverage-analysis-skill:v1 | Understanding, risks, reviewed case summaries, local knowledge evidence | coverage_analysis artifact | AITask artifacts and coverage draft only | Reviewer confirmation for residual gaps | UNABLE_TO_ANALYZE_COVERAGE | workflow_run_id, agent_step, matrix_artifact_id, gap_count, failure_code |
| 4 | TestDesignAgent | test_design:v1 | test-design-skill:v1 | Understanding, risks, coverage, target test types | test_design artifact | AITask artifacts and design draft only | Test designer review before accepted generation input | UNABLE_TO_DESIGN_TESTS | workflow_run_id, agent_step, scenario_outline_count, schema_validation_status |
| 5 | CaseGenerationAgent | evidence_case_generation:v1 | test-case-generation-skill:v1 | Test design, requirement, risk, coverage, ContextArtifact manifest | GeneratedCaseCandidate drafts | GeneratedCaseCandidate with status=generated only | Human review required after generation | UNABLE_TO_GENERATE_CASES | workflow_run_id, case_generation_task_id, candidate_ids, valid_candidate_count |
| 6 | CaseReviewAgent | evidence_case_review:v1 | testcase-review-skill:v1 | GeneratedCaseCandidate drafts and evidence | case_review artifact and review findings | Candidate review evidence fields only | Human reviewer decides accept/reject/needs-fix | UNABLE_TO_REVIEW_CASE | workflow_run_id, candidate_id, quality_score, recommended_action, human_gate=required |
| 7 | DedupAgent | case_dedup:v1 | testcase-review-skill:v1 | Candidate drafts and reviewed case summaries | dedup_analysis artifact | Dedup suggestion artifact only | Human reviewer confirms merge/removal | UNABLE_TO_DEDUP_CASES | workflow_run_id, duplicate_cluster_id, dedup_status, fallback_applied |
| 8 | AutomationReadinessAgent | automation_readiness:v1 | automation-draft-skill:v1 | Reviewed candidate drafts, tool metadata, execution constraints | automation_readiness artifact | Readiness fields only | Automation owner review before automation work | UNABLE_TO_ASSESS_AUTOMATION_READINESS | workflow_run_id, candidate_id, readiness, blocker_count, suggested_framework |

## Required Fields

Every workflow step must define:

- PromptVersion / SkillVersion seed.
- Input evidence.
- Output contract.
- Write permission.
- Human gate.
- Failure behavior.
- Trace requirement.

## Evidence-Only Boundary

The contract must not create or trigger:

- TestCase auto-promotion.
- TestRun.
- Report.
- provider call.
- vector index.
- graph job.
- MCP runtime.
- Artifact mutation.
- runtime orchestration.
- remote CI provider behavior.

GeneratedCaseCandidate remains review-gated. Human review is the only authority
that may accept, reject, request optimization, or later promote a candidate
through an existing non-agent review workflow.
