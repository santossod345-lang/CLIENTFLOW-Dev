"""
Production initialization script
Runs before the web server starts to ensure database migrations and setup
"""
import os
import sys
import time
import logging
from pathlib import Path
from sqlalchemy import create_engine, text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_prod")

def get_database_url():
    """Get database URL from environment"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        return None
    # Normalize for SQLAlchemy (some providers still expose postgres://)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    return db_url

def validate_database_connection(db_url, max_retries=5):
    """Validate database connection with exponential backoff"""
    engine = create_engine(db_url)
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4, 8, 16 seconds
                logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Database connection failed after {max_retries} attempts: {e}")
                return False
    
    return False

def run_alembic_migrations():
    """Run Alembic migrations"""
    try:
        import subprocess
        logger.info("Running Alembic migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd="/app" if os.path.exists("/app") else os.getcwd(),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            logger.info("✓ Migrations completed successfully")
            return True
        else:
            logger.error(f"Migrations failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False

def create_upload_directories():
    """Create required upload directories"""
    try:
        upload_dirs = [
            Path("/app/uploads") if os.path.exists("/app") else Path("./uploads"),
            Path("/app/uploads/logos") if os.path.exists("/app") else Path("./uploads/logos"),
        ]
        
        for dir_path in upload_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("✓ Upload directories created")
        return True
    except Exception as e:
        logger.error(f"Error creating upload directories: {e}")
        return False

def main():
    """Main initialization routine"""
    logger.info("Starting production initialization...")
    
    # Step 1: Get database URL
    db_url = get_database_url()
    if not db_url:
        logger.error("Cannot proceed without database URL")
        sys.exit(1)
    
    # Step 2: Validate database connection
    logger.info("Validating database connection...")
    if not validate_database_connection(db_url):
        logger.error("Cannot proceed without database connection")
        sys.exit(1)
    
    # Step 3: Run migrations
    logger.info("Running database migrations...")
    if not run_alembic_migrations():
        logger.warning("Migrations had issues, but continuing...")
    
    # Step 4: Create directories
    if not create_upload_directories():
        logger.warning("Could not create upload directories, but continuing...")
    
    logger.info("✓ Production initialization completed successfully")
    sys.exit(0)

if __name__ == "__main__":
    main()
