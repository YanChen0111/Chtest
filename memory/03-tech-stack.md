# Chtest Tech Stack

## 1. 第一版固定选型

V1 技术栈冻结，除非进入 ADR 流程，不再讨论更换主技术栈。

| 层 | 技术 | 原因 |
|---|---|---|
| Backend | FastAPI + Pydantic v2 | 适合 AI/工具型平台，类型清晰，开发效率高 |
| ORM / Migration | SQLAlchemy 2 + Alembic | PostgreSQL 生态成熟，迁移可控 |
| Database | PostgreSQL | 第一版真实落地，不走 SQLite 过渡 |
| Queue / Cache | Redis | 任务队列、任务锁、进度缓存、流式状态 |
| Worker | RQ 默认 | 单用户第一版 RQ 更轻，Redis 原生足够 |
| Frontend | Vue 3 + TypeScript + Vite | AI 可维护性好，适合工作台 |
| UI | Arco Design Vue | 适合后台工作台，表格/抽屉/表单能力完整 |
| LLM | Mock Provider + OpenAI-compatible adapter | 先 mock 跑通闭环，再接云模型/企业网关/本地模型 |
| Tool Execution | Local runner + optional Docker runner | 先保证能跑真实项目测试，后续隔离增强 |
| V1 Runner | pytest / subprocess allowlist | V1 P0 执行闭环 |
| V1 Web UI Test | Playwright | V1 P1 最小 Web 自动化闭环，支持截图和 trace |
| API Test | Newman V1.1 | 后置，不进入 V1 主路径 |
| Performance Test | JMeter V1.1/V2 | 后置，不进入 V1 主路径 |
| Mobile Test | Appium V3 | 后续接 Android/iOS，第一版不做 |
| Traffic Analysis | HAR/Fiddler V3 | 后续导入抓包结果分析，不第一版深度控制 Fiddler |
| Reports | Markdown + HTML + JSON | 便于平台展示、归档、PR 评论和 AI 二次分析 |
| Deploy | Docker Compose | 第一版需要 Postgres/Redis 一键启动 |

## 2. 为什么不用 SQLite 起步

用户已明确第一版直接使用 PostgreSQL + Redis。原因：

- 任务、artifact、评审状态、质量指标需要可靠事务。
- 用例候选、正式用例、AutomationDraft、执行结果之间需要清晰关系模型。
- Redis 队列是 AI 长任务、测试执行和进度推送的真实基础设施。
- 早期使用 SQLite 会让状态机、并发任务、迁移脚本、部署文档后续返工。

## 3. 单用户模式的实现方式

- 不做登录注册。
- 后端启动时创建默认用户 `default-user`。
- 所有数据写入默认 `workspace_id` 和 `user_id`。
- API 层保留 user/workspace 上下文字段，但通过依赖注入固定返回默认上下文。
- 后续扩展多用户时，替换上下文提供器即可。

## 4. LLM 接入要求

必须抽象为 Provider Adapter：

```text
LLMRequest
  provider
  model
  messages
  response_format
  temperature
  max_tokens
  tools
  metadata

LLMResponse
  content
  parsed_json
  tool_calls
  usage
  latency_ms
  raw_response_ref
```

必须记录 provider、model、PromptVersion、SkillVersion、agent_name、token、latency、cost estimate、success/failure、task_id、artifact_id。

## 5. Prompt/Skill 管理

Prompt 必须版本化，不能散落在业务代码里。Skill 是测试方法和操作规范，Prompt 是具体输出约束。

V1 Prompt：

```text
prompts/
  requirement_review/v1.md
  case_generation/v1.md
  automation_draft_generation/v1.md
  cicd_change_analysis/v1.md
  unit_test_generation/v1.md
  regression_selection/v1.md
  failure_analysis/v1.md
  report_generation/v1.md
```

V1 Skill：

```text
skills/
  requirement-review-skill/v1.md
  test-case-generation-skill/v1.md
  automation-draft-skill/v1.md
  unit-test-generation-skill/v1.md
  regression-selection-skill/v1.md
  tool-execution-skill/v1.md
  failure-analysis-skill/v1.md
  report-generation-skill/v1.md
```

具体格式遵循 `docs/contracts/05-prompt-skill-contract.md`。

## 6. MCP 与 Tool Adapter

第一版先做 Internal Tool Adapter，不直接依赖 MCP 成熟度。接口设计必须 MCP-ready。

```text
ToolDefinition
  name
  description
  input_schema
  output_schema
  risk_level
  approval_required
  timeout_seconds
  artifact_policy

ToolInvocation
  tool_name
  input
  output
  status
  approved_by
  started_at
  finished_at
  artifacts
```

后续 MCP 接入方向：GitHub MCP、Chtest MCP、第三方 MCP。

## 7. 数据存储边界

PostgreSQL 存：项目、仓库、环境、测试命令、需求、需求评审、风险矩阵、候选用例、正式用例、AutomationDraft、Git 变更、UnitTestPatch、工具定义、AI 任务、Prompt/Skill、执行记录、失败归因、报告索引。

Redis 存：AI 任务队列、测试执行队列、工具调用队列、任务进度缓存、临时锁、SSE/WebSocket 进度事件缓存。

文件/Artifact 存：原始需求文档、AI raw output、diff、patch、AutomationDraft 代码、执行日志、JUnit/coverage/trace/截图、HTML/Markdown/JSON 报告。

## 8. 后续可替换点

| 当前 | 后续可替换 |
|---|---|
| RQ | Celery / Dramatiq / Temporal |
| Local Artifact Store | MinIO / S3 |
| Local Runner | Docker/Kubernetes Runner |
| OpenAI-compatible adapter | 多 Provider 路由、私有模型网关 |
| Internal Tool Adapter | MCP Server / MCP Client 双向接入 |
| Rule-based code analysis | tree-sitter / codegraph / language server |
| Rule-based regression selection | coverage + call graph + historical failure model |
| Empty Knowledge Adapter | 外部 RAG / 企业知识库 / 缺陷库 |
