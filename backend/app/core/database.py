from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine for Supabase PostgreSQL
engine = create_engine(
    settings.supabase_url.replace("rest", "postgres"),
    # Add connection pooling for better performance
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes
    echo=settings.debug,  # Log SQL queries in debug mode
    connect_args={
        "sslmode": "require" if "supabase.co" in settings.supabase_url else "prefer"
    }
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

def get_db() -> Session:
    """
    Dependency to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all tables defined in models.
    This should be called during application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def check_database_connection():
    """
    Check if the database connection is working properly.
    Returns True if connection is successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Health check function for the database
async def get_database_health():
    """
    Get database health status for monitoring.
    """
    try:
        with SessionLocal() as db:
            # Simple query to check database connectivity
            db.execute("SELECT 1")
            return {
                "status": "healthy",
                "database": "connected",
                "engine": "postgresql"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": "disconnected"
        }
