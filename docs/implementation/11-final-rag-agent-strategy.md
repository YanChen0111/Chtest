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

## Final Architecture

Final Chtest should use a three-layer RAG design with an agent quality loop.

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

The three RAG layers are complementary:

| Layer | Purpose | Quality value | Maintenance cost |
|---|---|---|---|
| Structured Test Knowledge RAG | Turn documents into testing knowledge cards | High immediate gain for case quality | Medium |
| Hybrid Retrieval RAG | Improve recall over larger corpora | Better matching across wording differences | Medium-high |
| Test Relationship Graph RAG | Reason over requirement, module, API, risk, defect, and case relationships | Highest coverage and impact-analysis value | High |

## Layer 1: Structured Test Knowledge RAG

This is the first final-product layer to implement.

Instead of storing only document chunks, Chtest should extract testing-specific
knowledge cards:

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
source_artifact_id
source_document_version
source_section
source_quote_or_hash
knowledge_type
module_key
api_endpoint
risk_type
case_type_hint
applicability
confidence
safe_to_show
allowed_for_prompt
last_verified_at
```

Why this matters:

- CaseGenerationAgent can generate cases from test concepts, not raw prose.
- CaseReviewAgent can reject cases that lack evidence or miss required risk
  types.
- Human reviewers can see which knowledge produced a case.
- KnowledgeFeedbackAgent can turn accepted cases and review comments back into
  reusable testing knowledge.

Open-source acceleration:

- Use PageIndex-style ideas for tree-structured, traceable document navigation,
  especially for long requirements, API manuals, product specs, and test plans.
- Prefer adapting concepts and using its self-host/API surface after license and
  deployment review; do not directly paste large source files into Chtest.
- Keep Chtest's own `TestKnowledgeCard` schema as the product contract even if
  PageIndex or another provider supplies document tree retrieval.

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

Open-source acceleration:

- Prefer Haystack or LlamaIndex as provider implementations behind
  `KnowledgeAdapter`.
- Prefer library/API integration over copying framework code.
- Start with PostgreSQL full-text search and `pgvector` if Chtest wants the
  lowest extra service count.
- Use Qdrant only if corpus size, latency, or vector operations outgrow
  PostgreSQL.
- RAGFlow may be evaluated as an external provider service, but it should not
  replace Chtest's RAG knowledge page, review flow, or evidence model.

Required boundary:

```text
Chtest owns: evidence model, AI task records, case generation, review, reports.
Provider owns: retrieval implementation, indexing internals, optional rerank.
```

## Layer 3: Test Relationship Graph RAG

This layer is for the final quality ceiling, not the first implementation.

The graph should be built from Chtest's own reviewed and executed data:

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

## Agent System

Final Chtest should not rely on one large "generate cases" prompt. It should
compose focused agents:

| Agent | Responsibility |
|---|---|
| KnowledgeIngestionAgent | Extract TestKnowledgeCards from documents and reviewed artifacts |
| RequirementUnderstandingAgent | Extract acceptance points, constraints, ambiguity, and testability issues |
| RiskAnalysisAgent | Identify business, data, environment, regression, and technical risks |
| CoverageAnalysisAgent | Compare requirements and risks against existing cases and execution evidence |
| TestDesignAgent | Choose testing strategies: equivalence class, boundary value, state flow, error handling, security, regression |
| CaseGenerationAgent | Generate candidate cases with evidence links and generation reasons |
| CaseReviewAgent | Score generated cases and reject weak, duplicate, hallucinated, or unverifiable cases |
| DedupAgent | Merge equivalent candidates and preserve distinct risk coverage |
| AutomationReadinessAgent | Decide whether a reviewed case is suitable for pytest, Playwright, Newman, or JMeter automation |
| KnowledgeFeedbackAgent | Convert accepted cases, rejected cases, review comments, failures, and reports into improved knowledge |

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

Reference use:

- Awesome LLM Apps: use as examples for agent/RAG app patterns only.
- PageIndex: use for tree-structured, traceable document retrieval concepts and
  optional self-host/API evaluation.
- Haystack or LlamaIndex: use as the first production-style
  `KnowledgeAdapter` provider candidates.
- Microsoft GraphRAG: use for later relationship graph extraction and
  reasoning, preferably offline/background.
- RAGFlow: evaluate only as an external knowledge service, not as Chtest's
  internal product shell.

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

## Implementation Phases

### Phase 1: Test Knowledge Card Contract

- Define `TestKnowledgeCard` and `KnowledgeEvidence` contracts.
- Keep data derived from existing ContextArtifact and Artifact rows at first.
- Add import/extraction evidence but no vector database or graph runtime.
- Add golden smoke proving generated cases cite knowledge evidence.

### Phase 2: Knowledge Ingestion And Review

- Add KnowledgeIngestionAgent with deterministic mock/provider behavior first.
- Add review UI for extracted knowledge cards.
- Allow users to mark knowledge as approved, stale, unsafe, duplicate, or
  prompt-eligible.

### Phase 3: Case Generation With Evidence

- Update CaseGenerationAgent output contract so every candidate cites evidence,
  risk coverage, and generation reason.
- Add CaseReviewAgent quality scores and rejection reasons.
- Add CoverageGapAgent only after baseline evidence-backed generation works.

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
