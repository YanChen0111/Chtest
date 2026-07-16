# Reference Framework Review

## 1. 参考框架源码位置

- WHartTest：`/Users/yanchen/VscodeProject/Chtest/参考框架/WHartTest`，参考提交 `927bff2`
- MeterSphere：`/Users/yanchen/VscodeProject/Chtest/参考框架/metersphere`，参考提交 `5dc6df5`

## 2. WHartTest 源码观察

WHartTest 是 AI 驱动智能测试平台，当前源码结构包含：

```text
WHartTest_Django
WHartTest_Vue
WHartTest_Actuator
WHartTest_MCP
WHartTest_Skills
WHartTest_WeixinPluginHost
docs
deploy-scripts
```

关键参考点：

- `WHartTest_MCP`：FastMCP 工具服务，可参考测试平台工具、测试用例工具封装方式。
- `WHartTest_Skills`：包含 api-automation、playwright、ui-automation、agent-browser 等 Skill。
- `WHartTest_Django/testcases/models.py`：用例包含 `review_status`，状态包括 `pending_review`、`approved`、`needs_optimization`、`optimization_pending_review`、`unavailable`。
- `WHartTest_Django/testcases/filters.py`：支持按 `review_status` 和 `review_status_in` 过滤。
- `WHartTest_Vue/src/components/testcase/GenerateCasesModal.vue`：生成用例弹窗支持生成模式、测试类型、需求文档、需求模块、prompt、知识库、保存模块、用例选择。
- `WHartTest_Vue/src/views/TestCaseManagementView.vue`：集成 `GenerateCasesModal`、`OptimizationSuggestionModal`、执行弹窗、详情弹窗和流式 AI 聊天调用。
- `WHartTest_Vue/src/components/testcase/TestCaseList.vue` 与 `TestCaseDetail.vue`：用例列表和详情支持 review status 展示和变更。
- `WHartTest_Vue/src/views/DashboardView.vue`：按审核状态统计用例数量。

适合 Chtest 吸收：

- MCP 工具化方式。
- Skills 文件夹组织。
- AI 测试任务中心。
- 生成用例弹窗的配置项。
- review_status 状态机。
- 优化待审核流程。
- API/UI 自动化能力拆分。
- 执行器独立化思路。

不建议照搬：

- 默认 API key 和生产安全策略。
- Django monorepo 全量结构。
- 内置 knowledge/RAG 能力。
- 微信插件等非第一版核心能力。

## 3. MeterSphere 源码观察

MeterSphere 是企业级持续测试平台，当前源码结构包含：

```text
backend/services/case-management
backend/services/api-test
backend/services/test-plan
backend/services/project-management
backend/services/dashboard
frontend/src/views/case-management
frontend/src/views/api-test
frontend/src/views/test-plan
frontend/src/views/project-management
```

关键参考点：

- `frontend/src/router/routes/modules/caseManagement.ts`：包含用例评审列表、创建、详情、用例详情等路由。
- `frontend/src/views/case-management/caseReview/index.vue`：用例评审列表入口。
- `frontend/src/views/case-management/caseReview/create.vue`：创建评审。
- `frontend/src/views/case-management/caseReview/detail.vue`：评审详情展示已评审数量、总数和通过率。
- `frontend/src/views/case-management/caseReview/caseDetail.vue`：评审用例详情。
- `frontend/src/views/case-management/caseReview/components/passRateLine.vue`：通过/不通过/重新评审/评审中/未评审的进度条和 popover。
- `frontend/src/views/case-management/caseReview/components/reviewSubmit.vue`、`reviewResult.vue`、`reviewForm.vue`：评审提交与结果组件。
- `backend/services/case-management/.../CaseReviewController.java`：用例评审管理接口。
- `backend/services/case-management/.../CaseReviewFunctionalCaseController.java`：评审详情、批量评审、评审人状态等接口。
- `backend/services/case-management/src/main/resources/prompts/generate_step.st` 和 `generate_text.st`：可参考用例生成 prompt 组织。

适合 Chtest 吸收：

- 用例评审页的信息架构。
- 评审详情里的 reviewedCount/caseCount/passRate 展示。
- passRateLine 的多状态进度条思想。
- 批量评审、评审结果、评审记录。
- 测试资产模型和测试计划模型。
- 接口测试、Mock、场景自动化、报告的产品设计思想。

不建议照搬：

