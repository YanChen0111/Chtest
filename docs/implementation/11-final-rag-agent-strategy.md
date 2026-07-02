# Final Test Knowledge RAG And Agent Strategy

Date: 2026-07-01

## Purpose

This document records the final-version direction for Chtest's knowledge-driven
case generation and review system.

It is a future implementation strategy, not authorization to add a RAG runtime
to the current V2 slice. Current V2 work must still follow `NEXT_AI_TASK.md`
and the slice/task boundary in `docs/implementation/10-v2-scope-options.md`.

The final product goal is not a generic chat knowledge base. The goal is:

```text
Testing knowledge -> traceable evidence -> better generated cases
  -> agent review -> human review -> execution evidence
  -> feedback into testing knowledge
```

The final version should feel like an experienced test lead and automation
engineer sitting beside the user: it reduces repetitive analysis work, makes
test-design reasoning visible, catches missed risks before review, and turns
execution feedback into reusable testing knowledge.

This document is a planning document only. Before any behavior in this document
is implemented, the relevant product and contract documents must be promoted
first:

```text
docs/product/01-positioning-and-scope.md
  -> docs/contracts/*
  -> slice plan
  -> fixtures / golden evals
  -> implementation
```

## Current Progress

Current implemented foundation:

- V1 established ContextArtifact, AITask, Artifact, PromptVersion,
  SkillVersion, review gates, execution evidence, reports, and local-first
  boundaries.
- Slice 17 added the extension surface: RAG knowledge page,
  KnowledgeAdapterConfig, and MCP-ready ToolDefinition surfaces.
- Slice 19 added deterministic local ContextArtifact retrieval evidence without
  vector databases, embeddings, reranking, background indexing, or external
  RAG providers.
- Slices 24-28 improved evidence readability across local artifacts, reports,
  imported CI references, AI task artifacts, and quality gates.
- Slice 29 is the active execution-run-manifest path and remains separate from
  this final RAG/Agent strategy.

Current gap:

- Chtest can attach local ContextArtifact evidence to AI tasks, but it does not
  yet maintain a rich testing knowledge model.
- Case generation can use context, but the final version should prove why each
  generated case exists, which knowledge supported it, which risks it covers,
  and which gaps remain.
- Agent, Prompt, Skill, ToolDefinition, and KnowledgeAdapter are planned, but
  the final flow still needs explicit orchestration rules, prompt/skill
  version gates, and provider safety boundaries.

## Final Product Experience

The final Chtest experience should optimize the daily flow of a test engineer,
not the novelty of RAG itself.

### Main User Journey

```text
Import requirement / API doc / defect / historical test notes
  -> extract and review TestKnowledgeCards
  -> analyze requirement ambiguity and testability
  -> identify business, data, environment, security, and regression risks
  -> design test strategy and coverage matrix
  -> generate evidence-backed case candidates
  -> run agent review for gaps, duplicates, and hallucination risk
  -> human accepts, edits, rejects, or requests optimization
  -> generate automation draft only from reviewed cases
  -> execute approved automation in controlled runner
  -> analyze failures and report evidence
  -> convert accepted cases, review comments, and failures into knowledge
```

### AI Efficiency Map

| Testing step | Current pain | AI acceleration | Quality protection |
|---|---|---|---|
| Requirement review | Manual reading misses ambiguity and hidden constraints | RequirementUnderstandingAgent extracts acceptance points, contradictions, and questions | Schema-validated review output and human confirmation |
| Risk analysis | Senior tester experience is hard to scale | RiskAnalysisAgent applies risk taxonomy and project history | Risk ids become required evidence for generated cases |
| Test design | Boundary, exception, and regression cases are easy to skip | TestDesignAgent selects testing methods and coverage targets | CoverageAnalysisAgent checks gaps against knowledge and existing cases |
| Case generation | Repetitive drafting consumes time | CaseGenerationAgent drafts structured candidates with evidence links | CaseReviewAgent rejects weak, duplicate, unverifiable, or unsupported cases |
| Case review | Reviewers spend time finding basic issues | CaseReviewAgent pre-scores evidence, executability, and hallucination risk | Human review remains the promotion gate |
| Automation readiness | Manual judgment decides what can be automated | AutomationReadinessAgent labels pytest, Playwright, Newman, or JMeter suitability | AutomationDraft still requires approval before execution |
| Failure follow-up | Failure knowledge is lost in reports | FailureAnalysisAgent and KnowledgeFeedbackAgent extract BugPattern and CoverageGap | New knowledge cards require review before prompt eligibility |

