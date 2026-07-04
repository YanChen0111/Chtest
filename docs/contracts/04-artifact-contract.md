# Chtest Artifact Contract

## 1. 文档目的

Artifact 是 Chtest 质量证据链的基础。AI 输出、工具执行、失败归因、报告结论都必须能追溯到 artifact。

V1 artifact 存储在本地文件系统，元数据存 PostgreSQL。

## 2. 根目录

默认根目录：

```text
artifacts/
```

Docker 环境中挂载为 volume：

```text
/opt/chtest/artifacts
```

## 3. 路径规范

### 3.1 AI Task

```text
artifacts/projects/{project_id}/ai-tasks/{ai_task_id}/
  input.json
  context_manifest.json
  knowledge_retrieval.json
  test_knowledge_card_prompt_context_evidence.json
  test_knowledge_card_prompt_context_consumption.json
  test_knowledge_card_prompt_context_audit_summary.json
  test_knowledge_card_prompt_context_audit_review_decision.json
  test_knowledge_card_prompt_context_audit_review_summary_export.json
  test_knowledge_card_prompt_context_review_discrepancy.json
  raw_output.json
  parsed_output.json
  schema_validation.json
  error.json
```

### 3.2 Requirement Review

```text
artifacts/projects/{project_id}/requirements/{requirement_id}/reviews/{review_id}/
  requirement.md
  review.json
  risk_matrix.json
```

### 3.3 Case Generation

```text
artifacts/projects/{project_id}/case-generation/{generation_task_id}/
  prompt_input.json
  candidates.json
  duplicate_check.json
  metrics.json
  knowledge_evidence.json
  review_findings.json
```

`knowledge_evidence.json` stores normalized KnowledgeEvidence objects used by
generated candidates. `review_findings.json` stores agent review findings,
quality scores, coverage gap notes, and automation readiness notes. These files
are evidence for review only; they do not approve candidates or create TestCase
records.

### 3.3.1 Test Knowledge Cards

```text
artifacts/projects/{project_id}/test-knowledge-cards/{knowledge_card_id}/
  card.json
  source_manifest.json
  knowledge_evidence.json
  redaction_report.json
```

`card.json` stores a normalized TestKnowledgeCard snapshot. `source_manifest.json`
lists same-project source Artifact ids, hashes, sections, and safe quote/hash
pointers. `knowledge_evidence.json` stores normalized KnowledgeEvidence objects
derived from the card or used by generated cases.

### 3.3.2 Knowledge Feedback Drafts

```text
artifacts/projects/{project_id}/knowledge-feedback/{ai_task_id}/
  feedback_sources.json
  knowledge_feedback.json
  unsupported_claims.json
  schema_validation.json
  test_knowledge_card_handoff.json
  test_knowledge_card_candidate_review.json
  reviewed_test_knowledge_card_creation.json
  test_knowledge_card_prompt_eligibility.json
  test_knowledge_card_retrieval_boundary.json
```

`knowledge_feedback.json` stores draft KnowledgeFeedbackAgent output. It is
review evidence only and must not create TestKnowledgeCard rows, mark feedback
prompt-eligible, or mutate historical review/failure/report/case evidence.
`test_knowledge_card_handoff.json` stores only a future TestKnowledgeCard
candidate payload from approved feedback; it is not written under a
`test-knowledge-cards/{knowledge_card_id}` path unless a later scoped workflow
creates a real card.
`test_knowledge_card_candidate_review.json` stores candidate review evidence
for a handoff payload. It is not TestKnowledgeCard CRUD and must not create,
merge, archive, delete, relabel, or make prompt-eligible card rows.
`reviewed_test_knowledge_card_creation.json` stores reviewed creation evidence
for a future scoped TestKnowledgeCard creation workflow. It is not broad CRUD
and must not grant prompt eligibility.
`test_knowledge_card_prompt_eligibility.json` stores human review evidence for
card prompt eligibility. It must not change retrieval runtime behavior.
`test_knowledge_card_retrieval_boundary.json` stores future read-only
prompt-context selection evidence for prompt-eligible cards. It must not run
retrieval, rank cards, assemble prompts, or mutate cards.

### 3.4 Automation Draft

```text
artifacts/projects/{project_id}/automation-drafts/{automation_draft_id}/
  draft.py
  draft.spec.ts
  review.json
  execution_plan.json
  runtime/
    test_from_draft.py
    test_from_draft.spec.ts
```

`runtime/` stores approved AutomationDraft execution copies. Files in this directory are generated from reviewed draft code and remain under Chtest artifact root. They are not written into the target business repository.

### 3.5 CI/CD Quality

```text
artifacts/projects/{project_id}/cicd-quality/{cicd_run_id}/
  diff.patch
  changed_files.json
  ci_run_metadata.json
  risk_analysis.json
  unit_test.patch
  patch_scope_gate.json
  regression_plan.json
  quality_gate.json
  cicd_quality_report.json
  cicd_quality_report.md
  cicd_quality_report.html
```

Slice 15 artifact boundary:

- Slice 15 may create only `diff.patch`, `changed_files.json`, and
  `risk_analysis.json`.
- `diff.patch` is stored as an Artifact with
  `artifact_type=diff_patch`, `owner_entity_type=CICDRun`, and
  `owner_entity_id=cicd_run_id`.
- `changed_files.json` is stored as an Artifact with
  `artifact_type=changed_files`, `owner_entity_type=CICDRun`, and
  `owner_entity_id=cicd_run_id`.
- `risk_analysis.json` is stored as an Artifact with
  `artifact_type=risk_analysis`, `owner_entity_type=CICDRun`, and
  `owner_entity_id=cicd_run_id`.
- `changed_files.json` must include one item per persisted CICDChangedFile.
- `risk_analysis.json` metadata must include `model_provider`, `model_name`,
  `prompt_version`, `skill_version`, `overall_risk`, and
  `changed_file_count`.
- `unit_test.patch`, `patch_scope_gate.json`, `regression_plan.json`,
  `quality_gate.json`, and CI/CD quality report artifacts are Slice 16+.

Slice 20 CI import artifact rules:

- `ci_run_metadata.json` is stored as an Artifact with
  `artifact_type=ci_run_metadata`, `owner_entity_type=CICDRun`, and
  `owner_entity_id=cicd_run_id`.
- `ci_run_metadata.json` records imported CI run metadata from static JSON or an
  uploaded JSON payload handled locally.
- `ci_run_metadata.json` must include `source_type=ci_import`,
  `provider_is_inert_label=true`, `import_mode`, run conclusion, refs,
  changed files, and artifact references when supplied.
- Imported artifact references are inert references. They may include name,
  kind, external URL, sha256, and size metadata, but Chtest must not fetch,
  authenticate to, execute, or mutate those external URLs in Slice 20.
- Imported artifact reference display must preserve that the reference is not a
  local Artifact file and is not locally openable.
- Imported artifact reference display must show `inert_reference=true` when
  present and `remote_fetch_performed=false` from the owning
  `ci_run_metadata.json` metadata.
- Imported artifact references must not be given local artifact download links
  unless a later task creates a separate persisted local Artifact row.
- `ci_run_metadata.json` metadata must include
  `created_by_component=CICDRunMetadataImport`,
  `remote_fetch_performed=false`, `quality_gate_auto_decision=false`,
  `changed_file_count`, and `artifact_reference_count`.
- Slice 20 may also create `changed_files.json` from imported changed-file
  metadata. It must continue to match persisted CICDChangedFile rows.
- Imported CI metadata must not create or update `quality_gate.json` by itself.

Slice 16 artifact rules:

- `unit_test.patch` is stored as an Artifact with
  `artifact_type=unit_test_patch`, `owner_entity_type=UnitTestPatch`, and
  `owner_entity_id=unit_test_patch_id`.
