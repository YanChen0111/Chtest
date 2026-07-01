# Chtest Non Goals And Version Boundaries

## 1. 文档目的

本文用于防止 Chtest V1 失控。Chtest 长期可以演进为小团队 AI Testing Workbench 平台和 Agent/Skill/MCP 工具生态，但 V1 必须先做成个人测试工程师、自动化测试工程师真实可用的 AI 测试设计与自动化落地工作台。

## 2. 产品北极星

V1 只围绕三条最小闭环交付价值：

1. 需求到用例：更快完成需求评审、测试用例设计、用例评审和入库。
2. 用例到自动化：更快生成 pytest/Playwright 自动化草稿、审批执行并输出报告。
3. CI/CD 到质量：针对本地 diff 补单测、跑 pytest 回归、输出质量门禁和证据结论。

第一条和第二条是主线；第三条是支线但保留为 V1 差异化能力。

## 3. V1 范围

### 3.1 V1 必做

| 模块 | 必做能力 |
|---|---|
| 基础平台 | Docker Compose、PostgreSQL、Redis、backend、worker、frontend |
| 单用户上下文 | 默认用户、默认工作区、项目、模块、仓库、环境、测试命令 |
| AI Core | LLM Provider、PromptVersion、SkillVersion、AITask、artifact、调用日志 |
| 需求评审 | 需求录入、六维评分、风险矩阵、澄清问题、可测性建议 |
| 用例生成 | 结构化候选用例、字段校验、需求引用、重复检测初版 |
| 用例评审 | 接受、编辑后接受、驳回、要求优化、评审记录、质量指标 |
| 用例库 | 模块树、正式用例、测试套件基础能力 |
| AutomationDraft | 从需求/用例生成 pytest/Playwright 草稿，审批后执行 |
| TestRunner | 执行 pytest allowlist 命令，保存 stdout/stderr/JUnit/coverage |
| Playwright 最小闭环 | 执行脚本草稿或已有测试，保存 trace/screenshot |
| CI/CD 质量中心支线 | 本地 diff 分析、UnitTestPatch、审批、pytest 回归、质量门禁、CI/CD 质量报告 |
| 报告中心 | 需求评审报告、用例生成质量报告、自动化执行报告、CI/CD 质量报告 |
| 扩展接口 | RAG 知识库页面、Knowledge/RAG Adapter 空实现、Tool Adapter schema、MCP-ready 设计 |

### 3.2 V1 工具优先级

| 优先级 | 工具 | 范围 |
|---|---|---|
| P0 | TestRunner / pytest | V1 主执行闭环和 CI/CD 质量门禁闭环基础 |
| P1 | Playwright | V1 只做最小闭环：脚本草稿、审批、执行、trace/screenshot |
| P2 | Newman | V1.1，collection 执行和结果解析 |
| P3 | JMeter | V1.1/V2，jmx non-GUI 和 JTL 报告解析 |
| P4 | Appium / Fiddler | V3，移动设备和代理环境复杂度较高 |

## 4. V1 非目标

| 非目标 | 后置原因 |
|---|---|
| 多租户 / RBAC / 组织权限 | 与个人工具定位冲突，会显著增加复杂度 |
| 企业级审批流 | V1 只保留人工确认、用例评审、patch 审批和工具审批 |
| 内置完整 RAG / 向量库 | 用户明确要求 RAG 只作为接口保留 |
| 完整 MCP Server / 插件市场 | V1 先做 Internal Tool Adapter，后续再 MCP 化 |
| 完整低代码 UI 自动化平台 | 成本高，V1 只做 Playwright 草稿和执行 |
| 完整接口测试平台替代 Postman | Newman 后置到 V1.1，不重造全量 API 管理 |
| 完整 JMeter 平台 | JMeter 后置到 V1.1/V2 |
| Appium 设备农场 | 环境成本高，不适合 V1 |
| Fiddler 深度集成 | 证书、代理、桌面环境复杂，V3 再考虑 |
| 完整 CI/CD 云平台 | V1 的 CI/CD 质量中心只做本地 diff、手动触发、回归证据和质量门禁；GitHub Actions、GitLab CI、webhook、PR 评论放 V2，真实 CD 发布放 V3 |
| 团队缺陷管理 | V1 可导出报告，缺陷平台集成后置 |
| 大规模分布式执行 | 个人工具先保证本地 worker 稳定 |
| AI 自动修改业务源码 | V1 禁止，避免不可控风险 |

## 5. V1.1 范围

V1.1 是 V1 可用后的增强版本，目标是提高日常使用体验和工具覆盖。

可做：

- Excel 导入导出和字段映射模板。
- 更多测试框架自动识别。
- 覆盖率解析增强。
- Prompt/Skill A/B 对比。
- Newman collection 执行和结果解析。
- HAR 文件导入分析。
- JMeter 报告解析初版。
- 用例重复检测增强。
- 报告模板配置。
- 本地模型 Ollama 体验优化。
- CI/CD 质量中心的本地 pipeline stage 模板和更多测试框架识别。

## 6. V2 范围

V2 目标是增强外部集成和自动化能力。

可做：

- GitHub MCP 接入：PR、commit、Actions、Issue、评论。
- GitHub Actions / GitLab CI / Jenkins 运行记录导入。
- Chtest MCP Server：暴露项目、模块、用例、执行、报告能力。
- 外部 RAG Provider 正式接入。
- 远程执行器。
- API 测试中心增强：接口定义、环境变量、场景编排。
- Playwright 低代码初版：页面、元素、步骤、断言。
- CI Webhook。
- 报告自动评论到 PR。
- 远程 CI runner 对接，但不承担真实生产部署编排。

## 7. V3 范围

V3 是个人到小团队、工具生态扩展方向。

可做：

- Appium Android/iOS 执行。
- Fiddler/代理工具更深集成。
- 多项目模板和测试资产复用。
- 小团队轻权限。
- 分布式执行。
- CD 发布准备检查、发布窗口、回滚建议。
- 插件/Skill 包导入。
- 多模型路由和成本优化。
- 更完整的趋势分析。

## 8. 功能进入 V1 的判断标准

一个功能进入 V1 必须满足至少三条：

- 直接服务需求到用例闭环。
- 直接服务用例到自动化闭环。
- 直接服务 CI/CD 质量中心中的本地 diff 到 pytest 质量报告闭环。
- 能降低人工重复劳动。
- 能提升 AI 输出可控性。
- 能提高测试结论可信度。
- 实现成本不破坏单用户、低维护目标。

## 9. 后续 AI 开发约束

- 如果功能属于 V1 非目标，不要直接实现，先记录到 roadmap。
- 如果功能会改变 V1 技术栈，必须更新 ADR。
- 如果功能需要 RAG，不要内置向量库，只接 Knowledge Adapter。
- 如果功能需要 MCP，不要绕过 Tool Adapter 安全策略。
- 如果功能会让页面变成企业管理后台，优先裁剪。
- 如果功能会写文件，必须先检查 AI 写文件策略。
