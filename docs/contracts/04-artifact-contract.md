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
```

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
- V2 Slice 19 may create `knowledge_retrieval.json` only for deterministic
  local retrieval from eligible ContextArtifacts.
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