- `patch_scope_gate.json` is stored as an Artifact with
  `artifact_type=patch_scope_gate`, `owner_entity_type=UnitTestPatch`, and
  `owner_entity_id=unit_test_patch_id`.
- `patch_scope_gate.json` must include `allowed`, `checked_paths`,
  `blocked_paths`, `forbidden_patterns`, `risk_level`, and rejection `reason`
  when blocked.
- `regression_plan.json` is stored as an Artifact with
  `artifact_type=regression_plan`, `owner_entity_type=CICDRun`, and
  `owner_entity_id=cicd_run_id`.
- `quality_gate.json` is stored as an Artifact with
  `artifact_type=quality_gate`, `owner_entity_type=CICDRun`, and
  `owner_entity_id=cicd_run_id`.
- CI/CD quality reports must cite UnitTestPatch, PatchScopeGate, new-test,
  regression, QualityGateDecision, and related artifacts when available.

Slice 28 quality gate evidence summary rules:

- Quality gate evidence summary is a read-only display derived from existing
  QualityGateDecision, TestRun, UnitTestPatch, and Artifact evidence.
- Summary display may link only persisted local Artifact rows through
  `GET /api/artifacts/{artifact_id}/download`.
- Required evidence for UnitTestPatch/PatchScopeGate, new-test, and regression
  must remain visible even when missing.
- Blocking reasons must remain visible and must not be converted into passing
  evidence.
- Missing evidence, TestRun ids, and metric-like status detail are structured
  evidence references, not downloadable artifact files, unless they explicitly
  cite a persisted Artifact id.
- Summary display must not mutate Artifact rows, artifact files,
  QualityGateDecision, CICDRun, UnitTestPatch, TestRun, Report,
  FailureAnalysis, CI metadata, or review history.
- Summary display must not introduce quality gate computation changes, report
  generation changes, runner behavior changes, cloud storage, signed URLs,
  sharing, upload, delete, indexing, search, broad artifact browsing, remote CI
  provider behavior, RBAC, tenants, permissions, RAG runtime, or MCP runtime.

Slice 21 ReviewHistory artifact rules:

- ReviewHistory stores artifact references in `evidence_artifact_ids`; it does
  not create a dedicated `review_history` artifact type in Slice 21.
- Each id in `evidence_artifact_ids` must reference an existing persisted
  Artifact row in the same project.
- ReviewHistory must not duplicate raw artifact content, stdout/stderr, LLM
  output, CI logs, external artifact payloads, tokens, secrets, cookies, or
  credentials in ReviewHistory fields.
- If a future task creates a review history snapshot file, it must define a
  new artifact type and storage path in this contract before implementation.
- ReviewHistory artifact references are local evidence only. They must not
  trigger remote CI/CD provider calls, PR comments, commit status updates,
  merge, deploy, release, RAG runtime, MCP runtime, RBAC, tenants, or
  permissions behavior.

### 3.6 Test Run

```text
artifacts/projects/{project_id}/test-runs/{test_run_id}/
  runtime_manifest.json
  dependency_snapshot.json
  environment_snapshot.json
  stdout.log
  stderr.log
  junit.xml
  coverage.xml
  newman-report.json
  playwright-trace.zip
  screenshot.png
  parsed_result.json
```

`runtime_manifest.json` records runtime artifacts used by the TestRun. For AutomationDraft execution it must include the `automation_draft_code` artifact copied into the AutomationDraft `runtime/` directory.

`dependency_snapshot.json` records runner version, Python/Node version, lockfile hashes, package manager metadata, and runner image when available.

`environment_snapshot.json` records environment variable names and safe non-secret values used by the run. Secret values must appear only as redacted references.

Newman API execution adds `newman-report.json` with
`artifact_type=newman_json`. The parsed Newman summary is stored in
`parsed_result.json` as `artifact_type=parsed_output`.

Slice 29 execution run manifest artifact rules:

- Execution run manifest display is read-only and derived from existing
  TestRun fields plus persisted Artifact metadata.
- Runtime, dependency, and environment snapshot rows must remain visible even
  when the corresponding Artifact id is missing.
- Missing snapshot rows are unavailable evidence and must not be rendered as
  local artifact links.
- Local open links may be rendered only for persisted local Artifact rows
  through `GET /api/artifacts/{artifact_id}/download`.
- `runtime_manifest`, `dependency_snapshot`, `environment_snapshot`, `stdout`,
  `stderr`, `parsed_output`, `junit`, `coverage`, `trace`, `screenshot`,
  `newman_json`, and `jmeter_jtl` artifacts all remain evidence files. Opening
  them must not trigger runner execution, report generation, failure analysis,
  quality gate computation, artifact mutation, remote provider fetch, RAG
  runtime, or MCP runtime.
- Raw command text, parsed result metrics, and TestResult rows are structured
  evidence references, not downloadable artifact files, unless they cite a
  persisted Artifact id.

### 3.7 Report

```text
artifacts/projects/{project_id}/reports/{report_id}/
  report.md
  report.html
  report.json
  evidence_manifest.json
```

### 3.8 Context Artifact

```text
artifacts/projects/{project_id}/context-artifacts/{artifact_id}/
  content.md
  content.txt
  content.json
  content.yaml
  openapi.yaml
  redaction_report.json
```

V1 ContextArtifact uses the Artifact table with `owner_entity_type=Project` and `owner_entity_id=project_id`.

## 4. Artifact 类型

| artifact_type | MIME | 说明 |
|---|---|---|
| input_json | application/json | AI 或工具输入 |
| raw_llm_output | application/json | 模型原始输出 |
| parsed_output | application/json | 校验后的结构化输出 |
| schema_validation | application/json | schema 校验结果 |
| error_json | application/json | 错误详情 |
| requirement_md | text/markdown | 需求内容 |
| candidates_json | application/json | 候选用例 |
| automation_draft_code | text/plain | 自动化草稿代码 |
| runtime_manifest | application/json | TestRun 实际运行文件清单 |
| dependency_snapshot | application/json | 依赖和 runner 版本快照 |
| environment_snapshot | application/json | 脱敏后的执行环境快照 |
| patch | text/x-diff | unified diff |
| stdout | text/plain | 标准输出 |
| stderr | text/plain | 标准错误 |
| junit | application/xml | JUnit 结果 |
| coverage | application/xml | 覆盖率结果 |
| newman_json | application/json | Newman JSON 结果 |
| jmeter_jtl | text/csv or application/xml | JMeter JTL 结果 |
| playwright_trace | application/zip | Playwright trace |
| screenshot | image/png | 截图 |
| report_md | text/markdown | Markdown 报告 |
| report_html | text/html | HTML 报告 |
| report_json | application/json | JSON 报告 |
| context_markdown | text/markdown | 轻量上下文 Markdown |
| context_text | text/plain | 轻量上下文文本、日志、说明 |
| context_json | application/json | 轻量上下文 JSON、fixture |
| context_yaml | application/yaml | 轻量上下文 YAML |
| context_openapi | application/yaml or application/json | OpenAPI 片段或文件 |
| knowledge_retrieval | application/json | 确定性本地知识检索证据 |
| test_knowledge_card | application/json | Structured testing knowledge card snapshot |
| test_knowledge_card_handoff | application/json | Future TestKnowledgeCard handoff candidate payload |
| test_knowledge_card_candidate_review | application/json | Human review evidence for a handoff candidate |
| reviewed_test_knowledge_card_creation | application/json | Reviewed TestKnowledgeCard creation evidence |
| test_knowledge_card_prompt_eligibility | application/json | Human prompt eligibility review evidence |
| test_knowledge_card_retrieval_boundary | application/json | Future prompt-context selection evidence |
| test_knowledge_card_prompt_context_evidence | application/json | Future bounded prompt context evidence |
| test_knowledge_card_prompt_context_consumption | application/json | Future prompt context consumption citation evidence |
| test_knowledge_card_prompt_context_audit_summary | application/json | Future prompt context usage audit summary evidence |
| test_knowledge_card_prompt_context_audit_review_decision | application/json | Future prompt context audit review decision evidence |
| test_knowledge_card_prompt_context_audit_review_summary_export | application/json | Future prompt context audit review summary export evidence |
| test_knowledge_card_prompt_context_review_discrepancy | application/json | Future prompt context review discrepancy evidence |
| knowledge_evidence | application/json | Normalized knowledge evidence citations |
| case_review_findings | application/json | Generated-case review findings and coverage gaps |
| ci_run_metadata | application/json | Imported CI run metadata evidence |

