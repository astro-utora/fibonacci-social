import os
import sys
from logging.config import fileConfig
import logging
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger('alembic.env')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.database import SQLALCHEMY_DATABASE_URL

# Load environment variables
load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    logger.info("Running offline migrations")
    url = SQLALCHEMY_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
    logger.info("Offline migrations completed")

def run_migrations_online():
    """Run migrations in 'online' mode."""
    try:
        logger.info("Starting online migrations")
        configuration = config.get_section(config.config_ini_section)
        configuration["sqlalchemy.url"] = SQLALCHEMY_DATABASE_URL
        
        logger.info("Creating database engine")
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            logger.info("Configuring migration context")
            context.configure(
                connection=connection, 
                target_metadata=target_metadata,
                compare_type=True
            )

            logger.info("Running migrations")
            with context.begin_transaction():
                context.run_migrations()
                logger.info("Transaction completed")
            logger.info("Migrations completed successfully")

    except Exception as e:
        logger.error(f"Error during migration: {e}", exc_info=True)
        raise

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
