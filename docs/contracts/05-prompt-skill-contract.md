# Chtest Prompt And Skill Contract

## 1. 文档目的

本文定义 PromptVersion 和 SkillVersion 的文件格式、版本规则、输出约束和质量门禁。Chtest 的 AI 能力必须可追溯、可复盘、可比较，不能依赖临时口头提示词。

## 2. Prompt 目录

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
```

## 3. Skill 目录

```text
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

Slice 31 adds the knowledge-driven seeds above as versioned prompt/skill files.
They are seed artifacts only. They do not enable RAG runtime, vector databases,
GraphRAG runtime, MCP runtime, external provider calls, generated-case
auto-approval, or tool execution by themselves.

## 4. Prompt 文件格式

每个 Prompt 文件必须包含以下段落：

```markdown
# Prompt: requirement_review v1

## Agent
RequirementReviewAgent

## Purpose
Generate six-dimensional requirement review output.

## Input Schema
```json
{"type":"object","required":["requirement"],"properties":{"requirement":{"type":"string"}}}
```

## Output Schema
```json
{"type":"object","required":["scores","issues"],"properties":{"scores":{"type":"object"},"issues":{"type":"array"}}}
```

## Instructions
Return JSON only. Do not include markdown fences in the model output.

## Failure Output
{"error_code":"UNABLE_TO_REVIEW","message":"reason","recoverable":true}
```

规则：

- 主输出必须是 JSON。
- 不允许把自由散文作为主结果。
- 输出 schema 必须能被后端校验。
- Prompt 内容变化必须生成新 hash。
- 已发布版本不能覆盖。

## 4.1 Context Input Contract

RequirementReviewAgent and CaseGenerationAgent may receive local ContextArtifacts.

Prompt input must include:

```json
{
  "use_knowledge": false,
  "context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
  "context_manifest": [
    {
      "artifact_id": "00000000-0000-0000-0000-000000000371",
      "title": "coupon-api-notes.md",
      "mime_type": "text/markdown",
      "sha256": "sha256:example",
      "redaction_applied": false
    }
  ]
}
```

Rules:

- `use_knowledge=false` means external RAG/KnowledgeAdapter is disabled.
- ContextArtifact content is still available to the prompt when `context_artifact_ids` is non-empty.
- Prompt input artifacts must save `context_manifest.json`.
- Model output or parsed AITask output must expose `used_context_artifact_ids`.
- Model output must not claim external evidence when `used_knowledge=false`.

### 4.1.1 KnowledgeAdapter Provider Evaluation Plan Contract

This contract defines prompt/skill trace rules for future KnowledgeAdapter
provider evaluation plans. It is contract-only planning evidence and does not
assemble prompts, write runtime `prompt_input.json`, execute AITasks, call
providers, integrate provider SDKs, run retrieval, change ranking, create
vector indexes, create embeddings, rerank, run background indexing, run graph
jobs, invoke MCP runtime, enable providers, mutate KnowledgeAdapterConfig
runtime state, mutate KnowledgeEvidence rows, render frontend pages, add RBAC,
create tenants, change permissions, or install packages.

KnowledgeAdapter provider evaluation plan input must include:

- `knowledge_adapter_provider_evaluation_plan_action=evaluate_knowledge_adapter_provider_plan`.
- PromptVersion id/name/version and SkillVersion id/name/version when the
  evaluation is produced by a prompt or skill.
- Candidate provider name and provider family such as Haystack, LlamaIndex,
  GraphRAG, or local adapter.
- Provider version and adapter version.
- License name, license URL, license compatibility notes, and license review.
- Reference intake URLs or documentation snapshot artifact ids.
- Supported retrieval modes and supported source types.
- Expected KnowledgeEvidence normalization fields.
- Expected provider_state values and provider_state recommendation.
- Disabled by default policy.
- Fallback behavior expectations.
- Metrics to collect.
- Safety, redaction, source-hash, source manifest, and ReviewHistory ids.
- Failure code and visible reason when applicable.

KnowledgeAdapter provider evaluation plan output may include:

- Provider evaluation plan id or artifact id.
- `knowledge_adapter_provider_evaluation_plan` artifact or manifest naming.
- Evaluation actions such as `evaluate_provider_candidate`,
  `record_provider_evaluation`, `block_provider_candidate`, or
  `request_provider_evaluation_revision`.
- Provider suitability status values: `not_evaluated`, `suitable`,
  `suitable_with_constraints`, `blocked`, `needs_revision`, and
  `unsupported`.
- Normalized KnowledgeEvidence requirements.
- Provider_state recommendation.
- Disabled by default decision.
- Fallback behavior summary.
- License review result.
- Reference intake summary.
- Metrics plan.
- Blocker reasons and unresolved safety questions.
- Fallback labels such as `fallback_required`, `local_no_knowledge_fallback`,
  `normalization_required`, `citation_traceability_required`, and
  `license_review_required`.
- Source manifest ids, source hashes, ReviewHistory links, failure code, and
  visible reason.

KnowledgeAdapter provider evaluation plan rules:

- Provider evaluation records are planning evidence only. They must not be
  treated as provider configuration enablement, runtime provider connectivity,
  retrieval permission, prompt eligibility, or proof that provider evidence was
  used.
- `provider_state` is display/health metadata and must not start runtime
  retrieval.
- Disabled by default is required until a later scoped integration explicitly
  enables a provider.
- Fallback behavior must preserve local/no-knowledge evidence instead of
  fabricating KnowledgeEvidence.
- `used_knowledge` must not be auto-marked true by provider evaluation.
- Provider-specific payloads must not leak into TestKnowledgeCard,
  KnowledgeEvidence, GeneratedCaseCandidate, prompt context evidence, reports,
  or review surfaces.
- Missing, stale, unsafe, unlicensed, license-unknown, version-unknown,
  reference-missing, reference-mismatched, normalization-unsupported,
  redaction-failed, provider-state-unsafe, fallback-missing, cross-project,
  unbounded, credential-required, runtime-required, or provider-evaluation-
  mismatched input must produce a failure code and visible reason and must not
  append a successful provider-ready state.
- This contract must not write runtime `prompt_input.json`, execute a prompt,
  call a provider, integrate an SDK, store credentials, fetch remote URLs,
  create a vector index, create embeddings, rerank, run background indexing,
  run a graph job, invoke MCP runtime, create provider-backed prompt context
  evidence, mutate KnowledgeAdapterConfig outside declared evaluation
  evidence, mutate KnowledgeEvidence, render frontend pages, expose backend
  feature APIs, add endpoints, routers, services, workers, queues, schedulers,
  run migrations, add package upgrades, add RBAC, create tenants, or change
  permissions.