Playwright artifact rules:

- `playwright_trace` must point to a trace zip produced or copied by the
  controlled Playwright runner.
- `screenshot` must point to a PNG screenshot captured during the same TestRun.
- Both artifact types use `owner_entity_type=TestRun` and
  `owner_entity_id=test_run_id`.
- Metadata should include `created_by_component=PlaywrightRunner`, `runner_mode`,
  and the best available test node id or page URL.
- Trace and screenshot artifacts are evidence only; they must not trigger report
  generation or failure analysis automatically.

Newman artifact rules:

- `newman_json` must point to the JSON reporter output produced or copied by
  the controlled Newman runner.
- `parsed_output` for a Newman TestRun must summarize `total`, `passed`,
  `failed`, `skipped`, `error`, `request_count`, `assertion_count`,
  `collection_name`, and `duration_ms` when available.
- Optional Newman JUnit output may use the existing `junit` artifact type.
- Newman artifacts use `owner_entity_type=TestRun` and
  `owner_entity_id=test_run_id`.
- Metadata should include `created_by_component=NewmanRunner`,
  `runner_mode=newman_local`, `collection_name`, `request_count`,
  `assertion_count`, and redaction status.
- Artifact content and metadata must not store secrets, bearer tokens, cookies,
  or raw environment values.
- Newman artifacts are evidence only; they must not trigger report generation,
  FailureAnalysis, QualityGateDecision, remote CI/CD provider calls, or Postman
  cloud synchronization automatically.

JMeter artifact rules:

- `jmeter_jtl` must point to the JTL CSV or XML output produced or copied by the
  controlled JMeter runner.
- `parsed_output` for a JMeter TestRun must summarize `total`, `passed`,
  `failed`, `skipped`, `error`, `sampler_count`, `assertion_count`,
  `duration_ms`, and `average_latency_ms` when available.
- JMeter artifacts use `owner_entity_type=TestRun` and
  `owner_entity_id=test_run_id`.
- Metadata should include `created_by_component=JMeterRunner`,
  `runner_mode=jmeter_local`, `sampler_count`, `assertion_count`, JTL format,
  and redaction status.
- Artifact content and metadata must not store secrets, bearer tokens, cookies,
  or raw environment values.
- JMeter artifacts are evidence only; they must not trigger report generation,
  FailureAnalysis, QualityGateDecision, remote CI/CD provider calls,
  distributed load agents, cloud load testing, RAG runtime, or MCP runtime
  automatically.

Slice 24 local artifact access rules:

- Local artifact access is read-only and applies only to persisted Artifact rows
  whose `file_path` resolves under the configured artifact root.
- Clients must request artifacts by Artifact id, not by arbitrary path.
- The artifact service must use the existing local artifact store path
  normalization and containment checks before reading bytes.
- Returned `Content-Type` must come from Artifact `mime_type` when present.
- Returned download filename must be derived from the basename of Artifact
  `file_path`; path separators and unsafe filename characters must not be
  reflected into `Content-Disposition`.
- Missing Artifact rows, missing files, or unsafe paths must fail with explicit
  API errors instead of falling back to raw filesystem access.
- External imported artifact references are inert. They may store metadata such
  as name, kind, `external_url`, sha256, and size, but local artifact access must
  not fetch, proxy, download, authenticate to, or expose those external URLs.
- Artifact access must not mutate Artifact rows, artifact files, TestRun state,
  Report, FailureAnalysis, QualityGateDecision, CI metadata, or review history.
- Artifact access must not introduce cloud storage, signed URLs, sharing,
  upload, delete, retention policy, indexing, search, RBAC, tenants,
  permissions, RAG runtime, MCP runtime, marketplace, or remote provider
  behavior.

Slice 25 execution evidence summary rules:

- Execution evidence summary is a read-only display of existing Report,
  TestRun, TestResult, and Artifact evidence.
- Summary display may link only persisted local Artifact rows through
  `GET /api/artifacts/{artifact_id}/download`.
- Summary display must keep `evidence_manifest.evidence[]` support claims,
  `required` flags, artifact ids, artifact types, metric rows, TestResult rows,
  and `missing_evidence` visible.
- Missing evidence is not downloadable and must not be treated as passing
  evidence.
- Metric rows and TestResult rows are structured evidence references, not
  artifact files, unless they explicitly cite a persisted Artifact id.
- Report artifacts such as `report.md`, `report.json`, and
  `evidence_manifest.json` remain local read-only evidence files and can use the
  same local artifact access rules as TestRun artifacts.
- External imported artifact references remain inert and must not be shown as
  locally downloadable unless a separate persisted local Artifact row exists.
- Evidence summary must not mutate Artifact rows, artifact files, Report,
  TestRun, TestResult, FailureAnalysis, QualityGateDecision, CI metadata, or
  review history.
- Evidence summary must not introduce report generation changes, runner
  behavior changes, cloud storage, signed URLs, sharing, upload, delete,
  indexing, search, broad artifact browsing, RBAC, tenants, permissions, RAG
  runtime, MCP runtime, marketplace, or remote provider behavior.

Slice 26 CI imported artifact reference clarity rules:

- Imported artifact references are display-only external references.
- They are not local Artifact files and are not locally openable through local
  artifact access.
- The UI must not render `GET /api/artifacts/{artifact_id}/download` links for
  imported external references.
- Display should include reference name, kind, external URL, inert status, and
  `remote_fetch_performed=false` from the owning `ci_run_metadata` artifact.
- External references must remain inert even when they include sha256 or size
  metadata from the remote provider.
- Display clarity must not fetch, proxy, download, authenticate to, execute,
  mutate, cache, mirror, or validate external URL targets.
- Display clarity must not create TestRun, Report, FailureAnalysis,
  QualityGateDecision, UnitTestPatch, local Artifact payloads, remote provider
  status updates, credentials, RBAC, tenants, permissions, RAG runtime, MCP
  runtime, marketplace, or cloud sync behavior.

## 5. Metadata 契约

Artifact 表 metadata_json 最少包含：

```json
{
  "created_by_component": "RequirementReviewAgent",
  "source_entity_type": "AITask",
  "source_entity_id": "00000000-0000-0000-0000-000000000501",
  "safe_to_show": true,
  "redaction_applied": false,
  "description": "raw LLM output before schema validation"
}
```

ContextArtifact metadata_json must also include:

```json
{
  "title": "coupon-api-notes.md",
  "source_ref": "manual:coupon-api-notes.md",
  "redaction_applied": false,
  "redaction_report_artifact_id": null,
  "allowed_for_prompt": true
}
```

Knowledge retrieval artifact content must include:

