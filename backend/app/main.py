import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


def initialize_database():
    """
    Create schema on startup and seed demo data when needed.
    In local SQLite development, fail clearly on schema drift so developers can
    run the reset utility manually without startup reset side effects.
    """
    try:
        Base.metadata.create_all(bind=engine)
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
