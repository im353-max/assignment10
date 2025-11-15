import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from .config import settings

Base = declarative_base()

def get_engine(database_url: str | None = None):
    """
    Create the engine dynamically so tests can override the DB.
    """
    # If provided, tests override the DB
    if database_url is not None:
        return create_engine(database_url)

    # Detect pytest (works locally AND in GitHub Actions)
    if "PYTEST_CURRENT_TEST" in os.environ or os.getenv("TESTING") == "1":
        return create_engine("postgresql://postgres:postgres@localhost:5432/test_db")

    # Default production engine
    return create_engine(settings.DATABASE_URL)


def get_sessionmaker(engine=None):
    """
    Create a SQLAlchemy sessionmaker.
    If `engine` is provided, use it; otherwise, use default engine.
    """
    from .config import settings
    from sqlalchemy import create_engine

    if engine is None:
        engine = create_engine(settings.DATABASE_URL)

    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


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