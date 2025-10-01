from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
import sys
import os

# Add the backend root directory to sys.path so we can import the `app` package
backend_app_dir = os.path.dirname(os.path.dirname(__file__))
backend_root_dir = os.path.dirname(backend_app_dir)
if backend_root_dir not in sys.path:
    sys.path.insert(0, backend_root_dir)

# Ensure Alembic uses the same DATABASE_URL as the app settings
try:
    from app.core.settings import DATABASE_URL
    if DATABASE_URL:
        config.set_main_option("sqlalchemy.url", DATABASE_URL)
except Exception as e:
    # Fall back to alembic.ini if settings import fails
    pass

target_metadata = None

try:
    from app.core import models as core_models

    # Ensure brokerage/listing models reuse the core declarative base so relationships resolve
    import app.domain.listings as listings_package

    listings_package.Base = core_models.Base

    # Import modules that declare tables onto the shared Base
    from app.domain.listings import brokerage_models  # noqa: F401
    from app.domain.listings import enhanced_real_estate_models  # noqa: F401

    target_metadata = core_models.Base.metadata
except ImportError:
    target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