The product value target is measurable:

- Reduce first-pass case drafting time.
- Increase boundary, exception, and regression coverage.
- Reduce duplicate and vague generated cases.
- Increase human acceptance rate after agent review.
- Preserve evidence for every accepted recommendation.

## Final Architecture

Final Chtest should use a three-tier testing-knowledge capability with an agent
quality loop. This is intentionally not a generic RAG platform. Each tier must
earn its place by improving generated-case quality, automation readiness,
coverage visibility, or evidence traceability.

```text
ContextArtifact / imported knowledge
  -> TestKnowledgeCard extraction
  -> structured + keyword + vector retrieval
  -> test relationship graph retrieval
  -> RiskAnalysisAgent
  -> TestDesignAgent
  -> CaseGenerationAgent
  -> CaseReviewAgent / CoverageGapAgent
  -> human review
  -> execution and report evidence
  -> KnowledgeFeedbackAgent
```

The three tiers are complementary:

| Layer | Purpose | Quality value | Maintenance cost |
|---|---|---|---|
| L1 Structured Test Knowledge Evidence | Turn documents and reviewed work into testing knowledge cards | High immediate gain for case quality | Medium |
| L2 Hybrid Retrieval | Improve recall over larger corpora | Better matching across wording differences | Medium-high |
| L3 Test Relationship Graph | Reason over requirement, module, API, risk, defect, and case relationships | Highest coverage and impact-analysis value | High |

Optimization principle:

```text
Do not build RAG because RAG is fashionable.
Build testing knowledge only where it improves testing efficiency and quality.
```

Default final-version path:

```text
L1 is a core product capability.
L2 is optional and enabled only when eval data proves L1 recall is insufficient.
L3 is offline/background and enabled only after Chtest has enough reviewed data.
```

## Why This Optimized Design Exists

Open-source RAG and graph projects can reduce AI coding difficulty because they
show proven patterns for document ingestion, retrieval, reranking, graph
construction, and evaluation. The risk is that Chtest turns into a knowledge
platform instead of a testing workbench.

The optimized design keeps the benefit while containing the cost:

| Risk From Direct Open-Source Adoption | Chtest Optimization |
|---|---|
| Scope expands into a generic knowledge base | Only testing knowledge that affects case quality, automation, coverage, or evidence is allowed |
| Provider schemas leak into core models | Normalize every provider result into `KnowledgeEvidence` |
| Vector/graph infrastructure slows development | Ship L1 first; gate L2/L3 by eval evidence and data scale |
| RAG results are hard to explain | Generated cases must cite evidence ids, snippets, source artifacts, and review findings |
| AI coding copies too much framework code | Use libraries/providers behind adapters; do not paste large application code |
| Runtime becomes fragile | Providers are optional and disabled by default; core workflows fall back to local evidence |
| Evaluation is subjective | Every retrieval or agent change needs golden/eval fixtures before promotion |

For open-source source locations and migration rules, see:

- `docs/reference/01-open-source-migration-map.md`

Implementation order must follow quality leverage and maintenance cost:

1. Structured cards first, because they improve case quality without adding
   vector infrastructure.
2. Hybrid retrieval second, only when evals prove deterministic matching is not
   enough.
3. Graph reasoning last, after reviewed requirements, cases, failures, and
   reports are available as stable graph inputs.

## Layer 1: Structured Test Knowledge Evidence

This is the first final-product layer to implement.

