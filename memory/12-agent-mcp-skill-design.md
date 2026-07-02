# AI Testing Workbench Agent / MCP / Skill / Prompt Design

## 1. 总体原则

Chtest V1 的 AI 能力按四层组织：

```text
Agent 负责流程编排
Prompt 负责输出约束
Skill 负责测试方法和操作规范
Tool Adapter / MCP 负责工具调用
Knowledge/RAG Adapter 负责未来知识上下文接入
```

第一版优先做 Internal Tool Adapter 和本地 Prompt/Skill Registry。MCP 和 RAG 都保留接口，后续可接入。

## 2. V1 三条 AI 闭环

| 闭环 | Agent 链路 | 定位 |
|---|---|---|
| 需求到用例 | RequirementReviewAgent -> RiskAgent -> CaseGenerationAgent -> CaseReviewAgent | 主线 P0 |
| 用例到自动化 | AutomationDraftAgent -> ToolExecutionAgent -> FailureAnalysisAgent -> ReportAgent | 主线 P0/P1 |
| CI/CD 质量中心到质量报告 | CICDChangeAnalysisAgent -> UnitTestAgent -> RegressionAgent -> ToolExecutionAgent -> ReportAgent | 支线 P1 |

## 3. Agent 分工

| Agent | 职责 | 第一版是否做 |
|---|---|---|
| OrchestratorAgent | 编排跨步骤任务，推进状态机 | 是 |
| RequirementReviewAgent | 六维评分、需求问题识别、需求拆分 | 是 |
| RiskAgent | 生成测试风险矩阵 | 是 |
| CaseGenerationAgent | 生成结构化用例候选 | 是 |
| CaseReviewAgent | 检查用例质量，辅助优化 | 是 |
| AutomationDraftAgent | 从需求/用例生成 pytest/Playwright 草稿 | 是 |
| CICDChangeAnalysisAgent | 分析 diff、变更风险、影响范围 | 是，支线 |
| UnitTestAgent | 生成 UnitTestPatch | 是，支线 |
| RegressionAgent | 选择 pytest 回归范围 | 是，支线 |
| ToolExecutionAgent | 调度 pytest/Playwright 执行 | 是 |
| FailureAnalysisAgent | 失败归因、证据链整理 | 是 |
| ReportAgent | 生成测试报告和质量结论 | 是 |
| KnowledgeAgent | 管理知识检索和 evidence | 否，只保留 Adapter |

## 4. V1 Skill

| Skill | 用途 | V1 范围 |
|---|---|---|
| requirement-review-skill | 需求六维评分、需求问题和测试风险识别 | P0 |
| test-case-generation-skill | 从需求生成结构化测试用例候选 | P0 |
| testcase-review-skill | 评审 AI 生成用例是否完整、可测、可执行 | P0 |
| automation-draft-skill | 从需求/用例生成 pytest/Playwright 草稿 | P0/P1 |
| unit-test-generation-skill | 根据 diff 生成 UnitTestPatch | P1 支线 |
| regression-selection-skill | 根据变更范围选择 pytest 回归 | P1 支线 |
| tool-execution-skill | 约束 pytest/Playwright 工具执行 | P0/P1 |
| failure-analysis-skill | 分析失败日志、截图、trace、JUnit | P0/P1 |
| report-generation-skill | 生成 Markdown/HTML/JSON 测试报告 | P0 |
| api-testing-skill | Newman API 测试 | V1.1 |
| jmeter-performance-skill | JMeter 性能测试 | V1.1/V2 |

## 5. V1 Prompt

```text
prompts/
  requirement_review/v1.md
  risk_matrix/v1.md
  case_generation/v1.md
  case_review/v1.md
  automation_draft_generation/v1.md
  cicd_change_analysis/v1.md
  unit_test_generation/v1.md
  regression_selection/v1.md
  tool_execution/v1.md
  failure_analysis/v1.md
  report_generation/v1.md
```

Prompt/Skill 格式以 `docs/contracts/05-prompt-skill-contract.md` 为准。

## 6. MCP 与 Tool Adapter 关系

第一版采用 Internal Tool Adapter：

```text
Agent -> Tool Adapter -> Local command / API / artifact parser
```

后续 MCP 接入后：

```text
Agent -> MCP Client -> MCP Server -> External tool
Agent -> Internal Tool Adapter -> Local tool
```

两者共用 ToolDefinition：name、description、input_schema、output_schema、risk_level、approval_required、allowed_projects、timeout_seconds、artifact_policy。

工具风险级别：

| 风险 | 示例 | 审批 |
|---|---|---|
| low | 读取文件、读取 git diff、读取报告 | 可自动 |
| medium | 执行 pytest/Playwright、生成报告 | 建议确认 |
| high | 应用 patch、写文件、真实环境接口 | 必须确认 |
| forbidden | 删除仓库、推送主分支、执行任意 shell | 禁止 |

## 7. GitHub MCP 参考接入

