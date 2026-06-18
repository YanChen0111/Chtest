# Chtest V1 Delivery Plan

## 1. 文档目的

本文是 Chtest 第一版完整实施规划。它告诉后续 AI 或开发者先做什么、每一步交付什么、如何验收、哪些风险需要提前处理。

Chtest V1 目标：做成一个真实可运行的个人测试/自动化测试工程师 AI 测试设计与自动化落地工作台，而不是小 demo。

## 2. V1 交付北极星

V1 围绕三条最小闭环交付：

1. 需求到用例：需求评审 -> 候选用例 -> 人工评审 -> 用例库。
2. 用例到自动化：AutomationDraft -> 审批 -> pytest/Playwright 执行 -> 报告。
3. 代码到质量：Git diff -> UnitTestPatch -> 审批 -> pytest 回归 -> 质量结论。

第一条和第二条是主线，第三条是支线能力。

## 3. 开发总原则

- 每次只做一个可验收 Slice。
- 每个 Slice 必须能运行、能验证、能回滚。
- 先打通真实闭环，再增强细节。
- AI 输出先评审再入库。
- AutomationDraft 先审批再执行。
- UnitTestPatch 先审批再应用，且只允许写测试目录。
- 工具调用先安全再自动化。
- RAG 和 MCP 先留接口，不阻塞 V1 主流程。
- 文档、代码、测试、memory 必须同步更新。

## 4. 推荐目录结构

```text
Chtest/
  backend/
    app/
      core/
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
      tests/
    alembic/
  frontend/
    src/
      pages/
      components/
      stores/
      api/
      router/
  deploy/
    docker-compose.yml
    docker-compose.dev.yml
    env/
  prompts/
  skills/
  mcp_tools/
  artifacts/
  docs/
  memory/
```

## 5. V1 里程碑

```text
M0 Documentation And Contracts Gate
  -> M1 Platform Foundation
  -> M2 AI Runtime Core
  -> M3 Requirement To Case Mainline
  -> M4 AutomationDraft And Pytest Mainline
  -> M5 Playwright Minimal Loop
  -> M6 Reports And Failure Analysis
  -> M7 Git Quality Supporting Flow
  -> M8 Extension Surface And Hardening
```

## 6. M0 Documentation And Contracts Gate

目标：确保后续 AI 读取文档后能继续开发。

交付：

- 产品定位和范围：`docs/product/01-positioning-and-scope.md`。
- 产品 PRD 和页面 PRD。
- AI 质量指标。
- 版本边界和非目标。
- 数据模型契约。
- API 契约。
- 状态机契约。
- Artifact 契约。
- Prompt/Skill 契约。
- 三条 Golden Path fixtures。
- V1 开发流程、切片计划、测试验收文档。
- memory 接续文档。

验收：

- `docs/README.md` 能引导找到全部正式文档。
- `memory/README.md` 能引导下一次 AI 会话读取关键上下文。
- 新 AI 会话能准确说出 V1 定位、三条闭环、技术栈、禁止事项。

## 7. M1 Platform Foundation

目标：搭建真实可运行平台骨架。

### 7.1 后端

任务：

- 创建 FastAPI app。
- 创建 Settings。
- 创建 PostgreSQL 连接。
- 创建 Redis 连接。
- 创建 Alembic。
- 创建 `/health` 和 `/ready`。
- 创建默认单用户上下文。

建议模块：

```text
backend/app/core/config.py
backend/app/core/database.py
backend/app/core/redis.py
backend/app/core/single_user.py
backend/app/main.py
```

验收：

- backend 容器启动。
- `/health` 返回 ok。
- `/ready` 能检查 PostgreSQL 和 Redis。
- Alembic 能执行首个迁移。

### 7.2 前端

任务：

- 创建 Vue 3 + TypeScript + Vite。
- 接入 Arco Design Vue。
- 建立路由和主布局。
- 创建 Home、Project Settings 占位页。

验收：

- frontend 容器启动。
- 页面能访问。
- 能调用 `/health`。

### 7.3 部署

任务：

