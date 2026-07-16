FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY backend/pyproject.toml backend/uv.lock /app/backend/

RUN python -m pip install --no-cache-dir uv \
    && cd /app/backend \
    && uv sync --frozen --no-dev

COPY backend /app/backend
COPY prompts /app/prompts
COPY skills /app/skills

EXPOSE 8000

CMD ["/bin/sh", "-c", "/app/backend/.venv/bin/python -m alembic -c /app/backend/alembic.ini upgrade head && exec /app/backend/.venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]