```json
{
  "adapter_name": "default",
  "retrieval_mode": "deterministic_local",
  "query_text": "expired coupon validation",
  "query_terms": ["expired", "coupon", "validation"],
  "used_context_artifact_ids": ["00000000-0000-0000-0000-000000000371"],
  "results": [
    {
      "context_artifact_id": "00000000-0000-0000-0000-000000000371",
      "title": "coupon-api-notes.md",
      "source_ref": "manual:coupon-api-notes.md",
      "score": 2,
      "matched_terms": ["expired", "coupon"],
      "snippet": "Expired coupons cannot be applied during checkout.",
      "sha256": "sha256:example",
      "redaction_applied": false,
      "allowed_for_prompt": true
    }
  ]
}
```

Knowledge retrieval artifact rules:

- `artifact_type=knowledge_retrieval`.
- `owner_entity_type=AITask` and `owner_entity_id=ai_task_id`.
- `results` must cite persisted ContextArtifact ids; free-floating snippets are
  not valid evidence.
- Snippets must be bounded and safe to show.
- Secret-like values must be redacted before persistence.
- Scores must be deterministic for the same input artifacts and query terms.

Test knowledge card artifact rules:

- `card.json` is stored as an Artifact with
  `artifact_type=test_knowledge_card`, `owner_entity_type=TestKnowledgeCard`,
  and `owner_entity_id=knowledge_card_id`.
- `knowledge_evidence.json` is stored as an Artifact with
  `artifact_type=knowledge_evidence`. It may be owned by `AITask`,
  `CaseGenerationTask`, `GeneratedCaseCandidate`, or `TestKnowledgeCard`,
  depending on where the evidence is produced.
- `review_findings.json` is stored as an Artifact with
  `artifact_type=case_review_findings`, `owner_entity_type=CaseGenerationTask`
  or `GeneratedCaseCandidate`, and the corresponding owner id.
- KnowledgeEvidence entries must cite same-project source Artifact ids,
  TestKnowledgeCard ids, or reviewed project entities. Free-floating provider
  text is not valid source evidence.
- Provider-specific fields from future Haystack, LlamaIndex, GraphRAG, or other
  tools must be normalized before persistence. Raw provider payloads must not
  be used directly as GeneratedCaseCandidate evidence.
- Missing knowledge evidence, weak evidence, hallucination risk, duplicate risk,
  and coverage gaps must remain visible in `review_findings.json` or
  GeneratedCaseCandidate review fields.
- Slice 31 may persist normalized evidence refs directly on
  GeneratedCaseCandidate rows and return them through the candidate list API.
  That persistence does not require creating a new Artifact when the owning AI
  task output or case generation artifacts already contain the evidence.
- These artifacts are review evidence only. Opening or listing them must not
  approve candidates, create TestCase records, execute AutomationDrafts, run
  retrieval, build indexes, create embeddings, rerank results, run graph jobs,
  call external providers, invoke MCP runtime, mutate artifacts, generate
  reports, change runner behavior, call remote CI providers, add RBAC, create
  tenants, or change permissions.

Knowledge feedback artifact rules:

- `knowledge_feedback.json` is stored as an Artifact with
  `artifact_type=knowledge_feedback`, `owner_entity_type=AITask`, and
  `owner_entity_id=ai_task_id`.
- `feedback_sources.json` must include only same-project source ids and safe
  summaries from accepted/rejected GeneratedCaseCandidate, TestCase,
  ReviewHistory, FailureAnalysis, Report, TestRun/TestResult, KnowledgeEvidence,
  or existing TestKnowledgeCard records.
- `knowledge_feedback.json` stores draft feedback entries with feedback type,
  draft knowledge type, source entity, source quote/hash, recommendation,
  confidence, used KnowledgeEvidence ids, unsupported claims, review findings,
  `prompt_eligible=false`, and draft status.
- `unsupported_claims.json` stores claims rejected for insufficient source
  evidence. Unsupported claims must remain visible and must not be converted
  into fallback knowledge.
- Knowledge feedback artifacts must not create or mutate TestKnowledgeCard
  rows, set `allowed_for_prompt=true`, mutate ReviewHistory, FailureAnalysis,
  Report, TestRun, TestResult, TestCase, GeneratedCaseCandidate, or Artifact
  rows, approve generated cases, promote TestCase rows, generate Reports, run
  retrieval, call external providers, invoke MCP runtime, create vector indexes,
  create embeddings, rerank, run graph jobs, call remote CI providers, add
  RBAC, create tenants, or change permissions.

Knowledge feedback review gate artifact rules:

- `feedback_review.json` is stored as an Artifact with
  `artifact_type=feedback_review`. It may be owned by the future
  KnowledgeFeedbackDraft owner or by the AITask that produced the draft until a
  dedicated feedback-review entity exists.
- `feedback_review.json` must include feedback id, review action,
  reviewer_label, review_comment, evidence_artifact_ids, unsupported claims,
  prompt eligibility decision, prompt eligibility reason, ReviewHistory id
  when created, and optional future TestKnowledgeCard handoff payload.
- `approve_feedback`, `reject_feedback`, `request_revision`, and
  `mark_prompt_eligible` artifacts are human review evidence. They must not be
  produced solely by KnowledgeFeedbackAgent output, model confidence, or schema
  validity.
- `mark_prompt_eligible` artifacts require prior human approval, safe-to-show
  evidence, reviewed source citations, and a non-empty prompt eligibility
  reason. They must not create or mutate TestKnowledgeCard rows in this slice.
- Rejected feedback review artifacts must remain auditable and must not be
  cited as positive prompt knowledge.
- Feedback review artifacts may cite ReviewHistory, but invalid transitions,
  validation failures, or rejected source evidence must not append successful
  ReviewHistory.
- Feedback review artifacts must not add a review runtime API, frontend review
  page, TestKnowledgeCard CRUD, automatic prompt eligibility, automatic
  knowledge ingestion, provider calls, MCP runtime, vector/graph runtime,
  artifact mutation outside declared feedback-review outputs, historical
  evidence mutation, generated-case auto-approval, runner behavior changes,
  report generation behavior changes, RBAC, tenants, permissions, or remote CI
  provider behavior.

TestKnowledgeCard handoff artifact rules:

- `test_knowledge_card_handoff.json` is stored as an Artifact with
  `artifact_type=test_knowledge_card_handoff`, `owner_entity_type=AITask`, and
  `manifest_kind=test_knowledge_card_handoff` until a later scoped workflow
  owns a dedicated card-candidate entity.
- The artifact must include `source_feedback_id`, `review_history_id`,
  `review_artifact_id`, reviewer action, `source_entity_type`,
  `source_entity_id`, `source_artifact_ids`, `source_quote_or_hash`,
  `source_span`, `source_hashes`, schema validation status, failure code when
  applicable, and unsupported claims.
- `candidate_card_json` must include mapped `knowledge_type`, title, summary,
  body when present, source_type, source section/span, related ids, tags,
  confidence, `safe_to_show`, `redaction_applied`,
  `allowed_for_prompt=false`, `review_required=true`, and
  `evidence_artifact_ids`.
- `source_manifest` must cite only same-project source Artifact ids and
  bounded quote/hash pointers. It must not duplicate raw logs, large reports,
  credentials, tokens, provider payloads, or unsafe source content.
- `duplicate_knowledge_card_ids` and `merge_hint` are review evidence only.
  They must not merge, archive, replace, delete, relabel, or create
  TestKnowledgeCard rows.
- Handoff artifacts must not be stored in
  `artifacts/projects/{project_id}/test-knowledge-cards/{knowledge_card_id}/`
  unless a later workflow has created a real reviewed card id.
- Handoff artifacts must not create or mutate TestKnowledgeCard rows, set
  `allowed_for_prompt=true`, mutate Artifact rows outside declared handoff
  output, mutate ReviewHistory, FailureAnalysis, Report, TestRun, TestResult,
  TestCase, GeneratedCaseCandidate, or KnowledgeEvidence rows, approve
  generated cases, promote TestCase rows, generate Reports, run retrieval, call
  providers, invoke MCP runtime, create vector indexes, create embeddings,
  rerank, run graph jobs, call remote CI providers, add RBAC, create tenants,
  or change permissions.