- 编写 Docker Compose。
- 服务：postgres、redis、backend、worker、frontend。
- 创建 `.env.example`。
- 创建 volume：postgres_data、redis_data、artifacts。

验收：

- `docker compose up` 能启动所有服务。
- 服务之间网络连通。

## 8. M2 AI Runtime Core

目标：所有 AI 任务可追踪、可重试、可审计。

任务：

- 建立 Workspace、User、Project、Module、Repository、Environment、TestCommand。
- 建立 AITask、Artifact、LLMCallLog。
- 建立 Redis worker。
- 实现 LLM Provider Adapter。
- 支持 OpenAI-compatible provider 和 mock provider。
- 实现 PromptVersion。
- 实现 SkillVersion。
- 实现 JSON schema validation。
- 实现 AI Workbench 基础页面。

数据模型：

```text
workspaces
users
projects
modules
repositories
environments
test_commands
ai_tasks
artifacts
llm_call_logs
prompt_versions
skill_versions
```

验收：

- UI/API 能创建项目、模块、仓库、测试命令。
- UI/API 能创建 AI Task。
- Worker 能消费任务并更新状态。
- mock provider 能返回结构化结果。
- 调用日志记录 PromptVersion、SkillVersion、model、token、耗时。
- schema 校验失败时保存 raw artifact。

## 9. M3 Requirement To Case Mainline

目标：打通需求评审到用例评审入库主线。

### 9.1 Requirement Review

任务：

- Requirement model。
- RequirementReview model。
- RiskItem model。
- Requirement Review 页面。
- RequirementReviewAgent。
- RiskAgent。

验收：

- 使用 `docs/fixtures/01-golden-requirement-to-case.md` 输入需求。
- 生成六维评分。
- 生成至少 2 条风险。
- 用户可以编辑并保存评审结果。

### 9.2 Case Generation

任务：

- CaseGenerationTask。
- GeneratedCaseCandidate。
- CaseGenerationAgent。
- 用例 schema 校验。
- 初版重复检测。

验收：

- AI 生成候选用例。
- 候选用例有 steps、expected_results、priority、test_type、requirement_refs。
- 候选用例不会直接进入正式库。

### 9.3 Case Review

任务：

- CaseReviewSession，可先并入 generation task 视图。
- TestCase。
- Case Generation Review 页面。
- 用例质量指标。

验收：

- 用户可以接受、编辑后接受、驳回、要求优化。
- 通过评审的用例进入正式库。
- 批次展示采纳率、驳回率、修改率、重复率、评审进度。

## 10. M4 AutomationDraft And Pytest Mainline

目标：打通用例到自动化主线的 P0 执行闭环。

任务：

- AutomationDraft model。
- AutomationDraftAgent。
- automation_draft_generation Prompt/Skill。
- AutomationDraft 评审页面。
- ToolDefinition。
- ToolInvocation。
- TestRun。
- TestResult。
- TestRunnerTool。
- pytest allowlist 执行。
- stdout/stderr/JUnit artifact。

验收：

- 使用 `docs/fixtures/02-golden-case-to-playwright.md` 中 pytest 示例。
- 从 TestCase 生成 AutomationDraft。
- 未审批 AutomationDraft 不能执行。
- 审批后创建 TestRun。
- pytest 执行结果结构化入库。
- stdout/stderr/JUnit 保存为 artifact。

## 11. M5 Playwright Minimal Loop

目标：让 Web 自动化有最小可用闭环，不做完整低代码平台。

任务：

- PlaywrightTool 初版。
- Playwright AutomationDraft 支持 TypeScript 草稿。
- 执行已有 Playwright 测试或草稿。
- 保存 trace.zip、screenshot、stdout/stderr。
- Playwright 失败归因输入。

验收：

- 使用 `docs/fixtures/02-golden-case-to-playwright.md` 中 Playwright 示例。
- 草稿必须审批后执行。
- artifact 保存。
- 失败时进入 FailureAnalysisAgent。

## 12. M6 Reports And Failure Analysis

目标：生成有证据的质量报告。

任务：

- FailureAnalysis。
- Report。
- evidence_manifest。
- Report Center。
- automation_execution report。
- case_quality report。
- requirement_review report。

验收：

