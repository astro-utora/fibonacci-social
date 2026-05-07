from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path
from alembic.config import Config
from alembic import command
import logging
import sys

# Configure logging once at module level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_tables():
    Base.metadata.create_all(bind=engine)

def init_db():
    """Initialize database and run migrations"""
    try:
        logger.info("Initializing database...")
        
        # Create database connection
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            logger.info("Database connection successful")
        
        # Load Alembic configuration
        logger.info("Loading Alembic configuration...")
        alembic_cfg = Config("alembic.ini")
        
        # Run migrations
        logger.info("Running database migrations...")
        try:
            logger.info("Starting upgrade to head...")
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations completed successfully")
        except Exception as e:
            logger.error(f"Error during migrations: {e}", exc_info=True)
            raise
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        raise

# Dependency
def get_db():
    """Get database session"""
    with SessionLocal() as db:
        try:
            yield db
        finally:
            db.close() 