# Session Handoff

## 当前用户最新明确要求

- Chtest 项目必须放在 `/Users/yanchen/VscodeProject/Chtest`。
- 第一版就做单用户模式。
- 第一版直接使用 PostgreSQL + Redis。
- 不要一次性演示，要真实能大幅提高测试效率的 AI 工具。
- 最新定位已校准为：面向个人测试工程师、自动化测试工程师的 AI 测试设计与自动化落地工作台。
- 长期方向是小团队 AI 测试工作台 + Agent / Skill / MCP 测试工具生态。
- V1 三条最小闭环：需求到用例、用例到自动化、Git 到质量报告。
- Git Quality Center 是 V1 支线能力，不能压过需求到自动化主线。
- RAG 功能只保留接口，后续外部搭建后接入。
- MCP / Skill / Prompt / Agent 要分层设计并贯穿各流程。
- 新代码 push/PR/diff 后生成单测、执行回归，并有独立页面查看 Git 情况。
- 增加 Web 自动化能力，但 V1 只做 Playwright 最小闭环；Newman/JMeter 后置。
- 文档必须足够详细，方便后续 AI 读取后继续完成项目。
- 长期 AI 开发必须遵循 `docs/implementation/04-ai-vibecoding-governance.md`：小步 Task、每步验证、每个完成 Task 提交、可回滚；Slice 完成和重大上下文变化时更新 memory。
- 用户已确认 preflight 文档修复方案：
  - AutomationDraft 审批后采用 Chtest artifact runtime 临时执行目录，不直接写业务仓库。
  - `LLMCallLog` 使用独立表。
  - 补充前端 UI 指南，避免 V1 做成泛企业后台。

## 当前本地状态

- 本地目录：`/Users/yanchen/VscodeProject/Chtest`
- memory 目录：`/Users/yanchen/VscodeProject/Chtest/memory`
- WHartTest：`/Users/yanchen/VscodeProject/Chtest/参考框架/WHartTest`，参考提交 `927bff2`
- MeterSphere：`/Users/yanchen/VscodeProject/Chtest/参考框架/metersphere`，参考提交 `5dc6df5`
- 参考框架目录应保留本地，但默认不纳入 Chtest Git 提交记录。
- Chtest 已初始化为独立 Git 仓库，当前分支 `main`。
- Git remote `origin` 已设置为 `https://github.com/2696437448-cmyk/Chtest.git`。
- baseline commit 已存在：`3be8e82 docs(product): define chtest v1 planning baseline`。
- 当前 preflight 文档修复在隔离分支 `docs/preflight-vibecoding-fixes`，worktree 路径为 `/private/tmp/chtest-preflight-docs`。
- 当前未 push。

## 当前 Preflight 修复内容

本轮修复 vibe coding 开工前的契约断点：

- `docs/contracts/01-data-model-contract.md`
  - 补齐 `LLMCallLog`、`CaseQualityMetric`、`GitRiskAnalysis`、`RegressionPlan`、`KnowledgeProviderConfig`、`KnowledgeEvidence`、`McpServerConfig`。
  - 将 `FailureAnalysis.confidence` 固定为 `0.00-1.00`。
  - 明确 AutomationDraft `execution_strategy=artifact_runtime_copy` 和 `runtime_artifact_id`。
  - 强化 ToolDefinition/ToolInvocation 的 allowlist、安全路径、输出限制字段。
- `docs/architecture/03-implementation-technology.md`
  - 明确 Tool Adapter 非 shell、allowlist、canonicalize、timeout、stdout/stderr limit、redaction 规则。
  - 明确 AutomationDraft 审批后复制到 Chtest artifact runtime 目录执行。
- `docs/contracts/02-api-contract.md`
  - 明确 approve AutomationDraft 不写业务仓库，创建 TestRun 时生成 runtime artifact。
- `docs/contracts/04-artifact-contract.md`
  - 增加 AutomationDraft `runtime/` artifact 路径。
- `docs/implementation/04-ai-vibecoding-governance.md`
  - 增加 Tool/runtime 安全门禁。
- 新增：
  - `docs/implementation/slices/slice-03-project-core.md`
  - `docs/implementation/slices/slice-04-ai-runtime-core.md`
  - `docs/implementation/slices/slice-05-prompt-skill-registry.md`
  - `docs/implementation/slices/slice-02-frontend-foundation.md`
  - `docs/product/06-frontend-ui-guidelines.md`

## 本轮完成

本轮按用户整理的优化稿执行了系统性文档优化：

新增：

- `docs/product/01-positioning-and-scope.md`
- `docs/contracts/01-data-model-contract.md`
- `docs/contracts/02-api-contract.md`
- `docs/contracts/03-state-machines.md`
- `docs/contracts/04-artifact-contract.md`
- `docs/contracts/05-prompt-skill-contract.md`
- `docs/fixtures/01-golden-requirement-to-case.md`
- `docs/fixtures/02-golden-case-to-playwright.md`
- `docs/fixtures/03-golden-git-quality.md`
- `docs/implementation/01-v1-development-process.md`
- `docs/implementation/02-v1-slice-plan.md`
- `docs/implementation/03-testing-and-acceptance.md`

更新：