Instead of storing only document chunks, Chtest should extract testing-specific
knowledge cards. This layer should be treated as the product core, not as a
heavy RAG runtime.

```text
RequirementPoint
BusinessRule
APIContract
BoundaryCondition
ExceptionScenario
RiskPoint
BugPattern
ExistingTestCasePattern
AntiPattern
TestStrategyNote
```

Each `TestKnowledgeCard` should preserve:

```text
project_id
knowledge_card_id
card_version
source_artifact_id
source_artifact_sha256
source_document_version
source_section
source_quote_or_hash
source_span
knowledge_type
module_key
api_endpoint
risk_type
case_type_hint
applicability
confidence
review_status
prompt_eligibility_status
stale_status
replaced_by_knowledge_card_id
safe_to_show
allowed_for_prompt
last_verified_at
```

Lifecycle:

```text
extracted
  -> pending_review
  -> approved | rejected | duplicate | unsafe
  -> prompt_eligible | prompt_blocked
  -> stale
  -> replaced
```

Rules:

- Approved cards are versioned and should be treated as immutable evidence.
- If source content changes, create a new card version or replacement card; do
  not silently rewrite the evidence behind an existing generated case.
- `source_span` should identify the original paragraph, heading, row, or line
  range when available. Hash-only evidence is acceptable only when the source
  format cannot provide stable spans.
- `allowed_for_prompt=false` cards may be shown as local review metadata only
  when `safe_to_show=true`; they must not be sent to external models or
  providers.

Why this matters:

- CaseGenerationAgent can generate cases from test concepts, not raw prose.
- CaseReviewAgent can reject cases that lack evidence or miss required risk
  types.
- Human reviewers can see which knowledge produced a case.
- KnowledgeFeedbackAgent can turn accepted cases and review comments back into
  reusable testing knowledge.

Open-source acceleration:

- Use structure-aware document retrieval ideas for traceable professional
  documents, especially long requirements, API manuals, product specs, and test
  plans.
- Use document parsing/conversion projects only as adapters for source import;
  do not let their schemas replace `TestKnowledgeCard`.
- Keep Chtest's own `TestKnowledgeCard` schema as the product contract even if
  an external parser or retrieval provider supplies document tree retrieval.

Implementation notes:

- Start from existing `ContextArtifact` and `Artifact` rows.
- Extract cards deterministically in the first implementation, then add an
  optional `KnowledgeIngestionAgent`.
- Keep extracted cards reviewable: approved, stale, unsafe, duplicate, or
  prompt-eligible.
- Store only bounded safe snippets in card/evidence records; large content stays
  in Artifact files.
- Make card extraction idempotent by source artifact id, source section, and
  source hash.

## Layer 2: Hybrid Retrieval RAG

This layer is added when the knowledge base becomes too large for deterministic
matching and simple filters.

Recommended retrieval composition:

```text
metadata filters
  + keyword/full-text retrieval
  + vector semantic retrieval
  + optional rerank
  + evidence normalization
```

The output must still be Chtest evidence:

```text
KnowledgeEvidence
  evidence_id
  provider_name
  source_artifact_id
  knowledge_card_id
  snippet
  score
  matched_terms
  retrieval_reason
  safe_to_show
  allowed_for_prompt
```

Every `KnowledgeEvidence` item should also carry:

```text
retrieved_at
retrieval_mode
provider_version
prompt_input_allowed
source_card_version
evidence_artifact_id
```

`retrieval_mode` examples:

```text
structured_filter
keyword
full_text
vector
rerank
graph
manual_review
```

Open-source acceleration:

- Prefer Haystack or LlamaIndex as provider implementations behind
  `KnowledgeAdapter`.
- Prefer library/API integration over copying framework code.
- Start with PostgreSQL full-text search. Add `pgvector` only when eval data
  proves semantic retrieval improves generated cases.
- Use Qdrant only if corpus size, latency, or vector operations outgrow
  PostgreSQL.
- RAGFlow may be evaluated as an external provider service, but it should not
  replace Chtest's RAG knowledge page, review flow, or evidence model.

