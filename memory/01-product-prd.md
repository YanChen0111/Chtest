# Chtest Product PRD Memory

## 1. 产品定位

Chtest V1 是面向个人测试工程师、自动化测试工程师的 AI 测试设计与自动化落地工作台。

它不是企业协作测试管理平台。V1 不做组织、权限、团队审批、复杂项目治理和插件市场。长期方向是小团队 AI 测试工作台 + Agent / Skill / MCP 测试工具生态。

正式 PRD 以 `docs/product/01-positioning-and-scope.md` 和 `docs/product/02-v1-product-prd.md` 为准。

## 2. V1 三条最小闭环

| 闭环 | 内容 | 优先级 |
|---|---|---|
| 需求到用例 | 需求评审、候选用例、人工评审、正式用例库、质量指标 | 主线 P0 |
| 用例到自动化 | AutomationDraft、审批、pytest/Playwright 执行、失败归因、报告 | 主线 P0/P1 |
| CI/CD 到质量 | CI/CD 质量中心中的本地 Git diff、UnitTestPatch、审批、pytest 回归、CI/CD 质量报告 | 支线 P1 |

## 3. 第一版用户模式

- 一个默认用户。
- 一个默认工作空间。
- 支持多个测试项目、仓库、环境、测试命令。
- 不做登录注册、RBAC、多租户、组织架构。
- 数据模型保留 user/workspace 字段，方便后续升级。

## 4. 核心能力

### 4.1 需求评审

- Markdown / plain text 输入。
- 六维评分：完整度、清晰度、一致性、可测性、可行性、逻辑性。
- 风险矩阵。
- 澄清问题。
- 可测性改写建议。

### 4.2 用例生成与评审

- AI 生成结构化候选用例。
- 候选用例必须进入评审窗口。
- 支持接受、编辑后接受、驳回、要求优化。
- 通过评审后进入正式 TestCase。
- 记录采纳率、驳回率、人工修改率、字段完整率、重复率。

### 4.3 AutomationDraft

- 从 Requirement 或 TestCase 生成 pytest/Playwright 草稿。
- AI 不直接写业务项目。
- AutomationDraft 必须审批后执行。
- 执行后生成 TestRun、Artifact、Report。

### 4.4 CI/CD 质量中心

- V1 支线能力。
- 支持本地仓库 base/head 和手动 diff。
- CICDChangeAnalysisAgent 分析风险。
- UnitTestAgent 生成 UnitTestPatch。
- PatchScopeGate 只允许写测试目录。
- 审批后执行 pytest 新增测试和回归。
- 生成 CI/CD quality report。
- V1 不接 GitHub Actions/GitLab/webhook 云 CI；这些是 V2 能力。

### 4.5 Tool Adapter

V1：

- TestRunner/pytest P0。
- Playwright P1 最小闭环。

后置：

- Newman V1.1。
- JMeter V1.1/V2。
- Appium/Fiddler V3。

### 4.6 RAG/MCP

- RAG 不内置，只保留 Knowledge/RAG Adapter。
- RAG 知识库是 ContextArtifact、KnowledgeAdapter 配置状态和 evidence 展示页面，不是内置向量库或 rerank 平台。
- MCP 不作为 V1 强依赖，先实现 Internal Tool Adapter。
- ToolDefinition schema 保持 MCP-ready。

## 5. 第一版必须完成

| 模块 | 第一版目标 |
|---|---|
| Platform Shell | 单用户工作台、导航、项目上下文 |
| Project Core | 项目、模块、仓库、环境、测试命令配置 |
| AI Runtime | AITask、Artifact、LLMCallLog、Mock Provider |
| Prompt/Skill Registry | PromptVersion、SkillVersion、schema、hash |
| Requirement Review | 六维评分、风险矩阵、澄清问题 |
| Case Generation | 结构化候选用例 |
| Case Review Center | 用例生成评审窗口、批量评审、编辑、驳回、要求优化 |
| Case Quality Metrics | 采纳率、驳回率、人工修改率、字段完整率 |
| Test Case Library | 正式用例库、模块、等级、类型、来源、review_status |
| AutomationDraft | pytest/Playwright 草稿、审批、执行入口 |
| TestRunner | pytest allowlist 执行、stdout/stderr/JUnit artifact |
| Playwright Minimal Loop | 草稿/已有测试执行、trace/screenshot artifact |
| CI/CD 质量中心 | diff 记录、变更分析、UnitTestPatch、pytest 回归、质量报告 |
| Failure Analysis | 失败归因和证据链 |
| Report Center | Markdown/HTML/JSON 报告和质量结论 |
| Knowledge/RAG Adapter | 只预留接口，不实现 RAG |

## 6. 第一版不做

- 不做多用户权限、RBAC、团队协作流。
- 不搭建 RAG，不内置向量数据库。
- 不做完整文档解析、分块、精排、多模态知识库。
- 不深度二开 MeterSphere 或 WHartTest。
- 不做完整移动端自动化平台。
- 不做完整低代码 UI 自动化编排器。
- 不做完整接口测试平台替代 Postman。
- 不做完整 JMeter 平台。
- 不做完整 Fiddler 自动化控制。
- 不允许 AI 自动修改业务源码、自动提交主分支、自动 push。
- 不把参考框架源码作为 Chtest 运行依赖。

## 7. 产品验收标准

V1 必须能演示：

1. Docker Compose 启动 frontend、backend、worker、PostgreSQL、Redis。
2. 创建项目、模块、仓库、环境和测试命令。
3. 输入需求文档，生成六维评审、风险矩阵和候选用例。
4. 在评审窗口中接受、编辑、驳回、要求优化 AI 生成用例。
5. 查看该批次的采纳率、驳回率、人工修改率和评审通过率。
6. 把通过评审的用例沉淀到正式用例库。
7. 从需求/用例生成 AutomationDraft。
8. 审批 AutomationDraft 后执行 pytest 或 Playwright 最小闭环。
9. 在 CI/CD 质量中心导入 diff 或读取本地仓库变更。
10. 生成 UnitTestPatch 并进行人工评审。
11. 执行 pytest 新增测试和相关回归。
12. 查看失败归因、证据链和测试报告。
13. 查看 AI 任务输入、输出、PromptVersion、SkillVersion、模型、artifact 和质量门禁。
