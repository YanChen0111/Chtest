# Chtest Project Constraints

## 1. 产品范围约束

- 第一版固定单用户模式，不做 RBAC、多租户、组织架构。
- 第一版是面向个人测试工程师、自动化测试工程师的 AI 测试设计与自动化落地工作台，不是企业协作测试管理平台。
- 第一版必须是真实测试全流程闭环，不做一次性演示。
- 第一版必须直接使用 PostgreSQL + Redis。
- 第一版主线是需求到用例、用例到自动化；Git 到质量报告是支线能力。
- 第一版必须包含 AI 用例生成评审窗口和质量指标。
- 第一版必须包含 AutomationDraft，AI 自动化草稿必须审批后执行。
- 第一版必须包含 Git Quality Center，支持 push/PR/diff 后单测生成和回归测试查看，但不能压过主线。
- 第一版不搭建 RAG，不内置向量数据库，只预留 Knowledge/RAG Adapter。
- 第一版不深度二开 WHartTest 或 MeterSphere，只吸收可复刻能力。

## 2. AI 输出约束

- AI 生成用例不能直接进入正式用例库，必须经过评审。
- AI 生成 AutomationDraft 不能直接写业务项目，必须人工审批后执行。
- AI 生成 UnitTestPatch 默认只能修改测试目录。
- AI 不允许自动修改业务源码。
- AI 不允许自动提交、自动 push、自动合并。
- AI 输出必须保存 PromptVersion、SkillVersion、输入、输出、模型、时间、artifact。
- AI 输出必须经过质量门禁：结构完整、可执行、非重复、有明确断言。
- 失败归因必须附证据，不能只给结论。

## 3. Tool/MCP 约束

- 第一版先实现 Internal Tool Adapter，MCP 作为可扩展接口。
- 工具调用必须记录输入、输出、状态、耗时、artifact。
- 高风险工具调用必须人工审批。
- 测试执行命令必须属于项目配置的 allowlist。
- Runner 执行目录必须受限，不能任意执行系统命令。
- V1 工具优先级：TestRunner/pytest P0，Playwright P1，Newman V1.1，JMeter V1.1/V2，Appium/Fiddler V3。
- GitHub MCP 后续接入时必须使用最小权限 token。
- MCP 工具不能绕过 Chtest 的审批、日志和质量门禁。

## 4. 数据与安全约束

- `.env` 和密钥不得提交。
- LLM API key、GitHub token、Postman token 等只允许在本地环境变量或部署 secret 中出现。
- 参考框架源码默认不纳入 Chtest Git 提交记录。
- 报告中默认脱敏 token、password、secret、cookie。
- Artifact 中的敏感请求头和响应体必须支持脱敏策略。

## 5. 工程约束

- V1 技术栈冻结，除非进入 ADR 流程。
- 后端优先类型化，避免宽泛 `Any` 泛滥。
- 每个模块先写清 schema、状态机、API，再写 UI。
- 每个 Slice 必须有可运行验收命令。
- 每个完成 Task 必须测试并 commit；Slice 完成或重大上下文变化时更新 `memory/07-dev-log.md` 和 `memory/08-session-handoff.md`；会话结束但 Slice 未完成时更新 handoff 的 Task table。
- 不为了“平台化”过早拆微服务。
- 不为了“企业级”引入 Kafka、Kubernetes、复杂权限和插件市场。

## 6. 参考框架约束

WHartTest 可吸收：MCP/Skills/Agent 思路、生成用例弹窗、`review_status` 状态机、优化待审核流程、测试任务中心和执行器拆分、UI/API 自动化思路。

MeterSphere 可吸收：用例评审列表、创建、详情、用例详情页面结构、通过率/评审进度统计、测试资产、测试计划、报告治理、接口测试和场景自动化的产品设计思想。

不允许：直接复制大段受许可证约束源码作为 Chtest 实现；把两套框架的所有模块一起搬进第一版；为了兼容参考框架牺牲 Chtest 第一版简单可维护性。

## 7. 验收约束

第一版每个核心流程都必须有证据：

- API 能跑。
- Worker 能消费任务。
- PostgreSQL 有迁移。
- Redis 队列能推进任务。
- UI 能完成关键操作。
- AI 调用有日志。
- Prompt/Skill 版本可追溯。
- 工具调用有审批和日志。
- 生成用例有评审结果和质量指标。
- AutomationDraft 有审批、执行结果和 artifact。
- Git 变更有 diff 分析、UnitTestPatch、回归计划和报告。
- 测试执行有原始日志和结构化结果。
