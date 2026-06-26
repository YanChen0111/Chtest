# Chtest User Journey And Page PRD

## 1. 文档目的

本文是 Chtest V1 的页面级 PRD。它把主 PRD 中的能力拆成用户可操作的页面、流程、状态和验收标准，方便后续 AI 或开发者直接进入实现。

Chtest V1 不是企业协作平台，也不是展示型 demo。V1 必须围绕三条最小闭环交付真实效率提升：

```text
主线 A：需求 -> AI 需求评审 -> AI 用例生成 -> 人工评审 -> 用例库
主线 B：需求/用例 -> AI 自动化草稿 -> 审批 -> pytest/Playwright 执行 -> 报告
支线 C：CI/CD 质量中心：本地 diff -> AI 单测补丁 -> 审批 -> pytest 回归 -> 质量门禁 -> 证据报告
```

第一条和第二条是 V1 主心智；第三条是 V1 支线能力，满足 push/diff 后补单测和回归的明确诉求。

## 2. 产品使用心智

用户打开 Chtest 时，不应该面对复杂企业后台，而应该看到一个个人测试设计与自动化落地工作台：

- 我今天要测什么需求？
- AI 发现了哪些需求问题？
- AI 生成的用例质量如何？
- 哪些用例我已经接受、修改、驳回？
- 哪些用例可以生成自动化草稿？
- 自动化草稿是否已经审批并执行？
- 最近 CI/CD 变更或本地代码变更有没有补单测？
- 哪些上下文工件或外部知识证据被 AI 使用？
- 这次测试能不能给出可信报告？

因此第一版页面布局以工作流和证据链为中心，不以组织、权限、空间、成员管理为中心。

## 3. 主线 A：需求到用例闭环

### 3.1 入口

入口页面：AI 工作台或需求评审。

用户输入：项目、模块、需求文本或 Markdown 文件、需求来源、目标测试类型、可选上下文工件、是否使用外部知识库 evidence。

### 3.2 前置条件

- 至少存在一个项目。
- 至少存在一个模块。
- 已配置可用模型，或使用 mock LLM provider。
- Prompt/Skill Registry 已加载需求评审和用例生成模板。

### 3.3 用户步骤

1. 用户粘贴需求或上传 Markdown。
2. 用户可选择上下文工件，例如 API notes、OpenAPI 片段、fixture、日志摘要。
3. 用户点击“开始需求评审”。
4. 系统创建 AI 任务，并记录 `context_artifact_ids`。
5. RequirementReviewAgent 输出六维评分、风险矩阵、澄清问题、可测性建议。
6. 用户查看本次实际使用的上下文工件。
7. 用户确认或编辑需求评审结果。
8. 用户点击“生成用例”。
9. CaseGenerationAgent 生成候选用例。
10. 候选用例进入用例生成评审页面。
11. 用户接受、编辑后接受、驳回或要求优化。
12. 通过评审的候选用例进入用例库。
13. 系统记录批次质量指标。

### 3.4 成功输出

- 需求。
- 上下文工件。
- 需求评审。
- 风险项。
- 用例生成任务。
- 候选用例。
- 测试用例。
- 用例质量指标。

### 3.5 空状态

- 无项目：提示创建默认项目。
- 无模块：提示创建模块。
- 无模型配置：提示配置模型或使用 mock provider。
- 无需求内容：输入框显示示例占位，不允许提交。
- 无候选用例：展示生成失败原因、Prompt 版本、重试按钮。

### 3.6 错误状态

- LLM 调用失败：展示错误摘要、provider、模型、重试建议。
- JSON schema 校验失败：保留 raw output artifact，展示字段错误。
- 需求过长：提示拆分模块或压缩输入。
- 候选用例重复率过高：提示调整 Prompt/模块/测试类型后重试。

## 4. 主线 B：用例到自动化闭环

### 4.1 入口

入口页面：用例库、自动化草稿中心、AI 工作台。

第一版支持：

