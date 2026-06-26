# Chtest CI/CD Quality Center Design

## 1. 文档目的

CI/CD 质量中心是 Chtest V1 的支线能力。它负责把一次本地代码变更转换成测试补全、pytest 回归、失败归因、质量门禁和质量报告，但不压过“需求到用例、用例到自动化”两条主线。

用户可见页面名称统一为 `CI/CD 质量中心`。当前内部领域对象和契约名使用 `CICDRun`、`CICDChangedFile`、`CICDChangeAnalysisAgent`、`UnitTestPatch`、`QualityGateDecision`。

本文定义该模块的产品流程、技术实现、数据模型、安全边界、版本边界和 V1 验收标准。

## 2. 核心目标

- 让每次本地 diff 或 base/head 变更都有可见质量状态。
- 基于变更自动识别测试风险。
- 生成缺失单元测试 patch，但必须人工审批。
- 自动选择相关 pytest 回归测试。
- 运行新增 pytest 和回归测试。
- 失败时基于证据进行归因。
- 输出 passed、failed、needs_review 的质量门禁结论。
- 输出可追溯 CI/CD 质量报告。

## 3. V1 输入范围

| 输入方式 | V1 是否支持 | 说明 |
|---|---|---|
| 本地仓库路径 + base/head | 是 | 主路径 |
| 上传 diff 文件 | 是 | 适合无本地仓库或跨工具使用 |
| GitHub PR URL | 否 | V2 通过 GitHub MCP |
| GitHub webhook | 否 | V2 |
| CI 自动触发 | 否 | V2/V3 |
| 真实 CD 发布 | 否 | V3；V1 只给发布准备度和质量门禁结论 |

## 4. 处理流程

```text
Repository selected
  -> create CICDRun
  -> ChangeSetTool reads status/diff
  -> changed files categorized
  -> CICDChangeAnalysisAgent analyzes risk
  -> UnitTestAgent generates patch
  -> PatchScopeGate validates patch
  -> user reviews patch
  -> approved patch applied
  -> new tests executed
  -> RegressionAgent selects regression
  -> regression executed
  -> FailureAnalysisAgent analyzes failures
  -> QualityGateDecision generated
  -> ReportAgent generates CI/CD Quality Report
```

## 5. 文件变更分类

CICDChangedFile 建议字段：

```text
id
cicd_run_id
path
old_path
change_type: added | modified | deleted | renamed
language
file_role: source | test | config | docs | migration | fixture | build | unknown
risk_level: low | medium | high
risk_reasons[]
lines_added
lines_deleted
```

分类规则：

| 路径/特征 | file_role |
|---|---|
| `test/`, `tests/`, `__tests__/`, `e2e/`, `spec/` | test |
| `src/`, `app/`, `lib/`, `packages/` | source |
| `pyproject.toml`, `package.json`, `pom.xml`, `build.gradle` | build |
| `alembic/`, `migrations/` | migration |
| `.md`, `docs/` | docs |
| `fixtures/`, `mock/`, `data/` | fixture |

## 6. 风险评分

风险评分不是为了替代人工，而是为了决定测试深度。

建议规则：

| 条件 | 风险 |
|---|---|
| 修改核心业务源码且无对应测试变更 | high |
| 修改认证、权限、支付、交易、数据删除、调度逻辑 | high |
| 修改数据库迁移或 schema | high |
| 修改公共工具函数 | medium/high，取决于调用范围 |
| 只改文档 | low |
| 只改测试 | medium |
| 修改依赖配置 | medium/high |

CICDChangeAnalysisAgent 输出：

```json
{
  "summary": "string",
  "overall_risk": "medium",
  "impacted_modules": ["module-a"],
  "high_risk_files": [
    {
      "path": "src/foo.py",
      "reason": "core branch logic changed without test update"
    }
  ],
  "test_recommendations": [
    {
      "type": "unit",
      "target": "tests/test_foo.py",
      "reason": "changed branch lacks coverage"
    }
  ]
}
```

## 7. 单测生成设计

### 7.1 输入

- diff 内容。
- changed files。
- existing test files，按路径和命名规则查找。
- project language/framework hints。
- TestCommand allowlist。
- 用户指定测试目标，可选。

### 7.2 测试框架识别

| 项目特征 | 测试框架 |
|---|---|
| `pyproject.toml` + `pytest` | pytest |
| `package.json` + `jest` | jest |
| `package.json` + `vitest` | vitest |
| `playwright.config.*` | Playwright |
| `pom.xml` | Maven/JUnit |
| `build.gradle` | Gradle/JUnit |

V1 可以只实现 pytest、jest/vitest 的基本识别，其他框架先展示 unsupported。

### 7.3 Patch 约束

默认允许修改：

```text
test/
tests/
__tests__/
e2e/
spec/
qa/
docs/qa/
```

默认禁止：

- 修改业务源码。
- 删除测试。
- 添加 skip/xfail/only 掩盖失败。
- 修改锁文件。
- 修改 CI 配置。
- 写入绝对路径或真实凭证。

高风险写入必须人工确认，第一版建议直接拒绝。

### 7.4 Patch Review 状态

```text
generated
  -> scope_validated
  -> awaiting_review
  -> approved
  -> rejected
  -> edited
  -> applied
  -> apply_failed
  -> replaced
```