### 4.2 TestKnowledgeCard Prompt Context Evidence Contract

This contract defines prompt/skill trace rules for future TestKnowledgeCard
prompt context evidence. It is contract-only and does not assemble prompts,
execute AITasks, call providers, run retrieval, change ranking, create vector
indexes, create embeddings, rerank, run graph jobs, invoke MCP runtime, or
mutate TestKnowledgeCard rows.

Prompt context evidence input must include:

- `prompt_context_evidence_action=build_prompt_context_evidence`.
- PromptVersion id and SkillVersion id.
- PromptVersion name/version and SkillVersion name/version when available.
- Retrieval boundary artifact id.
- Selected TestKnowledgeCard ids and omitted TestKnowledgeCard ids.
- Prompt eligibility artifact ids and ReviewHistory ids.
- Source manifest ids, source artifact ids, source hash values, and source
  trace labels.
- Context manifest artifact id when available.
- Omission reason values and failure code when applicable.

Prompt context evidence rules:

- Every prompt context evidence artifact must preserve PromptVersion and
  SkillVersion trace before any selected card evidence is eligible for future
  prompt context.
- `context_manifest` entries for TestKnowledgeCard-derived context must point
  to prompt context evidence artifacts, source hashes, source artifact ids,
  bounded snippet metadata, redaction status, and `safe_to_show=true` evidence.
- Bounded snippet text may be present only when safe-to-show and reviewed
  redaction are proven. Otherwise the context entry must use source hash or
  source quote/hash pointer and record omission reason.
- A prompt or skill must not cite TestKnowledgeCard content unless the
  TestKnowledgeCard id appears in prompt context evidence and the referenced
  retrieval boundary artifact selected it.
- Prompt context evidence must not include raw large source text, hidden model
  context, unsafe provider payloads, vector store payloads, embedding vectors,
  reranker traces, graph runtime payloads, credentials, tokens, OAuth material,
  or provider request payloads.
- This contract must not set `used_knowledge=true`, write runtime
  `prompt_input.json`, execute a prompt, call a provider, mutate
  PromptVersion/SkillVersion rows, mutate artifacts outside declared prompt
  context evidence, approve generated cases, or bypass human review gates.

### 4.3 TestKnowledgeCard Prompt Context Consumption Contract

This contract defines prompt/skill citation rules for future TestKnowledgeCard
prompt context consumption. It is contract-only and does not assemble prompts,
execute AITasks, call providers, run retrieval, change ranking, create vector
indexes, create embeddings, rerank, run graph jobs, invoke MCP runtime, mutate
TestKnowledgeCard rows, or generate model citations.

Prompt context consumption input must include:

- `prompt_context_consumption_action=consume_prompt_context_evidence`.
- PromptVersion id/name/version and SkillVersion id/name/version.
- Prompt context evidence artifact id and context manifest artifact id.
- Consumed TestKnowledgeCard ids and consumed context entry ids.
- Consumed source hashes or source quote/hash pointers.
- Source artifact ids, source sections, source manifest ids, and retrieval
  boundary artifact id.
- Prompt eligibility artifact ids and ReviewHistory ids.
- Consuming agent step, intended output artifact type, skipped evidence ids,
  skip reasons, unsupported claim markers, and failure code when applicable.

Prompt context consumption rules:

- A prompt or skill may mark `used_knowledge=true` only when a future scoped
  consumption record includes at least one valid citation to consumed prompt
  context evidence.
- Every output citation that claims TestKnowledgeCard support must reference the
  prompt context evidence artifact id, context entry id, TestKnowledgeCard id,
  source hash or source quote/hash pointer, source artifact id, source section,
  ReviewHistory id, PromptVersion, and SkillVersion.
- `used_knowledge=false` is required when no valid prompt context evidence is
  consumed, when citations are missing, or when cited evidence is stale, unsafe,
  revoked, cross-project, unbounded, redaction-failed, context-mismatched,
  prompt-version-mismatched, skill-version-mismatched, or evidence-mismatched.
- Unsupported claims must remain visible as unsupported claims or review
  findings. They must not be promoted into knowledge-backed facts only because
  prompt context evidence was available.
- Prompt context consumption must not include raw large source text, hidden
  model context, unsafe provider payloads, vector store payloads, embedding
  vectors, reranker traces, graph runtime payloads, credentials, tokens, OAuth
  material, or provider request payloads.
- This contract must not write runtime `prompt_input.json`, execute a prompt,
  call a provider, mutate PromptVersion/SkillVersion rows, mutate prompt
  context evidence, mutate artifacts outside declared prompt context
  consumption, approve generated cases, auto-mark `used_knowledge=true`, or
  bypass human review gates.

### 4.4 TestKnowledgeCard Prompt Context Audit Summary Contract

This contract defines prompt/skill trace rules for future read-only audit
summaries of TestKnowledgeCard prompt context consumption. It is contract-only
and does not assemble prompts, execute AITasks, call providers, run retrieval,
change ranking, create vector indexes, create embeddings, rerank, run graph
jobs, invoke MCP runtime, render frontend pages, generate reports, mutate
TestKnowledgeCard rows, or generate model citations.

Prompt context audit summary input must include:

- `prompt_context_audit_summary_action=summarize_prompt_context_consumption`.
- PromptVersion id/name/version and SkillVersion id/name/version.
- Prompt context consumption artifact id.
- Prompt context evidence artifact id and context manifest artifact id.
- `used_knowledge` decision and usage status.
- Output citation ids and cited TestKnowledgeCard ids.
- Cited context entry ids, source hashes, source artifact ids, and source
  sections.
- Skipped evidence ids, skip reasons, unsupported claim summaries, and failure
  code when applicable.
- ReviewHistory ids and review flags.

Prompt context audit summary rules:

- Audit summaries must preserve PromptVersion and SkillVersion trace from the
  referenced prompt context consumption evidence.
- `used_knowledge` must be copied from prompt context consumption evidence and
  must not be recomputed, rewritten, or auto-marked by an audit summary.
- Cited entries must reference existing output citations, TestKnowledgeCard ids,
  context entry ids, source hashes or source quote/hash pointers,
  ReviewHistory ids, PromptVersion, and SkillVersion.
- Skipped evidence and unsupported claims must remain visible as skipped or
  unsupported. They must not be promoted into knowledge-backed facts only
  because an audit summary is generated.
- Prompt context audit summary must not include raw large source text, hidden
  model context, unsafe provider payloads, vector store payloads, embedding
  vectors, reranker traces, graph runtime payloads, credentials, tokens, OAuth
  material, provider request payloads, frontend-rendered markup, or
  report-rendered payloads.
