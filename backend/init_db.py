import os
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command

def init_database():
    # Load environment variables
    load_dotenv()
    
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    try:
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("Database initialization completed successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_database() 