# Open Source Reference Migration Map

## 1. 原则

Chtest 参考 WHartTest 和 MeterSphere，但不做源码级整体迁移。采用“能力复刻 + 数据模型重建 + UI 思路参考 + 工具接口重写”的方式。

- 不直接复制大段源码。
- 不引入不必要技术栈。
- 不迁移企业权限和团队协作复杂度。
- 优先迁移能提升个人测试效率的能力。

## 2. WHartTest 可迁移能力

| 来源 | 文件/模块 | 能力 | Chtest 处理 |
|---|---|---|---|
| WHartTest_MCP | `WHartTest_tools.py` | FastMCP 工具、项目/模块/用例查询、保存用例、编辑用例、截图保存 | V1 先实现 Tool Adapter；V2 映射为 Chtest MCP |
| WHartTest_MCP | `ms_mcp_api.py` | 对 MeterSphere 风格平台的 MCP 封装 | 参考工具描述和参数 schema |
| WHartTest_Skills | `api-automation-skill` | 接口模块、环境、变量、接口调试、用例、报告、套件执行 | V1 参考 Skill 结构；Newman/JMeter 适配器在执行与报告契约稳定后接入 |
| WHartTest_Skills | `playwright-cli` | 浏览器操作、snapshot、trace、locator、network | V1 参考为 Playwright Skill 和 Tool |
| WHartTest_Skills | `playwright-skill` | Playwright 脚本执行和 helper | V1 参考执行器设计，不直接迁移实现 |
| WHartTest_Skills | `ui-automation-skill` | UI 自动化操作规范 | V2 低代码 UI 自动化时参考 |
| WHartTest_Actuator | `executor.py`、`websocket_client.py` | 独立执行器、WebSocket 接任务、Playwright 执行、结果回传 | V1 worker 本地执行；V2 远程执行器参考该模型 |
| WHartTest_Django | `testcases/models.py` | review_status、优先级、类型、截图 | V1 复刻状态机和字段思想 |
| WHartTest_Vue | `GenerateCasesModal.vue` | 生成用例弹窗：需求、模块、prompt、知识库、测试类型 | V1 复刻交互结构 |
| WHartTest_Vue | `OptimizationSuggestionModal.vue` | 优化建议和二次评审 | V1 复刻要求优化流程 |

## 3. WHartTest 不迁移能力

- 微信插件。
- Django monorepo 结构。
- 内置 knowledge/RAG。
- 默认 API key 和部署方式。
- 完整远程桌面执行器打包逻辑。

## 4. MeterSphere 可迁移能力

| 来源 | 文件/模块 | 能力 | Chtest 处理 |
|---|---|---|---|
| caseReview | `frontend/src/views/case-management/caseReview` | 用例评审列表、创建、详情、用例详情、评审提交 | V1 复刻页面信息架构 |
| caseReview | `passRateLine.vue` | 通过/不通过/重新评审/评审中/未评审进度条 | V1 复刻质量条和指标 |
| caseReview backend | `CaseReviewController.java`、`CaseReviewFunctionalCaseController.java` | 评审、批量评审、评审详情 | V1 用 FastAPI 重写对应 API |
| api-test routes | `router/routes/modules/apiTest.ts` | debug、management、scenario、report 路由结构 | V2 API 测试中心页面参考 |
| api-test frontend | `debug`、`management`、`scenario`、`report` | 接口调试、接口管理、场景、报告 | V1 参考页面信息架构；Newman 执行在 V1.1 接入，API 管理增强放 V2 |
| api-test backend | `apiCaseAiTemplate.vm` | 接口测试用例生成模板 | V1 参考 Prompt 输出约束 |
| test-plan | `testPlan`、`report` | 测试计划、执行状态、报告、进度条 | V1 个人测试套件和执行报告参考 |
| report components | `reportDrawer`、`reportList`、`execStatus` | 报告列表、详情抽屉、状态展示 | V1 报告中心参考 |

## 5. MeterSphere 不迁移能力

- Spring Boot 微服务架构。
- Kafka、MinIO、复杂插件体系。
- 企业组织、权限、团队协作。
- 完整 Mock 服务。
- 全量接口测试平台。

## 6. 第一版复刻优先级