- This contract must not write runtime `prompt_input.json`, execute a prompt,
  call a provider, mutate PromptVersion/SkillVersion rows, mutate prompt
  context consumption evidence, mutate artifacts outside declared prompt
  context audit summary, approve generated cases, rewrite `used_knowledge`,
  render frontend pages, generate reports, or bypass human review gates.

### 4.5 TestKnowledgeCard Prompt Context Audit Review Decision Contract

This contract defines prompt/skill trace rules for future human review
decisions of TestKnowledgeCard prompt context audit summaries. It is
contract-only and does not assemble prompts, execute AITasks, call providers,
run retrieval, change ranking, create vector indexes, create embeddings,
rerank, run graph jobs, invoke MCP runtime, render frontend pages, generate
reports, mutate TestKnowledgeCard rows, create prompt eligibility, or generate
model citations.

Prompt context audit review decision input must include:

- `prompt_context_audit_review_decision_action=review_prompt_context_audit_summary`.
- PromptVersion id/name/version and SkillVersion id/name/version.
- Prompt context audit summary artifact id.
- Prompt context consumption artifact id.
- Prompt context evidence artifact id and context manifest artifact id.
- `used_knowledge` decision and usage status.
- Output citation ids and cited TestKnowledgeCard ids.
- Cited context entry ids, source hashes, source artifact ids, and source
  sections.
- Skipped evidence ids, skip reasons, unsupported claim summaries, review
  flags, and failure code when applicable.
- Review action, reviewer comment, accepted citation ids, questioned citation
  ids, rejected citation ids, follow-up flags, and requested clarification.
- ReviewHistory ids from prior evidence and the review decision ReviewHistory
  id when a future scoped workflow persists one.

Prompt context audit review decision rules:

- Audit review decisions must preserve PromptVersion and SkillVersion trace
  from the referenced prompt context audit summary evidence.
- `used_knowledge` must be copied from prompt context audit summary evidence
  and must not be recomputed, rewritten, or auto-marked by a review decision.
- Allowed review actions are `accepted`, `needs_clarification`,
  `rejected_for_missing_evidence`, `rejected_for_unsupported_claim`,
  `rejected_for_citation_mismatch`, `rejected_for_stale_evidence`, and
  `rejected_for_cross_project_evidence`.
- Accepted, questioned, and rejected citation ids must reference existing
  output citations, TestKnowledgeCard ids, context entry ids, source hashes or
  source quote/hash pointers, ReviewHistory ids, PromptVersion, and
  SkillVersion.
- `accepted` must not create prompt eligibility, approve TestKnowledgeCard
  content, approve generated cases, mutate prompt context audit summary
  evidence, or change `used_knowledge`.
- `needs_clarification` and rejected decisions must keep skipped evidence and
  unsupported claims visible. They must not be promoted into knowledge-backed
  facts, deleted, or replaced with generated citations.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched, or audit
  summary-mismatched input must produce a failure code and must not append a
  successful ReviewHistory decision.
- Prompt context audit review decision must not include raw large source text,
  hidden model context, unsafe provider payloads, vector store payloads,
  embedding vectors, reranker traces, graph runtime payloads, credentials,
  tokens, OAuth material, provider request payloads, frontend-rendered markup,
  or report-rendered payloads.
- This contract must not write runtime `prompt_input.json`, execute a prompt,
  call a provider, mutate PromptVersion/SkillVersion rows, mutate prompt
  context audit summary evidence, mutate artifacts outside declared prompt
  context audit review decision, approve generated cases, create prompt
  eligibility, rewrite `used_knowledge`, render frontend pages, generate
  reports, or bypass human review gates.

### 4.6 TestKnowledgeCard Prompt Context Audit Review Summary Export Contract

This contract defines prompt/skill trace rules for future summary exports of
TestKnowledgeCard prompt context audit review decisions. It is contract-only
and does not assemble prompts, execute AITasks, call providers, run retrieval,
change ranking, create vector indexes, create embeddings, rerank, run graph
jobs, invoke MCP runtime, render frontend pages, generate reports, expose
export/download endpoints, mutate TestKnowledgeCard rows, create prompt
eligibility, or generate model citations.

Prompt context audit review summary export input must include:

- `prompt_context_audit_review_summary_export_action=export_prompt_context_audit_review_summary`.
- PromptVersion id/name/version and SkillVersion id/name/version.
- Prompt context audit review decision artifact id.
- Prompt context audit summary artifact id.
- Prompt context consumption artifact id.
- Prompt context evidence artifact id and context manifest artifact id.
- `used_knowledge` decision and usage status.
- Review action and review outcome summary.
- Accepted citation ids, questioned citation ids, rejected citation ids, and
  output citation ids.
- Cited TestKnowledgeCard ids, context entry ids, source hashes, source
  artifact ids, and source sections.
- Skipped evidence ids, skip reasons, unsupported claim references, unresolved
  follow-up flags, reviewer comment summary, and failure code when applicable.
- ReviewHistory ids from prior evidence and the review decision ReviewHistory
  id when a future scoped workflow persists one.

Prompt context audit review summary export rules:

- Summary exports must preserve PromptVersion and SkillVersion trace from the
  referenced prompt context audit review decision evidence.
- `used_knowledge` must be copied from prompt context audit review decision
  evidence and must not be recomputed, rewritten, or auto-marked by a summary
  export.
- Accepted, questioned, and rejected citation groups must reference existing
  output citations, TestKnowledgeCard ids, context entry ids, source hashes or
  source quote/hash pointers, ReviewHistory ids, PromptVersion, and
  SkillVersion.
- Accepted citation groups must not create prompt eligibility, approve
  TestKnowledgeCard content, approve generated cases, mutate prompt context
  audit review decision evidence, or change `used_knowledge`.
- Questioned citation groups, rejected citation groups, unresolved follow-up
  flags, skipped evidence, and unsupported claims must remain visible. They
  must not be promoted into knowledge-backed facts, deleted, filtered, or
  replaced with generated citations.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched,
  audit-summary-mismatched, or review-decision-mismatched input must produce a
  failure code and must not append a successful summary export.
- Prompt context audit review summary export must not include raw large source
  text, hidden model context, unsafe provider payloads, vector store payloads,
  embedding vectors, reranker traces, graph runtime payloads, credentials,
  tokens, OAuth material, provider request payloads, frontend-rendered markup,
  report-rendered payloads, export-rendered payloads, or downloadable provider
  payloads.