- Spring Boot + Kafka + MySQL + MinIO 全量基础设施。
- 复杂插件体系第一版实现。
- 大体量企业架构。
- 许可证受限源码二开。
- 团队协作、组织权限等企业治理能力。

## 4. GitHub MCP / MCP 参考点

参考方向：

- MCP Tools 适合把 Git、测试执行、报告生成等外部工具暴露给 AI 调用。
- MCP Prompts 适合作为可复用提示模板入口。
- MCP Resources 适合暴露仓库文件、测试报告、用例资产等上下文。
- GitHub MCP Server 可作为后续 GitHub 仓库、PR、Actions、Issue、代码安全等工具接入参考。

Chtest 第一版不直接重依赖 MCP，而是先做 Internal Tool Adapter，并保持 MCP-ready 接口。

## 5. Chtest 第一版复刻清单

| 能力 | 参考来源 | Chtest 第一版做法 |
|---|---|---|
| 用例生成弹窗 | WHartTest | 做需求、测试类型、prompt、目标模块、生成模式选择 |
| 用例评审状态 | WHartTest | 复刻 pending/approved/needs_optimization/optimization_pending/unavailable |
| 优化待审核 | WHartTest | 驳回/要求优化后生成新候选并进入二次评审 |
| Skill 体系 | WHartTest | 内置测试方法 Skill，后续支持 ZIP/Git 导入 |
| MCP 思想 | WHartTest/GitHub MCP | 第一版先 Tool Adapter，后续接 MCP |
| 用例评审列表 | MeterSphere | 做生成批次列表和正式评审列表 |
| 评审详情 | MeterSphere | 展示已评审数、总数、通过率、状态分布 |
| 通过率进度条 | MeterSphere | 复刻多状态质量条：通过、驳回、待优化、评审中、未评审 |
| 批量评审 | MeterSphere | 支持批量接受/驳回/要求优化 |
| 接口测试思想 | MeterSphere/Postman | V1.1 通过 Newman 调度实现，V1 先不进入主路径 |
| 测试资产治理 | MeterSphere | 模块、等级、类型、来源、评审记录、执行结果 |

## 6. Chtest 取舍

| 领域 | 参考来源 | Chtest 第一版取舍 |
|---|---|---|
| AI/MCP/Skills | WHartTest | 重点吸收，先轻量工具化，后续完整 MCP |
| 执行器 | WHartTest | 吸收思想，轻量实现 |
| 用例评审 | MeterSphere + WHartTest | 第一版核心能力 |
| 测试资产 | MeterSphere | 吸收模型，简化权限 |
| 测试计划/套件 | MeterSphere | 第一版做个人套件和执行计划 |
| 接口测试 | MeterSphere/Postman | V1.1 接 Newman，后续增强场景编排 |
| 性能测试 | JMeter | V1.1/V2 调度 JMeter non-GUI，后续解析更多指标 |
| Web UI 测试 | WHartTest/Playwright | 第一版接 Playwright 执行和 trace，低代码后置 |
| RAG | WHartTest/外部 | 第一版只预留接口 |
| 企业权限 | MeterSphere | 第一版不做 |

## 7. 可行性评估

以个人使用 Codex 5.5 长期开发，项目可行，但必须小步拆分：

- 高可行：memory、项目骨架、PostgreSQL/Redis、项目/仓库/环境、AI 任务、artifact、报告。
- 高可行：用例生成候选、评审窗口、review_status、质量指标落库。
- 高可行：CI/CD Quality Center 基础版、diff 分析、单测 patch 评审。
- 中可行：测试 patch 生成、回归选择、测试执行、失败归因。
- 中可行：Playwright 最小闭环；Newman/JMeter 后置调度。
- 中低可行：完整 UI 低代码编排、完整 APP 自动化、Fiddler 深度控制。
- 暂不建议：内置 RAG、完整 MeterSphere 级别企业测试平台、完整 WHartTest 级 AI 子系统。

## 8. 最优落地路线

1. 先做 Chtest 自有单用户平台基础。
2. 跑通 AI Task + Prompt + Skill。
3. 跑通需求评审到用例生成评审和质量指标。
4. 做 AutomationDraft + pytest/Playwright 最小闭环。
5. 做 CI/CD Quality Center 支线，支持 diff 到 UnitTestPatch 和 pytest 回归。
6. 后续接 Newman/JMeter 工具调度。
6. 做失败归因和报告中心。
7. 再接 GitHub webhook 和 GitHub MCP。
8. 再接外部 RAG 服务。