| 优先级 | 能力 | 来源 |
|---|---|---|
| P0 | 用例生成弹窗 | WHartTest |
| P0 | review_status 状态机 | WHartTest |
| P0 | 用例评审详情和通过率 | MeterSphere |
| P0 | Prompt/Skill 目录化 | WHartTest |
| P0 | Tool/MCP 思路 | WHartTest MCP |
| P1 | Playwright 执行 artifact | WHartTest Actuator / Skills |
| P1 | API 测试报告结构 | MeterSphere api-test report |
| P1 | 测试套件/计划状态 | MeterSphere test-plan |
| P2 | 远程执行器 | WHartTest Actuator |
| P2 | API 场景编排 | MeterSphere api-test scenario |
| P3 | 完整低代码 UI 自动化 | WHartTest UI automation |
| P3 | 完整 Mock / 企业集成 | MeterSphere |

## 7. 迁移实现方式

```text
参考源码观察
  -> 提炼能力和数据字段
  -> 写 Chtest 自有 schema
  -> 写 FastAPI service/router
  -> 写 Vue 页面
  -> 写 worker/tool adapter
  -> 写测试和验收
```

不要用复制粘贴替代设计。Chtest 的实现必须符合单用户、轻量、可维护的路线。

## 8. Final-Version Tool And Knowledge Reference Map

This section records the open-source projects future AI coding sessions may use
to improve implementation speed. The rule is migration by adapter and evidence
contract, not large source-code copy.

### 8.1 Testing Tool References

| Capability | Primary GitHub reference | What Chtest should migrate | Chtest boundary |
|---|---|---|---|
| Python/unit regression execution | `https://github.com/pytest-dev/pytest` | Test discovery behavior, JUnit output expectations, fixture-friendly command patterns | Keep execution behind TestCommand, ToolDefinition, ToolInvocation, and Artifact records |
| Web automation | `https://github.com/microsoft/playwright` | Trace, screenshot, browser test execution, codegen/MCP ideas for future UI automation | Do not build a full low-code platform until Playwright evidence loop is stable |
| API collection execution | `https://github.com/postmanlabs/newman` | Postman collection CLI execution, JSON/JUnit report parsing, request/assertion summaries | Do not reimplement Postman management; use Newman as a runner adapter |
| Performance evidence | `https://github.com/apache/jmeter` | Non-GUI `jmeter -n -t ... -l ...`, JTL CSV/XML parsing, sampler metrics | Do not build full JMeter GUI/platform parity |
| Traffic capture / Fiddler-like capability | `https://github.com/mitmproxy/mitmproxy` | HAR/flow import, HTTP evidence analysis, optional future proxy-controlled capture | Treat proxy execution as high-risk; start with imported traffic evidence |
| Test report presentation | `https://github.com/allure-framework/allure2` | Multi-framework report organization, labels, suites, attachments, trend ideas | Chtest Report and Artifact contracts remain source of truth |
| CI local replay reference | `https://github.com/nektos/act` | GitHub Actions local-run concepts and environment reproduction ideas | Optional future adapter only; Chtest remains test-quality pipeline, not CI clone |
| Programmable automation reference | `https://github.com/dagger/dagger` | Reproducible local/CI automation graph concepts | Reference only unless a later slice explicitly adds an adapter |
| CI/CD platform evidence reference | `https://github.com/harness/harness`, Jenkins, GitLab, GitHub Actions runner | Run/job/step/artifact/log/status concepts | Import evidence or model ideas; do not implement general build/deploy/release orchestration |

### 8.2 Knowledge And RAG References

