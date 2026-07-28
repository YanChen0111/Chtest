<div align="center">

# Chtest

## 让 AI 生成的每一条测试结论，都有审查、有执行、有证据

**面向测试工程师的本地优先 AI 测试证据工作台**

从需求风险分析、用例设计、自动化生成，到受控执行、失败诊断和质量报告，
Chtest 将零散的 AI 能力组织成一条可复核、可追溯的测试闭环。

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3-42B883?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

[产品优势](#为什么选择-chtest) · [测试闭环](#一条真正闭环的-ai-测试链路) · [界面预览](#产品界面) · [快速开始](#快速开始)

</div>

![Chtest AI 测试工作台](docs/release/v1/screenshots/ai-workbench.png)

## 测试工作的难点，不是再生成一批内容

AI 可以快速生成用例和代码，但真实测试工作还必须回答：

- **为什么测？** 这条用例覆盖了哪个需求、风险或代码变更？
- **凭什么信？** AI 使用了什么上下文，输出是否经过结构校验和人工审查？
- **能不能跑？** 自动化脚本是否获批，执行环境和命令是否受控？
- **结果可靠吗？** 通过或失败的结论，能否追溯到日志、产物和运行记录？
- **下一步做什么？** 失败后如何定位，覆盖缺口如何补齐，经验如何沉淀？

Chtest 的目标不是替代测试工程师做判断，而是让测试工程师更早发现风险、更快形成资产，并用证据做出更可信的质量决策。

## 为什么选择 Chtest

| 常见 AI 测试工具 | Chtest 的产品选择 | 带来的测试价值 |
| :--- | :--- | :--- |
| 生成一次即结束 | 从需求分析贯通到报告与知识反馈 | 减少工具切换和测试资产断点 |
| 只展示最终答案 | 记录 Prompt、Skill、模型、上下文和 Artifact | 结论可解释，问题可复盘 |
| AI 输出直接进入下游 | 用例、自动化草稿和测试补丁设置人工门禁 | 保留测试人员的判断权，降低误执行风险 |
| 报告与执行证据分离 | 报告结论必须关联 TestRun、日志和证据清单 | 让通过、失败和质量门禁有据可查 |
| 通用知识库只做相似度召回 | 建模需求、风险、用例、执行、失败与测试知识关系 | 支持覆盖分析、影响分析和回归建议 |
| 依赖单一云模型或平台 | 本地优先、Mock 可运行、模型与检索提供商可替换 | 降低数据外发和厂商锁定成本 |

### 对不同角色的直接价值

| 角色 | 使用 Chtest 后可以获得什么 |
| :--- | :--- |
| 功能测试工程师 | 从需求中提取风险与测试点，审查 AI 候选用例，减少遗漏并保留判断过程 |
| 自动化测试工程师 | 将已审查用例转成可编辑、需审批的自动化草稿，并统一查看执行证据 |
| 测试负责人 | 从覆盖、审批、执行和报告证据判断质量，而不是只看一个“通过率”数字 |
| 研发与质量协作者 | 对本地代码变更进行风险分析、补充限定范围的单测，并获得可复核的质量门禁 |

## 一条真正闭环的 AI 测试链路

```text
需求 / 本地代码变更
        |
        v
AI 需求审查与风险识别 -----> 测试知识与项目上下文
        |
        v
候选用例生成与质量检查
        |
        v
人工审查、编辑、批准
        |
        v
自动化草稿 / 单元测试补丁
        |
        v
人工审批 + 受控执行
        |
        v
TestRun + 日志 + Artifact + 环境快照
        |
        v
失败分析 + 证据报告 + 质量门禁
        |
        v
经审查的测试知识反馈
```

这条链路把三个经常断开的环节连接起来：

1. **风险到覆盖**：每条候选用例说明覆盖的需求、风险、生成原因和自动化就绪度。
2. **资产到执行**：只有经过审查的用例与自动化草稿才能进入后续流程。
3. **执行到决策**：运行结果、日志、环境和证据清单共同支撑报告结论。

## 典型使用场景

### 需求评审后，快速形成可审查的测试方案

导入需求和项目上下文，识别边界、异常路径与高风险点，生成候选用例。测试人员可以逐条编辑、批准或拒绝，最终资产保留完整来源和审查记录。

### 从已批准用例推进自动化，而不是直接执行 AI 代码

基于正式用例生成 pytest 或 Playwright 草稿，检查代码、目标路径、运行说明和风险提示。只有人工批准后，草稿才能进入受控执行。

### 用证据解释一次失败，而不只是展示红色状态

将 TestRun、TestResult、标准输出、错误日志、运行环境和 Artifact 关联到失败分析与报告，帮助测试人员判断是产品缺陷、环境问题还是自动化脚本问题。

### 在提交代码前评估本地变更风险

读取本地 Git diff，分析受影响范围，生成限定测试范围的 UnitTestPatch，运行新增测试与回归测试，并基于实际证据给出质量门禁结论。

## 产品界面

### 测试知识工作台：让项目经验参与生成，也接受人工治理

测试知识不是直接进入 Prompt 的原始文档。Chtest 将知识整理为可审查卡片，记录安全状态、来源、检索证据、覆盖关系和提供商降级情况。

![Chtest 测试知识库](docs/release/v1/screenshots/rag-knowledge-base.png)

<table>
  <tr>
    <td width="50%">
      <strong>CI/CD 质量中心</strong><br><br>
      从本地代码变更、风险分析、测试补丁到回归证据与质量门禁。<br><br>
      <img src="docs/release/v1/screenshots/cicd-quality-center.png" alt="Chtest CI/CD 质量中心">
    </td>
    <td width="50%">
      <strong>报告中心</strong><br><br>
      将测试结论与运行证据、失败分析和 Artifact 关联起来。<br><br>
      <img src="docs/release/v1/screenshots/report-center.png" alt="Chtest 报告中心">
    </td>
  </tr>
</table>

## 核心能力

| 工作域 | 核心能力 | 价值输出 |
| :--- | :--- | :--- |
| 需求与风险 | 需求审查、风险项、上下文引用 | 可解释的测试重点与风险清单 |
| 用例工程 | 候选生成、质量检查、覆盖缺口、人工评审、用例库 | 可维护、可追溯的正式测试资产 |
| 自动化工程 | pytest / Playwright 草稿、编辑、审批、执行 | 从用例到自动化的受控转化 |
| 多类型执行 | pytest、Playwright、Newman、JMeter 工作流 | 统一的运行记录与执行入口 |
| 证据与报告 | TestRun、TestResult、Artifact、失败分析、证据清单 | 可复核的测试结论 |
| 代码变更质量 | Git diff 风险、UnitTestPatch、回归执行、QualityGate | 面向本地变更的质量决策 |
| 测试知识 | 知识导入、卡片审查、混合检索、关系图、反馈闭环 | 可治理、可复用的项目测试经验 |
| AI 治理 | Prompt / Skill 版本、Schema 校验、模型记录、人工决策 | 可审计的 AI 使用过程 |

## 可信测试，不靠一句“AI 说通过了”

Chtest 把安全与可信控制放进工作流，而不是只写在使用说明里：

- AI 输出必须结构化并通过 Schema 校验。
- 未批准的候选用例不能进入正式用例库。
- 未批准的 AutomationDraft 不能执行。
- UnitTestPatch 不能修改业务源文件。
- 工具执行使用 allowlist，不接受任意 Shell 字符串。
- 报告缺少证据清单时，不能给出“测试通过”结论。
- 不安全、包含秘密或未获批准的知识不能参与最终生成。
- 每次关键晋级保留人工决策与状态转换记录。

V1 聚焦单用户、本地优先场景，不引入 RBAC、租户、企业协作、云 CI 平台或无审批的 AI 代码修改。

## 技术架构

| 层级 | 技术 |
| :--- | :--- |
| 前端 | Vue 3、TypeScript、Vite、Pinia、Vue Router、Arco Design Vue |
| 后端 | Python 3.12、FastAPI、Pydantic、SQLAlchemy、Alembic |
| 数据与队列 | PostgreSQL 16、pgvector（可选）、Redis 7 |
| 测试执行 | pytest、Playwright、Newman、JMeter |
| 工程与验证 | Docker Compose、Vitest、pytest、uv |

```text
frontend/       Vue 3 测试工作台
backend/        FastAPI API、领域服务、迁移与测试
worker/         后台任务与执行处理
deploy/         Docker Compose 本地开发环境
prompts/        版本化 Prompt 定义
skills/         版本化 AI Skill 定义
artifacts/      本地测试证据与运行产物
storage/        本地配置及开发数据
docs/           产品、契约、架构、实施与发布文档
memory/         AI 编码会话交接与项目连续性记录
```

## 快速开始

### 环境要求

- Git
- Docker Desktop 或 Docker Engine
- Docker Compose v2

### 1. 克隆并创建配置

```bash
git clone https://github.com/YanChen0111/Chtest.git
cd Chtest
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

默认配置使用内置 Mock LLM，无需 API Key 即可启动。接入真实模型时，在 `.env` 中配置 `LLM_PROVIDER`、`LLM_BASE_URL`、`LLM_API_KEY` 和 `LLM_MODEL`。

### 2. 启动工作台

```bash
docker compose --env-file .env -f deploy/docker-compose.yml up --build
```

### 3. 打开服务

- 前端工作台：<http://localhost:5173>
- 后端 API：<http://localhost:8000>
- API 文档：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/health>

后端容器启动时会自动执行 Alembic 数据库迁移。首次构建需要下载镜像和依赖，请等待服务健康检查完成。

停止服务：

```bash
docker compose --env-file .env -f deploy/docker-compose.yml down
```

## 验证项目

后端测试：

```powershell
backend\.venv\Scripts\python.exe -m pytest backend/app/tests -q
```

前端测试与生产构建：

```bash
npm --prefix frontend install
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

## 项目文档

- [文档导航](docs/README.md)
- [产品定位与范围](docs/product/01-positioning-and-scope.md)
- [V1 手动演示流程](docs/release/v1/manual-walkthrough.md)
- [V1 发布证据](docs/release/v1/README.md)
- [API 契约](docs/contracts/02-api-contract.md)
- [状态机契约](docs/contracts/03-state-machines.md)
- [Artifact 契约](docs/contracts/04-artifact-contract.md)

## 项目状态

Chtest 正在持续开发中。仓库已具备需求到用例、用例到自动化证据、代码变更质量门禁和测试知识治理等核心闭环。生产使用前，请独立评估部署安全、数据备份、执行隔离和模型提供商配置。

## 许可证

当前仓库尚未添加开源许可证。除非后续提供明确的 `LICENSE` 文件，否则请勿假定项目已授予开源使用、修改或分发许可。