- This contract must not write runtime `prompt_input.json`, execute a prompt,
  call a provider, mutate PromptVersion/SkillVersion rows, mutate prompt
  context audit review decision evidence, mutate artifacts outside declared
  prompt context audit review summary export, approve generated cases, create
  prompt eligibility, rewrite `used_knowledge`, render frontend pages,
  generate reports, expose export/download endpoints, or bypass human review
  gates.

### 4.7 TestKnowledgeCard Prompt Context Review Discrepancy Tracking Contract

This contract defines prompt/skill trace rules for future discrepancy tracking
across TestKnowledgeCard prompt context consumption, audit summaries, review
decisions, and summary exports. It is contract-only and does not assemble
prompts, execute AITasks, call providers, run retrieval, change ranking, create
vector indexes, create embeddings, rerank, run graph jobs, invoke MCP runtime,
render frontend pages, generate reports, expose export/download endpoints,
mutate TestKnowledgeCard rows, create prompt eligibility, auto-resolve
discrepancies, or generate model citations.

Prompt context review discrepancy input must include:

- `prompt_context_review_discrepancy_action=track_prompt_context_review_discrepancy`.
- PromptVersion id/name/version and SkillVersion id/name/version.
- Prompt context audit review summary export artifact id.
- Prompt context audit review decision artifact id.
- Prompt context audit summary artifact id.
- Prompt context consumption artifact id.
- Prompt context evidence artifact id and context manifest artifact id.
- `used_knowledge` decision and usage status.
- Review action, review outcome summary, accepted citation group, questioned
  citation group, and rejected citation group.
- Affected citation ids, skipped evidence ids, skip reasons, unsupported claim
  references, unresolved follow-up flags, discrepancy type, evidence gap
  summary, mismatch reason, reviewer note, severity, resolution status, and
  failure code when applicable.
- Source hashes, source artifact ids, source sections, ReviewHistory ids, and
  review decision ReviewHistory id when available.

Prompt context review discrepancy tracking rules:

- Discrepancy records must preserve PromptVersion and SkillVersion trace from
  referenced review summary export, audit review decision, audit summary, and
  consumption evidence.
- `used_knowledge` must be copied from referenced review evidence and must not
  be recomputed, rewritten, or auto-marked by discrepancy tracking.
- Affected citation ids must reference existing output citations,
  TestKnowledgeCard ids, context entry ids, source hashes or source quote/hash
  pointers, ReviewHistory ids, PromptVersion, and SkillVersion.
- Discrepancy types include `citation_mismatch`, `missing_evidence`,
  `unsupported_claim`, `stale_evidence`, `cross_project_evidence`,
  `context_manifest_mismatch`, `prompt_version_mismatch`,
  `skill_version_mismatch`, `used_knowledge_mismatch`, and
  `unresolved_follow_up`.
- Resolution status values are audit labels only. They must not create prompt
  eligibility, approve TestKnowledgeCard content, approve generated cases,
  mutate review summary export evidence, auto-resolve discrepancies, or change
  `used_knowledge`.
- Affected citation ids, questioned/rejected citation groups, unresolved
  follow-up flags, skipped evidence, unsupported claims, evidence gap summary,
  and mismatch reason must remain visible. They must not be promoted into
  knowledge-backed facts, deleted, filtered, or replaced with generated
  citations.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, evidence-mismatched,
  audit-summary-mismatched, review-decision-mismatched, or
  summary-export-mismatched input must produce a failure code and must not
  append a successful discrepancy record.
- Prompt context review discrepancy tracking must not include raw large source
  text, hidden model context, unsafe provider payloads, vector store payloads,
  embedding vectors, reranker traces, graph runtime payloads, credentials,
  tokens, OAuth material, provider request payloads, frontend-rendered markup,
  report-rendered payloads, export-rendered payloads, downloadable provider
  payloads, or generated replacement evidence.
- This contract must not write runtime `prompt_input.json`, execute a prompt,
  call a provider, mutate PromptVersion/SkillVersion rows, mutate review
  summary export evidence, mutate artifacts outside declared prompt context
  review discrepancy tracking, approve generated cases, create prompt
  eligibility, rewrite `used_knowledge`, render frontend pages, generate
  reports, expose export/download endpoints, auto-resolve discrepancies, or
  bypass human review gates.

Prompt context discrepancy resolution review input must include:

- `prompt_context_discrepancy_resolution_review_action=review_prompt_context_discrepancy_resolution`.
- PromptVersion id/name/version and SkillVersion id/name/version.
- Prompt context review discrepancy artifact id.
- Prompt context audit review summary export artifact id.
- Prompt context audit review decision artifact id.
- Prompt context audit summary artifact id.
- Prompt context consumption artifact id.
- Prompt context evidence artifact id and context manifest artifact id.
- `used_knowledge` decision.
- Discrepancy type, affected citation ids, evidence gap summary, mismatch
  reason, reviewer note from discrepancy tracking, severity, current
  resolution status, unresolved follow-up flags, and unsupported claim
  references.
- Resolution action, accepted discrepancy ids, rejected discrepancy ids,
  acknowledged discrepancy ids, clarification requested fields, resulting
  resolution status, reviewer note, follow-up flags, and failure code when
  applicable.
- Visible reason when resolution review input is invalid.
- Source hashes, source artifact ids, source sections, ReviewHistory ids, and
  discrepancy ReviewHistory id when available.

Prompt context discrepancy resolution review rules:

- Resolution review records must preserve PromptVersion and SkillVersion trace
  from referenced discrepancy tracking, review summary export, audit review
  decision, audit summary, and consumption evidence.
- `used_knowledge` must be copied from referenced review evidence and must not
  be recomputed, rewritten, or auto-marked by discrepancy resolution review.
- Accepted discrepancy ids, rejected discrepancy ids, acknowledged discrepancy
  ids, and affected citation ids must reference existing discrepancy ids,
  output citations, TestKnowledgeCard ids, context entry ids, source hashes or
  source quote/hash pointers, ReviewHistory ids, PromptVersion, and
  SkillVersion.
- Resolution action values include `acknowledge_discrepancy`,
  `reject_discrepancy_resolution`, `request_discrepancy_clarification`, and
  `mark_resolved_by_later_review`.
- Resulting resolution status values are audit labels only. They must not
  create prompt eligibility, approve TestKnowledgeCard content, approve
  generated cases, mutate prompt context review discrepancy evidence,
  auto-resolve discrepancies, or change `used_knowledge`.