| Capability | Primary GitHub reference | What Chtest should migrate | Chtest boundary |
|---|---|---|---|
| Knowledge adapter framework | `https://github.com/deepset-ai/haystack` | Retriever pipeline/provider adapter ideas | Normalize output into KnowledgeEvidence; provider optional |
| Knowledge adapter framework | `https://github.com/run-llama/llama_index` | Index/retriever abstractions and document connector ideas | Do not expose LlamaIndex schema directly in Chtest APIs |
| Relationship graph reasoning | `https://github.com/microsoft/graphrag` | Offline graph extraction and relationship reasoning patterns | Use only after deterministic Test Relationship Graph and eval gates exist |
| External RAG service reference | `https://github.com/infiniflow/ragflow` | External provider/service evaluation ideas | RAGFlow must not replace Chtest knowledge page, review flow, or evidence model |
| Vector database | `https://github.com/qdrant/qdrant` | Scalable vector storage if pgvector is insufficient | Only after full-text/pgvector eval proves need |
| Compact vector option | PostgreSQL `pgvector` extension | Lowest-service-count semantic retrieval | Optional L2 provider, not a default requirement |
| Document parsing | `https://github.com/microsoft/markitdown`, `https://github.com/Unstructured-IO/unstructured` | Convert PDF/Word/HTML/Markdown into safe source artifacts | Parsed output must become ContextArtifact/TestKnowledgeCard evidence |

### 8.3 MCP References

| Capability | Primary GitHub reference | What Chtest should migrate | Chtest boundary |
|---|---|---|---|
| MCP server/client SDK | `https://github.com/modelcontextprotocol/python-sdk` | MCP server/client implementation pattern for future Chtest MCP | Must route through ToolDefinition, ToolInvocation, approval, and Artifact evidence |
| GitHub MCP ideas | GitHub MCP server implementations and docs | PR, commit, Actions, Issue, comment read/import workflows | Start read-only; no merge, push, deploy, or PR comment automation until explicitly promoted |

### 8.4 AI Coding Use Pattern

When a future AI session uses an open-source project, it should write or update
the slice plan with:

```text
Reference repository:
License:
Version/commit:
Documentation entry:
Capability to migrate:
Reuse mode:
Chtest-owned input contract:
Chtest-owned output contract:
Fallback behavior:
Focused verification:
```

Preferred reuse order:

1. Reference design and behavior.
2. Use a stable library API behind Chtest adapters.
3. Run an external provider/service behind `KnowledgeAdapter` or `ToolAdapter`.
4. Vendor only a small isolated helper after license review.

Do not:

- paste large application modules into Chtest;
- let provider schemas replace Chtest contracts;
- add a runtime dependency without a fallback path;
- add vector, graph, MCP, or remote CI behavior without a slice that explicitly
  promotes it.

## 9. Project Core 后端迁移记录

本次后端迁移参考了 WHartTest 的项目、模块、环境和执行器模型，但只迁移能支撑 Chtest V1 本地优先 CI/CD 质量证据与门禁中心的最小项目上下文。

| Chtest 目标 | 参考代码 | 吸收点 | V1 处理 |
|---|---|---|---|
| Project 聚合根 | `参考框架/WHartTest/WHartTest_Django/projects/models.py` | 项目作为后续模块、环境、测试资产的归属根 | 重建为 SQLAlchemy `Project`，名称在 workspace 内唯一，不迁移全局唯一和团队成员模型 |
| Module 树 | `参考框架/WHartTest/WHartTest_Django/api_modules/models.py`、`testcases/models.py` | 自关联父子模块、按项目归属 | 重建为 `Module`，增加契约要求的 `level/path/sort_order`，限制 1 到 5 级 |
| Environment 配置 | `参考框架/WHartTest/WHartTest_Django/api_environments/models.py` | 环境按项目隔离、变量配置、同项目唯一 | V1 使用 `variables_json` 保存本地执行变量；父级继承、数据库配置、全局 header 延后 |
| TestCommand/执行入口 | `参考框架/WHartTest/WHartTest_Actuator/models.py`、`executor.py` | 执行输入/输出用结构化模型表达，便于本地 worker 和报告解析 | V1 先落 `TestCommand`，记录命令、工作目录、JUnit/coverage 解析开关；真正执行与结果模型放后续 Slice |

本次没有迁移以下内容：

- `ProjectCredential` 明文凭据和登录角色。
- `ProjectMember`、RBAC、团队协作权限。
- WHartTest 环境继承、数据库连接配置、全局请求头。
- 远程 WebSocket 执行器和完整用例/任务编排。

这些能力会在后续版本按契约拆分实现；V1 当前目标是先让项目、模块、仓库、环境、测试命令具备稳定持久化能力，提高后续 API、执行器、报告和质量门禁开发效率。
