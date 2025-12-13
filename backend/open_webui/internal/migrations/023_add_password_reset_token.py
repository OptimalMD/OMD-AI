"""Peewee migrations -- 023_add_password_reset_token.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['table_name']            # Return model in current state by name
    > Model = migrator.ModelClass                   # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.run(func, *args, **kwargs)           # Run python function with the given args
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.add_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)
    > migrator.add_constraint(model, name, sql)
    > migrator.drop_index(model, *col_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.drop_constraints(model, *constraints)

"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Add password_reset_token table for password reset functionality."""
    
    migrator.sql(
        """
        CREATE TABLE IF NOT EXISTS password_reset_token (
            token VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            expires_at BIGINT NOT NULL,
            used BOOLEAN DEFAULT 0,
            created_at BIGINT NOT NULL
        );
        """
    )
    
    # Add index on user_id for faster lookups
    with suppress(Exception):
        migrator.sql(
            "CREATE INDEX IF NOT EXISTS idx_password_reset_token_user_id ON password_reset_token(user_id);"
        )
    
    # Add index on expires_at for cleanup tasks
    with suppress(Exception):
        migrator.sql(
            "CREATE INDEX IF NOT EXISTS idx_password_reset_token_expires_at ON password_reset_token(expires_at);"
        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Rollback the migration."""
    
    migrator.sql("DROP TABLE IF EXISTS password_reset_token;")