- Accepted/rejected/acknowledged discrepancy ids, affected citation ids,
  questioned/rejected citation groups, unresolved follow-up flags, skipped
  evidence, unsupported claims, evidence gap summary, and mismatch reason must
  remain visible. They must not be promoted into knowledge-backed facts,
  deleted, filtered, or replaced with generated citations.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, discrepancy-mismatched,
  evidence-mismatched, audit-summary-mismatched, review-decision-mismatched,
  or summary-export-mismatched input must produce a failure code and visible
  reason and must not append a successful resolution review.
- Prompt context discrepancy resolution review must not include raw large
  source text, hidden model context, unsafe provider payloads, vector store
  payloads, embedding vectors, reranker traces, graph runtime payloads,
  credentials, tokens, OAuth material, provider request payloads,
  frontend-rendered markup, report-rendered payloads, export-rendered
  payloads, downloadable provider payloads, or generated replacement evidence.
- This contract must not write runtime `prompt_input.json`, execute a prompt,
  call a provider, mutate PromptVersion/SkillVersion rows, mutate prompt
  context review discrepancy evidence, mutate artifacts outside declared
  prompt context discrepancy resolution review, approve generated cases, create
  prompt eligibility, rewrite `used_knowledge`, render frontend pages,
  generate reports, expose export/download endpoints, auto-resolve
  discrepancies, or bypass human review gates.

Prompt context discrepancy resolution summary export input must include:

- `prompt_context_discrepancy_resolution_summary_export_action=export_prompt_context_discrepancy_resolution_summary`.
- PromptVersion id/name/version and SkillVersion id/name/version.
- Prompt context discrepancy resolution review artifact id.
- Prompt context review discrepancy artifact id.
- Prompt context audit review summary export artifact id.
- Prompt context audit review decision artifact id.
- Prompt context audit summary artifact id.
- Prompt context consumption artifact id.
- Prompt context evidence artifact id and context manifest artifact id.
- `used_knowledge` decision and usage status.
- Resolution action, resulting resolution status, accepted discrepancy ids,
  rejected discrepancy ids, acknowledged discrepancy ids, clarification
  requested fields, affected citation ids, evidence gap summary, mismatch
  reason, reviewer note, follow-up flags, unsupported claim references, and
  failure code when applicable.
- Resolution outcome summary, accepted discrepancy group, rejected discrepancy
  group, acknowledged discrepancy group, clarification requested field group,
  unresolved follow-up flag group, reviewer comment summary, resulting
  resolution status group, and visible reason when export input is invalid.
- Source hashes, source artifact ids, source sections, ReviewHistory ids,
  discrepancy ReviewHistory id, and resolution review ReviewHistory id when
  available.

Prompt context discrepancy resolution summary export rules:

- Resolution summary export records must preserve PromptVersion and
  SkillVersion trace from referenced resolution review, discrepancy tracking,
  review summary export, audit review decision, audit summary, and consumption
  evidence.
- `used_knowledge` must be copied from referenced review evidence and must not
  be recomputed, rewritten, or auto-marked by discrepancy resolution summary
  export.
- Accepted discrepancy group, rejected discrepancy group, acknowledged
  discrepancy group, clarification requested field group, and affected
  citation ids must reference existing discrepancy ids, output citations,
  TestKnowledgeCard ids, context entry ids, source hashes or source quote/hash
  pointers, ReviewHistory ids, PromptVersion, and SkillVersion.
- Resolution outcome summary and resulting resolution status group are audit
  labels only. They must not create prompt eligibility, approve
  TestKnowledgeCard content, approve generated cases, mutate discrepancy
  resolution review evidence, auto-resolve discrepancies, or change
  `used_knowledge`.
- Accepted/rejected/acknowledged discrepancy groups, clarification requested
  field group, unresolved follow-up flag group, affected citation ids,
  questioned/rejected citation groups, skipped evidence, unsupported claims,
  evidence gap summary, and mismatch reason must remain visible. They must not
  be promoted into knowledge-backed facts, deleted, filtered, or replaced with
  generated citations.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, discrepancy-mismatched,
  resolution-review-mismatched, evidence-mismatched, audit-summary-mismatched,
  review-decision-mismatched, or summary-export-mismatched input must produce
  a failure code and visible reason and must not append a successful resolution
  summary export.
- Prompt context discrepancy resolution summary export must not include raw
  large source text, hidden model context, unsafe provider payloads, vector
  store payloads, embedding vectors, reranker traces, graph runtime payloads,
  credentials, tokens, OAuth material, provider request payloads,
  frontend-rendered markup, report-rendered payloads, export-rendered
  payloads, downloadable provider payloads, or generated replacement evidence.
- This contract must not write runtime `prompt_input.json`, execute a prompt,
  call a provider, mutate PromptVersion/SkillVersion rows, mutate prompt
  context discrepancy resolution review evidence, mutate artifacts outside
  declared prompt context discrepancy resolution summary export, approve
  generated cases, create prompt eligibility, rewrite `used_knowledge`, render
  frontend pages, generate reports, expose export/download endpoints,
  auto-resolve discrepancies, or bypass human review gates.

Prompt context discrepancy resolution audit handoff input must include:

- `prompt_context_discrepancy_resolution_audit_handoff_action=build_prompt_context_discrepancy_resolution_audit_handoff`.
- PromptVersion id/name/version and SkillVersion id/name/version.
- Prompt context discrepancy resolution summary export artifact id.
- Prompt context discrepancy resolution review artifact id.
- Prompt context review discrepancy artifact id.
- Prompt context audit review summary export artifact id.
- Prompt context audit review decision artifact id.
- Prompt context audit summary artifact id.
- Prompt context consumption artifact id.
- Prompt context evidence artifact id and context manifest artifact id.
- `used_knowledge` decision and usage status.
- Resolution outcome summary, accepted discrepancy group, rejected discrepancy
  group, acknowledged discrepancy group, clarification requested fields,
  clarification requested field group, resulting resolution status group,
  affected citation ids, evidence gap summary, mismatch reason, unresolved
  follow-up flags, unsupported claim references, and failure code when
  applicable.
- Handoff summary, evidence chain status, included artifact ids, excluded
  artifact reasons, unresolved evidence gaps, source manifest ids, source
  hashes, context manifest references, ReviewHistory links, failure code, and
  visible reason when audit handoff input is invalid.
- Source hashes, source artifact ids, source sections, source quote/hash
  pointers, ReviewHistory ids, discrepancy ReviewHistory id, resolution review
  ReviewHistory id, and summary export ReviewHistory id when available.

Prompt context discrepancy resolution audit handoff rules:

- Audit handoff records must preserve PromptVersion and SkillVersion trace from
  referenced resolution summary export, resolution review, discrepancy
  tracking, review summary export, audit review decision, audit summary, and
  consumption evidence.
