import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from app.api.routes.crud import router as api_router
from app.db.seed import seed_demo_data
from app.db.database import Base, DATABASE_URL, engine, is_dev_mode, is_sqlite_url

logger = logging.getLogger(__name__)


def _handle_sqlite_schema_mismatch(error: Exception) -> None:
    logger.debug("Startup database error", exc_info=error)
    raise RuntimeError(
        "SQLite schema mismatch detected. Please run:\n"
        "python reset_db.py\n"
        "Then restart: python -m uvicorn app.main:app --reload --port 8000"
    ) from error


def _ensure_sqlite_phase4_schema() -> None:
    """Apply additive SQLite-only dev columns so older local DBs keep starting."""
    if not (is_dev_mode() and is_sqlite_url(DATABASE_URL)):
        return
    inspector = inspect(engine)
    if "visits" not in inspector.get_table_names():
        return
    visit_columns = {column["name"] for column in inspector.get_columns("visits")}
    additions = {
        "recurrence_group_id": "ALTER TABLE visits ADD COLUMN recurrence_group_id VARCHAR(80)",
        "recurrence_rule": "ALTER TABLE visits ADD COLUMN recurrence_rule VARCHAR(40)",
        "recurrence_end_date": "ALTER TABLE visits ADD COLUMN recurrence_end_date DATE",
        "generated_from_recurring": "ALTER TABLE visits ADD COLUMN generated_from_recurring BOOLEAN DEFAULT 0",
    }
    with engine.begin() as conn:
        for column_name, statement in additions.items():
            if column_name not in visit_columns:
                conn.execute(text(statement))


def initialize_database():
    """
    Create schema on startup and seed demo data when needed.
    In local SQLite development, fail clearly on schema drift so developers can
    run the reset utility manually without startup reset side effects.
    """
    try:
        Base.metadata.create_all(bind=engine)
        _ensure_sqlite_phase4_schema()
        seed_demo_data()
    except OperationalError as exc:
        if is_dev_mode() and is_sqlite_url(DATABASE_URL):
            _handle_sqlite_schema_mismatch(exc)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title='Home Health MVP API', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(api_router, prefix='/api')


@app.get('/api/health')
def health_check():
    return {'status': 'ok'}
