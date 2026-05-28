"""Development utility to reset the local SQLite database."""

from app.db.database import Base, DATABASE_URL, engine, is_sqlite_url, sqlite_db_path
from app.main import seed_demo_data


def reset_sqlite_db() -> None:
    if not is_sqlite_url(DATABASE_URL):
        raise RuntimeError("reset_db.py is intended for SQLite development databases only.")

    db_path = sqlite_db_path(DATABASE_URL)
    if db_path and db_path.exists():
        db_path.unlink()
        print(f"Deleted database file: {db_path}")
    else:
        print("No existing SQLite database file found. Creating a new one.")

    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    print("Database reset complete. Tables recreated and demo data seeded.")


if __name__ == "__main__":
    reset_sqlite_db()