TestKnowledgeCard Candidate Review artifact rules:

- `test_knowledge_card_candidate_review.json` is stored as an Artifact with
  `artifact_type=test_knowledge_card_candidate_review`,
  `owner_entity_type=AITask`, and
  `manifest_kind=test_knowledge_card_candidate_review` until a later scoped
  workflow owns a dedicated card-candidate review entity.
- The candidate review artifact must include `source_handoff_artifact_id`,
  `source_feedback_id`, candidate review action, candidate review decision,
  reviewer_label, reviewer_comment, `review_history_id` when present,
  `candidate_review_artifact_id`, `candidate_card_json`,
  `source_artifact_ids`, `source_quote_or_hash`, `source_span`,
  `evidence_artifact_ids`, unsupported claims, schema validation status, and
  failure code when applicable.
- Candidate review artifacts must record `approve_candidate_for_creation`,
  `reject_candidate`, `request_candidate_revision`, `flag_duplicate`,
  `request_merge_review`, and `defer_prompt_eligibility` as human review
  evidence only.
- `duplicate_knowledge_card_ids`, `merge_hint`,
  `duplicate_review_required`, and `merge_review_required` are review-routing
  evidence only. They must not merge, archive, replace, delete, relabel, or
  create TestKnowledgeCard rows.
- Candidate review artifacts must record `allowed_for_prompt=false` and
  `prompt_eligibility_decision=deferred` unless a later explicitly scoped card
  workflow grants prompt eligibility after a card row exists.
- Candidate review artifacts must not be stored in
  `artifacts/projects/{project_id}/test-knowledge-cards/{knowledge_card_id}/`
  unless a later workflow has created a real reviewed card id.
- Candidate review artifacts must not create or mutate TestKnowledgeCard rows,
  set `allowed_for_prompt=true`, mutate Artifact rows outside declared
  candidate review output, mutate ReviewHistory, FailureAnalysis, Report,
  TestRun, TestResult, TestCase, GeneratedCaseCandidate, or KnowledgeEvidence
  rows, approve generated cases, promote TestCase rows, generate Reports, run
  retrieval, call providers, invoke MCP runtime, create vector indexes, create
  embeddings, rerank, run graph jobs, call remote CI providers, add RBAC,
  create tenants, or change permissions.

Reviewed TestKnowledgeCard Creation artifact rules:

- `reviewed_test_knowledge_card_creation.json` is stored as an Artifact with
  `artifact_type=reviewed_test_knowledge_card_creation`,
  `owner_entity_type=AITask`, and
  `manifest_kind=reviewed_test_knowledge_card_creation` until a later scoped
  implementation owns a dedicated creation entity.
- The creation artifact must include `creation_action`,
  `create_reviewed_test_knowledge_card`, approved candidate review action,
  `candidate_review_artifact_id`, `source_handoff_artifact_id`,
  `source_feedback_id`, ReviewHistory ids, `candidate_card_json`,
  `source_manifest`, duplicate/merge precondition result,
  `allowed_for_prompt=false`, `prompt_eligibility_decision=deferred`,
  unsupported claims, schema validation status, and failure code when
  applicable.
- `source_manifest` must cite only same-project source Artifact ids, source
  hashes, source spans, safe quote/hash pointers, ReviewHistory ids, and
  candidate review evidence. It must not duplicate raw logs, large reports,
  credentials, tokens, provider payloads, or unsafe source content.
- Creation artifacts must record duplicate/merge preconditions. Unresolved
  duplicate or merge conflicts must block creation and must not merge, archive,
  replace, delete, relabel, or create conflicting TestKnowledgeCard rows.
- Creation artifacts must record `allowed_for_prompt=false`. They must not set
  `allowed_for_prompt=true` or mark a card prompt-eligible.
- Creation artifacts must not mutate Artifact rows outside declared creation
  output, mutate ReviewHistory, FailureAnalysis, Report, TestRun, TestResult,
  TestCase, GeneratedCaseCandidate, KnowledgeEvidence, or existing
  TestKnowledgeCard rows, approve generated cases, promote TestCase rows,
  generate Reports, run retrieval, call providers, invoke MCP runtime, create
  vector indexes, create embeddings, rerank, run graph jobs, call remote CI
  providers, add RBAC, create tenants, or change permissions.

TestKnowledgeCard Prompt Eligibility artifact rules:

- `test_knowledge_card_prompt_eligibility.json` is stored as an Artifact with
  `artifact_type=test_knowledge_card_prompt_eligibility`,
  `owner_entity_type=TestKnowledgeCard`, and
  `manifest_kind=test_knowledge_card_prompt_eligibility` until a later scoped
  implementation owns a dedicated eligibility entity.
- The prompt eligibility artifact must include `prompt_eligibility_action`,
  `test_knowledge_card_id`, reviewer_label, reviewer_comment,
  prompt eligibility reason, creation artifact id, source manifest artifact id,
  source artifact ids, source quote/hash, redaction report artifact id,
  `safe_to_show`, `redaction_applied`, unsupported claims, ReviewHistory id,
  decision, `allowed_for_prompt`, and failure code when applicable.
- `mark_card_prompt_eligible` artifacts require `safe_to_show=true`, reviewed
  redaction status, same-project source evidence, reviewed source citations,
  and a non-empty prompt eligibility reason.
- `deny_card_prompt_eligibility`,
  `request_prompt_eligibility_revision`, and
  `revoke_card_prompt_eligibility` artifacts must keep or set
  `allowed_for_prompt=false` and preserve reviewer reason and source evidence.
- Prompt eligibility artifacts must not contain raw large source text,
  credentials, tokens, unsafe provider payloads, vector store payloads,
  embedding vectors, reranker traces, or graph runtime payloads.
- Prompt eligibility artifacts must not mutate Artifact rows outside declared
  prompt eligibility output, mutate source artifacts, rewrite creation
  artifacts, mutate historical ReviewHistory, FailureAnalysis, Report,
  TestRun, TestResult, TestCase, GeneratedCaseCandidate, KnowledgeEvidence, or
  unrelated TestKnowledgeCard rows, run retrieval, call providers, invoke MCP
  runtime, create vector indexes, create embeddings, rerank, run graph jobs,
  call remote CI providers, add RBAC, create tenants, or change permissions.

TestKnowledgeCard Retrieval Boundary artifact rules:

- `test_knowledge_card_retrieval_boundary.json` is stored as an Artifact with
  `artifact_type=test_knowledge_card_retrieval_boundary`,
  `owner_entity_type=AITask` or `owner_entity_type=Project`, and
  `manifest_kind=test_knowledge_card_retrieval_boundary` until a later scoped
  prompt-context workflow owns a dedicated selection entity.
- The retrieval boundary artifact must include `select_prompt_eligible_cards`,
  project id, prompt request id when available, selected TestKnowledgeCard ids,
  excluded TestKnowledgeCard ids, `excluded_card_reason`, prompt eligibility
  artifact ids, creation artifact ids, source manifest artifact id, source
  artifact ids, source quote/hash, ReviewHistory ids, `safe_to_show`,
  redaction status, `prompt_eligible`, `allowed_for_prompt`, unsupported
  claims, selection reason, and failure code when applicable.
- Selected card evidence requires `allowed_for_prompt=true`, `prompt_eligible`,
  `safe_to_show=true`, reviewed redaction status, same-project source
  evidence, source manifest, reviewed source citations, ReviewHistory, and
  prompt eligibility artifact evidence.
