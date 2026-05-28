from datetime import date, datetime, time
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Caregiver, Client, FamilyContact, FamilyMessage, IntakeRequest, Visit
from app.schemas.schemas import (
    CaregiverCreate,
    CaregiverUpdate,
    ClientCreate,
    ClientUpdate,
    FamilyContactCreate,
    FamilyContactUpdate,
    FamilyMessageCreate,
    IntakeCreate,
    IntakeUpdate,
    VisitCreate,
    VisitUpdate,
)

router = APIRouter()


def get_or_404(db: Session, model, obj_id: int):
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    today = date.today()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)

    recent = db.query(Visit).order_by(Visit.updated_at.desc()).limit(5).all()
    recent_activity = [
        {
            "id": v.id,
            "type": "visit",
            "message": f"Visit #{v.id} is {v.status.replace('_', ' ')}",
            "updated_at": v.updated_at.isoformat(),
        }
        for v in recent
    ]

    return {
        "active_clients_count": db.query(Client).filter(Client.status == "active").count(),
        "visits_today_count": db.query(Visit).filter(Visit.scheduled_start >= start, Visit.scheduled_start <= end).count(),
        "caregivers_on_shift_count": db.query(Caregiver).filter(Caregiver.status.in_(["on_shift", "available"])) .count(),
        "intake_requests_count": db.query(IntakeRequest).count(),
        "pending_visits_count": db.query(Visit).filter(Visit.status == "scheduled").count(),
        "completed_visits_count": db.query(Visit).filter(Visit.status == "completed").count(),
        "missed_visits_count": db.query(Visit).filter(Visit.status == "missed").count(),
        "recent_activity": recent_activity,
    }


@router.get('/clients')
def list_clients(db: Session = Depends(get_db)):
    return db.query(Client).order_by(Client.last_name.asc()).all()


