# flake8: noqa: E402

import os
import sys
from logging.config import fileConfig

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from alembic import context
from alembic.autogenerate import renderers
from pgvector.sqlalchemy import Vector
from sqlalchemy import engine_from_config, pool

from app.models.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# 1. Fix the renderer to add imports AND render correctly
@renderers.dispatch_for(Vector)
def render_vector(type_, autogen_context):
    """Render Vector type and ensure import is added."""
    # CRITICAL: Add import to autogen_context
    autogen_context.imports.add("import pgvector.sqlalchemy")

    # Render the Vector with dimension
    if hasattr(type_, "dim") and type_.dim is not None:
        return f"pgvector.sqlalchemy.Vector(dim={type_.dim})"
    return "pgvector.sqlalchemy.Vector()"


# 2. Process all revision directives to force import
def process_revision_directives(context, revision, directives):
    """Ensure pgvector import is always included."""
    if directives and len(directives) > 0:
        migration_script = directives[0]
        # Force add the import
        migration_script.imports.add("import pgvector.sqlalchemy")

        # Also check if any operations use Vector type
        for op in migration_script.upgrade_ops.ops:
            if hasattr(op, "columns"):
                for col in op.columns:
                    if hasattr(col, "type") and isinstance(col.type, Vector):
                        migration_script.imports.add("import pgvector.sqlalchemy")
                        break


# 3. Include Vector in type comparison
def include_object(object, name, type_, reflected, compare_to):
    """Include Vector types in comparison."""
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
        include_object=include_object,
        user_module_prefix="pgvector.sqlalchemy.",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            include_object=include_object,
            user_module_prefix="pgvector.sqlalchemy.",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