GitHub MCP 适合 V2 接入：仓库文件读取、PR 详情、commit/diff、Actions 状态和日志、Issue/PR 评论、安全信息。

V1 先做本地 Git Tool。

CI/CD 质量中心工具调用顺序：

```text
ChangeSetTool.get_repo_status
ChangeSetTool.get_diff
CICDChangeAnalysisAgent.analyze
UnitTestAgent.generate_patch
PatchScopeGate.validate
ToolApproval.apply_patch_if_approved
TestRunner.run_new_tests
RegressionAgent.select_pytest_regression
TestRunner.run_regression
FailureAnalysisAgent.analyze
ReportAgent.generate_cicd_quality_report
```

## 8. RAG Adapter 设计

第一版不搭建 RAG，只定义接口：

```text
KnowledgeAdapter.search_context(query, project_id, filters) -> evidence[]
KnowledgeAdapter.get_document(document_id) -> document
KnowledgeAdapter.list_sources(project_id) -> source[]
```

`rank_evidence` 或 rerank 逻辑是后续外部 provider 能力，不是 V1 内置 RAG 的必交接口。

未配置时：`used_knowledge = false`，`evidence = []`。任何 Agent 都不能因为没有 RAG 而失败。

## 9. 页面映射

| 页面 | 对应能力 |
|---|---|
| AI Workbench | Agent 编排、Prompt/Skill 选择、任务状态 |
| Requirement Review | RequirementReviewAgent、RiskAgent |
| Case Generation Review | CaseGenerationAgent、CaseReviewAgent |
| Test Case Library | Test Asset Service、Case Metrics、AutomationDraft 入口 |
| Automation Draft Center | AutomationDraftAgent、草稿评审、执行入口 |
| CI/CD 质量中心 | CICDChangeAnalysisAgent、UnitTestAgent、RegressionAgent |
| Automation Execution Center | ToolExecutionAgent、Tool Adapter |
| Tool Adapter / MCP Center | ToolDefinition、ToolInvocation、McpServerConfig |
| Report Center | FailureAnalysisAgent、ReportAgent |
| RAG 知识库 | ContextArtifact、Knowledge/RAG Adapter 配置和 evidence 展示 |

## 10. 第一版边界

第一版做：Internal Tool Adapter、本地 Prompt/Skill Registry、Agent 状态机、RAG 知识库 surface、Knowledge/RAG Adapter 空实现、需求到用例、AutomationDraft + pytest/Playwright、CI/CD 质量中心本地支线。

第一版不做：完整 MCP Server、完整外部 MCP marketplace、完整内置 RAG、Skill ZIP/Git 导入、Newman/JMeter 主路径、Appium 设备管理、Fiddler 深度自动化控制。

## 11. 最终版测试知识 RAG 与 Agent 方向

最终版方案见：

- `docs/implementation/11-final-rag-agent-strategy.md`

最终版 Chtest 的知识库不定位为通用聊天知识库，而是测试知识证据系统：

```text
测试知识 -> 可追溯 evidence -> 用例生成
  -> Agent 质量评审 -> 人工评审
  -> 执行证据 -> 反馈回知识库
```

推荐三层测试知识能力，而不是一次性建设重型 RAG 平台：

| 层级 | 目的 | 主要参考 |
|---|---|---|
| L1 Structured Test Knowledge Evidence | 把需求、接口、缺陷、测试规范抽取成 TestKnowledgeCard 和 KnowledgeEvidence | 结构化文档解析、测试领域 schema |
| L2 Hybrid Retrieval | 大知识库下用结构化过滤、全文检索、可选向量和 rerank 提升召回 | PostgreSQL full-text、pgvector、Haystack / LlamaIndex behind KnowledgeAdapter |
| L3 Test Relationship Graph | 用需求、模块、接口、风险、缺陷、用例、执行结果做覆盖和影响分析 | 确定性关系图优先，Microsoft GraphRAG-style offline reasoning 后置 |

最终版 Agent 分工应扩展为：

```text
KnowledgeIngestionAgent
RequirementUnderstandingAgent
RiskAnalysisAgent
CoverageAnalysisAgent
TestDesignAgent
CaseGenerationAgent
CaseReviewAgent
DedupAgent
AutomationReadinessAgent
KnowledgeFeedbackAgent
```

开源复用原则：

- 优先通过库、API、外部 provider 或独立服务复用开源能力。
- 不把大型 RAG 平台源码直接拷进 Chtest 核心模块。
- 所有 provider 结果必须转换成 Chtest 的 KnowledgeEvidence。
- 每个 provider 引入前必须记录许可证、版本、升级方式、fallback 行为和
  golden/eval 验证。
- 开源参考清单、迁移边界和 AI coding 填写模板见
  `docs/reference/01-open-source-migration-map.md`。
- L1 是最终版主线能力；L2/L3 必须由 eval 证明能提升用例接受率、覆盖率、
  自动化可执行性或证据可查验性后再启用。
- 任何检索或图能力都不能绕过 GeneratedCaseCandidate、CaseReviewAgent 和
  人工评审状态机。