- `used_knowledge` must be copied from referenced summary export and review
  evidence and must not be recomputed, rewritten, or auto-marked by discrepancy
  resolution audit handoff.
- Included artifact ids must reference persisted artifacts. Excluded artifact
  reasons must name why an upstream artifact was not included and must not hide
  unresolved follow-up flags, unsupported claims, skipped evidence, source
  hashes, evidence gap summary, mismatch reason, ReviewHistory links,
  PromptVersion, or SkillVersion.
- Evidence chain status values are `complete`, `incomplete`, `blocked`, and
  `failed_validation`. They are audit labels only. They must not create prompt
  eligibility, approve TestKnowledgeCard content, approve generated cases,
  mutate discrepancy resolution summary export evidence, auto-resolve
  discrepancies, or change `used_knowledge`.
- Handoff summary, included artifact ids, excluded artifact reasons,
  unresolved evidence gaps, unresolved follow-up flags, affected citation ids,
  questioned/rejected citation groups, skipped evidence, unsupported claims,
  source hashes, evidence gap summary, and mismatch reason must remain visible.
  They must not be promoted into knowledge-backed facts, deleted, filtered, or
  replaced with generated citations.
- Missing, stale, unsafe, cross-project, revoked, unsupported, unbounded,
  citation-mismatched, context-mismatched, prompt-version-mismatched,
  skill-version-mismatched, redaction-failed, discrepancy-mismatched,
  resolution-review-mismatched, summary-export-mismatched,
  evidence-mismatched, audit-summary-mismatched, review-decision-mismatched,
  audit-handoff-mismatched, or incomplete required input must produce a failure
  code and visible reason and must not append a successful audit handoff.
- Prompt context discrepancy resolution audit handoff must not include raw
  large source text, hidden model context, unsafe provider payloads, vector
  store payloads, embedding vectors, reranker traces, graph runtime payloads,
  credentials, tokens, OAuth material, provider request payloads,
  frontend-rendered markup, report-rendered payloads, export-rendered
  payloads, downloadable provider payloads, external archive payloads, runtime
  `prompt_input.json`, or generated replacement evidence.
- This contract must not write runtime `prompt_input.json`, execute a prompt,
  call a provider, mutate PromptVersion/SkillVersion rows, mutate prompt
  context discrepancy resolution summary export evidence, mutate artifacts
  outside declared prompt context discrepancy resolution audit handoff, upload
  artifacts, approve generated cases, create prompt eligibility, rewrite
  `used_knowledge`, render frontend pages, generate reports, expose
  export/download endpoints, integrate with an external archive, auto-resolve
  discrepancies, or bypass human review gates.

## 5. Skill 文件格式

每个 Skill 文件必须包含以下段落：

```markdown
# Skill: test-case-generation-skill v1

## Applies To
- CaseGenerationAgent

## Methodology
- Equivalence partitioning
- Boundary value analysis
- State transition testing
- Error guessing

## Input Contract
Describe accepted input fields.

## Output Contract
Describe required output fields.

## Quality Gates
- Every case must have explicit expected result.
- Every case must reference requirement text.

## Forbidden Actions
- Do not create vague cases like "verify it works".
- Do not skip negative scenarios for P0/P1 flows.

## Tool Permissions
- KnowledgeAdapter.search_context optional.
```

## 6. V1 Prompt/Skill 映射

| 流程 | Agent | Prompt | Skill |
|---|---|---|---|
| 需求评审 | RequirementReviewAgent | requirement_review:v1 | requirement-review-skill:v1 |
| 风险矩阵 | RequirementReviewAgent | risk_matrix:v1 | requirement-review-skill:v1 |
| 用例生成 | CaseGenerationAgent | case_generation:v1 | test-case-generation-skill:v1 |
| 用例评审 | CaseReviewAgent | case_review:v1 | testcase-review-skill:v1 |
| 自动化草稿 | AutomationDraftAgent | automation_draft_generation:v1 | automation-draft-skill:v1 |
| CI/CD 变更分析 | CICDChangeAnalysisAgent | cicd_change_analysis:v1 | regression-selection-skill:v1 |
| 单测 patch | UnitTestAgent | unit_test_generation:v1 | unit-test-generation-skill:v1 |
| 回归选择 | RegressionAgent | regression_selection:v1 | regression-selection-skill:v1 |
| 工具执行计划 | ToolExecutionAgent | tool_execution:v1 | tool-execution-skill:v1 |
| 失败归因 | FailureAnalysisAgent | failure_analysis:v1 | failure-analysis-skill:v1 |
| 报告生成 | ReportAgent | report_generation:v1 | report-generation-skill:v1 |
| 知识卡片抽取 | KnowledgeIngestionAgent | knowledge_card_extraction:v1 | knowledge-ingestion-skill:v1 |
| 需求理解 | RequirementUnderstandingAgent | requirement_understanding:v1 | requirement-review-skill:v1 |
| 风险分析 | RiskAnalysisAgent | risk_analysis:v1 | risk-analysis-skill:v1 |
| 覆盖分析 | CoverageAnalysisAgent | coverage_analysis:v1 | coverage-analysis-skill:v1 |
| 测试设计 | TestDesignAgent | test_design:v1 | test-design-skill:v1 |
| 证据化用例生成 | CaseGenerationAgent | evidence_case_generation:v1 | test-case-generation-skill:v1 |
| 证据化用例评审 | CaseReviewAgent | evidence_case_review:v1 | testcase-review-skill:v1 |
| 用例去重 | DedupAgent | case_dedup:v1 | testcase-review-skill:v1 |
| 自动化可行性 | AutomationReadinessAgent | automation_readiness:v1 | automation-draft-skill:v1 |
| 知识反馈 | KnowledgeFeedbackAgent | knowledge_feedback:v1 | knowledge-feedback-skill:v1 |

## 6.1 Requirement-To-Reviewed-Case Workflow Seed Contract

This workflow contract binds the planned requirement-to-reviewed-case agents to
PromptVersion and SkillVersion seed files. It is seed/contract only: it does
not enable runtime orchestration, workflow queues, RAG runtime, MCP runtime,
provider calls, vector search, graph runtime, background indexing, tool
execution, or automatic TestCase promotion.

Global rules:

- Every step records the PromptVersion seed, SkillVersion seed, prompt hash,
  skill hash, input evidence ids, output ids, schema result, quality gate
  result, and failure behavior on the future AITask trace.
- `use_knowledge=false` remains the default unless a later runtime contract
  explicitly enables knowledge retrieval. Local ContextArtifacts may be cited
  only when they are present in `context_manifest`.
