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

### 3.5 Git Quality

```text
artifacts/projects/{project_id}/git-quality/{change_set_id}/
  diff.patch
  changed_files.json
  risk_analysis.json
  unit_test.patch
  patch_scope_gate.json
```

### 3.6 Test Run

```text
artifacts/projects/{project_id}/test-runs/{test_run_id}/
  stdout.log
  stderr.log
  junit.xml
  coverage.xml
  playwright-trace.zip
  screenshot.png
  parsed_result.json
```

### 3.7 Report

```text
artifacts/projects/{project_id}/reports/{report_id}/
  report.md
  report.html
  report.json
  evidence_manifest.json
```

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
| patch | text/x-diff | unified diff |
| stdout | text/plain | 标准输出 |
| stderr | text/plain | 标准错误 |
| junit | application/xml | JUnit 结果 |
| coverage | application/xml | 覆盖率结果 |
| playwright_trace | application/zip | Playwright trace |
| screenshot | image/png | 截图 |
| report_md | text/markdown | Markdown 报告 |
| report_html | text/html | HTML 报告 |
| report_json | application/json | JSON 报告 |

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

## 7. 脱敏规则

展示 stdout、stderr、raw LLM output 前必须执行基础脱敏：

- API key：`sk-...`、`ghp_...`、`AKIA...`。
- Authorization header。
- Cookie。
- password/token/secret 字段。
- 本机绝对路径可保留，但报告导出时建议截断用户目录。

脱敏后保存 redaction_applied=true。

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