- `docs/product/02-v1-product-prd.md`
- `docs/product/05-non-goals-and-version-boundaries.md`
- `docs/architecture/03-implementation-technology.md`
- `docs/implementation/01-v1-delivery-plan.md`
- `docs/README.md`
- `memory/README.md`
- `memory/00-ai-session-protocol.md`
- `memory/11-implementation-slices.md`
- `memory/13-ai-readable-project-brief.md`
- `memory/08-session-handoff.md`
- `memory/07-dev-log.md`

## 当前正式文档结构重点

- 定位：`docs/product/01-positioning-and-scope.md`
- 总 PRD：`docs/product/02-v1-product-prd.md`
- 页面 PRD：`docs/product/03-user-journey-and-page-prd.md`
- 数据模型契约：`docs/contracts/01-data-model-contract.md`
- API 契约：`docs/contracts/02-api-contract.md`
- 状态机：`docs/contracts/03-state-machines.md`
- Artifact：`docs/contracts/04-artifact-contract.md`
- Prompt/Skill：`docs/contracts/05-prompt-skill-contract.md`
- Golden Path 0：`docs/fixtures/00-v1-demo-path.md`
- Golden Path 1：`docs/fixtures/01-golden-requirement-to-case.md`
- Golden Path 2：`docs/fixtures/02-golden-case-to-playwright.md`
- Golden Path 3：`docs/fixtures/03-golden-git-quality.md`
- 开发流程：`docs/implementation/01-v1-development-process.md`
- 切片计划：`docs/implementation/02-v1-slice-plan.md`
- Slice 1 Task Plan：`docs/implementation/slices/slice-01-platform-foundation.md`
- Slice 2 Task Plan：`docs/implementation/slices/slice-02-backend-core.md`
- Slice 2.5 Task Plan：`docs/implementation/slices/slice-02-frontend-foundation.md`
- Slice 3 Task Plan：`docs/implementation/slices/slice-03-project-core.md`
- Slice 4 Task Plan：`docs/implementation/slices/slice-04-ai-runtime-core.md`
- Slice 5 Task Plan：`docs/implementation/slices/slice-05-prompt-skill-registry.md`
- 前端 UI 指南：`docs/product/06-frontend-ui-guidelines.md`
- 测试验收：`docs/implementation/03-testing-and-acceptance.md`
- AI vibecoding 治理：`docs/implementation/04-ai-vibecoding-governance.md`

## 下次 AI 会话开工步骤

1. 进入 `/Users/yanchen/VscodeProject/Chtest`。
2. 读取 `memory/README.md`。
3. 读取 `memory/13-ai-readable-project-brief.md`。
4. 读取 `docs/product/01-positioning-and-scope.md`。
5. 读取 `docs/contracts/*`。
6. 根据任务读取 `docs/fixtures/*`。
7. 查看 `docs/implementation/01-v1-development-process.md`。
8. 读取 `docs/implementation/04-ai-vibecoding-governance.md`。
9. 查看 `docs/implementation/02-v1-slice-plan.md` 或 `memory/11-implementation-slices.md`。
10. 如涉及前端，读取 `docs/product/06-frontend-ui-guidelines.md`。
11. 查看 `git status --short`。
12. 进入 Slice 1 Task 1：Initialize repository directories。
13. 每次只做一个 Slice 内的 1-3 个 Task；每个完成 Task 必须验证并 commit；Slice 完成或重大上下文变化时更新 handoff。


## Memory 更新原则

```text
Git 记录代码历史。
Memory 记录会话接续。
Contracts 记录实现真相。
```

- 每个 Task：测试 + commit。
- 每个 Slice：测试汇总 + commit 汇总 + 更新 memory。
- 每个重大变化：立即更新 memory。
- `memory/07-dev-log.md` 写长期摘要。
- `memory/08-session-handoff.md` 写下一轮 AI 如何接手。

## AI Vibecoding Task Table Template

| Task | Status | Verification Command | Commit | Notes |
|---|---|---|---|---|
| - | planned | - | - | - |

Allowed statuses: `planned`, `doing`, `blocked`, `done`, `reverted`.

## Commit Record Template

| Commit | Content | Verification |
|---|---|---|
| - | - | - |

## Verification / Risk Template

```text
Unverified items:
Risk:
Next verification command:
Latest stable commit:
Next recommended Task:
```

## 推荐下一步

开始实现 V1 平台骨架：

- 按 `docs/implementation/slices/slice-01-platform-foundation.md` 执行 Slice 1 Task 1，初始化 backend/frontend/worker/deploy/prompts/skills/mcp_tools/artifacts 目录。
- 写 `deploy/docker-compose.yml`，启动 PostgreSQL + Redis。
- 建 FastAPI 健康检查和数据库连接。
- 建 Alembic 迁移骨架。
- 做单用户上下文。
- 按 Slice 2.5 建 Vue 3 + Vite + Arco + router/store/API 前端骨架。
- 再进入 Slice 3 Project Core。

## 仍需用户确认

- 是否需要把初始化后的本地仓库做第一次 commit 并 push 到 `https://github.com/2696437448-cmyk/Chtest`。
- LLM 第一接入方式：OpenAI 官方 API、Azure OpenAI、兼容代理网关，还是 Ollama。