- 从已通过评审的 TestCase 生成 pytest 自动化草稿。
- 从已通过评审的 UI TestCase 生成 Playwright 自动化草稿。
- 审批或编辑自动化草稿。
- 审批后通过 TestRunner/Playwright 执行。
- 保存 stdout/stderr/JUnit/trace/screenshot artifact。
- 生成执行报告。

### 4.2 前置条件

- 至少存在一个 approved TestCase。
- 已配置 TestCommand。
- Prompt/Skill Registry 已加载 automation_draft_generation。
- ToolDefinition 已注册 TestRunnerTool 或 PlaywrightTool。

### 4.3 用户步骤

1. 用户从 TestCase 详情点击“生成自动化草稿”。
2. AutomationDraftAgent 生成 pytest 或 Playwright 草稿。
3. 草稿进入自动化草稿中心。
4. 用户查看代码、执行说明、风险说明。
5. 用户执行 edit、approve 或 reject。
6. 审批通过后用户点击“执行”。
7. ToolExecutionAgent 调用 TestRunnerTool 或 PlaywrightTool。
8. 系统保存执行 artifact。
9. FailureAnalysisAgent 在失败时归因。
10. ReportAgent 生成 automation_execution report。

### 4.4 成功输出

- 自动化草稿。
- 工具调用。
- 测试运行。
- 测试结果。
- 工件。
- 失败分析，可选。
- 报告。

### 4.5 空状态

- 无 approved TestCase：提示先完成用例评审。
- 无 TestCommand：提示配置 pytest 或 Playwright 命令。
- 无 ToolDefinition：提示初始化工具。
- 无可生成草稿：展示原因，例如测试类型不支持。

### 4.6 错误状态

- AutomationDraft schema 校验失败：保留 raw output。
- 未审批执行：禁止创建 TestRun。
- 工具执行失败：保存 stdout/stderr 并展示失败分类。
- Playwright locator 失败：保存 trace/screenshot，进入失败归因。

## 5. 支线 C：CI/CD 质量中心闭环

### 5.1 入口

入口页面：CI/CD 质量中心。

第一版输入方式：本地仓库路径、base/head commit、手动上传 diff。GitHub Actions、GitLab CI、webhook、GitHub MCP、PR 评论是 V2 能力。

### 5.2 前置条件

- 项目已配置 Repository。
- Repository local_path 在 allowlist 工作目录内。
- 至少配置一个 pytest TestCommand。
- ChangeSetTool 可读取 diff。
- UnitTestAgent 和 RegressionAgent 对应 Prompt/Skill 已加载。

### 5.3 用户步骤

1. 用户选择仓库、base/head 或上传 diff。
2. ChangeSetTool 读取变更文件和 diff。
3. CICDChangeAnalysisAgent 输出变更摘要、风险等级、影响模块、建议测试范围。
4. UnitTestAgent 生成 UnitTestPatch。
5. PatchScopeGate 校验只修改测试目录。
6. 用户在 Patch Review 中接受、拒绝、编辑或重新生成。
7. 用户确认后系统应用 patch。
8. TestRunner 执行新增 pytest。
9. RegressionAgent 推荐 pytest 回归命令。
10. TestRunner 执行回归。
11. FailureAnalysisAgent 分析失败日志和 JUnit。
12. 系统生成 QualityGateDecision。
13. ReportAgent 生成 CI/CD 质量报告。

### 5.4 成功输出

- CICDRun。
- CICDChangedFile。
- `risk_analysis.json` artifact。
- 单测补丁。
- RegressionPlan。
- 测试运行。
- 失败分析。
- 质量门禁结论。
- CI/CD 质量报告。

## 6. 页面清单

### 6.1 首页 / AI 工作台

目标：统一发起 AI 测试任务，查看最近任务和关键指标。

| 区域 | 内容 |
|---|---|
| 顶部操作区 | 新建需求评审、新建用例生成、新建自动化草稿、新建 CI/CD 任务 |
| 最近任务 | AI 任务状态、Agent、耗时、结果入口 |
| 今日质量概览 | 用例采纳率、草稿通过率、执行通过率、回归通过率 |
| 待处理 | 待评审用例、待审批自动化草稿、待审批补丁、失败测试 |

