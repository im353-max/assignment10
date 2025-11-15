import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from .config import settings

Base = declarative_base()

def get_engine():
    """
    Create the engine dynamically so tests can override the DB.
    """
    # Detect pytest (works locally AND in GitHub Actions)
    if "PYTEST_CURRENT_TEST" in os.environ or os.getenv("TESTING") == "1":
        database_url = "sqlite:///:memory:"
    else:
        database_url = settings.DATABASE_URL

    try:
        return create_engine(database_url, echo=False)
    except SQLAlchemyError as e:
        print(f"Error creating engine: {e}")
        raise


def get_sessionmaker():
    """
    Return a new sessionmaker bound to a dynamically created engine.
    """
    engine = get_engine()
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )


def get_db():
    """
    Dependency that provides a DB session.
    """
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# 👇 NEW: Global engine + SessionLocal required by tests
# ---------------------------------------------------------

engine = get_engine()
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)