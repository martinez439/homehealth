from datetime import datetime, timedelta
import json

from app.db.database import SessionLocal
from app.models.models import Caregiver, Client, IntakeRequest, Visit


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        if db.query(Client).count() == 0:
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

        clients = db.query(Client).order_by(Client.id.asc()).all()
        caregivers = db.query(Caregiver).order_by(Caregiver.id.asc()).all()
        if db.query(Visit).count() == 0 and clients and caregivers:
            now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            tasks = json.dumps([
                {"label": "Meal preparation", "completed": False},
                {"label": "Medication reminder", "completed": False},
                {"label": "Mobility assistance", "completed": False},
                {"label": "Light housekeeping", "completed": False},
                {"label": "Companionship", "completed": False},
            ])
            db.add_all([
                Visit(client_id=clients[0].id, caregiver_id=caregivers[0].id, scheduled_start=now + timedelta(hours=1), scheduled_end=now + timedelta(hours=3), status='scheduled', service_type='Companion Care', task_checklist=tasks),
                Visit(client_id=clients[min(1, len(clients)-1)].id, caregiver_id=caregivers[min(1, len(caregivers)-1)].id, scheduled_start=now - timedelta(hours=2), scheduled_end=now - timedelta(hours=1), status='completed', service_type='Skilled Nursing', checked_in_at=now - timedelta(hours=2), checked_out_at=now - timedelta(hours=1), task_checklist=tasks),
            ])
        db.commit()
    finally:
        db.close()