验收：用户能在 30 秒内找到今天待处理的测试工作。

### 6.2 项目设置

目标：维护单用户项目上下文。

| 区域 | 内容 |
|---|---|
| 项目 | 项目名称、描述、默认语言、默认测试类型 |
| 模块树 | 5 级模块树 |
| 仓库 | 本地仓库路径、默认 base branch |
| 环境 | dev/test/local-prod 配置 |
| TestCommand | pytest、Playwright 命令 allowlist；Newman/JMeter 后置 |
| 上下文工件 | 本地上下文文档、API notes、OpenAPI 片段、fixture、日志摘要；展示 safe_to_show、redaction_applied |

验收：后续 AI 任务都能引用项目、模块、仓库、测试命令和已通过安全检查的上下文工件。

### 6.3 需求评审

目标：让 AI 在测试开始前发现需求问题。

| 区域 | 内容 |
|---|---|
| 左侧输入 | 需求文本、文件、模块、测试类型、上下文工件选择器、use_knowledge 开关 |
| 中间评分 | 六维评分、总分、风险等级 |
| 右侧问题 | 澄清问题、冲突、不可测描述、改写建议、used_context_artifact_ids |
| 下方风险矩阵 | 风险项、影响范围、建议测试策略 |

关键操作：开始评审、编辑评分、保存评审、生成用例。

### 6.4 用例生成评审

目标：AI 生成的用例必须经过人工评审后入库。

| 区域 | 内容 |
|---|---|
| 左侧 | 需求模块、生成批次、模块树 |
| 中间 | 候选用例表格、状态、优先级、类型、重复提示 |
| 右侧 | 用例详情、步骤、预期、AI 理由、需求引用、编辑表单 |
| 顶部 | 生成数、采纳率、驳回率、修改率、重复率、评审进度 |

关键操作：接受、编辑后接受、驳回、要求优化、批量评审。

### 6.5 用例库和测试套件

目标：沉淀可复用测试资产，并作为自动化草稿入口。

| 区域 | 内容 |
|---|---|
| 模块树 | 5 级模块组织 |
| 用例表 | 标题、类型、优先级、来源、review_status、最近执行结果 |
| 详情抽屉 | 步骤、预期、数据、需求引用、已发布版本 |
| 自动化入口 | 生成 pytest/Playwright AutomationDraft |
| 套件 | 用例组合、执行策略、关联命令 |

### 6.6 自动化草稿中心

目标：让 AI 自动化脚本先以草稿形式进入人工评审，不直接写业务项目。

| 区域 | 内容 |
|---|---|
| 草稿列表 | 来源用例、target_framework、状态、生成时间 |
| 代码查看 | draft_code、suggested_file_path、diff/编辑视图 |
| 说明区 | execution_notes、risk_notes、Prompt/Skill 版本 |
| 评审区 | edit、approve、reject |
| 执行区 | 选择 TestCommand、执行、查看 TestRun |

规则：AutomationDraft 不使用 `approve_after_edit`；该动作仅用于 GeneratedCaseCandidate。

验收：未审批的 AutomationDraft 不能执行；审批后可触发 pytest 或 Playwright。

### 6.7 执行中心

目标：统一调度 V1 测试执行工具。

| 区域 | 内容 |
|---|---|
| 工具列表 | TestRunner、Playwright；Newman/JMeter 后置 |
| 执行表单 | 项目、环境、命令、参数、artifact 策略 |
| 执行进度 | queued/running/passed/failed/error/timeout/cancelled |
| artifact | stdout、stderr、JUnit、coverage、trace、screenshot |

验收：pytest 和 Playwright 至少一个能从 UI/API 触发执行并结构化保存结果。

### 6.8 CI/CD 质量中心

