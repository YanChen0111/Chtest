# Implementation Technology Guide

## 1. 技术选型总览

V1 技术栈冻结，除非进入 ADR 流程，不再讨论更换主技术栈。

| 层 | 技术 | 第一版用途 |
|---|---|---|
| Backend | FastAPI | API、状态机、任务入口 |
| Schema | Pydantic v2 | 请求/响应/AI 输出校验 |
| ORM | SQLAlchemy 2 | PostgreSQL 数据访问 |
| Migration | Alembic | 数据库迁移 |
| DB | PostgreSQL 16 | 核心数据 |
| Queue | Redis + RQ | AI 任务和工具执行队列 |
| Frontend | Vue 3 + TypeScript + Vite | Web 控制台 |
| UI | Arco Design Vue | 表格、抽屉、表单、统计图 |
| Runner | sandboxed subprocess contract + allowlist | pytest/TestCommand 执行；Docker runner-ready |
| Web Test | Playwright | V1 最小 Web 自动化闭环 |
| API Test | Newman | V1.1 后置 |
| Performance | JMeter | V1.1/V2 后置 |
| Report | Markdown/HTML/JSON | 可读和可机器分析报告 |
| Deploy | Docker Compose | 本地一致环境 |
| LLM | Mock Provider + OpenAI-compatible Provider | 先 mock 跑通，再接真实模型 |

## 2. 后端实现规则

- 每个业务模块包含 `models.py`、`schemas.py`、`service.py`、`router.py`。
- 长任务只在 API 创建任务，不在请求线程里执行。
- 业务状态变化写入数据库，进度事件写入 Redis。
- Pydantic schema 要区分 Create/Update/Read/Internal。
- AI 输出必须先经过 JSON schema 校验，再进入业务表。
- 模型字段、API、状态机必须遵循 `docs/contracts/`。

## 3. Worker 实现规则

Worker 处理三类任务：

```text
AI Task
  -> 调用 LLM/mock provider
  -> 校验输出
  -> 写业务结果
  -> 写 artifact

Tool Task
  -> 校验工具参数
  -> 检查审批和 allowlist
  -> 执行工具
  -> 解析结果
  -> 写 TestRun/TestResult

Report Task
  -> 读取业务数据和 artifact
  -> 生成 md/html/json
  -> 写 Report
```

## 4. Tool Adapter 接口

```text
ToolAdapter.run(input, context) -> ToolResult

ToolResult
  status: success | failed | cancelled | timeout
  stdout_ref
  stderr_ref
  artifacts[]
  parsed_result
  started_at
  finished_at
  exit_code
```

所有工具必须注册 ToolDefinition：

```text
name
description
input_schema
output_schema
risk_level
approval_required
timeout_seconds
allowed_projects
command_allowlist
allowed_working_directories
forbidden_shell_operators
max_stdout_bytes
max_stderr_bytes
artifact_policy
```

V1 禁止任意 shell。所有命令必须来自 TestCommand 或 ToolDefinition allowlist。

### 4.1 Tool Allowlist 安全规则

Tool Adapter 必须在执行前完成以下检查：

1. ToolDefinition 必须存在、启用，并匹配项目范围。
2. 命令必须来自 TestCommand 或 ToolDefinition `command_allowlist_json`，不能接受前端或 AI 直接传入的任意 shell 字符串。
3. 命令执行必须使用参数数组或等价的非 shell 模式，不使用 `shell=True`。
4. 命令字符串或参数中出现 `;`、`&&`、`||`、`|`、`>`、`>>`、`<`、`$(`、反引号时必须拒绝，除非未来有明确的工具级解析器白名单。
5. working directory 必须先 canonicalize，解析符号链接后仍位于 Repository 或 ToolDefinition 的 allowlisted root 下。
6. artifact 输出路径必须先 canonicalize，解析后仍位于 configured artifact root 下。
7. timeout 必须强制执行，超时后 ToolInvocation 进入 `timeout`。
8. stdout/stderr 捕获必须遵循 `max_stdout_bytes` 和 `max_stderr_bytes`，超出部分截断并在 artifact metadata 标记。
9. stdout、stderr、raw provider output 和报告展示前必须执行 secret redaction。
10. medium/high risk 或 `approval_required=true` 的工具必须先进入 approval 状态。

