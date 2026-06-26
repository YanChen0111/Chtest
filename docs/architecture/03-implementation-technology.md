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
| Runner | Python subprocess + allowlist | pytest/TestCommand 执行 |
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
artifact_policy
```

V1 禁止任意 shell。所有命令必须来自 TestCommand 或 ToolDefinition allowlist。

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
7. 审批后通过 TestRunnerTool 或 PlaywrightTool 执行。
8. 结果进入 TestRun/TestResult/Report。

V1 支持：pytest、Playwright。Newman/JMeter 后置。

## 7. CI/CD 管理实现技术

CI/CD 管理是 V1 支线能力。第一版使用本地 git 命令和手动 diff 输入，不接云 CI/CD 平台：

- `git status --short`
- `git diff --name-status base head`
- `git diff --unified=80 base head`
- `git show --stat commit`

实现步骤：

1. 后端读取 repository local_path。
2. 用户选择 base/head 或上传 diff。
3. ChangeSetTool 生成 CICDRun 和 CICDChangedFile。
4. CICDChangeAnalysisAgent 生成风险摘要。
5. UnitTestAgent 生成 UnitTestPatch artifact。
6. PatchScopeGate 校验路径。
7. 用户确认后才允许应用 patch。
8. TestRunner 执行新增 pytest 和回归。

Patch 规则：V1 只允许写测试目录，禁止修改业务源码。

前端实现使用 A 方案浅色工作台设计，页面名称为 `CI/CD 管理`。内部模块、API 或数据对象使用 `cicd_quality`、`CICDRun`、`CICDChangedFile`、`UnitTestPatch`。

## 8. 测试执行实现技术

### pytest

- V1 P0 支持。
- 从 TestCommand allowlist 选择命令。
- 设置 working directory。
- 限制 timeout。
- 收集 stdout/stderr。
- 尝试解析 JUnit 和 coverage。

### Playwright

- V1 P1 支持最小闭环。
- 支持运行已有测试。
- 支持执行审批后的 AutomationDraft。
- artifact: trace.zip、screenshot、video 可选、console、network 可后置。

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