目标：让本地代码变更形成测试补全和回归证据。V1 的 CI/CD 质量中心是本地 diff 与回归证据工作流，不是 GitHub Actions/GitLab 云平台。

| 区域 | 内容 |
|---|---|
| 仓库概览 | repo、branch、base、head、changed files |
| Diff 风险 | 风险等级、影响模块、变更摘要 |
| 单测生成 | UnitTestPatch diff、测试意图、覆盖目标、门禁结果 |
| 回归计划 | pytest 命令、风险解释、预计耗时 |
| 执行结果 | 新增测试、回归测试、stdout/stderr/JUnit |
| 报告 | 是否建议合并、阻塞风险、失败归因、CI/CD 质量报告 |

验收：每个 CICDRun 最终能给出“可合并/不建议合并/需人工判断”的质量结论。

### 6.9 报告中心

目标：输出可追溯测试结论。

| 区域 | 内容 |
|---|---|
| 报告列表 | 类型、关联对象、结论、生成时间 |
| 报告详情 | 摘要、指标、失败证据、未覆盖风险、建议下一步 |
| 导出 | Markdown、HTML、JSON |

验收：报告结论必须引用 evidence/artifact，不能只有 AI 文字判断。

### 6.10 RAG 知识库

目标：管理 V1 的上下文工件、知识适配器配置状态和 evidence 展示，但不内置向量库、embedding、分块或 rerank 流水线。

| 区域 | 内容 |
|---|---|
| 知识源分组 | 项目文档、API notes、OpenAPI、fixture、日志、历史缺陷摘要 |
| 上下文工件表 | 名称、类型、owner、safe_to_show、redaction_applied、allowed_for_prompt、最近使用 |
| 详情抽屉 | 摘要、安全元数据、context_manifest、最近 AI 任务 |
| Evidence 测试 | query、provider 状态、evidence id、source、snippet、score |

规则：`use_knowledge=false` 只表示不使用外部 KnowledgeAdapter，不表示禁用已选择的 `context_artifact_ids`。

### 6.11 Prompt / Skill 中心

目标：管理 AI 行为规范和版本。

| 区域 | 内容 |
|---|---|
| Prompt 列表 | name、version、hash、适用 Agent、状态 |
| Skill 列表 | name、version、输入输出 schema、质量门禁 |
| 效果指标 | 采纳率、失败率、schema 通过率、平均 token |

### 6.12 工具适配器 / MCP 中心

目标：集中管理可调用工具和安全策略。

| 区域 | 内容 |
|---|---|
| ToolDefinition | 名称、schema、风险等级、是否审批、超时 |
| ToolInvocation | 调用时间、输入摘要、状态、artifact |
| MCP Placeholder | 未来 MCP Server 配置，第一版可为空 |

## 7. 页面级通用规则

- 长任务必须显示状态、耗时、Agent、当前阶段。
- AI 输出必须显示 Prompt/Skill/model 追踪信息。
- 会写文件、应用 patch、触发真实工具执行的操作必须有确认。
- AutomationDraft 未审批不能执行。
- UnitTestPatch 未审批不能应用。
- 表格必须支持按项目、模块、状态、来源、时间过滤。
- 失败状态必须保留原始 artifact，不允许只显示“失败”。
- RAG 知识库不能暗示 V1 已内置向量检索或 rerank。
- 第一版不要求复杂权限，但所有操作都必须有审计记录。

## 8. 第一版页面验收清单

- 用户可以从 Home 进入三条最小闭环。
- 需求评审能生成可保存的六维评分和风险矩阵。
- 用例生成评审能完成人工评审闭环。
- 自动化草稿中心能生成、评审、执行 pytest/Playwright 草稿。
- CI/CD 质量中心能完成 diff 分析、patch 评审、pytest 回归、报告生成。
- 报告中心能查看 Markdown/HTML/JSON 报告。
- RAG 知识库能管理上下文工件、展示安全元数据和外部 evidence 状态。
- Prompt/Skill/Tool 的版本和调用记录可追踪。