@router.post('/clients')
def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    obj = Client(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.get('/clients/{id}')
def get_client(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Client, id)


@router.put('/clients/{id}')
def update_client(id: int, payload: ClientUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Client, id)
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    db.commit(); db.refresh(obj)
    return obj


@router.delete('/clients/{id}')
def delete_client(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, Client, id)
    db.delete(obj); db.commit()
    return {"ok": True}


@router.get('/caregivers')
def list_caregivers(db: Session = Depends(get_db)):
    return db.query(Caregiver).order_by(Caregiver.last_name.asc()).all()


@router.post('/caregivers')
def create_caregiver(payload: CaregiverCreate, db: Session = Depends(get_db)):
    obj = Caregiver(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.get('/caregivers/{id}')
def get_caregiver(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Caregiver, id)


@router.put('/caregivers/{id}')
def update_caregiver(id: int, payload: CaregiverUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Caregiver, id)
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    db.commit(); db.refresh(obj)
    return obj


@router.delete('/caregivers/{id}')
def delete_caregiver(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, Caregiver, id)
    db.delete(obj); db.commit()
    return {"ok": True}


@router.get('/intake')
def list_intake(db: Session = Depends(get_db)):
    return db.query(IntakeRequest).order_by(IntakeRequest.created_at.desc()).all()


@router.post('/intake')
def create_intake(payload: IntakeCreate, db: Session = Depends(get_db)):
    obj = IntakeRequest(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.put('/intake/{id}')
def update_intake(id: int, payload: IntakeUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, IntakeRequest, id)
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    db.commit(); db.refresh(obj)
    return obj


@router.get('/visits')
def list_visits(db: Session = Depends(get_db)):
    return db.query(Visit).order_by(Visit.scheduled_start.asc()).all()


@router.post('/visits')
def create_visit(payload: VisitCreate, db: Session = Depends(get_db)):
    obj = Visit(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.get('/visits/{id}')
def get_visit(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Visit, id)


@router.put('/visits/{id}')
def update_visit(id: int, payload: VisitUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Visit, id)
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    db.commit(); db.refresh(obj)
    return obj


@router.delete('/visits/{id}')
def delete_visit(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, Visit, id)
    db.delete(obj); db.commit()
    return {"ok": True}


DEFAULT_TASK_CHECKLIST = [
    {"label": "Meal preparation", "completed": False},
    {"label": "Medication reminder", "completed": False},
    {"label": "Mobility assistance", "completed": False},
    {"label": "Light housekeeping", "completed": False},
    {"label": "Companionship", "completed": False},
]


def _parse_checklist(raw: str):
    try:
        parsed = json.loads(raw or '[]')
        return parsed if isinstance(parsed, list) else DEFAULT_TASK_CHECKLIST
    except json.JSONDecodeError:
        return DEFAULT_TASK_CHECKLIST


def _visit_payload(db: Session, visit: Visit):
    client = db.get(Client, visit.client_id)
    caregiver = db.get(Caregiver, visit.caregiver_id)
    return {
        "id": visit.id,
        "client_id": visit.client_id,
        "caregiver_id": visit.caregiver_id,
        "client_name": f"{client.first_name} {client.last_name}" if client else "Unknown Client",
        "caregiver_name": f"{caregiver.first_name} {caregiver.last_name}" if caregiver else "Unknown Caregiver",
        "scheduled_start": visit.scheduled_start.isoformat(),
        "scheduled_end": visit.scheduled_end.isoformat(),
        "status": visit.status,
        "service_type": visit.service_type,
        "address": client.address if client else "",
        "city": client.city if client else "",
        "checked_in_at": visit.checked_in_at.isoformat() if visit.checked_in_at else None,
        "checked_out_at": visit.checked_out_at.isoformat() if visit.checked_out_at else None,
        "check_in_location": visit.check_in_location,
        "check_out_location": visit.check_out_location,
        "mileage_start": visit.mileage_start,
        "mileage_end": visit.mileage_end,
        "mileage_total": visit.mileage_total,
        "task_checklist": _parse_checklist(visit.task_checklist),
        "caregiver_notes": visit.caregiver_notes,
        "missed_alert_sent": visit.missed_alert_sent,
    }


@router.get('/caregiver/visits')
def caregiver_visits(caregiver_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Visit).order_by(Visit.scheduled_start.asc())
    if caregiver_id:
        query = query.filter(Visit.caregiver_id == caregiver_id)
    visits = query.all()
    return [_visit_payload(db, v) for v in visits]


@router.get('/caregiver/visits/{visit_id}')
def caregiver_visit_detail(visit_id: int, db: Session = Depends(get_db)):
    visit = get_or_404(db, Visit, visit_id)
    return _visit_payload(db, visit)


@router.post('/caregiver/visits/{visit_id}/check-in')
def caregiver_check_in(visit_id: int, payload: dict, db: Session = Depends(get_db)):
    visit = get_or_404(db, Visit, visit_id)
    if visit.status != 'scheduled':
        raise HTTPException(status_code=400, detail='Visit cannot be checked in from current status')
    visit.checked_in_at = datetime.utcnow()
    visit.status = 'in_progress'
    visit.check_in_location = payload.get('location')
    db.commit(); db.refresh(visit)
    return _visit_payload(db, visit)


@router.post('/caregiver/visits/{visit_id}/check-out')
def caregiver_check_out(visit_id: int, payload: dict, db: Session = Depends(get_db)):
    visit = get_or_404(db, Visit, visit_id)
    if not visit.checked_in_at:
        raise HTTPException(status_code=400, detail='Visit must be checked in before checking out')
    visit.checked_out_at = datetime.utcnow()
    visit.status = 'completed'
    visit.check_out_location = payload.get('location')
    if visit.mileage_start is not None and visit.mileage_end is not None:
        visit.mileage_total = max(0, visit.mileage_end - visit.mileage_start)
    db.commit(); db.refresh(visit)
    return _visit_payload(db, visit)


@router.post('/caregiver/visits/{visit_id}/notes')
def caregiver_notes(visit_id: int, payload: dict, db: Session = Depends(get_db)):
    visit = get_or_404(db, Visit, visit_id)
    visit.caregiver_notes = payload.get('caregiver_notes', '')
    db.commit(); db.refresh(visit)
    return _visit_payload(db, visit)


@router.put('/caregiver/visits/{visit_id}/tasks')
def caregiver_tasks(visit_id: int, payload: dict, db: Session = Depends(get_db)):
    visit = get_or_404(db, Visit, visit_id)
    tasks = payload.get('task_checklist', DEFAULT_TASK_CHECKLIST)
    visit.task_checklist = json.dumps(tasks)
    db.commit(); db.refresh(visit)
    return _visit_payload(db, visit)


@router.put('/caregiver/visits/{visit_id}/mileage')
def caregiver_mileage(visit_id: int, payload: dict, db: Session = Depends(get_db)):
    visit = get_or_404(db, Visit, visit_id)
    visit.mileage_start = payload.get('mileage_start')
    visit.mileage_end = payload.get('mileage_end')
    if visit.mileage_start is not None and visit.mileage_end is not None:
        visit.mileage_total = max(0, visit.mileage_end - visit.mileage_start)
    db.commit(); db.refresh(visit)
    return _visit_payload(db, visit)


@router.get('/caregiver/alerts/missed-check-ins')
def missed_checkins(caregiver_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Visit).filter(Visit.status == 'scheduled', Visit.scheduled_start < datetime.utcnow(), Visit.checked_in_at.is_(None))
    if caregiver_id:
        query = query.filter(Visit.caregiver_id == caregiver_id)
    visits = query.all()
    return {"count": len(visits), "visits": [_visit_payload(db, v) for v in visits]}


def _ensure_client(db: Session, client_id: int) -> Client:
    return get_or_404(db, Client, client_id)


def _family_client_payload(db: Session, client: Client):
    latest_visit = db.query(Visit).filter(Visit.client_id == client.id).order_by(Visit.updated_at.desc()).first()
    latest_message = db.query(FamilyMessage).filter(FamilyMessage.client_id == client.id).order_by(FamilyMessage.updated_at.desc()).first()
    latest_contact = db.query(FamilyContact).filter(FamilyContact.client_id == client.id).order_by(FamilyContact.updated_at.desc()).first()
    timestamps = [client.updated_at]
    if latest_visit:
        timestamps.append(latest_visit.updated_at)
    if latest_message:
        timestamps.append(latest_message.updated_at)
    if latest_contact:
        timestamps.append(latest_contact.updated_at)
    last_updated = max(timestamps)
    return {
        "id": client.id,
        "first_name": client.first_name,
        "last_name": client.last_name,
        "full_name": f"{client.first_name} {client.last_name}",
        "care_level": client.care_level,
        "status": client.status,
        "address": client.address,
        "city": client.city,
        "state": client.state,
        "last_updated": last_updated.isoformat(),
    }


@router.get('/family/client/{client_id}')
def family_client(client_id: int, db: Session = Depends(get_db)):
    client = _ensure_client(db, client_id)
    return _family_client_payload(db, client)


@router.get('/family/client/{client_id}/visits/upcoming')
def family_upcoming_visits(client_id: int, db: Session = Depends(get_db)):
    _ensure_client(db, client_id)
    visits = (
        db.query(Visit)
        .filter(Visit.client_id == client_id, Visit.status.in_(['scheduled', 'in_progress']))
        .order_by(Visit.scheduled_start.asc())
        .limit(10)
        .all()
    )
    return [_visit_payload(db, visit) for visit in visits]


@router.get('/family/client/{client_id}/visits/completed')
def family_completed_visits(client_id: int, db: Session = Depends(get_db)):
    _ensure_client(db, client_id)
    visits = (
        db.query(Visit)
        .filter(Visit.client_id == client_id, Visit.status == 'completed')
        .order_by(Visit.scheduled_start.desc())
        .limit(10)
        .all()
    )
    return [_visit_payload(db, visit) for visit in visits]


@router.get('/family/client/{client_id}/notes')
def family_notes(client_id: int, db: Session = Depends(get_db)):
    _ensure_client(db, client_id)
    visits = (
        db.query(Visit)
        .filter(Visit.client_id == client_id, Visit.caregiver_notes != '')
        .order_by(Visit.updated_at.desc())
        .limit(20)
        .all()
    )
    notes = []
    for visit in visits:
        caregiver = db.get(Caregiver, visit.caregiver_id)
        notes.append({
            "id": visit.id,
            "visit_id": visit.id,
            "caregiver_name": f"{caregiver.first_name} {caregiver.last_name}" if caregiver else "Care team",
            "note": visit.caregiver_notes,
            "service_type": visit.service_type,
            "timestamp": (visit.checked_out_at or visit.updated_at).isoformat(),
        })
    return notes


@router.get('/family/client/{client_id}/contacts')
def family_contacts(client_id: int, db: Session = Depends(get_db)):
    _ensure_client(db, client_id)
    return db.query(FamilyContact).filter(FamilyContact.client_id == client_id).order_by(FamilyContact.is_primary.desc(), FamilyContact.last_name.asc()).all()


@router.post('/family/client/{client_id}/contacts')
def create_family_contact(client_id: int, payload: FamilyContactCreate, db: Session = Depends(get_db)):
    _ensure_client(db, client_id)
    contact = FamilyContact(client_id=client_id, **payload.model_dump())
    if contact.is_primary:
        db.query(FamilyContact).filter(FamilyContact.client_id == client_id).update({FamilyContact.is_primary: False})
    db.add(contact); db.commit(); db.refresh(contact)
    return contact


@router.put('/family/contacts/{contact_id}')
def update_family_contact(contact_id: int, payload: FamilyContactUpdate, db: Session = Depends(get_db)):
    contact = get_or_404(db, FamilyContact, contact_id)
    data = payload.model_dump()
    if data.get('is_primary'):
        db.query(FamilyContact).filter(FamilyContact.client_id == contact.client_id, FamilyContact.id != contact.id).update({FamilyContact.is_primary: False})
    for key, value in data.items():
        setattr(contact, key, value)
    db.commit(); db.refresh(contact)
    return contact


@router.delete('/family/contacts/{contact_id}')
def delete_family_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = get_or_404(db, FamilyContact, contact_id)
    db.delete(contact); db.commit()
    return {"ok": True}


@router.get('/family/client/{client_id}/messages')
def family_messages(client_id: int, db: Session = Depends(get_db)):
    _ensure_client(db, client_id)
    return db.query(FamilyMessage).filter(FamilyMessage.client_id == client_id).order_by(FamilyMessage.created_at.desc()).all()


@router.post('/family/client/{client_id}/messages')
def create_family_message(client_id: int, payload: FamilyMessageCreate, db: Session = Depends(get_db)):
    _ensure_client(db, client_id)
    message = FamilyMessage(client_id=client_id, status='new', **payload.model_dump())
    db.add(message); db.commit(); db.refresh(message)
    return message


def _timeline_item(item_id: str, item_type: str, title: str, description: str, timestamp: datetime):
    return {
        "id": item_id,
        "type": item_type,
        "title": title,
        "description": description,
        "timestamp": timestamp.isoformat(),
    }


@router.get('/family/client/{client_id}/timeline')
def family_timeline(client_id: int, db: Session = Depends(get_db)):
    _ensure_client(db, client_id)
    items = []
    visits = db.query(Visit).filter(Visit.client_id == client_id).order_by(Visit.updated_at.desc()).limit(20).all()
    for visit in visits:
        caregiver = db.get(Caregiver, visit.caregiver_id)
        caregiver_name = f"{caregiver.first_name} {caregiver.last_name}" if caregiver else "Care team"
        if visit.status == 'completed':
            items.append(_timeline_item(
                f"visit-{visit.id}",
                "completed_visit",
                "Visit completed",
                f"{caregiver_name} completed {visit.service_type or 'a care visit'}.",
                visit.checked_out_at or visit.updated_at,
            ))
        if visit.checked_in_at:
            items.append(_timeline_item(
                f"check-in-{visit.id}",
                "check_in",
                "Caregiver checked in",
                f"{caregiver_name} arrived for {visit.service_type or 'care'}.",
                visit.checked_in_at,
            ))
        if visit.checked_out_at:
            items.append(_timeline_item(
                f"check-out-{visit.id}",
                "check_out",
                "Caregiver checked out",
                f"{caregiver_name} finished the visit.",
                visit.checked_out_at,
            ))
        if visit.caregiver_notes:
            items.append(_timeline_item(
                f"note-{visit.id}",
                "care_note",
                "Care note added",
                visit.caregiver_notes,
                visit.updated_at,
            ))

    messages = db.query(FamilyMessage).filter(FamilyMessage.client_id == client_id).order_by(FamilyMessage.created_at.desc()).limit(10).all()
    for message in messages:
        items.append(_timeline_item(
            f"message-{message.id}",
            "family_message",
            "Family message received",
            f"{message.sender_name}: {message.subject}",
            message.created_at,
        ))

    contacts = db.query(FamilyContact).filter(FamilyContact.client_id == client_id).order_by(FamilyContact.updated_at.desc()).limit(5).all()
    for contact in contacts:
        items.append(_timeline_item(
            f"contact-{contact.id}",
            "contact_update",
            "Family contact updated",
            f"{contact.first_name} {contact.last_name} is listed as {contact.relationship or 'a family contact'}.",
            contact.updated_at,
        ))

    items.sort(key=lambda item: item["timestamp"], reverse=True)
    return items[:25]