- The write permission granted by this contract is limited to the named draft
  output for each step and its AITask/artifact trace metadata. It grants no
  permission to mutate requirements, canonical TestCase records, automation
  scripts, reports, providers, vector indexes, graph stores, MCP tools, or
  external systems.
- GeneratedCaseCandidate records remain review-gated. No agent output may
  automatically promote a candidate into TestCase.
- When input evidence is missing or inconsistent, the agent must return the
  documented structured failure output instead of inventing evidence or
  fetching remote context.

| Agent | PromptVersion / SkillVersion seed | Input evidence | Output contract and write permission | Quality gates | Forbidden actions | Human gate | Failure behavior |
|---|---|---|---|---|---|---|---|
| RequirementUnderstandingAgent | `requirement_understanding:v1` / `requirement-review-skill:v1` | Requirement id, source requirement text, requirement artifact ids, ContextArtifact manifest when supplied, requester notes, prior review findings. | Requirement understanding draft with normalized intent, actors, flows, constraints, ambiguities, assumptions, evidence refs, and `used_context_artifact_ids`; write permission is AITask output plus draft artifact only. | Must cite the requirement text or artifact for each normalized statement; ambiguities and assumptions must be explicit; schema must pass. | Do not rewrite the source requirement, close ambiguity without evidence, call external knowledge, or create cases. | Human gate requires product/test owner review when ambiguities, assumptions, or conflicting evidence are present before downstream design is treated as accepted. | Return `UNABLE_TO_UNDERSTAND_REQUIREMENT` with missing/conflicting evidence details; downstream steps must treat the output as blocked, not as low-confidence success. |
| RiskAnalysisAgent | `risk_analysis:v1` / `risk-analysis-skill:v1` | Accepted or draft requirement understanding, requirement refs, domain risk notes, historical defect/knowledge evidence ids when locally supplied. | Risk analysis draft with risk ids, severity, likelihood, affected flows, evidence refs, and mitigation notes; write permission is AITask output plus risk draft artifact only. | Each P0/P1 risk must cite input evidence and affected behavior; risk ids must be stable within the output; schema must pass. | Do not fabricate production incidents, query external risk sources, change requirement priority, or approve mitigations. | Human gate requires test lead review for P0/P1 risks and unresolved mitigation gaps before case generation priority is accepted. | Return `UNABLE_TO_ANALYZE_RISK`; block risk-derived prioritization and preserve upstream understanding unchanged. |
| CoverageAnalysisAgent | `coverage_analysis:v1` / `coverage-analysis-skill:v1` | Requirement understanding, risk analysis draft, existing reviewed case ids when supplied, coverage matrix evidence, local knowledge evidence ids. | Coverage analysis draft with covered behaviors, uncovered behaviors, trace gaps, risk-to-coverage mapping, and evidence refs; write permission is AITask output plus coverage draft artifact only. | Every gap must map to a requirement or risk ref; covered claims must cite reviewed cases or supplied evidence; schema must pass. | Do not mark coverage complete without evidence, mutate existing cases, promote candidates, or pull cases from external systems. | Human gate requires reviewer confirmation for accepted residual gaps or coverage-complete claims. | Return `UNABLE_TO_ANALYZE_COVERAGE`; downstream test design must include a gap marker rather than assuming full coverage. |
| TestDesignAgent | `test_design:v1` / `test-design-skill:v1` | Requirement understanding, risk analysis, coverage analysis, constraints, target test levels/types, local methodology notes. | Test design draft with scenario groups, techniques, priorities, negative/boundary/state coverage, data needs, and trace refs; write permission is AITask output plus design draft artifact only. | Must include positive, negative, and boundary/state considerations where applicable; every scenario group must trace to requirement/risk/coverage evidence; schema must pass. | Do not generate executable automation, create TestCase records, omit P0/P1 negative paths without rationale, or use hidden knowledge. | Human gate requires test designer review before design guidance is used as accepted input for candidate generation. | Return `UNABLE_TO_DESIGN_TESTS`; case generation must stop or proceed only with an explicit human-supplied design override. |
| CaseGenerationAgent | `evidence_case_generation:v1` / `test-case-generation-skill:v1` | Human-accepted or draft test design, requirement/risk/coverage evidence, ContextArtifact manifest, existing case refs for avoidance only. | GeneratedCaseCandidate drafts with title, priority, type, preconditions, steps, expected results, input data, requirement refs, risk refs, knowledge evidence ids, and AI reason; write permission is AITask output plus generated candidate drafts only. | Every candidate must have steps, expected results, requirement refs, evidence refs, and AI reason; P0/P1 flows require negative or boundary candidates unless explicitly justified; schema must pass. | Do not create canonical TestCase, auto-approve, execute tools, mutate requirements, or use RAG/provider/vector/graph/MCP runtime. | Human gate requires reviewer action before any candidate is accepted, rejected, or later promoted by non-agent workflow. | Return `UNABLE_TO_GENERATE_CASES`; no empty success output and no fallback to generic "verify it works" cases. |
| CaseReviewAgent | `evidence_case_review:v1` / `testcase-review-skill:v1` | GeneratedCaseCandidate drafts, requirement/risk/coverage/design evidence, duplicate hints, reviewer policy, local knowledge evidence ids. | Review draft with per-case findings, quality score, coverage gap notes, correction suggestions, reject/needs-fix recommendation, and evidence refs; write permission is AITask output plus review findings on candidate draft only. | Findings must cite candidate fields and evidence; severity and recommendation must be structured; no pass recommendation without checking steps, expected results, refs, and duplicates; schema must pass. | Do not approve as human, promote to TestCase, delete candidates, rewrite source requirements, or call external reviewers/tools. | Human gate is mandatory: a human reviewer decides accept/reject/needs-fix and any TestCase promotion outside this seed contract. | Return `UNABLE_TO_REVIEW_CASE`; candidate stays in pending/needs-review state and cannot advance by agent output alone. |
| DedupAgent | `case_dedup:v1` / `testcase-review-skill:v1` | GeneratedCaseCandidate drafts, reviewed case ids when supplied, case titles/steps/expected results, requirement and risk refs, review findings. | Dedup draft with duplicate groups, similarity reasons, keep/merge/split suggestions, and evidence refs; write permission is AITask output plus dedup suggestion artifact only. | Duplicate claims must cite matching fields; keep/merge suggestions must preserve requirement/risk coverage; schema must pass. | Do not delete, merge, hide, or mutate cases; do not infer duplicates from title alone; do not promote candidates. | Human gate requires reviewer confirmation before any merge, removal, or canonical case change. | Return `UNABLE_TO_DEDUP_CASES`; leave all candidates unchanged and mark dedup status inconclusive. |
| AutomationReadinessAgent | `automation_readiness:v1` / `automation-draft-skill:v1` | Reviewed candidate drafts, review findings, dedup suggestions, target framework notes, execution constraints, known test data/dependency evidence. | Automation readiness draft with readiness status, blockers, data/fixture needs, suggested framework fit, risk notes, and trace refs; write permission is AITask output plus readiness fields on candidate draft only. | Must distinguish automatable, manual-only, blocked, and needs-design states; blockers must cite evidence; no readiness claim without preconditions and expected results; schema must pass. | Do not generate automation code, execute tests, create runner commands, mutate repositories, call providers, or promote candidates. | Human gate requires automation owner review before automation drafting or implementation work is scheduled. | Return `UNABLE_TO_ASSESS_AUTOMATION_READINESS`; readiness remains unknown and no automation task may be created from the failed output. |

