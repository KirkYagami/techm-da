# app/database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------------------
# 1. BUILD THE DATABASE URL
# Format: dialect+driver://user:password@host:port/database
# ------------------------------------------------------------------
DATABASE_URL = (
    f"mysql+pymysql://"              # dialect=mysql, driver=pymysql
    f"{os.getenv('DB_USER')}:"       # username
    f"{os.getenv('DB_PASSWORD')}@"   # password
    f"{os.getenv('DB_HOST')}:"       # host (e.g., localhost)
    f"{os.getenv('DB_PORT')}/"       # port (default 3306)
    f"{os.getenv('DB_NAME')}"        # database name
)

# ------------------------------------------------------------------
# 2. CREATE THE ENGINE
# The Engine is the starting point for all SQLAlchemy operations.
# It manages the raw connection to the database.
# ------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    
    # --- Connection Pool Settings (explained in Section 6) ---
    pool_size=10,           # Max persistent connections in the pool
    max_overflow=20,        # Extra connections allowed beyond pool_size
    pool_timeout=30,        # Seconds to wait for a connection before error
    pool_recycle=1800,      # Recycle connections every 30 min (avoids stale conns)
    pool_pre_ping=True,     # Test connection health before using it
    
    echo=False,             # Set True to print all SQL queries (for debugging)
)

# ------------------------------------------------------------------
# 3. CREATE A SESSION FACTORY
# SessionLocal is a class. Each call to SessionLocal() creates a NEW
# database session — a "unit of work" for a single request.
# ------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,   # We manage commits manually (important for txn control)
    autoflush=False,    # Don't auto-flush to DB before every query
    bind=engine         # Attach this factory to our engine
)

# ------------------------------------------------------------------
# 4. CREATE THE DECLARATIVE BASE
# All ORM models inherit from this Base.
# Base keeps track of all models registered with it.
# ------------------------------------------------------------------
Base = declarative_base()

# ------------------------------------------------------------------
# 5. DEPENDENCY — get_db()
# This is a FastAPI dependency that provides a DB session per request.
# The `yield` makes it a context manager — the session is ALWAYS closed
# after the request, even if an exception occurs.
# ------------------------------------------------------------------
def get_db():
    db = SessionLocal()   # Open a session
    try:
        yield db          # Give the session to the route function
    finally:
        db.close()        # Always close, even on errors (returns conn to pool)