- Excluded card evidence must preserve `excluded_card_reason` for
  `allowed_for_prompt=false`, `prompt_eligibility_denied`,
  `prompt_eligibility_revision_requested`, `prompt_eligibility_revoked`, stale,
  cross-project, unsafe, missing, unbounded, unsupported, redaction failed,
  source manifest mismatch, missing ReviewHistory, or missing prompt
  eligibility artifact evidence.
- Retrieval boundary artifacts must not contain raw large source text,
  credentials, tokens, unsafe provider payloads, vector store payloads,
  embedding vectors, reranker traces, graph runtime payloads, or prompt
  assembly payloads.
- Retrieval boundary artifacts must not mutate Artifact rows outside declared
  retrieval evidence output, mutate source artifacts, mutate prompt eligibility
  artifacts, rewrite creation artifacts, mutate historical ReviewHistory,
  FailureAnalysis, Report, TestRun, TestResult, TestCase,
  GeneratedCaseCandidate, KnowledgeEvidence, or unrelated TestKnowledgeCard
  rows, run retrieval, change deterministic retrieval ranking, call providers,
  invoke MCP runtime, create vector indexes, create embeddings, rerank, run
  graph jobs, call remote CI providers, add RBAC, create tenants, or change
  permissions.

TestKnowledgeCard Prompt Context Evidence artifact rules:

- `test_knowledge_card_prompt_context_evidence.json` is stored as an Artifact
  with `artifact_type=test_knowledge_card_prompt_context_evidence`,
  `owner_entity_type=AITask` or `owner_entity_type=Project`, and
  `manifest_kind=test_knowledge_card_prompt_context_evidence` until a later
  scoped prompt workflow owns a dedicated prompt request entity.
- The prompt context evidence artifact must include
  `build_prompt_context_evidence`, prompt request id or AITask id when
  available, PromptVersion id, SkillVersion id, retrieval boundary artifact
  id, selected TestKnowledgeCard ids, omitted TestKnowledgeCard ids, omission
  reason, context manifest artifact id when available, source manifest ids,
  source artifact ids, source hash or source quote/hash pointer, prompt
  eligibility artifact ids, ReviewHistory ids, `safe_to_show`, redaction
  status, bounded snippet entries, source trace label, and failure code when
  applicable.
- Text entries require `safe_to_show=true`, reviewed redaction status,
  same-project source evidence, retrieval boundary evidence, prompt
  eligibility artifact evidence, and bounded snippet length. When those cannot
  be proven, the artifact must use source hash or source quote/hash pointer and
  record an omission reason.
- Prompt context evidence artifacts must not contain raw large source text,
  credentials, tokens, unsafe provider payloads, vector store payloads,
  embedding vectors, reranker traces, graph runtime payloads, executable prompt
  assembly payloads, or provider request/response payloads.
- Prompt context evidence artifacts must not mutate Artifact rows outside
  declared prompt context evidence output, mutate source artifacts, mutate
  retrieval boundary artifacts, mutate prompt eligibility artifacts, rewrite
  creation artifacts, mutate historical ReviewHistory, FailureAnalysis,
  Report, TestRun, TestResult, TestCase, GeneratedCaseCandidate,
  KnowledgeEvidence, or unrelated TestKnowledgeCard rows, run prompt assembly,
  execute AITasks, call providers, change retrieval ranking, invoke MCP
  runtime, create vector indexes, create embeddings, rerank, run graph jobs,
  call remote CI providers, add RBAC, create tenants, or change permissions.

TestKnowledgeCard Prompt Context Consumption artifact rules:

- `test_knowledge_card_prompt_context_consumption.json` may be stored as an
  Artifact with `artifact_type=test_knowledge_card_prompt_context_consumption`,
  `owner_entity_type=AITask` or `owner_entity_type=Project`, and
  `manifest_kind=test_knowledge_card_prompt_context_consumption` in a later
  scoped implementation.
- The prompt context consumption artifact must include
  `consume_prompt_context_evidence`, prompt request id or AITask id when
  available, consuming agent step, intended output artifact type,
  PromptVersion id, SkillVersion id, prompt context evidence artifact id,
  context manifest artifact id, consumed TestKnowledgeCard ids, consumed
  context entry ids, consumed source hashes or source quote/hash pointers,
  output citation ids, skipped evidence ids, skip reasons, ReviewHistory ids,
  `used_knowledge` decision, unsupported claim markers, and failure code when
  applicable.
- `used_knowledge=true` may appear only when at least one output citation
  points to consumed prompt context evidence, source hash or source quote/hash
  pointer, same-project source artifact, PromptVersion, SkillVersion, and
  ReviewHistory. Otherwise the artifact must keep `used_knowledge=false`,
  record skipped evidence, or record a failure code.
- Prompt context consumption artifacts must not contain raw large source text,
  credentials, tokens, unsafe provider payloads, vector store payloads,
  embedding vectors, reranker traces, graph runtime payloads, executable prompt
  assembly payloads, or provider request/response payloads.
- Prompt context consumption artifacts must not mutate Artifact rows outside
  declared prompt context consumption output, mutate source artifacts, mutate
  prompt context evidence artifacts, mutate retrieval boundary artifacts,
  mutate prompt eligibility artifacts, rewrite creation artifacts, mutate
  historical ReviewHistory, FailureAnalysis, Report, TestRun, TestResult,
  TestCase, GeneratedCaseCandidate, KnowledgeEvidence, or unrelated
  TestKnowledgeCard rows, run prompt assembly, execute AITasks, call providers,
  change retrieval ranking, invoke MCP runtime, create vector indexes, create
  embeddings, rerank, run graph jobs, call remote CI providers, add RBAC,
  create tenants, or change permissions.

TestKnowledgeCard Prompt Context Audit Summary artifact rules:

- `test_knowledge_card_prompt_context_audit_summary.json` may be stored as an
  Artifact with `artifact_type=test_knowledge_card_prompt_context_audit_summary`,
  `owner_entity_type=AITask` or `owner_entity_type=Project`, and
  `manifest_kind=test_knowledge_card_prompt_context_audit_summary` in a later
  scoped implementation.
- The prompt context audit summary artifact must include
  `summarize_prompt_context_consumption`, prompt request id or AITask id when
  available, consuming agent step, intended output artifact type, prompt
  context consumption artifact id, prompt context evidence artifact id,
  context manifest artifact id, `used_knowledge` decision, usage status, cited
  TestKnowledgeCard ids, output citation ids, skipped evidence ids, skip
  reasons, unsupported claim summaries, source hashes, PromptVersion id,
  SkillVersion id, ReviewHistory ids, review flags, and failure code when
  applicable.
- Audit summary artifacts are read-only views of consumption evidence. They
  must not invent citations, rewrite `used_knowledge`, promote unsupported
  claims, or turn skipped evidence into cited evidence.
- Prompt context audit summary artifacts must not contain raw large source
  text, credentials, tokens, unsafe provider payloads, vector store payloads,
  embedding vectors, reranker traces, graph runtime payloads, executable prompt
  assembly payloads, provider request/response payloads, frontend-rendered
  markup, or report-rendered payloads.
- Prompt context audit summary artifacts must not mutate Artifact rows outside
  declared audit summary output, mutate source artifacts, mutate prompt context
  consumption artifacts, mutate prompt context evidence artifacts, mutate
  retrieval boundary artifacts, mutate prompt eligibility artifacts, rewrite
  creation artifacts, mutate historical ReviewHistory, FailureAnalysis, Report,
  TestRun, TestResult, TestCase, GeneratedCaseCandidate, KnowledgeEvidence, or
  unrelated TestKnowledgeCard rows, run prompt assembly, execute AITasks, call
  providers, change retrieval ranking, invoke MCP runtime, create vector
  indexes, create embeddings, rerank, run graph jobs, render frontend pages,
  generate reports, call remote CI providers, add RBAC, create tenants, or
  change permissions.

