import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from app.api.routes.admin_routes import router as admin_router
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.crud import router as api_router
from app.api.routes.file_routes import router as file_router
from app.core_config import get_settings
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


def _ensure_sqlite_phase5_schema() -> None:
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
    try:
        Base.metadata.create_all(bind=engine)
        _ensure_sqlite_phase5_schema()
        seed_demo_data()
    except OperationalError as exc:
        if is_dev_mode() and is_sqlite_url(DATABASE_URL):
            _handle_sqlite_schema_mismatch(exc)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


settings = get_settings()
app = FastAPI(title='Home Health MVP API', lifespan=lifespan, debug=not settings.is_production)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins or ["http://localhost:5173"], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])


@app.middleware("http")
async def security_headers_and_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled request error", extra={"request_id": request_id})
        if settings.is_production:
            return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id})
        raise
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


app.include_router(auth_router, prefix='/api')
app.include_router(admin_router, prefix='/api')
app.include_router(file_router, prefix='/api')
app.include_router(api_router, prefix='/api')


@app.get('/api/health')
def health_check():
    return {'status': 'ok'}