Required boundary:

```text
Chtest owns: evidence model, AI task records, case generation, review, reports.
Provider owns: retrieval implementation, indexing internals, optional rerank.
```

Promotion gates:

- Knowledge card count or document volume makes deterministic retrieval
  inadequate.
- Eval fixtures show higher required-case coverage, boundary/exception coverage,
  or historical-defect coverage.
- Evidence precision does not drop below the accepted threshold.
- Provider failure can fall back to L1 without blocking case generation.
- No provider-specific payload is returned directly to generated cases.

Provider safety rules:

- Providers may receive only redacted, prompt-eligible content.
- Provider output is never trusted directly; it is normalized into
  `KnowledgeEvidence` and attached to an AITask or review artifact.
- External provider unavailability must degrade to local structured evidence or
  `used_knowledge=false`, not block the core workflow.
- Provider calls must record model/provider name, version/config hash, input
  artifact ids, output artifact ids, latency, and failure reason.

## Layer 3: Test Relationship Graph

This layer is for the final quality ceiling, not the first implementation.

The graph should be built from Chtest's own reviewed and executed data before
any GraphRAG-style provider is introduced:

```text
Requirement -> BusinessRule
Requirement -> Module
Module -> API
API -> RiskPoint
RiskPoint -> TestCase
BugPattern -> RegressionCase
GeneratedCaseCandidate -> ReviewHistory
TestRun -> FailureAnalysis
FailureAnalysis -> BugPattern
Report -> EvidenceManifest
ContextArtifact -> TestKnowledgeCard
```

Queries the graph should support:

```text
Which modules are affected by this requirement?
Which historical defects should be regressed?
Which high-risk flows have only happy-path tests?
Which generated cases duplicate existing reviewed cases?
Which API constraints are not covered by current cases?
Which failures should become new BugPattern knowledge?
```

Open-source acceleration:

- Use Microsoft GraphRAG as a reference for extracting structured data and
  graph communities from private text.
- Treat GraphRAG indexing as an offline or background pipeline because its own
  documentation warns that indexing can be expensive and needs prompt tuning.
- Do not put GraphRAG indexing on the synchronous case-generation request path.
- Keep graph outputs normalized into Chtest's own `KnowledgeEvidence` and
  `CoverageGap` contracts.

Implementation notes:

- Start with deterministic edges from existing Chtest rows: requirement ids,
  risk ids, module ids, API endpoints, test case ids, test run ids, and report
  artifact ids.
- Use graph outputs as coverage and impact-analysis evidence, not as automatic
  approval authority.
- Run graph extraction asynchronously and record graph build artifacts.
- Case generation must still work if the graph is missing, stale, or disabled.

## Agent System

Final Chtest should not rely on one large "generate cases" prompt. It should
compose focused agents:

