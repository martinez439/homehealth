from datetime import datetime, time, timedelta
import json

from app.db.database import SessionLocal
from app.models.models import Caregiver, CaregiverAvailability, Client, FamilyContact, FamilyMessage, IntakeRequest, Visit


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


        if caregivers and db.query(CaregiverAvailability).count() == 0:
            availability_rows = []
            for caregiver in caregivers:
                for day in range(7):
                    is_weekday = day < 5
                    availability_rows.append(CaregiverAvailability(
                        caregiver_id=caregiver.id,
                        day_of_week=day,
                        available=is_weekday,
                        start_time=time(8, 0) if is_weekday else None,
                        end_time=time(17, 0) if is_weekday else None,
                        notes='Concierge daytime care window' if is_weekday else 'Unavailable for routine visits',
                    ))
            db.add_all(availability_rows)

        if db.query(Visit).count() == 0 and clients and caregivers:
            now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            tasks = json.dumps([
                {"label": "Meal preparation", "completed": True},
                {"label": "Medication reminder", "completed": True},
                {"label": "Mobility assistance", "completed": True},
                {"label": "Light housekeeping", "completed": False},
                {"label": "Companionship", "completed": True},
            ])
            pending_tasks = json.dumps([
                {"label": "Meal preparation", "completed": False},
                {"label": "Medication reminder", "completed": False},
                {"label": "Mobility assistance", "completed": False},
                {"label": "Light housekeeping", "completed": False},
                {"label": "Companionship", "completed": False},
            ])
            jane = clients[0]
            michael = clients[min(1, len(clients)-1)]
            alex = caregivers[0]
            sam = caregivers[min(1, len(caregivers)-1)]
            db.add_all([
                Visit(client_id=jane.id, caregiver_id=alex.id, scheduled_start=now + timedelta(hours=1), scheduled_end=now + timedelta(hours=3), status='scheduled', service_type='Companion Care', task_checklist=pending_tasks),
                Visit(client_id=jane.id, caregiver_id=alex.id, scheduled_start=now - timedelta(days=1, hours=2), scheduled_end=now - timedelta(days=1), status='completed', service_type='Personal Care', checked_in_at=now - timedelta(days=1, hours=2), checked_out_at=now - timedelta(days=1), task_checklist=tasks, caregiver_notes='Jane enjoyed breakfast, completed her medication reminder, and was in good spirits during companionship time.'),
                Visit(client_id=michael.id, caregiver_id=sam.id, scheduled_start=now - timedelta(hours=2), scheduled_end=now - timedelta(hours=1), status='completed', service_type='Skilled Nursing', checked_in_at=now - timedelta(hours=2), checked_out_at=now - timedelta(hours=1), task_checklist=tasks, caregiver_notes='Vitals were stable and the care plan was followed. Michael reported feeling comfortable after the visit.'),
                Visit(client_id=michael.id, caregiver_id=sam.id, scheduled_start=now + timedelta(days=1, hours=2), scheduled_end=now + timedelta(days=1, hours=4), status='scheduled', service_type='Skilled Nursing', task_checklist=pending_tasks),
            ])



        clients = db.query(Client).order_by(Client.id.asc()).all()
        caregivers = db.query(Caregiver).order_by(Caregiver.id.asc()).all()
        if clients and caregivers and db.query(Visit).filter(Visit.recurrence_group_id.isnot(None)).count() == 0:
            now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            weekday_offset = (7 - now.weekday()) % 7
            first_start = (now + timedelta(days=weekday_offset)).replace(hour=9)
            first_end = first_start + timedelta(hours=2)
            recurrence_group = 'demo-weekly-concierge-care'
            recurring_visits = []
            for week in range(4):
                recurring_visits.append(Visit(
                    client_id=clients[0].id,
                    caregiver_id=caregivers[0].id,
                    scheduled_start=first_start + timedelta(weeks=week),
                    scheduled_end=first_end + timedelta(weeks=week),
                    status='scheduled',
                    service_type='Recurring Companion Care',
                    notes='Auto-generated recurring demo visit.',
                    recurrence_group_id=recurrence_group,
                    recurrence_rule='weekly',
                    recurrence_end_date=(first_start + timedelta(weeks=3)).date(),
                    generated_from_recurring=week > 0,
                ))
            db.add_all(recurring_visits)

        if len(clients) > 1 and caregivers and not any(v.service_type == 'Conflict Test Visit' for v in db.query(Visit).all()):
            now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            conflict_start = (now + timedelta(days=(7 - now.weekday()) % 7)).replace(hour=10)
            db.add(Visit(
                client_id=clients[1].id,
                caregiver_id=caregivers[0].id,
                scheduled_start=conflict_start,
                scheduled_end=conflict_start + timedelta(hours=2),
                status='scheduled',
                service_type='Conflict Test Visit',
                notes='Seeded overlap for Phase 4 conflict detection testing.',
            ))

        clients = db.query(Client).order_by(Client.id.asc()).all()
        if clients and db.query(FamilyContact).count() == 0:
            contacts = []
            for client in clients:
                contacts.extend([
                    FamilyContact(client_id=client.id, first_name='Emily', last_name=client.last_name, relationship='Daughter', phone='555-4100', email=f'emily.{client.last_name.lower()}@example.com', is_primary=True, receives_updates=True),
                    FamilyContact(client_id=client.id, first_name='David', last_name=client.last_name, relationship='Son', phone='555-4101', email=f'david.{client.last_name.lower()}@example.com', is_primary=False, receives_updates=True),
                ])
            db.add_all(contacts)

        if clients and db.query(FamilyMessage).count() == 0:
            messages = []
            for client in clients:
                messages.append(FamilyMessage(
                    client_id=client.id,
                    sender_name=f'Emily {client.last_name}',
                    sender_email=f'emily.{client.last_name.lower()}@example.com',
                    message_type='care_update_request',
                    subject='Weekly care update',
                    message='Could you please include any changes in appetite or mood in the next update?',
                    status='reviewed',
                ))
            db.add_all(messages)

        db.commit()
    finally:
        db.close()