这些规则同时适用于 pytest、Playwright、GitTool、PatchScopeGate、ReportTool，以及后续 Newman/JMeter。

### 4.2 Runner Sandbox Contract

V1 runner execution must expose the same safety contract whether the first implementation uses local subprocess or a Docker runner.

Required runtime fields:

```text
runner_mode: local_subprocess | docker_runner
run_workspace
repository_mount_path
repository_readonly
artifact_root
network_enabled
cpu_limit
memory_limit_mb
timeout_seconds
environment_snapshot_ref
dependency_snapshot_ref
```

Rules:

1. Each TestRun must use an isolated per-run workspace or runtime directory.
2. Repository access must be read-only by default. Writable paths are limited to test output directories and artifact root.
3. AutomationDraft runtime files must be copied from Chtest artifacts into the run workspace or passed as explicit readonly inputs.
4. Network access defaults to disabled for unit/pytest runs unless TestCommand or Environment explicitly enables it.
5. Environment variables must be materialized from Environment records and safe defaults; secret values are referenced and redacted in artifacts.
6. Dependency snapshots record package manager files, lockfiles, Python/Node versions, and runner image when available.
7. Runner stdout/stderr, JUnit, coverage, trace, screenshot, and runtime_manifest must remain under artifact root.
8. Local subprocess mode is acceptable for early V1 dev only if it enforces the same path, timeout, redaction, and allowlist checks.

## 5. Prompt / Skill 实现规则

- Prompt 存文件，同时在 DB 记录 PromptVersion 和 hash。
- Skill 存 markdown，同时在 DB 记录 SkillVersion、适用 Agent、输入输出 schema、质量门禁。
- AI Task 必须绑定 PromptVersion 和 SkillVersion。
- Prompt 输出必须优先使用 JSON schema。
- Prompt 禁止包含 secret、真实 token、生产密码。
- 具体格式遵循 `docs/contracts/05-prompt-skill-contract.md`。

## 6. AutomationDraft 实现技术

AutomationDraft 是 V1 主线 B 的关键实体。

实现步骤：

1. 用户从 Requirement 或 TestCase 发起自动化草稿生成。
2. AutomationDraftAgent 读取上下文和 Prompt/Skill。
3. LLM/mock provider 输出结构化 draft。
4. 后端校验 draft_code、target_framework、suggested_file_path。
5. 保存 AutomationDraft，不写入业务项目。
6. 用户审批或编辑。
7. 审批后，后端将 draft_code 写入 Chtest artifact runtime 目录，并创建 `automation_draft_code` Artifact。
8. ToolExecutionAgent 使用 artifact runtime 文件和 allowlisted TestCommand 触发 TestRunnerTool 或 PlaywrightTool。
9. TestRun 记录 `runtime_artifact_ids`，并写入 `runtime_manifest.json`。
10. 结果进入 TestRun/TestResult/Report。

### 6.1 AutomationDraft Runtime 策略

V1 采用 `artifact_runtime_copy` 策略：

```text
AutomationDraft.draft_code
  -> user approves
  -> artifacts/projects/{project_id}/automation-drafts/{automation_draft_id}/runtime/{safe_file_name}
  -> runtime_artifact_id
  -> TestRunnerTool / PlaywrightTool
```

规则：

- AutomationDraft 生成和审批阶段只写 Chtest 数据库与 artifact，不写目标业务仓库。
- 审批后创建临时 runtime 文件，路径只能位于 Chtest artifact root 下。
- runtime 文件名来自 `suggested_file_path` 的安全化结果；必须去除绝对路径、`..`、shell 特殊字符和仓库外路径。
- TestCommand 的 working directory 仍必须在 allowlisted repository path 下；runtime 文件作为明确参数传入执行器。
- TestRun 必须记录本次实际执行的 runtime artifact id，报告和失败归因必须能追溯到该文件。
- 运行通过并不代表自动化资产已经进入业务仓库；Promote 是后续人工导出或 patch 流程。
- 如果用户希望把草稿落到业务仓库，应走未来的 manual export 或 Git Quality UnitTestPatch 流程，不在 V1 自动写入。