TestKnowledgeCard Prompt Context Audit Review Decision artifact rules:

- `test_knowledge_card_prompt_context_audit_review_decision.json` may be stored
  as an Artifact with
  `artifact_type=test_knowledge_card_prompt_context_audit_review_decision`,
  `owner_entity_type=AITask` or `owner_entity_type=Project`, and
  `manifest_kind=test_knowledge_card_prompt_context_audit_review_decision` in
  a later scoped implementation.
- The prompt context audit review decision artifact must include
  `review_prompt_context_audit_summary`, prompt request id or AITask id when
  available, prompt context audit summary artifact id, prompt context
  consumption artifact id, prompt context evidence artifact id, context
  manifest artifact id, `used_knowledge` decision, usage status, review
  action, reviewer label when available, reviewer comment, accepted citation
  ids, questioned citation ids, rejected citation ids, follow-up flags,
  requested clarification fields, unsupported claim references, source hashes,
  PromptVersion id, SkillVersion id, ReviewHistory id, and failure code when
  applicable.
- Allowed review actions are `accepted`, `needs_clarification`,
  `rejected_for_missing_evidence`, `rejected_for_unsupported_claim`,
  `rejected_for_citation_mismatch`, `rejected_for_stale_evidence`, and
  `rejected_for_cross_project_evidence`.
- Audit review decision artifacts are human review evidence about audit summary
  artifacts. They must not invent citations, rewrite `used_knowledge`, promote
  unsupported claims, create prompt eligibility, approve TestKnowledgeCard
  content, approve generated cases, or turn skipped evidence into cited
  evidence.
- Prompt context audit review decision artifacts must not contain raw large
  source text, credentials, tokens, unsafe provider payloads, vector store
  payloads, embedding vectors, reranker traces, graph runtime payloads,
  executable prompt assembly payloads, provider request/response payloads,
  frontend-rendered markup, or report-rendered payloads.
- Prompt context audit review decision artifacts must not mutate Artifact rows
  outside declared audit review decision output, mutate source artifacts,
  mutate prompt context audit summary artifacts, mutate prompt context
  consumption artifacts, mutate prompt context evidence artifacts, mutate
  retrieval boundary artifacts, mutate prompt eligibility artifacts, rewrite
  creation artifacts, mutate historical ReviewHistory, FailureAnalysis, Report,
  TestRun, TestResult, TestCase, GeneratedCaseCandidate, KnowledgeEvidence, or
  unrelated TestKnowledgeCard rows, run prompt assembly, execute AITasks, call
  providers, change retrieval ranking, invoke MCP runtime, create vector
  indexes, create embeddings, rerank, run graph jobs, render frontend pages,
  generate reports, call remote CI providers, add RBAC, create tenants, or
  change permissions.

TestKnowledgeCard Prompt Context Audit Review Summary Export artifact rules:

- `test_knowledge_card_prompt_context_audit_review_summary_export.json` may be
  stored as an Artifact with
  `artifact_type=test_knowledge_card_prompt_context_audit_review_summary_export`,
  `owner_entity_type=AITask` or `owner_entity_type=Project`, and
  `manifest_kind=test_knowledge_card_prompt_context_audit_review_summary_export`
  in a later scoped implementation.
- The prompt context audit review summary export artifact must include
  `export_prompt_context_audit_review_summary`, prompt request id or AITask id
  when available, prompt context audit review decision artifact id, prompt
  context audit summary artifact id, prompt context consumption artifact id,
  prompt context evidence artifact id, context manifest artifact id,
  `used_knowledge` decision, usage status, review action, review outcome
  summary, accepted citation group, questioned citation group, rejected
  citation group, unresolved follow-up flags, unsupported claim references,
  reviewer comment summary, source hashes, PromptVersion id, SkillVersion id,
  ReviewHistory links, and failure code when applicable.
- Summary export artifacts are evidence packages about audit review decision
  artifacts. They must not invent citations, rewrite `used_knowledge`, promote
  unsupported claims, create prompt eligibility, approve TestKnowledgeCard
  content, approve generated cases, turn skipped evidence into cited evidence,
  render reports, or expose download endpoints.
- Prompt context audit review summary export artifacts must not contain raw
  large source text, credentials, tokens, unsafe provider payloads, vector
  store payloads, embedding vectors, reranker traces, graph runtime payloads,
  executable prompt assembly payloads, provider request/response payloads,
  frontend-rendered markup, report-rendered payloads, or downloadable provider
  payloads.
- Prompt context audit review summary export artifacts must not mutate Artifact
  rows outside declared summary export output, mutate source artifacts, mutate
  prompt context audit review decision artifacts, mutate prompt context audit
  summary artifacts, mutate prompt context consumption artifacts, mutate prompt
  context evidence artifacts, mutate retrieval boundary artifacts, mutate
  prompt eligibility artifacts, rewrite creation artifacts, mutate historical
  ReviewHistory, FailureAnalysis, Report, TestRun, TestResult, TestCase,
  GeneratedCaseCandidate, KnowledgeEvidence, or unrelated TestKnowledgeCard
  rows, run prompt assembly, execute AITasks, call providers, change retrieval
  ranking, invoke MCP runtime, create vector indexes, create embeddings,
  rerank, run graph jobs, render frontend pages, generate reports, expose
  export/download endpoints, call remote CI providers, add RBAC, create
  tenants, or change permissions.

TestKnowledgeCard Prompt Context Review Discrepancy artifact rules:

- `test_knowledge_card_prompt_context_review_discrepancy.json` may be stored
  as an Artifact with
  `artifact_type=test_knowledge_card_prompt_context_review_discrepancy`,
  `owner_entity_type=AITask` or `owner_entity_type=Project`, and
  `manifest_kind=test_knowledge_card_prompt_context_review_discrepancy` in a
  later scoped implementation.
- The prompt context review discrepancy artifact must include
  `track_prompt_context_review_discrepancy`, prompt request id or AITask id
  when available, review summary export artifact id, prompt context audit
  review decision artifact id, prompt context audit summary artifact id,
  prompt context consumption artifact id, prompt context evidence artifact id,
  context manifest artifact id, `used_knowledge` decision, usage status,
  discrepancy type, affected citation ids, evidence gap summary, mismatch
  reason, reviewer note, severity, resolution status, unresolved follow-up
  flags, unsupported claim references, source hashes, PromptVersion id,
  SkillVersion id, ReviewHistory links, and failure code when applicable.
- Discrepancy artifacts are evidence about mismatches. They must not invent
  citations, rewrite `used_knowledge`, promote unsupported claims, create
  prompt eligibility, approve TestKnowledgeCard content, approve generated
  cases, turn skipped evidence into cited evidence, auto-resolve
  discrepancies, render reports, or expose download endpoints.
- Prompt context review discrepancy artifacts must not contain raw large source
  text, credentials, tokens, unsafe provider payloads, vector store payloads,
  embedding vectors, reranker traces, graph runtime payloads, executable
  prompt assembly payloads, provider request/response payloads,
  frontend-rendered markup, report-rendered payloads, downloadable provider
  payloads, or generated replacement evidence.
- Prompt context review discrepancy artifacts must not mutate Artifact rows
  outside declared discrepancy output, mutate source artifacts, mutate review
  summary export artifacts, mutate prompt context audit review decision
  artifacts, mutate prompt context audit summary artifacts, mutate prompt
  context consumption artifacts, mutate prompt context evidence artifacts,
  mutate retrieval boundary artifacts, mutate prompt eligibility artifacts,
  rewrite creation artifacts, mutate historical ReviewHistory, FailureAnalysis,
  Report, TestRun, TestResult, TestCase, GeneratedCaseCandidate,
  KnowledgeEvidence, or unrelated TestKnowledgeCard rows, run prompt assembly,
  execute AITasks, call providers, change retrieval ranking, invoke MCP
  runtime, create vector indexes, create embeddings, rerank, run graph jobs,
  render frontend pages, generate reports, expose export/download endpoints,
  call remote CI providers, add RBAC, create tenants, or change permissions.