| Agent | Responsibility | Prompt | Skill | Write permission |
|---|---|---|---|---|
| OrchestratorAgent | Select workflow, create AITask steps, enforce state and review gates | none, state-machine driven | governance rules | AITask only |
| KnowledgeIngestionAgent | Extract TestKnowledgeCards from documents and reviewed artifacts | knowledge_card_extraction | knowledge-ingestion-skill | draft knowledge cards and artifacts |
| RequirementUnderstandingAgent | Extract acceptance points, constraints, ambiguity, and testability issues | requirement_understanding | requirement-review-skill | RequirementReview artifact |
| RiskAnalysisAgent | Identify business, data, environment, regression, security, and technical risks | risk_analysis | risk-analysis-skill | RiskItem artifact or draft rows |
| CoverageAnalysisAgent | Compare requirements and risks against existing cases and execution evidence | coverage_analysis | coverage-analysis-skill | CoverageGap artifact |
| TestDesignAgent | Choose testing strategies: equivalence class, boundary value, state flow, error handling, security, regression | test_design | test-design-skill | TestDesign artifact |
| CaseGenerationAgent | Generate candidate cases with evidence links and generation reasons | evidence_case_generation | test-case-generation-skill | GeneratedCaseCandidate only |
| CaseReviewAgent | Score generated cases and reject weak, duplicate, hallucinated, or unverifiable cases | evidence_case_review | testcase-review-skill | review findings only |
| DedupAgent | Merge equivalent candidates and preserve distinct risk coverage | case_dedup | testcase-review-skill | duplicate links only |
| AutomationReadinessAgent | Decide whether a reviewed case is suitable for pytest, Playwright, Newman, or JMeter automation | automation_readiness | automation-draft-skill | readiness labels only |
| AutomationDraftAgent | Generate automation drafts from reviewed cases | automation_draft_generation | automation-draft-skill | AutomationDraft only |
| ToolExecutionAgent | Execute approved local tools through ToolDefinition and ToolInvocation | tool_execution | tool-execution-skill | ToolInvocation/TestRun artifacts |
| FailureAnalysisAgent | Classify failures and cite logs, traces, screenshots, and parsed results | failure_analysis | failure-analysis-skill | FailureAnalysis artifact |
| ReportAgent | Produce report conclusions from structured evidence only | report_generation | report-generation-skill | Report artifacts |
| KnowledgeFeedbackAgent | Convert accepted cases, rejected cases, review comments, failures, and reports into improved knowledge | knowledge_feedback | knowledge-feedback-skill | draft knowledge cards only |

The main final workflow should be:

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

Synchronous path:

```text
RequirementUnderstandingAgent
RiskAnalysisAgent
TestDesignAgent
CaseGenerationAgent
CaseReviewAgent
DedupAgent
AutomationReadinessAgent
```

Asynchronous or review-batched path:

```text
KnowledgeIngestionAgent
CoverageAnalysisAgent
Graph extraction
KnowledgeFeedbackAgent
large provider reindex
```

Human review gates:

- TestKnowledgeCard prompt eligibility.
- GeneratedCaseCandidate promotion into TestCase.
- AutomationDraft approval before execution.
- UnitTestPatch application.
- High-risk ToolInvocation.
- KnowledgeFeedbackAgent-created cards before reuse.

Failure behavior:

- Missing knowledge evidence downgrades quality score and creates coverage gap
  notes; it must not fabricate evidence.
- Provider timeout falls back to local structured evidence.
- Schema-invalid output creates `schema_validation.json` and retry guidance,
  not silent partial promotion.
- CaseReviewAgent rejection keeps the generated candidate auditable but blocks
  TestCase promotion.

Each generated case candidate should include:

```text
title
preconditions
steps
expected_results
case_type
covered_requirement_ids
covered_risk_ids
source_knowledge_evidence_ids
generation_reason
automation_readiness
quality_score
review_findings
coverage_gap_notes
```

`quality_score` should be explainable through sub-scores:

```text
requirement_coverage_score
risk_coverage_score
boundary_coverage_score
exception_coverage_score
historical_defect_coverage_score
executability_score
expected_result_verifiability_score
evidence_completeness_score
hallucination_risk_score
automation_readiness_score
```

CaseReviewAgent quality gates:

```text
requirement coverage
risk coverage
boundary coverage
exception coverage
historical defect coverage
duplicate risk
step executability
expected result verifiability
evidence completeness
hallucination risk
automation readiness
```

## Prompt And Skill Strategy

Prompt files define shape; Skill files define testing judgment.

The final version should add prompt/skill families gradually:

```text
prompts/
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
  knowledge-ingestion-skill/v1.md
  risk-analysis-skill/v1.md
  coverage-analysis-skill/v1.md
  test-design-skill/v1.md
  knowledge-feedback-skill/v1.md
```

Existing V1 skills should be extended rather than replaced:

- `requirement-review-skill` becomes the base for requirement understanding.
- `test-case-generation-skill` adds evidence-backed generation rules.
- `testcase-review-skill` adds hallucination, duplicate, and coverage gates.
- `automation-draft-skill` adds automation readiness reasoning before draft
  generation.
