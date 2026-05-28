import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./homehealth.db"


def is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite")


def is_dev_mode() -> bool:
    env = os.getenv("APP_ENV", "development").lower()
    return env in {"dev", "development", "local"}


def sqlite_db_path(url: str) -> Path | None:
    if not url.startswith("sqlite:///"):
        return None
    return Path(url.replace("sqlite:///", "", 1)).resolve()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_sqlite_db_file(url: str) -> bool:
    """
    Development helper: remove the local SQLite DB file so schema can be recreated
    from current SQLAlchemy models. This intentionally only runs for SQLite + dev mode.
    """
    if not (is_dev_mode() and is_sqlite_url(url)):
        return False

    db_path = sqlite_db_path(url)
    if not db_path or not db_path.exists():
        return False

    db_path.unlink()
    return True
