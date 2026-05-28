from datetime import date, datetime, time
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Caregiver, Client, IntakeRequest, Visit
from app.schemas.schemas import (
    CaregiverCreate,
    CaregiverUpdate,
    ClientCreate,
    ClientUpdate,
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
