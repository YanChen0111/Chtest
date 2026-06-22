# Implementation Slices

> 本文件用于后续把开发任务直接交给 AI。每个 Slice 都要足够小、可验收、可回滚。

## Definition Of Done

每个 Slice 完成前必须具备：

- 数据模型或明确不需要数据模型。
- API 契约或明确只做内部能力。
- 状态机或复用现有状态机。
- mock 数据或 fixture。
- 最小测试或 smoke 验证。
- UI 或 API 验证入口。
- artifact/log。
- 失败状态。
- 更新 `memory/07-dev-log.md` 和 `memory/08-session-handoff.md`。

## Slice 1: Repository and Deploy Skeleton

目标：建立真实平台运行骨架。

交付：`backend/`、`frontend/`、`worker/`、`deploy/`、`prompts/`、`skills/`、`mcp_tools/`、`artifacts/` 目录；`deploy/docker-compose.yml`；`.env.example`。

验收：PostgreSQL、Redis 可启动；backend health check 可访问；worker 能连接 Redis。

## Slice 2: Backend Core

目标：FastAPI + PostgreSQL + Redis 基础能力。

交付：FastAPI app、Settings、SQLAlchemy 2 session、Alembic、`/health`、`/ready`、默认单用户上下文。

验收：后端启动成功；`/ready` 能检查 PostgreSQL 和 Redis；Alembic 能创建首批基础表。

## Slice 2.5: Frontend Foundation

目标：在进入 Slice 3 前建立 Vue 3 + TypeScript + Vite + Arco 前端基础工程。

交付：`frontend/package.json`、Vite 配置、Vue app、Arco Design Vue、router、store、API client、WorkbenchLayout、AI Workbench 空壳、frontend Docker dev command。

验收：`npm --prefix frontend run build` 通过；`npm --prefix frontend run test -- --run` 通过；`docker compose -f deploy/docker-compose.yml config` 通过。

## Slice 3: Project Core

目标：平台能管理项目上下文。

交付：Workspace、User、Project、Module、Repository、Environment、TestCommand models；CRUD API；Project Settings 页面。前端任务必须依赖 Slice 2.5，不允许临时手写一套 ad hoc frontend 结构。

验收：UI/API 可以创建项目、模块、仓库、环境、测试命令；数据写入 PostgreSQL。

## Slice 4: AI Runtime Core

目标：所有 AI/执行任务可追踪。

交付：AITask、Artifact、LLMCallLog、Redis queue、Worker 消费示例任务、任务列表和详情页。

验收：UI/API 创建任务；Worker 推进 created -> pending -> running -> succeeded/failed；artifact 可查看。

## Slice 5: Prompt And Skill Registry

目标：统一管理 PromptVersion 和 SkillVersion。

交付：PromptVersion、SkillVersion models；文件加载；hash；JSON schema 输出校验；调用日志。

验收：mock LLM 调用保存 prompt/skill 版本、输入输出、token、耗时；schema 失败保存 raw artifact。

## Slice 6: Requirement Review

目标：跑通需求质量评审。

交付：Requirement、RequirementReview、RiskItem；需求录入页面；六维评分 prompt/skill；风险矩阵生成任务。

验收：使用 `docs/fixtures/01-golden-requirement-to-case.md` 输入需求，生成六维评分、问题列表、风险矩阵。

## Slice 7: Case Generation Candidate

目标：生成候选用例但不直接入库。

交付：CaseGenerationTask、GeneratedCaseCandidate、用例生成 prompt/skill、字段完整性校验、重复检查初版。

验收：基于 fixture 生成候选用例；候选状态为 generated 或 under_review；正式用例库不会被直接写入。

## Slice 8: Case Generation Review Window

目标：完成候选用例评审闭环。

交付：生成批次列表、评审详情页、候选用例表格、详情/编辑抽屉、接受、编辑后接受、驳回、要求优化。

验收：用户可以完成一批候选用例评审；通过评审的用例进入 TestCase；记录评审记录。

## Slice 9: Case Metrics Dashboard

目标：让 AI 用例质量可度量。

交付：CaseQualityMetric、批次质量统计、通过率/评审进度条、prompt/model/skill 维度聚合。

验收：展示 generated_count、approved_count、rejected_count、acceptance_rate、edit_rate、review_progress。

## Slice 10: Test Case Library And Suites

目标：沉淀可复用测试资产。

交付：TestCase、TestCaseStep 可用 JSON steps 初版、TestSuite、模块树、用例/套件页面。

验收：通过评审的用例可进入正式库；可创建测试套件并关联用例。

## Slice 11: AutomationDraft Foundation

目标：补齐用例到自动化中间层。

交付：AutomationDraft model、AutomationDraft API、AutomationDraftAgent mock 输出、评审状态机、草稿详情页。

验收：基于 TestCase 生成 pytest 或 Playwright 草稿；未审批不能执行。

## Slice 12: TestRunner Pytest Execution

目标：V1 P0 执行闭环。

交付：ToolDefinition、ToolInvocation、TestRun、TestResult 初版、TestRunnerTool、pytest allowlist 执行、AutomationDraft runtime artifact 追踪、runner sandbox metadata、runtime_manifest、dependency_snapshot、environment_snapshot、stdout/stderr/JUnit artifact。

验收：审批后的 AutomationDraft 可触发 pytest TestRun；TestRun 记录实际执行的 `runtime_artifact_ids`、runtime manifest、dependency snapshot、environment snapshot 和 runner sandbox metadata；执行结果结构化入库。

## Slice 13: Playwright Minimal Loop

目标：Web 自动化最小闭环。

交付：PlaywrightTool 初版、执行已有测试或草稿、trace/screenshot artifact、失败归因输入。

验收：使用 `docs/fixtures/02-golden-case-to-playwright.md` 可生成草稿、审批、执行、保存 artifact。

## Slice 14: Failure Analysis And Report

目标：生成有证据的质量报告。

交付：FailureAnalysis、Report、evidence_manifest、Report Center、AutomationDraft repair task 入口。

验收：失败有证据链；失败的 AutomationDraft 可创建 review-gated repair task；报告输出 md/html/json；无证据时不能给出 passed 结论。

## Slice 15: Git Quality Foundation

目标：支线能力：本地 diff 有质量视图。

交付：GitChangeSet、GitChangedFile、diff 导入 API、本地 git diff 解析、Git 质量任务列表和详情页。

验收：使用 `docs/fixtures/03-golden-git-quality.md` 的 diff 可看到变更文件、类型和风险摘要。

## Slice 16: UnitTestPatch And Regression

目标：根据 diff 生成单测 patch 并跑 pytest 回归。

交付：UnitTestPatch、UnitTestAgent、PatchScopeGate、Patch 评审页面、RegressionPlan、pytest 回归执行。

验收：AI 生成 patch；patch 默认只包含测试目录变更；用户审批后应用；新增测试和回归结果进入 Git Quality Center。

## Slice 17: Extension Surface

目标：预留后续 RAG/MCP 扩展接口。

交付：KnowledgeAdapter 空实现、McpServerConfig placeholder、ToolDefinition schema MCP-ready、文档更新。

验收：未配置 RAG/MCP 时主流程仍可运行；后续可接外部 RAG 和 GitHub MCP。
