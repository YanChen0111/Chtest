# Agent / MCP / Skill / Prompt Design

## Layer Responsibilities

| Layer | Responsibility |
|---|---|
| Agent | Orchestrates workflow, state transitions, and structured outputs |
| Prompt | Defines task-specific input/output format and quality requirements |
| Skill | Stores testing methodology, quality gates, and forbidden actions |
| Tool Adapter | Executes approved local tools in V1 |
| MCP | Future standardized external tool access through ToolDefinition |
| Knowledge Adapter | Future RAG/knowledge context access through a stable interface |

Core rule:

```text
Agent chooses the step.
Prompt constrains the shape.
Skill supplies testing judgment.
ToolDefinition/MCP performs approved operations.
Artifact records evidence.
```

No layer may bypass review gates, Artifact persistence, PromptVersion,
SkillVersion, ToolInvocation status, or schema validation.

## V1 Agents

- OrchestratorAgent.
- RequirementReviewAgent.
- RiskAgent.
- CaseGenerationAgent.
- CaseReviewAgent.
- AutomationDraftAgent.
- CICDChangeAnalysisAgent.
- UnitTestAgent.
- RegressionAgent.
- ToolExecutionAgent.
- FailureAnalysisAgent.
- ReportAgent.

## V1 Skills

- `requirement-review-skill`.
- `test-case-generation-skill`.
- `testcase-review-skill`.
- `automation-draft-skill`.
- `unit-test-generation-skill`.
- `regression-selection-skill`.
- `tool-execution-skill`.
- `failure-analysis-skill`.
- `report-generation-skill`.

Newman and JMeter skills are added after the V1 execution/report loop is stable.

## V1 Prompt Set

```text
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
```

## Internal Tool Adapter First

V1 does not require MCP. It implements Internal Tool Adapter first and stores every tool as ToolDefinition.

```text
Agent -> ToolDefinition -> ToolInvocation -> Local tool -> Artifact parser -> TestRun/TestResult/Report
```

MCP servers can later map into the same ToolDefinition fields: name, input schema, output schema, risk level, approval requirement, timeout, and artifact policy.

## RAG Integration Boundary

V1 only implements Knowledge Adapter. When no external knowledge provider is configured, it returns empty evidence. Agents must continue normally and record `used_knowledge=false`.

## Final RAG And Agent Direction

Final-version knowledge-driven case generation is documented in
`docs/implementation/11-final-rag-agent-strategy.md`.

The target is a testing knowledge evidence system, not a generic chat knowledge
base. Future work should add structured `TestKnowledgeCard` and
`KnowledgeEvidence` contracts first, then optional Haystack/LlamaIndex provider
integration, and only later GraphRAG-style relationship reasoning after Chtest
has enough reviewed requirements, cases, failures, and reports.

## Final AI Workflow Direction

The final product should use multiple focused agents instead of one broad
"generate cases" prompt:

```text
KnowledgeIngestionAgent
  -> RequirementUnderstandingAgent
  -> RiskAnalysisAgent
  -> CoverageAnalysisAgent
  -> TestDesignAgent
  -> CaseGenerationAgent
  -> CaseReviewAgent
  -> DedupAgent
  -> human review
  -> AutomationReadinessAgent
  -> AutomationDraftAgent
  -> ToolExecutionAgent
  -> FailureAnalysisAgent
  -> ReportAgent
  -> KnowledgeFeedbackAgent
```

Final workflow planning should define this matrix before implementation:

| Field | Purpose |
|---|---|
| Agent | Workflow step owner |
| PromptVersion | Structured input and output schema |
| SkillVersion | Testing method, quality gates, and forbidden actions |
| Input evidence | ContextArtifact, TestKnowledgeCard, KnowledgeEvidence, TestRun, Report |
| Output artifact | Parsed JSON, review findings, generated cases, reports, feedback cards |
| Write permission | Which entity, if any, the agent may create or mutate |
| Human gate | Whether promotion or execution requires approval |
| Failure behavior | Retry, degrade, reject, or create coverage gap |
| Metrics | Acceptance rate, edit distance, hallucination, duplicates, execution pass |

Early work that can be completed before full RAG or MCP runtime:

- Define prompt and skill files for knowledge-card extraction, risk analysis,
  coverage analysis, evidence-backed case generation, evidence-backed case
  review, dedup, automation readiness, and knowledge feedback.
- Extend PromptVersion and SkillVersion tracking so every AITask records exact
  prompt and skill hashes.
- Keep ToolDefinition strict enough that local tools and future MCP tools share
  the same risk, approval, timeout, and artifact policy.
- Keep KnowledgeAdapter optional; missing or unhealthy knowledge providers must
  not fail the requirement-to-case workflow.

MCP remains a transport and tool-integration layer. It must not own case
promotion, report conclusions, knowledge trust, or review bypass.
