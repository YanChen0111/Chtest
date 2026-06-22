# Chtest Platform Architecture

## 1. 架构目标

Chtest V1 是面向个人测试工程师、自动化测试工程师的 AI 测试证据工作台。第一版采用单用户、模块化单体 + Worker + Tool Adapter 架构，目标是保证功能真实可运行、开发复杂度可控，后续可扩展 MCP/RAG/更多执行器。

V1 服务三条最小闭环：

1. 需求到用例。
2. 用例到自动化。
3. Git 到质量报告。

## 2. 容器架构

```text
┌─────────────────────────────────────────────────────────────┐
│                        Docker Network                        │
│                                                             │
│  ┌─────────────┐      ┌─────────────┐                       │
│  │  frontend   │ ---> │   backend   │                       │
│  │ Vue3/Vite   │      │  FastAPI    │                       │
│  └─────────────┘      └──────┬──────┘                       │
│                              │                              │
│              ┌───────────────┼────────────────┐             │
│              ▼               ▼                ▼             │
│       ┌────────────┐   ┌────────────┐   ┌────────────┐       │
│       │ PostgreSQL │   │   Redis    │   │  storage   │       │
│       └────────────┘   └─────┬──────┘   └────────────┘       │
│                              │                              │
│                              ▼                              │
│                      ┌─────────────┐                        │
│                      │   worker    │                        │
│                      │     RQ      │                        │
│                      └──────┬──────┘                        │
│                             ▼                               │
│                    ┌────────────────┐                       │
│                    │ Tool Adapters  │                       │
│                    │ pytest/Playwright                      │
│                    └────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## 3. 服务职责

| 服务 | 技术 | 职责 |
|---|---|---|
| frontend | Vue 3 + Vite + TypeScript + Arco | 工作台 UI、评审窗口、草稿审批、任务状态、报告展示 |
| backend | FastAPI + Pydantic v2 | API、业务服务、状态机、单用户上下文、SSE/WebSocket |
| worker | Python + RQ | AI 任务、工具执行、报告生成、artifact 处理 |
| postgres | PostgreSQL 16 | 核心业务数据、评审、指标、执行结果 |
| redis | Redis 7 | 队列、任务进度、锁、事件缓存 |
| storage | local volume | diff、patch、日志、trace、报告等 artifact |

## 4. 后端模块边界

```text
backend/app/
  main.py
  core/
    config.py
    database.py
    redis.py
    single_user.py
  modules/
    projects/
    requirements/
    case_generation/
    test_cases/
    automation_drafts/
    git_quality/
    ai_tasks/
    prompts/
    skills/
    tools/
    executions/
    reports/
    knowledge/
  workers/
    enqueue.py
    handlers/
  migrations/
```

| 模块 | 主要职责 |
|---|---|
| projects | 项目、模块、仓库、环境、测试命令 |
| requirements | 需求录入、需求评审、风险矩阵 |
| case_generation | 用例候选生成、生成批次、候选评审 |
| test_cases | 正式用例库、模块树、用例步骤、套件 |
| automation_drafts | pytest/Playwright 草稿生成、审批、执行入口 |
| git_quality | diff、变更分析、UnitTestPatch、回归计划 |
| ai_tasks | AI 任务状态机、artifact、LLM 调用日志 |
| prompts | PromptVersion、schema、hash |
| skills | SkillVersion、质量门禁、禁止事项 |
| tools | ToolDefinition、ToolInvocation、审批 |
| executions | TestRun、TestResult、执行日志解析 |
| reports | Markdown/HTML/JSON 报告生成、evidence manifest |
| knowledge | Knowledge/RAG Adapter 空实现和配置 |

## 5. 前端页面结构

```text
frontend/src/
  views/
    ai-workbench/
    requirement-review/
    case-generation-review/
    test-case-library/
    automation-draft-center/
    git-quality-center/
    execution-center/
    tool-center/
    prompt-skill-center/
    report-center/
    settings/
  components/
    review/
    testcase/
    automation/
    git/
    execution/
    report/
  stores/
  api/
  router/