- 失败有证据链。
- 报告输出 md/html/json。
- 无 evidence 的报告不能标记 passed。
- 未归因失败不能给出通过结论。

## 13. M7 Git Quality Supporting Flow

目标：保留用户明确要求的 push/diff 后补单测和回归能力，但作为 V1 支线推进。

任务：

- GitChangeSet。
- GitChangedFile。
- GitRiskAnalysis。
- UnitTestPatch。
- RegressionPlan。
- GitTool。
- GitDiffAgent。
- UnitTestAgent。
- RegressionAgent。
- PatchScopeGate。
- Git Quality Center 页面。

验收：

- 使用 `docs/fixtures/03-golden-git-quality.md`。
- 用户可选择本地仓库和 base/head 或上传 diff。
- 系统展示 changed files。
- AI 生成风险摘要。
- AI 生成 UnitTestPatch。
- PatchScopeGate 阻止业务源码修改。
- 用户批准后才应用 patch。
- pytest 新增测试和回归可执行。
- 生成 GitQualityReport。

## 14. M8 Extension Surface And Hardening

目标：让 V1 可长期使用和扩展。

任务：

- Knowledge/RAG Adapter 空实现。
- MCP Server 配置占位。
- Tool Adapter schema 对齐 MCP tool schema。
- Prompt/Skill 版本效果指标。
- Docker 环境分层：dev/test/local-prod。
- artifact 清理策略。
- 日志脱敏。
- 备份/恢复说明。

验收：

- 未配置 RAG/MCP 时主流程可运行。
- ToolDefinition 可映射到未来 MCP。
- 文档说明如何接外部 RAG。
- Docker 环境可重复启动。

## 15. 每个 Slice 的 Definition Of Done

每个 Slice 完成前必须满足：

- 有数据模型或明确不需要数据模型。
- 有 API 契约或明确只做内部能力。
- 有状态机或复用现有状态机。
- 有 mock 数据或 fixture。
- 有最小测试或 smoke 验证。
- UI 能访问或 API 能调用。
- 错误状态可见。
- artifact 和日志可追踪。
- memory 的 `07-dev-log.md` 和 `08-session-handoff.md` 已更新。

## 16. 推荐第一批实现任务

第一批不应该先做复杂 AI 生成，而是先搭平台骨架：

1. 初始化目录结构。
2. 写 Docker Compose。
3. 启动 PostgreSQL + Redis。
4. 建 FastAPI `/health`、`/ready`。
5. 建 Alembic。
6. 建 Vue + Arco 基础布局。
7. 建 Project、Module、Repository、Environment、TestCommand。
8. 建 Worker 空任务。
9. 建 mock LLM provider。
10. 建 Prompt/Skill Registry。

完成后再进入需求评审和用例生成。

## 17. 风险与应对

| 风险 | 应对 |
|---|---|
| 功能范围过大 | 严格按 V1/V1.1/V2 边界执行 |
| AI 输出不可控 | JSON schema + 评审窗口 + 指标反馈 |
| 工具调用危险 | Tool allowlist + 审批 + artifact + 禁止任意 shell |
| RAG 拖慢进度 | V1 只做空 Adapter |
| UI 变成企业后台 | 页面围绕三条最小闭环设计 |
| 测试工具环境复杂 | TestRunner/pytest 优先，Playwright 最小闭环，其余后置 |
| 后续 AI 读不懂上下文 | 每次更新 memory，保持 docs/README 和 memory/README 最新 |

## 18. 后续 AI 开发开工协议

每次新的 AI 会话必须：

1. 进入 `/Users/yanchen/VscodeProject/Chtest`。
2. 读取 `memory/README.md`。
3. 读取 `memory/13-ai-readable-project-brief.md`。
4. 查看 `docs/product/01-positioning-and-scope.md`。
5. 查看 `docs/contracts/*`。
6. 查看本次任务相关 `docs/fixtures/*`。
7. 查看 `docs/implementation/01-v1-development-process.md`。
8. 查看 `memory/11-implementation-slices.md`。
9. 查看 `git status --short`。
10. 选择一个最小 Slice。
11. 实现、验证、更新 memory。