Slice 33 MCP-ready tool and KnowledgeAdapter safety artifact rules:

- ToolDefinition safety is metadata only. Listing ToolDefinition rows or
  MCP-ready schemas must not create artifacts by itself.
- Every executed ToolInvocation must preserve bounded artifacts according to
  its `artifact_policy`: stdout, stderr, structured output, validation errors,
  runtime manifests, dependency snapshots, environment snapshots, or other
  explicitly named output artifacts.
- Failed, timed-out, rejected, cancelled, or validation-blocked invocations
  should persist bounded error evidence when available. They must not rewrite
  previous successful artifacts or create Report conclusions by themselves.
- `artifact_policy` must not authorize artifact upload, mutation, deletion,
  signed URLs, cloud storage, broad artifact browsing, remote fetch, MCP
  transport capture, or provider SDK side effects.
- KnowledgeAdapter safety uses `provider_state` only as display/health metadata
  in config or safety-policy artifacts. `provider_state=disabled` and
  `provider_state=unhealthy` must produce local/no-knowledge fallback evidence
  when a workflow continues without provider results.
- Future external provider outputs must normalize into Chtest
  `KnowledgeEvidence` plus persisted Artifact metadata before they are cited by
  prompts, GeneratedCaseCandidate rows, or review surfaces. Raw provider
  payloads, provider schemas, transport details, credentials, tokens, OAuth
  state, API keys, remote URLs, vector DB settings, embedding model settings,
  reranker settings, graph runtime settings, and MCP transport settings must
  not be persisted as reviewable business evidence.
- Safety artifacts must not create TestKnowledgeCard rows, mutate Artifact
  rows outside their declared outputs, approve or reject GeneratedCaseCandidate
  rows, promote TestCase rows, create ToolInvocation rows from configuration
  changes, generate Reports, start MCP runtime, call provider SDKs, create
  vector indexes, create embeddings, rerank, run graph jobs, or update remote
  CI provider state.

## 6. Evidence Manifest

报告必须生成 evidence_manifest.json：

```json
{
  "report_id": "00000000-0000-0000-0000-000000001401",
  "conclusion": "passed",
  "evidence": [
    {
      "artifact_id": "00000000-0000-0000-0000-000000001501",
      "artifact_type": "junit",
      "supports_claim": "3 pytest cases passed",
      "required": true
    }
  ],
  "missing_evidence": []
}
```

如果 missing_evidence 非空，报告 conclusion 不能是 `passed`。

Evidence manifest artifact rules:

- `evidence_manifest.json` is stored as an Artifact with
  `artifact_type=report_json`, `owner_entity_type=Report`, and
  `owner_entity_id=report_id`.
- `metadata_json` must include `manifest_kind=evidence_manifest`,
  `related_entity_type`, `related_entity_id`, and `evidence_count`.
- Every evidence item must reference a persisted Artifact id or a structured
  TestRun/TestResult metric.
- Report conclusions must cite evidence before AI explanation. A report cannot
  conclude `passed` when required TestRun/TestResult/artifact evidence is
  missing.

## 7. 脱敏规则

展示 stdout、stderr、raw LLM output、ContextArtifact、logs、OpenAPI、fixture 前必须执行基础脱敏：

- API key：`sk-...`、`ghp_...`、`AKIA...`。
- Authorization header。
- Cookie。
- password/token/secret 字段。
- 手机号、邮箱、身份证或常见个人敏感信息。
- 内部生产域名、生产数据库连接串、生产 IP、生产账号。
- 本机绝对路径可保留，但报告导出时建议截断用户目录。

脱敏后保存 redaction_applied=true。

ContextArtifact 安全规则：

- ContextArtifact 写入前必须执行 secret scan。
- ContextArtifact 展示前必须再次走 redaction view，不直接信任保存时状态。
- `safe_to_show` 必须由服务端计算，不能完全信任客户端传值。
- 如果发现高风险 secret，服务端应拒绝写入或保存脱敏版本，并记录 `redaction_report.json`。
- 默认允许的 MIME：`text/markdown`, `text/plain`, `application/json`, `application/yaml`, `text/yaml`。
- V1 单个 ContextArtifact 最大 1 MiB；单个 AITask 最多注入 10 个 ContextArtifact，合计不超过 2 MiB。
- 二进制文件、压缩包、图片、视频不能作为 ContextArtifact 注入 prompt；它们只能作为普通 Artifact 证据保存。

Extension Surface artifact rules:

- RAG 知识库页面展示的 project knowledge must come from ContextArtifact
  Artifact rows.
- KnowledgeAdapterConfig is configuration state and must not create retrieval
  artifact types in V1.
- If an AI task uses project context, its prompt input artifact must include
  `context_manifest.json` with exact ContextArtifact ids and hashes.
- AI tasks must keep `used_knowledge=false` while KnowledgeAdapter is
  `not_configured`, `disabled`, or V1 `configured_stub`.
- `provider_state=disabled` or `provider_state=unhealthy` must keep
  `used_knowledge=false` unless a later explicit provider slice records valid
  normalized KnowledgeEvidence. Fallback must be visible in metadata or
  bounded error artifacts.
- V2 Slice 19 may create `knowledge_retrieval.json` only for deterministic
  local retrieval from eligible ContextArtifacts.
- Slice 30 may define `test_knowledge_card`, `knowledge_evidence`, and
  `case_review_findings` artifact rules for structured testing knowledge
  evidence. Defining these artifact types must not enable a RAG runtime,
  external provider, vector index, embedding, reranking, graph runtime, or MCP
  runtime.
- V1 must not create vector index, embedding, chunk, reranking, MCP transport, or
  external provider response artifacts.
- Slice 19 still must not create vector index, embedding, chunk, reranking, MCP
  transport, or external provider response artifacts.

## 8. 保留与清理

V1 默认不自动删除 artifact。后续可加清理策略：

| 类型 | 建议保留 |
|---|---|
| 报告 | 长期 |
| 用例生成候选 | 长期 |
| raw LLM output | 90 天或长期，用户可配置 |
| stdout/stderr | 30-90 天 |
| trace/video/screenshot | 30 天 |

## 9. 写入规则

- Artifact 写入必须先写临时文件，再原子 rename。
- 写入后计算 sha256。
- DB 记录 file_path、size_bytes、sha256。
- 业务表只保存 artifact_id，不保存大文本证据。
- 文件写入失败时，相关任务必须 failed 或 partial_failed，不能假装成功。
- ContextArtifact 写入必须记录 title、source_ref、safe_to_show、redaction_applied、allowed_for_prompt。
- AI prompt input artifact 必须生成 `context_manifest.json`，记录本次实际使用的 context artifact id、sha256、title、mime_type、redaction_applied。

Slice 27 AI task evidence artifact link rules:

- AI task evidence artifact links are read-only local Artifact links derived
  from persisted Artifact rows owned by an AITask.
- `safe_to_show=true` is required before the AI Workbench may render a direct
  local open link.
- `safe_to_show=false` artifacts remain visible as metadata and must be marked
  not directly openable in the UI.
- Raw LLM output artifacts must not be inlined in the AI Workbench even when
  their metadata is visible.
- Artifact links must use the existing local artifact access rules and must not
  accept arbitrary file paths from the client.
- AI task artifact links must not mutate Artifact rows, artifact files, AITask,
  LLMCallLog, prompt/skill versions, context artifacts, Report,
  FailureAnalysis, QualityGateDecision, review history, RAG runtime, MCP
  runtime, RBAC, tenants, or permissions.