```

## 6. 队列设计

| 队列 | 任务 |
|---|---|
| `ai.default` | 普通 AI 任务 |
| `ai.long` | 用例批量生成、失败归因、报告生成 |
| `automation.draft` | AutomationDraft 生成 |
| `git.quality` | diff 分析、UnitTestPatch 生成、回归计划 |
| `tool.execution` | pytest/TestRunner、Playwright 调度 |
| `report.generate` | HTML/Markdown/JSON 报告生成 |

Newman/JMeter 后置到 V1.1/V2，不进入 V1 主队列要求。

## 7. 核心数据模型

核心字段以 `docs/contracts/01-data-model-contract.md` 为准。

```text
Workspace
User
Project
Module
Repository
Environment
TestCommand
Requirement
RequirementReview
RiskItem
CaseGenerationTask
GeneratedCaseCandidate
TestCase
AutomationDraft
GitChangeSet
GitChangedFile
GitRiskAnalysis
UnitTestPatch
RegressionPlan
AITask
Artifact
LLMCallLog
PromptVersion
SkillVersion
ToolDefinition
ToolInvocation
TestRun
TestResult
FailureAnalysis
Report
KnowledgeProviderConfig
KnowledgeEvidence
```

## 8. API 设计原则

- REST API 为主，SSE/WebSocket 用于任务进度。
- 所有创建 AI 任务的 API 返回 `ai_task_id`。
- 所有长任务结果通过 artifact 和业务实体回写。
- 所有工具调用必须落 `ToolInvocation`。
- 所有 AI 调用必须落 `LLMCallLog`。
- 核心 API 以 `docs/contracts/02-api-contract.md` 为准。

示例 API：

```text
POST /api/projects
POST /api/requirements
POST /api/requirements/{id}/review
POST /api/case-generation/tasks
POST /api/case-review/items/{id}/approve
POST /api/automation/drafts
POST /api/automation/drafts/{id}/approve
POST /api/test-runs
POST /api/git/change-sets
POST /api/git/change-sets/{id}/unit-test-patches
GET  /api/reports/{id}
GET  /api/ai-tasks/{id}
```

## 9. Artifact 设计

Artifact 结构以 `docs/contracts/04-artifact-contract.md` 为准。

```text
artifacts/projects/{project_id}/
  ai-tasks/{ai_task_id}/
  requirements/{requirement_id}/
  case-generation/{generation_task_id}/
  automation-drafts/{automation_draft_id}/
  git-quality/{change_set_id}/
  test-runs/{test_run_id}/
  reports/{report_id}/
```

## 10. 安全与执行边界

- `TestCommand` 必须配置 allowlist。
- Tool Adapter 不接受任意 shell 字符串。
- 高风险工具调用需要人工确认。
- AutomationDraft 未审批不能执行。
- UnitTestPatch 应用必须经过 PatchScopeGate。
- UnitTestPatch 只允许写测试目录。
- V1 禁止 AI 自动修改业务源码。
- artifact 写入必须限定在项目 storage 目录。
- 报告和日志必须脱敏 token、cookie、password、secret。

## 11. 可扩展接口

| 接口 | 第一版 | 后续 |
|---|---|---|
| Knowledge/RAG Adapter | 空实现 | 接外部 RAG |
| MCP Adapter | 配置占位 | 接 GitHub MCP、Chtest MCP |
| Runner Adapter | 本地/容器执行 pytest/Playwright | 分布式执行器 |
| Object Storage | 本地 volume | MinIO/S3 |
| API Test Adapter | 后置 | Newman/Postman CLI |
| Performance Adapter | 后置 | JMeter non-GUI |
| Code Analysis | diff/规则 | tree-sitter/codegraph/LSP |