用户操作：

- 接受 patch。
- 拒绝 patch 并记录原因。
- 编辑 patch 后接受。
- 重新生成。
- 下载 patch。

## 8. 回归选择设计

RegressionAgent 输入：

- `risk_analysis.json` artifact。
- changed files。
- test commands。
- test case library。
- historical test results，可选。

输出：

```json
{
  "strategy": "targeted_regression",
  "recommended_commands": [
    {
      "command_id": "cmd_pytest_unit",
      "reason": "source python files changed",
      "risk_level": "medium"
    }
  ],
  "recommended_suites": [],
  "manual_attention": [
    "database migration changed; confirm test database reset"
  ]
}
```

策略：

| 场景 | 策略 |
|---|---|
| 低风险文档变更 | 可不执行或执行 smoke |
| 普通源码变更 | 执行新增测试 + 相关单测 |
| 公共模块变更 | 相关单测 + 集成 smoke |
| 数据库/配置/依赖变更 | 相关单测 + 集成 + 手动确认 |
| 无法判断 | 建议全量回归或人工选择 |

## 9. 执行设计

执行顺序：

1. Patch 应用后运行新增测试。
2. 新增测试通过后运行推荐回归。
3. 回归失败进入失败归因。
4. 所有结果写入 TestRun/TestResult。

TestRun 字段建议：

```text
id
project_id
cicd_run_id
tool_name
command
working_directory
status
started_at
finished_at
duration_ms
exit_code
stdout_artifact_id
stderr_artifact_id
parsed_result_json
```

TestResult 字段建议：

```text
run_id
test_name
test_file
status: passed | failed | skipped | error
failure_message
failure_artifact_ids[]
duration_ms
```

## 10. 页面设计

CI/CD 质量中心详情页建议布局：

| 区域 | 内容 |
|---|---|
| Header | 仓库、branch、base、head、整体风险、质量门禁结论 |
| Changed Files | 文件路径、类型、风险、行数变化 |
| AI Risk Analysis | 摘要、影响模块、高风险原因、建议测试 |
| Unit Test Patch | diff viewer、scope gate、测试意图、操作按钮 |
| Regression Plan | 推荐命令、原因、风险、用户确认 |
| Execution | 新增测试和回归结果、artifact |
| Failure Analysis | 分类、证据、建议 |
| Quality Gate | passed、failed、needs_review、阻塞原因 |
| Report | CI/CD 质量报告、导出 |

## 11. API 草案

```text
POST /api/cicd/runs
GET  /api/cicd/runs
GET  /api/cicd/runs/{id}
POST /api/cicd/runs/{id}/analyze
POST /api/cicd/runs/{id}/unit-test-patches
POST /api/cicd/unit-test-patches/{id}/approve
POST /api/cicd/unit-test-patches/{id}/reject
POST /api/cicd/unit-test-patches/{id}/apply
POST /api/cicd/runs/{id}/run-new-tests
POST /api/cicd/runs/{id}/select-regression
POST /api/cicd/runs/{id}/run-regression
POST /api/cicd/runs/{id}/quality-gate
POST /api/cicd/runs/{id}/generate-report
```

## 12. 安全边界

- Repository local_path 必须在用户配置的 allowlist 根目录下。
- Git 命令只能执行固定 allowlist，不允许拼接任意 shell。
- diff 输出必须限制最大大小。
- patch 应用前必须 scope gate。
- 测试命令必须来自 TestCommand allowlist。
- stdout/stderr 需要脱敏后展示。
- 高风险工具调用必须审批。
- 禁止自动 git push。

## 13. Artifact 设计

每个 CICDRun 建议 artifact 目录：

```text
artifacts/projects/{project_id}/cicd-quality/{cicd_run_id}/
  diff.patch
  changed_files.json
  risk_analysis.json
  unit_test.patch
  patch_scope_gate.json
  new_tests_stdout.log
  new_tests_stderr.log
  regression_stdout.log
  regression_stderr.log
  junit.xml
  coverage.xml
  failure_analysis.json
  quality_gate.json
  cicd_quality_report.md
  cicd_quality_report.html
  cicd_quality_report.json
```

## 14. V1 验收标准

- 能创建 CICDRun。
- 能读取本地 base/head diff 或上传 diff。
- 能展示变更文件、文件角色、风险等级。
- CICDChangeAnalysisAgent 能生成风险摘要。
- UnitTestAgent 能生成 patch artifact。
- Patch Scope Gate 能阻止业务源码修改。
- 用户可以审批、拒绝、重新生成 patch。
- 能执行新增测试和至少一个回归命令。
- 失败结果能进入 FailureAnalysisAgent。
- 能生成 QualityGateDecision。
- 能生成 CI/CD quality report。

## 15. V2 扩展

- GitHub MCP 读取 PR、commit、Actions 日志。
- GitHub Actions / GitLab CI / Jenkins 运行记录导入。
- PR 评论自动发布报告。
- CI webhook 自动触发。
- 基于过往失败和覆盖率优化回归选择。
- 更强代码结构分析和调用影响分析。

## 16. V3 扩展

- 远程 runner 和分布式执行。
- CD 发布准备检查、发布窗口、回滚建议。
- 小团队质量策略和 branch protection 集成。
- 多项目趋势分析和质量门禁规则模板。