- `failure-analysis-skill` adds BugPattern and CoverageGap extraction rules.

Promotion rules:

- A new PromptVersion or SkillVersion starts as draft.
- It must pass schema examples and at least one golden fixture before it can be
  active.
- It must improve or preserve evidence precision, hallucination rate, duplicate
  rate, and human acceptance rate before replacing an active version.
- Rollback keeps older prompt/skill versions addressable by hash.
- Prompt/Skill changes that affect output fields must update contracts and
  fixtures first.

Prompt inputs must include explicit evidence sections:

```text
task_input
approved_knowledge_cards
knowledge_evidence
source_artifact_manifest
existing_cases_summary
execution_evidence_summary
forbidden_claims
output_schema
```

Prompt outputs must include:

```text
used_knowledge_evidence_ids
unsupported_claims
confidence
review_findings
schema_version
```

Skills must include:

```text
methodology
quality_gates
forbidden_actions
evidence_requirements
review_escalation_rules
tool_permissions
failure_output
```

## MCP And Tool Strategy

MCP remains a tool access layer, not the orchestrator and not the RAG product.

Final Chtest should keep this separation:

| Layer | Owns | Must not own |
|---|---|---|
| Agent | Workflow decisions, AITask state, structured outputs | Raw tool execution or provider schema |
| Skill | Testing methodology and quality gates | Runtime credentials or hidden side effects |
| Prompt | Input/output shape and task instruction | Product truth or unversioned behavior |
| ToolDefinition | Tool schema, risk, approval, timeout, artifact policy | Business workflow decisions |
| MCP Server | External tool operation | Case promotion, report conclusion, or review bypass |
| KnowledgeAdapter | Retrieval provider boundary | TestCase schema, Artifact schema, or Agent state |

Early MCP-ready work that is useful before full MCP runtime:

- Keep ToolDefinition schemas strict and JSON-schema based.
- Classify tool risk levels and approval requirements.
- Preserve ToolInvocation artifacts for every tool call.
- Keep local tools and future MCP tools behind the same review and artifact
  policy.
- Define config state for disabled/configured/unhealthy providers without
  breaking core local workflows.

MCP must not bypass:

- human approval for high-risk tools;
- Artifact persistence;
- ToolInvocation status;
- report evidence requirements;
- generated-case review gates;
- prompt/skill version tracking.

## Development Reuse Policy

To improve development efficiency, Chtest may use open-source projects, but
reuse must be controlled:

| Reuse mode | Preferred use |
|---|---|
| Library dependency | Haystack, LlamaIndex, pgvector client libraries, parsers |
| External service provider | RAGFlow, PageIndex API/self-host, Qdrant, GraphRAG offline service |
| Reference implementation | Awesome LLM Apps examples, PageIndex retrieval patterns, GraphRAG methodology |
| Vendored source | Only small isolated modules after license review, attribution, and upgrade plan |

Rules:

- Do not copy large open-source application code into Chtest's core modules.
- Do not replace Chtest's AITask, Artifact, ReviewHistory, TestCase, Report, or
  KnowledgeAdapter contracts with provider-specific schemas.
- Every provider result must be converted into Chtest `KnowledgeEvidence`.
- Every dependency must have a documented license, version pin, upgrade owner,
  and fallback behavior before implementation.
- The first code slice for any provider must include one golden smoke proving
  evidence traceability and no hidden runtime side effects.
- Do not introduce copyleft or unclear-license code into distributed Chtest
  artifacts without explicit approval and a NOTICE/update plan.
- Prefer adapter packages and isolated services over framework-wide ownership
  transfer into Chtest.

Reference use:

- Haystack or LlamaIndex: use as the first production-style
  `KnowledgeAdapter` provider candidates.
- Microsoft GraphRAG: use for later relationship graph extraction and
  reasoning, preferably offline/background.
- RAGFlow: evaluate only as an external knowledge service, not as Chtest's
  internal product shell.
- Qdrant or pgvector: use only after PostgreSQL full-text and structured
  filtering are insufficient.
