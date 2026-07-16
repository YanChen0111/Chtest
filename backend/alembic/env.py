from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from backend.app.models.base import Base

# Import modules for autogenerate metadata discovery.
from backend.app.modules.ai_runtime import models as _ai_runtime_models  # noqa: F401
from backend.app.modules.automation import models as _automation_models  # noqa: F401
from backend.app.modules.cases import models as _cases_models  # noqa: F401
from backend.app.modules.cicd import models as _cicd_models  # noqa: F401
from backend.app.modules.execution import models as _execution_models  # noqa: F401
from backend.app.modules.extension import models as _extension_models  # noqa: F401
from backend.app.modules.knowledge import models as _knowledge_models  # noqa: F401
from backend.app.modules.projects import models as _projects_models  # noqa: F401
from backend.app.modules.prompt_skill import models as _prompt_skill_models  # noqa: F401
from backend.app.modules.reporting import models as _reporting_models  # noqa: F401
from backend.app.modules.requirements import models as _requirements_models  # noqa: F401
from backend.app.modules.review_history import models as _review_history_models  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def database_url() -> str:
    return os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
