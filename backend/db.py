# backend/db.py
"""
Database configuration with connection pooling and session management
"""
import os
import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# Database URL (try both environment variable names)
DB_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
USE_CSV = os.getenv("USE_CSV_FALLBACK", "false").lower() in ("1", "true", "yes")
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

# Database engine configuration
if not USE_CSV:
    if not DB_URL:
        raise RuntimeError(
            "DATABASE_URL or DB_URL must be set in .env when USE_CSV_FALLBACK=false"
        )
    
    logger.info(f"🔗 Connecting to database...")
    
    # Create engine with connection pooling
    engine = create_engine(
        DB_URL,
        echo=False,  # Set to True for SQL query logging
        future=True,
        poolclass=QueuePool,
        pool_size=10,  # Number of persistent connections
        max_overflow=20,  # Additional connections during peak load
        pool_timeout=30,  # Seconds to wait for available connection
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_pre_ping=True,  # Verify connection health before using
    )
    
    # Session factory
    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False  # Keep objects accessible after commit
    )
    
    # Event listeners for debugging
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        logger.debug("✅ Database connection established")
    
    @event.listens_for(engine, "close")
    def receive_close(dbapi_conn, connection_record):
        logger.debug("🔌 Database connection closed")
    
    logger.info("✅ Database engine configured successfully")
    
else:
    logger.warning("⚠️ CSV fallback mode - database features disabled")
    engine = None
    SessionLocal = None

# Base class for models
Base = declarative_base()
# Metadata is accessible via Base.metadata

def get_db_session():
    """
    Dependency function for FastAPI endpoints
    Yields a database session and ensures cleanup
    """
    if USE_CSV:
        raise RuntimeError("Database not available in CSV mode")
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database - create all tables"""
    if USE_CSV:
        logger.warning("⚠️ Cannot initialize database in CSV mode")
        return
    
    logger.info("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")

def check_db_connection():
    """Check if database connection is working"""
    if USE_CSV:
        return False

    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        logger.info("✅ Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False
    finally:
        db.close()