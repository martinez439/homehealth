"""Development utility to reset the local SQLite database."""

from app.db.database import Base, DATABASE_URL, SessionLocal, engine
from app.db.seed import seed_demo_data
from app.models import models  # noqa: F401 - ensures model metadata is imported


def _is_local_sqlite_database(url: str) -> bool:
    return url.startswith("sqlite:///") and ":memory:" not in url


def _sqlite_db_path(url: str) -> str:
    return url.replace("sqlite:///", "", 1)


def reset_sqlite_db() -> None:
    if not _is_local_sqlite_database(DATABASE_URL):
        raise RuntimeError("reset_db.py is intended for local SQLite development databases only.")

    db_path = _sqlite_db_path(DATABASE_URL)

    session = SessionLocal()
    try:
        session.close()
    except Exception:
        pass

    import os

    if os.path.exists(db_path):
        os.remove(db_path)

    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    print("Local SQLite database reset complete.")


if __name__ == "__main__":
    reset_sqlite_db()
