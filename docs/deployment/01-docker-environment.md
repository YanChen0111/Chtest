# Docker Environment Design

## 1. 目标

第一版开发、测试和本地运行都使用 Docker Compose 控制环境。目标是让后续 AI 和开发者能用固定命令启动 PostgreSQL、Redis、backend、worker、frontend，避免本机环境差异。

## 2. 服务清单

| Service | Image/Build | Port | 说明 |
|---|---|---:|---|
| postgres | postgres:16 | 5432 | 主数据库 |
| redis | redis:7 | 6379 | 队列和缓存 |
| backend | build ./backend | 8000 | FastAPI API |
| worker | build ./backend | none | RQ/Celery worker |
| frontend | build ./frontend | 5173 | Vue dev server |
| runner | optional profile | none | 后续隔离执行测试 |

## 3. 目录挂载

```text
./storage:/app/storage
./prompts:/app/prompts:ro
./skills:/app/skills:ro
./mcp_tools:/app/mcp_tools:ro
./backend:/app/backend
./frontend:/app/frontend
```

## 4. 环境变量

```text
APP_ENV=dev
DATABASE_URL=postgresql+psycopg://chtest:chtest@postgres:5432/chtest
REDIS_URL=redis://redis:6379/0
ARTIFACT_ROOT=/app/storage
DEFAULT_USER_ID=default-user
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
TOOL_EXECUTION_MODE=local
```

## 5. docker-compose 设计

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: chtest
      POSTGRES_USER: chtest
      POSTGRES_PASSWORD: chtest
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chtest -d chtest"]
      interval: 5s
      timeout: 3s
      retries: 20

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 20

  backend:
    build: ./backend
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - ./storage:/app/storage
      - ./prompts:/app/prompts:ro
      - ./skills:/app/skills:ro

  worker:
    build: ./backend
    command: python -m app.worker
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./storage:/app/storage
      - ./prompts:/app/prompts:ro
      - ./skills:/app/skills:ro

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_BASE_URL: http://localhost:8000

volumes:
  postgres-data:
```

## 6. 启动命令

```bash
cp .env.example .env
docker compose up -d postgres redis
docker compose up backend worker frontend
```

## 7. 健康检查

- Backend: `GET /health` 返回服务状态。
- Ready: `GET /ready` 检查 Postgres、Redis、artifact root。
- Worker: 后端创建 ping 任务，worker 消费后写回结果。

## 8. 环境分层

| 环境 | 用途 | 配置 |
|---|---|---|
| dev | 本地开发 | 热更新、详细日志、mock LLM 可选 |
| test | 自动化测试 | 独立 DB、短 timeout、mock 工具 |
| local-prod | 本机稳定运行 | 关闭热更新、保留日志和 artifact |

## 9. 安全要求

- `.env` 不提交。
- `storage/` 不提交。
- 工具执行目录必须在项目工作区内。
- 禁止容器挂载宿主机敏感目录。
- LLM/GitHub/Postman token 只通过 env 注入。