- Document parsing projects such as MarkItDown or Unstructured may help import
  Word, PDF, HTML, or Markdown content, but Chtest still owns the final
  `TestKnowledgeCard` and `KnowledgeEvidence` contracts.

## Open-Source Reference Intake Workflow

Every open-source reference used for AI coding must pass this intake before a
slice implementation starts:

1. Record the repository URL, license, version or commit, and documentation
   location in the slice plan or reference map.
2. Identify the exact capability to migrate: parser, retriever, reranker,
   graph extraction, eval metric, or adapter pattern.
3. Decide the reuse mode: reference only, library dependency, external provider,
   or small vendored utility after license review.
4. Define the Chtest-owned input and output contracts before reading provider
   internals.
5. Normalize all provider outputs into `KnowledgeEvidence`, `Artifact`,
   `AITask`, `ReviewHistory`, or `Report` records.
6. Add one golden/eval fixture proving evidence traceability and fallback
   behavior.
7. Keep the provider disabled by default until the focused verification passes.

AI coding prompt template for future slices:

```text
Goal:
Use <repo URL> only for <specific capability>.

Allowed reuse:
<reference only | library adapter | external provider | small vendored helper>.

Chtest-owned contract:
Input: <schema/API>
Output: KnowledgeEvidence / TestKnowledgeCard / Artifact / Report

Non-goals:
No provider schema leak, no generic chat UI, no auto-approval, no hidden index,
no runtime dependency unless explicitly enabled.

Verification:
<focused pytest/golden command> plus git diff --check.
```

## Maintenance Model

The heavy final strategy needs explicit maintenance. Without this, RAG quality
will decay and generated cases will become harder to trust.

Daily or per-import maintenance:

```text
new document import
  -> parse
  -> extract TestKnowledgeCards
  -> run schema validation
  -> run safety/redaction checks
  -> update retrieval indexes
  -> record import evidence
```

Weekly maintenance:

```text
review low-hit knowledge cards
review high false-positive retrievals
deduplicate overlapping cards
mark stale source documents
sample generated cases for quality
update prompts and skills only with eval evidence
```

Release maintenance:

```text
import failures and post-release defects
update BugPattern knowledge
refresh risk tags for changed modules
rerun retrieval/case-generation eval set
record quality trend in AI metrics
```

Feedback loop:

```text
accepted case -> positive example
rejected case -> negative example
review comment -> TestStrategyNote
failure analysis -> BugPattern
missing coverage -> CoverageGap
```

## Evaluation Gates

Every major RAG or Agent change needs an evaluation fixture set:

```text
input requirement
available knowledge cards
expected required cases
expected boundary cases
expected exception cases
expected regression cases
forbidden hallucinated cases
expected evidence ids
```

Metrics:

```text
knowledge recall
evidence precision
required-case coverage
boundary/exception coverage
historical-defect coverage
duplicate rate
hallucination rate
human acceptance rate
edit distance after review
automation readiness rate
first-run pass rate after automation
```

No provider, embedding model, reranker, graph extraction prompt, or case
generation prompt should be promoted without a focused golden/eval smoke.

Minimum promotion thresholds should be defined per fixture set. Initial default
thresholds for future planning:

| Metric | Initial gate |
|---|---|
| Schema valid rate | 100% for golden fixtures |
| Evidence precision | no unsupported evidence in golden fixtures |
| Hallucination rate | zero forbidden hallucinations in golden fixtures |
| Duplicate rate | no duplicate P0/P1 candidates after DedupAgent |
| Required-case coverage | all expected required cases present |
| Boundary/exception coverage | all expected P0/P1 boundaries and exceptions present |
| Human acceptance rate | must improve against previous active prompt/skill in sampled review |
| Regression defect coverage | must include expected historical defect cases when evidence exists |

These thresholds are starting gates, not product SLAs. Later slices can tune
them with real project data.

## Implementation Phases

### Phase 1: Test Knowledge Card Contract

