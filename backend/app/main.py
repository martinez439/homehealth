import logging
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.api.routes.crud import router as api_router
from app.db.database import Base, DATABASE_URL, SessionLocal, engine, is_dev_mode, is_sqlite_url
from app.models.models import Caregiver, Client, IntakeRequest, Visit

logger = logging.getLogger(__name__)


def _handle_sqlite_schema_mismatch(error: Exception) -> None:
    logger.warning(
        "SQLite schema mismatch detected. Please run:\npython reset_db.py\n"
        "Then restart: uvicorn app.main:app --reload --port 8000"
    )
    logger.debug("Startup database error", exc_info=error)
    raise SystemExit(1)


def initialize_database():
    """
    Create schema on startup and seed demo data when needed.
    In local SQLite development, fail gracefully on schema drift so devs can
    run the reset utility manually without Windows file-lock crashes.
    """
    Base.metadata.create_all(bind=engine)
    try:
        seed_demo_data()
    except OperationalError as exc:
        if is_dev_mode() and is_sqlite_url(DATABASE_URL):
            _handle_sqlite_schema_mismatch(exc)
        raise


app = FastAPI(title='Home Health MVP API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(api_router, prefix='/api')


def seed_demo_data():
    db = SessionLocal()
    try:
        if db.query(Client).count() > 0:
            return

        clients = [
            Client(first_name='Jane', last_name='Doe', phone='555-2010', address='14 Harbor Lane', city='San Diego', state='CA', zip_code='92101', care_level='Personal Care', status='active'),
            Client(first_name='Michael', last_name='Roe', phone='555-2011', address='9 Elm Street', city='San Diego', state='CA', zip_code='92102', care_level='Skilled Nursing', status='active'),
        ]
        caregivers = [
            Caregiver(first_name='Alex', last_name='Kim', phone='555-3010', email='alex@example.com', certification='RN', status='on_shift'),
            Caregiver(first_name='Sam', last_name='Lee', phone='555-3011', email='sam@example.com', certification='CNA', status='available'),
        ]
        intake = IntakeRequest(client_name='Ava Patel', phone='555-9090', city='La Jolla', care_needs='Post-surgery support', preferred_schedule='Weekday mornings', urgency='high', status='new')

        db.add_all(clients + caregivers + [intake])
        db.flush()

        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        visits = [
            Visit(client_id=clients[0].id, caregiver_id=caregivers[0].id, scheduled_start=now + timedelta(hours=1), scheduled_end=now + timedelta(hours=3), status='scheduled', service_type='Companion Care'),
            Visit(client_id=clients[1].id, caregiver_id=caregivers[1].id, scheduled_start=now - timedelta(hours=2), scheduled_end=now - timedelta(hours=1), status='completed', service_type='Skilled Nursing'),
        ]
        db.add_all(visits)
        db.commit()
    finally:
        db.close()


initialize_database()


@app.get('/api/health')
def health_check():
    return {'status': 'ok'}
