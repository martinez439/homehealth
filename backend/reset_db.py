"""Development utility to reset the local SQLite database."""

from pathlib import Path

from app.db.database import DATABASE_URL, engine, Base, SessionLocal
from app.models import models  # noqa: F401 - ensures model metadata is imported
from app.db.seed import seed_demo_data


def _is_local_sqlite_database(url: str) -> bool:
    return url.startswith("sqlite:///") and ":memory:" not in url


def _sqlite_db_path(url: str) -> Path:
    return Path(url.replace("sqlite:///", "", 1)).resolve()


def reset_sqlite_db() -> None:
    if not _is_local_sqlite_database(DATABASE_URL):
        raise RuntimeError("reset_db.py is intended for local SQLite development databases only.")

    db_path = _sqlite_db_path(DATABASE_URL)

    # Keep SessionLocal imported here intentionally so this utility only depends
    # on database primitives, model metadata, and the explicit seed function.
    _ = SessionLocal

    engine.dispose()

    if db_path.exists():
        db_path.unlink()

    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    print("Local SQLite database reset complete.")


if __name__ == "__main__":
    reset_sqlite_db()