- Define `TestKnowledgeCard` and `KnowledgeEvidence` contracts.
- Keep data derived from existing ContextArtifact and Artifact rows at first.
- Add import/extraction evidence but no vector database or graph runtime.
- Add golden smoke proving generated cases cite knowledge evidence.
- Define card versioning, review status, prompt eligibility, and stale/replaced
  behavior before any generated case relies on cards.

### Phase 2: Knowledge Ingestion And Review

- Add KnowledgeIngestionAgent with deterministic mock/provider behavior first.
- Add review UI for extracted knowledge cards.
- Allow users to mark knowledge as approved, stale, unsafe, duplicate, or
  prompt-eligible.
- Add `knowledge_card_extraction` prompt and `knowledge-ingestion-skill` in
  draft status with schema fixtures.

### Phase 3: Case Generation With Evidence

- Update CaseGenerationAgent output contract so every candidate cites evidence,
  risk coverage, and generation reason.
- Add CaseReviewAgent quality scores and rejection reasons.
- Add CoverageGapAgent only after baseline evidence-backed generation works.
- Extend `case_generation` and `case_review` prompts into evidence-backed
  versions only after contract and fixture updates.

### Phase 3.5: Agent Workflow Contract

- Define which agents are synchronous, asynchronous, read-only, or write-capable.
- Add workflow artifacts for requirement understanding, risk analysis, test
  design, coverage analysis, case review, dedup, and automation readiness.
- Record PromptVersion, SkillVersion, KnowledgeEvidence ids, and output schema
  validation for every model-backed agent step.
- Add failure and fallback behavior for missing knowledge, provider timeouts,
  and schema-invalid output.

### Phase 4: External KnowledgeAdapter Provider

- Add one provider behind the existing KnowledgeAdapter boundary.
- Preferred candidates: Haystack or LlamaIndex.
- Keep provider runtime optional and disabled by default.
- Add provider health/config state without failing core workflows.

### Phase 5: Hybrid Search And Rerank

- Add keyword/full-text + vector retrieval + rerank only when eval data proves
  deterministic retrieval is insufficient.
- Prefer pgvector first if Chtest should stay operationally compact.
- Add Qdrant only for scale requirements.

### Phase 6: Test Relationship Graph

- Build graph from Chtest's own reviewed cases, requirements, failures, and
  reports.
- Start with offline extraction and read-only graph evidence.
- Use GraphRAG-style methods only after the graph schema and eval gates are
  stable.

### Phase 7: Closed-Loop Optimization

- Use accepted cases, rejected cases, review edits, execution failures, and
  reports to update draft knowledge cards.
- Compare prompt/skill versions using acceptance, edit distance, hallucination,
  duplicate, coverage, and execution metrics.
- Promote knowledge, prompts, and skills only through reviewable eval evidence.

## Non-goals Until Explicitly Promoted

- No generic chat knowledge base.
- No unreviewed case promotion into the TestCase library.
- No hidden vector or graph indexing during normal case generation.
- No provider-specific schema leaking into Chtest contracts.
- No large copied open-source application code in core modules.
- No RAG provider result treated as trusted without evidence.
- No bypassing human review because retrieval confidence is high.

## Recommended Next Planning Slice

After the current execution-readability slices, the first narrow planning slice
for this strategy should be:

```text
Slice N: Test Knowledge Card Contract
```

Smallest boundary:

- Define `TestKnowledgeCard`, `KnowledgeEvidence`, and evidence-backed
  generated-case fields in contracts.
- Add one fixture that shows requirement text, knowledge cards, generated case
  candidates, review findings, and evidence ids.
- Do not add vector database, embeddings, reranking, graph runtime, external
  provider calls, or frontend implementation in the planning task.

Recommended next documentation slices:

1. Test Knowledge Card Contract.
2. Evidence-backed generated case contract.
3. Agent workflow contract for requirement-to-reviewed-case.
4. Prompt/Skill draft contracts for knowledge extraction and evidence-backed
   case review.
5. MCP-ready ToolDefinition and KnowledgeAdapter safety contract review.
