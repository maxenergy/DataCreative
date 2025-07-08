```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..core.config import settings # Get DATABASE_URL from settings

# Create a SQLAlchemy engine
# For SQLite, connect_args is needed to enable foreign key support if not enabled by default in some Python versions
engine_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False} # Required for SQLite with FastAPI

engine = create_engine(
    settings.DATABASE_URL, **engine_args
)

# Create a SessionLocal class. Instances of this class will be actual database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class. Our ORM models will inherit from this class.
Base = declarative_base()

# Dependency to get DB session in FastAPI path operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    """
    Creates all database tables defined by models inheriting from Base.
    This should be called once on application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        # Depending on the application, you might want to handle this more gracefully
        # or ensure the application doesn't start if DB setup fails.

if __name__ == "__main__":
    # For manual table creation or testing
    print(f"Creating database tables for URL: {settings.DATABASE_URL}")
    # Note: Models need to be imported for Base.metadata to be populated before calling create_all
    # from . import models # Assuming models.py is in the same directory or adjust import
    # create_db_and_tables()
    print("If you ran this directly, ensure your ORM models (e.g., in db/models.py) are imported before create_db_and_tables is called.")
```
