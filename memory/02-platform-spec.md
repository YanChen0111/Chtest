# Chtest Platform Spec Memory

## 1. 总体架构

V1 采用单用户、模块化单体 + Worker 架构。底层真实使用 PostgreSQL + Redis。平台定位是个人测试/自动化测试工程师的 AI 测试设计与自动化落地工作台，不是企业协作测试管理系统。

正式架构以 `docs/architecture/01-platform-architecture.md` 和 `docs/contracts/*` 为准。

## 2. 核心页面

```text
AI Workbench
Requirement Review
Case Generation Review
Test Case Library
Automation Draft Center
Automation Execution Center
CI/CD Quality Center
Report Center
Prompt & Skill Center
Tool Adapter / MCP Center
RAG Knowledge Base
Settings
```

## 3. Backend Control Plane

```text
Project Service
Requirement Service
Case Generation Service
Case Review Service
Test Asset Service
Automation Draft Service
CI/CD Quality Service (powers CI/CD Quality Center)
Tool Adapter Service
AI Task Service
Execution Service
Report Service
Prompt/Skill Service
Knowledge Adapter Service
Single User Context
Audit Log Service
```

## 4. AI Orchestration Plane

```text
OrchestratorAgent
RequirementReviewAgent
RiskAgent
CaseGenerationAgent
CaseReviewAgent
AutomationDraftAgent
CICDChangeAnalysisAgent
UnitTestAgent
RegressionAgent
ToolExecutionAgent
FailureAnalysisAgent
ReportAgent
```

## 5. 三条核心流程

### 5.1 需求到用例

```text
自然语言/需求文档
  -> RequirementReviewAgent 六维评分
  -> RiskAgent 生成风险矩阵
  -> CaseGenerationAgent 生成用例候选批次
  -> 字段完整性/重复/断言质量检查
  -> Case Generation Review Window
  -> 用户接受 / 编辑后接受 / 驳回 / 要求优化
  -> 通过评审的用例进入 Test Case Library
  -> 记录 generation metrics 和 review metrics
```

关键要求：AI 生成用例不得直接进入正式库，必须先进入候选批次和评审窗口。

### 5.2 用例到自动化

```text
Requirement/TestCase
  -> AutomationDraftAgent 生成 pytest/Playwright 草稿
  -> Automation Draft Center 展示代码、说明、风险
  -> 用户审批/编辑/拒绝
  -> ToolExecutionAgent 调用 TestRunnerTool 或 PlaywrightTool
  -> TestRun/TestResult 保存执行结果
  -> Artifact Store 保存 stdout/stderr/JUnit/trace/screenshot
  -> FailureAnalysisAgent 失败归因
  -> ReportAgent 生成自动化执行报告
```

关键要求：AutomationDraft 未审批不能执行，AI 不能直接写业务项目。

### 5.3 CI/CD 质量中心到质量报告

```text
手动 diff / 本地 base-head
  -> CI/CD 质量中心创建 CICDRun
  -> ChangeSetTool 收集 diff、文件状态
  -> CICDChangeAnalysisAgent 分析变更文件和风险等级
  -> UnitTestAgent 生成 UnitTestPatch
  -> PatchScopeGate 校验只写测试目录
  -> Patch Review Window 展示 patch、解释、风险和命令
  -> 用户接受/拒绝/编辑/重新生成 patch
  -> TestRunner 执行新增 pytest
  -> RegressionAgent 选择相关 pytest 回归范围
  -> TestRunner 执行回归
  -> FailureAnalysisAgent 归因
  -> ReportAgent 生成 CI/CD 质量报告
```

关键要求：CI/CD 质量中心是 V1 支线能力，本地优先；底层可继续使用 CICDRun/UnitTestPatch；GitHub MCP/PR 评论/CI webhook 后置 V2。

## 6. 核心状态机

状态机以 `docs/contracts/03-state-machines.md` 为准，包含：

- AITask。
- GeneratedCaseCandidate。
- AutomationDraft。
- UnitTestPatch。
- ToolInvocation。
- TestRun。
- Report。
- PromptVersion / SkillVersion。

## 7. 核心数据实体

字段级定义以 `docs/contracts/01-data-model-contract.md` 为准，核心实体包括：

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
CICDRun
CICDChangedFile
UnitTestPatch
RegressionPlan
AITask
Artifact
PromptVersion
SkillVersion
ToolInvocation
TestRun
Report
```

## 8. 质量指标

- 用例生成：generated_count、field_complete_rate、duplicate_rate、acceptance_rate、edit_rate、rejection_rate。
- AutomationDraft：draft_generated_count、approval_rate、execution_pass_rate、manual_edit_rate。
- CI/CD 质量中心：patch_scope_pass_rate、patch_apply_rate、new_test_pass_rate、regression_pass_rate。
- 失败归因：evidence_complete_rate、classification_accuracy、unresolved_failure_rate。

详细指标以 `docs/product/04-ai-quality-metrics.md` 为准。

## 9. Knowledge/RAG Adapter

第一版不搭建 RAG，只预留接口。RAG 知识库页面只管理 ContextArtifact、KnowledgeAdapter 配置状态和 evidence 展示。未配置外部知识服务时返回空 evidence。Agent 必须能在没有 RAG 的情况下工作。

## 10. 第一版 Sprint 拆分

| 迭代 | 模块 | 验收 |
|---|---|---|
| Sprint 1 | Repo + Docker + Memory | Git 初始化；PostgreSQL/Redis compose 可启动；memory 完整 |
| Sprint 2 | Backend/Frontend Skeleton | FastAPI/Vue 可启动；健康检查通过 |
| Sprint 3 | Project Core | 可以创建项目、模块、仓库、环境、测试命令 |
| Sprint 4 | AI Task + Prompt/Skill Core | 可以创建任务、推进状态、保存 artifact、选择 PromptVersion/SkillVersion |
| Sprint 5 | Requirement Review | 可以生成六维评分和风险矩阵 |
| Sprint 6 | Case Generation Review | 可以生成候选用例并在评审窗口操作 |
| Sprint 7 | Case Metrics | 可以展示采纳率、驳回率、修改率、评审进度 |
| Sprint 8 | Test Case Library | 通过评审的用例入库，支持查询和 review_status |
| Sprint 9 | AutomationDraft | 可以从用例生成 pytest/Playwright 草稿并审批 |
| Sprint 10 | TestRunner / pytest | 审批后的草稿可触发 pytest 执行并保存 artifact |
| Sprint 11 | Playwright Minimal Loop | 可以执行 Playwright 草稿/已有测试并保存 trace/screenshot |
| Sprint 12 | Failure + Report Center | 可以生成失败归因、证据链和质量报告 |
| Sprint 13 | CI/CD 质量中心 | 可以读取 diff、生成风险摘要、UnitTestPatch、pytest 回归和报告 |
| Sprint 14 | MCP/RAG Adapter Surface | 可以配置 MCP 占位接口和 RAG 知识库 surface，未接入时主流程正常 |