### 6.2 AutomationDraft Repair Loop

After an approved AutomationDraft execution fails, Chtest may create a repair task. Repair is evidence-driven and review-gated.

```text
failed TestRun
  -> FailureAnalysis
  -> AutomationRepairTask
  -> repaired AutomationDraft candidate
  -> human review/edit
  -> approved repaired draft
  -> new TestRun
```

Rules:

- Repair input must include the failed TestRun, runtime_manifest, stdout/stderr/JUnit/trace artifacts, and FailureAnalysis.
- Repair output must be stored as a new draft revision or repair artifact; it must not silently overwrite the approved draft.
- Repair attempts must have a maximum retry count configured per project or tool, default `2`.
- Repair must preserve AutomationDraft approval gates and artifact runtime execution strategy.
- If evidence is missing, repair must return `insufficient_evidence` instead of inventing fixture names, locators, or environment assumptions.

V1 支持：pytest、Playwright。Newman/JMeter 后置。

## 7. Git Quality Center 实现技术

Git Quality 是 V1 支线能力。第一版使用本地 git 命令：

- `git status --short`
- `git diff --name-status base head`
- `git diff --unified=80 base head`
- `git show --stat commit`

实现步骤：

1. 后端读取 repository local_path。
2. 用户选择 base/head 或上传 diff。
3. GitTool 生成 GitChangeSet 和 GitChangedFile。
4. GitDiffAgent 生成风险摘要。
5. UnitTestAgent 生成 UnitTestPatch artifact。
6. PatchScopeGate 校验路径。
7. 用户确认后才允许应用 patch。
8. TestRunner 执行新增 pytest 和回归。

Patch 规则：V1 只允许写测试目录，禁止修改业务源码。

## 8. 测试执行实现技术

### pytest

- V1 P0 支持。
- 从 TestCommand allowlist 选择命令。
- 设置 working directory。
- 限制 timeout。
- 收集 stdout/stderr。
- 尝试解析 JUnit 和 coverage。
- 执行 AutomationDraft 时，pytest 目标文件来自 Chtest artifact runtime 目录，不直接来自业务仓库写入。

### Playwright

- V1 P1 支持最小闭环。
- 支持运行已有测试。
- 支持执行审批后的 AutomationDraft。
- artifact: trace.zip、screenshot、video 可选、console、network 可后置。
- 执行 AutomationDraft 时，Playwright spec 文件来自 Chtest artifact runtime 目录；locator 失败必须保存 trace/screenshot 后进入失败归因。

### Newman

- V1.1 后置。
- collection/environment 文件作为 artifact。
- 执行后收集 JSON result。
- AI 分析失败请求、断言、响应体。

### JMeter

- V1.1/V2 后置。
- 执行 non-GUI：`jmeter -n -t test.jmx -l result.jtl -e -o html-report`。
- 解析 JTL：请求数、错误率、平均响应、P95/P99。

## 9. 前端实现规则

- 页面以三条最小闭环为中心，不做营销页。
- 表格、抽屉、详情页、状态条为主。
- 长任务使用 SSE/WebSocket 展示进度。
- 用例评审、AutomationDraft 评审和 Patch 评审必须支持差异查看。
- 报告页必须同时展示结论、证据和原始 artifact 链接。
- 不做企业权限和团队后台导航。

## 10. 测试策略

| 层 | 测试 |
|---|---|
| Backend service | pytest + test database |
| API | FastAPI TestClient |
| Worker | fake Redis / test queue |
| Tool Adapter | mock subprocess + small fixture |
| Frontend | Vitest + Playwright smoke |
| E2E | Docker Compose smoke |

第一版每个 Slice 至少包含 smoke 验证命令，并优先用 `docs/fixtures/` 验证主流程。
