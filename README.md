<div align="center">

# Chtest

**面向测试工程师的本地优先 AI 测试证据工作台**

将需求与本地代码变更转化为可人工审查、受控执行、证据可追溯、质量可度量的测试资产。

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3-42B883?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

[功能概览](#核心能力) · [界面预览](#界面预览) · [快速开始](#快速开始) · [项目文档](#项目文档)

</div>

## 项目简介

Chtest V1 服务于个人测试工程师与自动化测试工程师。它不只是生成测试用例，而是围绕一条完整的测试证据闭环组织 AI 分析、人工审批、自动化执行、失败诊断和报告输出。

```text
需求或本地代码变更
  -> AI 风险与测试分析
  -> 人工审查的测试用例或测试补丁
  -> 审批后的自动化草稿
  -> 受控测试执行
  -> 运行产物与证据
  -> 失败分析或修复候选
  -> 证据报告与 AI 质量度量
```

项目坚持四项产品原则：

- **本地优先**：项目上下文、测试资产和执行证据由本地工作台管理。
- **人工把关**：AI 只生成候选、草稿和分析，关键晋级与执行必须经过人工审查。
- **证据驱动**：测试结论关联运行记录、产物、上下文来源和模型调用信息。
- **可替换 AI**：模型与知识检索能力通过适配层接入，不把核心工作流绑定到单一提供商。

## 界面预览

### AI 工作台

集中查看 AI 任务、模型连接、上下文使用和结构化输出。

![Chtest AI 工作台](docs/release/v1/screenshots/ai-workbench.png)

### 测试知识库

管理可审查的测试知识卡片、检索证据、覆盖关系和提供商状态。

![Chtest 测试知识库](docs/release/v1/screenshots/rag-knowledge-base.png)

<table>
  <tr>
    <td width="50%">
      <strong>CI/CD 质量中心</strong><br><br>
      <img src="docs/release/v1/screenshots/cicd-quality-center.png" alt="Chtest CI/CD 质量中心">
    </td>
    <td width="50%">
      <strong>报告中心</strong><br><br>
      <img src="docs/release/v1/screenshots/report-center.png" alt="Chtest 报告中心">
    </td>
  </tr>
</table>

## 核心能力

| 能力 | 说明 |
| :--- | :--- |
| 需求审查 | 对需求进行结构化分析、风险识别，并记录使用的上下文与 AI 任务证据 |
| 测试用例生成 | 基于需求、风险与测试知识生成候选用例，经过编辑、批准后进入用例库 |
| 自动化草稿 | 从已审查用例生成 pytest / Playwright 自动化草稿，执行前强制人工审批 |
| 多类型执行 | 提供 pytest、Playwright、Newman 与 JMeter 工作流及最近运行记录 |
| 失败分析与报告 | 将运行结果、日志和 Artifact 组织为可追溯的失败分析与证据报告 |
| CI/CD 质量中心 | 分析本地 Git diff，审查限定范围的单元测试补丁并产出质量门禁结论 |
| 测试知识 RAG | 导入并审查测试知识卡片，执行混合检索、覆盖分析与证据链查询 |
| AI 治理 | 记录 Prompt、Skill、模型、输入输出 Artifact、Schema 校验和人工决策 |

## 技术栈

| 层级 | 技术 |
| :--- | :--- |
| 前端 | Vue 3、TypeScript、Vite、Pinia、Vue Router、Arco Design Vue |
| 后端 | Python 3.12、FastAPI、Pydantic、SQLAlchemy、Alembic |
| 数据与队列 | PostgreSQL 16、pgvector（可选）、Redis 7 |
| 测试执行 | pytest、Playwright、Newman、JMeter |
| 工程化 | Docker Compose、Vitest、uv |

## 系统结构

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

### 1. 克隆仓库

```bash
git clone https://github.com/YanChen0111/Chtest.git
cd Chtest
```

### 2. 创建本地配置

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

默认配置使用内置 Mock LLM，无需 API Key 即可启动。接入真实模型时，再在 `.env` 中设置 `LLM_PROVIDER`、`LLM_BASE_URL`、`LLM_API_KEY` 和 `LLM_MODEL`。

### 3. 启动工作台

```bash
docker compose --env-file .env -f deploy/docker-compose.yml up --build
```

### 4. 打开服务

- 前端工作台：<http://localhost:5173>
- 后端 API：<http://localhost:8000>
- API 文档：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/health>

后端容器启动时会自动执行 Alembic 数据库迁移。首次构建需要下载镜像和依赖，请等待各服务健康检查完成。

停止服务：

```bash
docker compose --env-file .env -f deploy/docker-compose.yml down
```

## 本地开发与验证

### 后端

```powershell
backend\.venv\Scripts\python.exe -m pytest backend/app/tests -q
```

### 前端

```bash
npm --prefix frontend install
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

## 安全边界

Chtest 将 AI 输出视为待审查内容，而不是可信指令：

- 未批准的生成用例不能进入正式用例库。
- 未批准的 AutomationDraft 不能执行。
- UnitTestPatch 不能修改业务源文件。
- 工具执行使用 allowlist，不接受任意 Shell 字符串。
- 报告没有关联证据时不能宣称测试通过。
- 密钥、凭据和不安全知识不得进入 Prompt 上下文。

V1 是单用户、本地优先工作台，不包含 RBAC、租户、企业协作、云 CI 平台或无审批的 AI 代码修改。

## 项目文档

- [文档导航](docs/README.md)
- [产品定位与范围](docs/product/01-positioning-and-scope.md)
- [V1 手动演示流程](docs/release/v1/manual-walkthrough.md)
- [V1 发布证据](docs/release/v1/README.md)
- [API 契约](docs/contracts/02-api-contract.md)
- [状态机契约](docs/contracts/03-state-machines.md)
- [Artifact 契约](docs/contracts/04-artifact-contract.md)

## 项目状态

Chtest 正在持续开发中。仓库已经具备完整的 V1 证据闭环和自动化验收基础，后续功能仍可能调整；生产使用前请独立评估部署、安全、数据备份和模型提供商配置。

## 许可证

当前仓库尚未添加开源许可证。除非后续提供明确的 `LICENSE` 文件，否则请勿假定项目已授予开源使用、修改或分发许可。
