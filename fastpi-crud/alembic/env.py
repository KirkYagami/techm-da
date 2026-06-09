# alembic/env.py  (replace the auto-generated content)

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Load .env
load_dotenv()

# This is the Alembic config object — provides .ini file values
config = context.config

# Set the database URL from environment (overrides alembic.ini)
config.set_main_option(
    "sqlalchemy.url",
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# *** CRITICAL: Import your Base so Alembic can see all models ***
# This is how Alembic knows what tables/columns exist
from app.database import Base
from app import models  # noqa: F401 — import needed to register models with Base

target_metadata = Base.metadata  # Alembic compares this against the live DB


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (just outputs SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against live DB."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't pool during migrations
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()