## 6.2 Knowledge Feedback Seed Contract

KnowledgeFeedbackAgent is bound to `knowledge_feedback:v1` and
`knowledge-feedback-skill:v1`. This seed contract is draft-only: it does not
enable runtime orchestration, TestKnowledgeCard CRUD, prompt-eligible
auto-marking, automatic knowledge ingestion, provider calls, vector search,
graph runtime, MCP runtime, tool execution, or historical evidence mutation.

| Agent | PromptVersion / SkillVersion seed | Input evidence | Output contract and write permission | Quality gates | Forbidden actions | Human gate | Failure behavior |
|---|---|---|---|---|---|---|---|
| KnowledgeFeedbackAgent | `knowledge_feedback:v1` / `knowledge-feedback-skill:v1` | Accepted/rejected GeneratedCaseCandidate summaries, reviewed TestCase summaries, ReviewHistory comments/actions/evidence ids, FailureAnalysis summaries, Report summaries/evidence manifests, TestRun/TestResult summaries, normalized KnowledgeEvidence, existing TestKnowledgeCard summaries. | Draft KnowledgeFeedbackDraft entries with feedback_type, draft_knowledge_type, source_entity_type/id, source_quote_or_hash, source_span, recommendation, confidence, used_knowledge_evidence_ids, unsupported_claims, review_findings, `prompt_eligible=false`; write permission is AITask output plus feedback draft artifact only. | Every feedback item cites source evidence; accepted and rejected examples are labeled separately; failure/report-derived bug patterns cite execution or report evidence; schema passes; unsupported claims remain visible. | Do not create or approve TestKnowledgeCard rows, mark prompt-eligible, mutate ReviewHistory/FailureAnalysis/Report/TestRun/TestCase/GeneratedCaseCandidate/Artifact rows, call providers, use MCP/tools, or fabricate fallback knowledge. | Human review is required before feedback can become a TestKnowledgeCard or prompt-eligible knowledge. | Return `UNABLE_TO_CREATE_KNOWLEDGE_FEEDBACK` with empty feedback and visible unsupported claims when evidence is insufficient. |

Trace requirements:

- Record `prompt_version`, `skill_version`, prompt hash, skill hash, input
  evidence ids, output artifact ids, schema validation status, unsupported
  claim count, and failure code.
- Model confidence is advisory only. It must not imply approval or prompt
  eligibility.

## 7. 输出 JSON 约束

### 7.1 用例生成输出

```json
{
  "cases": [
    {
      "title": "过期优惠券不可提交订单",
      "priority": "P0",
      "test_type": "functional",
      "precondition": "存在一张已过期优惠券",
      "steps": ["登录", "进入结算页", "选择过期优惠券", "提交订单"],
      "expected_results": ["系统阻止提交", "展示错误提示"],
      "input_data": {"coupon_status": "expired"},
      "requirement_refs": ["过期优惠券不可使用"],
      "risk_refs": ["RISK-001"],
      "ai_reason": "覆盖优惠券有效期边界"
    }
  ]
}
```

### 7.2 AutomationDraft 输出

```json
{
  "drafts": [
    {
      "target_framework": "pytest",
      "title": "test_expired_coupon_cannot_checkout",
      "suggested_file_path": "tests/test_coupon_checkout.py",
      "draft_language": "python",
      "draft_code": "def test_expired_coupon_cannot_checkout():\n    assert True",
      "execution_notes": ["需要替换为真实 fixture"],
      "risk_notes": ["草稿不能直接写入业务仓库"]
    }
  ]
}
```

### 7.3 UnitTestPatch 输出

```json
{
  "patch": "diff --git a/tests/test_coupon.py b/tests/test_coupon.py\n...",
  "target_framework": "pytest",
  "test_intent": "cover expired coupon rejection",
  "coverage_target": ["coupon validation branch"],
  "risk_notes": ["patch only modifies tests/"]
}
```

### 7.4 RegressionPlan 输出

```json
{
  "recommended_test_command_ids": ["00000000-0000-0000-0000-000000000302"],
  "reasons": ["Changed source branch is covered by pytest unit command."],
  "risk_coverage": ["src/coupon.py coupon.amount > order_total"],
  "needs_review": false
}
```

### 7.5 Report 输出

```json
{
  "conclusion": "passed",
  "summary": "Patch scope, new tests, and regression passed with evidence.",
  "metrics": {"new_tests_passed": true, "regression_passed": true},
  "evidence_artifact_ids": ["00000000-0000-0000-0000-000000001601"],
  "next_actions": []
}
```

## 8. 质量门禁

| 输出 | 门禁 |
|---|---|
| RequirementReview | 必须包含六维评分和至少一个测试设计建议 |
| GeneratedCaseCandidate | 必须有步骤、预期、需求引用、AI 理由 |
| AutomationDraft | 必须标明 target_framework、suggested_file_path、draft_code |
| UnitTestPatch | 必须通过 PatchScopeGate，不能修改业务源码 |
| RegressionPlan | 每个推荐命令必须有 reason |
| FailureAnalysis | 无证据时必须返回 insufficient_evidence |
| Report | 每个结论必须引用 artifact 或结构化指标 |

## 9. 版本与指标

每次 AI Task 必须记录：

- prompt_name。
- prompt_version。
- prompt_hash。
- skill_name。
- skill_version。
- skill_hash。
- model_provider。
- model_name。
- schema_valid。
- quality_gate_result。

指标按 PromptVersion 和 SkillVersion 聚合：采纳率、编辑率、驳回率、schema 通过率、执行通过率、失败率、平均 token、平均耗时。
