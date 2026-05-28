import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./homehealth.db"


def is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite")


def is_dev_mode() -> bool:
    env = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development")).lower()
    return env in {"dev", "development", "local"}


def sqlite_db_path(url: str) -> Path | None:
    if not url.startswith("sqlite:///"):
        return None
    return Path(url.replace("sqlite:///", "", 1)).resolve()

engine_kwargs = {}
if is_sqlite_url(DATABASE_URL):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
