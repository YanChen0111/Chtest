# Chtest Roadmap

## 1. 总体路线

V1 先证明一条 AI 测试证据闭环，再扩展三条最小闭环路线：需求到用例、用例到自动化、Git 到质量报告。每个阶段必须可运行、可验证、可回滚。

`docs/fixtures/00-v1-demo-path.md` 是 release spine。任何宽功能都不能替代这个最小证据闭环。

```text
Foundation
  -> AI Runtime Core
  -> V1 Minimum Demo Evidence Loop
  -> Requirement To Case
  -> AutomationDraft + Pytest
  -> Playwright Minimal Loop
  -> Reports / Failure Analysis
  -> Git Quality Supporting Flow
  -> MCP/RAG Extension Surface
```

## 2. Phase 1: Foundation

目标：启动真实开发环境，建立后端、前端、worker 和基础设施。

交付：

- Docker Compose。
- PostgreSQL / Redis。
- FastAPI app。
- Alembic。
- 单用户上下文。
- 按 Slice 2.5 Frontend Foundation 建 Vue 3 + Vite + Arco 前端基础工程。
- Project / Module / Repository / Environment / TestCommand CRUD。

验收：

- `docker compose up` 启动服务。
- `/health`、`/ready` 通过。
- 可以创建项目、模块、仓库和测试命令。

## 3. Phase 2: AI Runtime Core

交付：

- AITask。
- Artifact。
- LLMCallLog。
- PromptVersion。
- SkillVersion。
- Redis worker。
- Mock LLM Provider。
- AI Workbench 基础页面。
- ContextArtifact metadata。
- Mock-provider eval bench。

验收：

- UI/API 创建 AI task。
- Worker 消费并写回状态。
- Prompt/Skill/model/token/artifact 可追踪。
- schema 校验失败能保存 raw output。
- AI task 能记录使用的 context artifact ids 或空列表。
- mock-provider eval bench 输出 schema_valid_rate、evidence_complete_rate、unsafe_output_rate。

## 4. Phase 3: Requirement Review

交付：

- Requirement。
- RequirementReview。
- RiskItem。
- 六维评分 prompt/skill。
- 风险矩阵页面。

验收：

- 使用 `docs/fixtures/01-golden-requirement-to-case.md` 输入需求后生成评分、问题、风险矩阵。
- 结果可编辑保存。

## 5. Phase 4: Case Generation Review

交付：

- CaseGenerationTask。
- GeneratedCaseCandidate。
- 用例评审窗口。
- TestCase。
- 质量指标。

验收：

- AI 生成候选用例。
- 人工接受/编辑/驳回/要求优化。
- 通过用例进入正式库。
- 展示采纳率、驳回率、修改率。

## 6. Phase 5: AutomationDraft And Pytest Execution

目标：打通用例到自动化主线 P0。

交付：

- AutomationDraft。
- AutomationDraftAgent mock 输出。
- AutomationDraft 评审页面。
- ToolDefinition。
- ToolInvocation。
- TestRun/TestResult。
- TestRunnerTool。
- pytest allowlist 执行。
- docker runner mode 优先产品验收，local subprocess 作为开发 fallback。
- runner sandbox metadata。
- runtime_manifest、dependency_snapshot、environment_snapshot。
- stdout/stderr/JUnit artifact。

验收：

- 使用 `docs/fixtures/02-golden-case-to-playwright.md` 的 pytest 示例生成草稿。
- 未审批 AutomationDraft 不能执行。
- 审批后 pytest 可执行并结构化保存结果。
- TestRun 记录实际执行的 AutomationDraft runtime artifact、`runtime_manifest.json`、`dependency_snapshot.json`、`environment_snapshot.json` 和 runner sandbox metadata。
- V1 Minimum Demo 能从需求走到报告，并展示证据链。

## 7. Phase 6: Playwright Minimal Loop

目标：Web 自动化最小闭环，不做完整低代码 UI 平台。

交付：

- PlaywrightTool。
- Playwright AutomationDraft。
- trace/screenshot artifact。
- Playwright 失败进入失败归因。

验收：

- 能执行审批后的 Playwright 草稿或已有测试。
- artifact 保存。
- 失败可归因。

## 8. Phase 7: Reports And Failure Analysis

交付：

- FailureAnalysis。
- AutomationRepairTask。
- Report。
- Evidence manifest。
- Report Center。
- Case quality report。
- Automation execution report。

验收：

- 失败有证据链。
- 失败的 AutomationDraft 可创建 review-gated repair task。
- 报告输出 md/html/json。
- 未归因失败不能给出通过结论。

## 9. Phase 8: Git Quality Supporting Flow

目标：覆盖本地 diff 后单测生成和 pytest 回归，但作为 V1 支线能力。

交付：

- GitChangeSet。
- GitChangedFile。
- GitRiskAnalysis。
- UnitTestPatch。
- RegressionPlan。
- diff 导入和 base/head 分析。
- patch 评审。
- pytest 新增测试和回归。

验收：

- 使用 `docs/fixtures/03-golden-git-quality.md`。
- 读取 diff。
- 生成风险摘要。
- 生成 UnitTestPatch。
- PatchScopeGate 阻止业务源码修改。
- 审批后执行 pytest 回归。
- 生成 GitQualityReport。

## 10. Phase 9: Extension Surface

交付：

- Knowledge/RAG Adapter empty provider。
- McpServerConfig placeholder。
- MCP-ready ToolDefinition schema。
- Newman/JMeter 后续接入预留。

验收：

- 未配置 RAG/MCP 主流程仍可运行。
- 后续可接外部 RAG、GitHub MCP、Newman、JMeter。

## 后续扩展

- GitHub webhook。
- GitHub MCP 接入。
- Chtest 自建 MCP Server。
- Skill ZIP/Git 导入。
- Newman collection 执行和报告解析。
- JMeter non-GUI 执行和 JTL 报告解析。
- 完整 Playwright 低代码编排。
- Appium Android/iOS。
- Fiddler/HAR 抓包分析。
- 外部 RAG 服务接入。
- 多模型路由。
- 过往失败学习。
- 小团队轻权限和多项目质量趋势。
