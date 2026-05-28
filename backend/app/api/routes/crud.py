from datetime import date, datetime, time, timedelta
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Caregiver, CaregiverAvailability, Client, FamilyContact, FamilyMessage, IntakeRequest, User, Visit
from app.audit import write_audit_log
from app.auth import require_admin, require_caregiver_or_admin, require_family_or_admin
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
    VisitMove,
    VisitUpdate,
    RecurringVisitCreate,
    CaregiverAvailabilityCreate,
    CaregiverAvailabilityUpdate,
)

router = APIRouter()


def get_or_404(db: Session, model, obj_id: int):
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj


def _ensure_family_client_access(current_user: User, client_id: int) -> None:
    if current_user.role == "family" and current_user.client_id != client_id:
        raise HTTPException(status_code=403, detail="Forbidden")


def _ensure_caregiver_visit_access(current_user: User, visit: Visit) -> None:
    if current_user.role == "caregiver" and current_user.caregiver_id != visit.caregiver_id:
        raise HTTPException(status_code=403, detail="Forbidden")


def _client_name(db: Session, client_id: int) -> str:
    client = db.get(Client, client_id)
    return f"{client.first_name} {client.last_name}" if client else "Unknown Client"


def _caregiver_name(db: Session, caregiver_id: int) -> str:
    caregiver = db.get(Caregiver, caregiver_id)
    return f"{caregiver.first_name} {caregiver.last_name}" if caregiver else "Unassigned Caregiver"


def _calendar_visit_payload(db: Session, visit: Visit, conflicts: list[dict] | None = None):
    visit_conflicts = [c for c in (conflicts or []) if visit.id in c.get("visit_ids", [])]
    return {
        "id": visit.id,
        "client_id": visit.client_id,
        "caregiver_id": visit.caregiver_id,
        "client_name": _client_name(db, visit.client_id),
        "caregiver_name": _caregiver_name(db, visit.caregiver_id),
        "scheduled_start": visit.scheduled_start.isoformat(),
        "scheduled_end": visit.scheduled_end.isoformat(),
        "status": visit.status,
        "service_type": visit.service_type,
        "notes": visit.notes,
        "recurrence_group_id": visit.recurrence_group_id,
        "recurrence_rule": visit.recurrence_rule,
        "recurrence_end_date": visit.recurrence_end_date.isoformat() if visit.recurrence_end_date else None,
        "generated_from_recurring": visit.generated_from_recurring,
        "has_conflict": bool(visit_conflicts),
        "conflicts": visit_conflicts,
    }


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def _availability_conflict(db: Session, visit: Visit):
    availability = (
        db.query(CaregiverAvailability)
        .filter(
            CaregiverAvailability.caregiver_id == visit.caregiver_id,
            CaregiverAvailability.day_of_week == visit.scheduled_start.weekday(),
        )
        .first()
    )
    if not availability:
        return {
            "type": "outside_availability",
            "severity": "warning",
            "visit_ids": [visit.id],
            "message": f"{_caregiver_name(db, visit.caregiver_id)} has no availability configured for this day.",
        }
    if not availability.available:
        return {
            "type": "outside_availability",
            "severity": "severe",
            "visit_ids": [visit.id],
            "message": f"{_caregiver_name(db, visit.caregiver_id)} is marked unavailable for this day.",
        }
    if availability.start_time and availability.end_time:
        start_t = visit.scheduled_start.time()
        end_t = visit.scheduled_end.time()
        if start_t < availability.start_time or end_t > availability.end_time:
            return {
                "type": "outside_availability",
                "severity": "severe",
                "visit_ids": [visit.id],
                "message": f"Visit for {_client_name(db, visit.client_id)} falls outside {_caregiver_name(db, visit.caregiver_id)}'s availability window.",
            }
    return None


def _detect_conflicts(db: Session, start: datetime | None = None, end: datetime | None = None, visit: Visit | None = None):
    query = db.query(Visit)
    if visit:
        visits = [visit]
    else:
        if start:
            query = query.filter(Visit.scheduled_end >= start)
        if end:
            query = query.filter(Visit.scheduled_start <= end)
        visits = query.order_by(Visit.scheduled_start.asc()).all()

    conflicts = []
    seen_pairs = set()
    all_for_overlap = db.query(Visit).order_by(Visit.scheduled_start.asc()).all() if visit else visits
    for current in visits:
        if current.scheduled_end <= current.scheduled_start:
            conflicts.append({
                "type": "invalid_time",
                "severity": "severe",
                "visit_ids": [current.id],
                "message": f"Visit #{current.id} ends before it starts.",
            })
        availability = _availability_conflict(db, current)
        if availability:
            conflicts.append(availability)
        overlaps = [candidate for candidate in all_for_overlap if candidate.id != current.id and candidate.caregiver_id == current.caregiver_id and _overlaps(current.scheduled_start, current.scheduled_end, candidate.scheduled_start, candidate.scheduled_end)]
        for other in overlaps:
            pair = tuple(sorted([current.id, other.id]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            conflicts.append({
                "type": "double_booking",
                "severity": "severe",
                "visit_ids": list(pair),
                "message": f"{_caregiver_name(db, current.caregiver_id)} is double-booked for visits #{pair[0]} and #{pair[1]}.",
            })
    return conflicts


def _assert_no_severe_conflicts(db: Session, visit: Visit):
    conflicts = _detect_conflicts(db, visit=visit)
    severe = [c for c in conflicts if c["severity"] == "severe"]
    if severe:
        raise HTTPException(status_code=409, detail={"message": "Severe scheduling conflict detected", "conflicts": severe})


def _copy_visit_fields(visit: Visit, data: dict):
    for key, value in data.items():
        setattr(visit, key, value)


def _recurrence_delta(rule: str):
    if rule == "daily":
        return timedelta(days=1)
    if rule == "weekly":
        return timedelta(weeks=1)
    if rule == "biweekly":
        return timedelta(weeks=2)
    return None


def _add_month(dt: datetime) -> datetime:
    month = dt.month + 1
    year = dt.year + (month - 1) // 12
    month = ((month - 1) % 12) + 1
    days = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return dt.replace(year=year, month=month, day=min(dt.day, days[month - 1]))


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
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
def list_clients(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(Client).order_by(Client.last_name.asc()).all()


@router.post('/clients')
def create_client(payload: ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = Client(**payload.model_dump())
    db.add(obj); db.flush()
    write_audit_log(db, action='client_created', entity_type='client', entity_id=obj.id, description='Client created', user=current_user)
    db.commit(); db.refresh(obj)
    return obj


@router.get('/clients/{id}')
def get_client(id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return get_or_404(db, Client, id)


@router.put('/clients/{id}')
def update_client(id: int, payload: ClientUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, Client, id)
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    write_audit_log(db, action='client_updated', entity_type='client', entity_id=obj.id, description='Client updated', user=current_user)
    db.commit(); db.refresh(obj)
    return obj


@router.delete('/clients/{id}')
def delete_client(id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, Client, id)
    write_audit_log(db, action='client_deleted', entity_type='client', entity_id=obj.id, description='Client deleted', user=current_user)
    db.delete(obj); db.commit()
    return {"ok": True}


@router.get('/caregivers')
def list_caregivers(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(Caregiver).order_by(Caregiver.last_name.asc()).all()


@router.post('/caregivers')
def create_caregiver(payload: CaregiverCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = Caregiver(**payload.model_dump())
    db.add(obj); db.flush()
    write_audit_log(db, action='caregiver_created', entity_type='caregiver', entity_id=obj.id, description='Caregiver created', user=current_user)
    db.commit(); db.refresh(obj)
    return obj


@router.get('/caregivers/{id}')
def get_caregiver(id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return get_or_404(db, Caregiver, id)


@router.put('/caregivers/{id}')
def update_caregiver(id: int, payload: CaregiverUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, Caregiver, id)
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    write_audit_log(db, action='caregiver_updated', entity_type='caregiver', entity_id=obj.id, description='Caregiver updated', user=current_user)
    db.commit(); db.refresh(obj)
    return obj


@router.delete('/caregivers/{id}')
def delete_caregiver(id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, Caregiver, id)
    write_audit_log(db, action='caregiver_deleted', entity_type='caregiver', entity_id=obj.id, description='Caregiver deleted', user=current_user)
    db.delete(obj); db.commit()
    return {"ok": True}


@router.get('/caregivers/{caregiver_id}/availability')
def caregiver_availability(caregiver_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    get_or_404(db, Caregiver, caregiver_id)
    return db.query(CaregiverAvailability).filter(CaregiverAvailability.caregiver_id == caregiver_id).order_by(CaregiverAvailability.day_of_week.asc()).all()


@router.post('/caregivers/{caregiver_id}/availability')
def create_caregiver_availability(caregiver_id: int, payload: CaregiverAvailabilityCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    get_or_404(db, Caregiver, caregiver_id)
    if payload.start_time and payload.end_time and payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail='Availability end time must be after start time')
    obj = CaregiverAvailability(caregiver_id=caregiver_id, **payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.put('/caregivers/availability/{availability_id}')
def update_caregiver_availability(availability_id: int, payload: CaregiverAvailabilityUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, CaregiverAvailability, availability_id)
    if payload.start_time and payload.end_time and payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail='Availability end time must be after start time')
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    db.commit(); db.refresh(obj)
    return obj


@router.delete('/caregivers/availability/{availability_id}')
def delete_caregiver_availability(availability_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, CaregiverAvailability, availability_id)
    db.delete(obj); db.commit()
    return {"ok": True}


@router.get('/intake')
def list_intake(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(IntakeRequest).order_by(IntakeRequest.created_at.desc()).all()


@router.post('/intake')
def create_intake(payload: IntakeCreate, db: Session = Depends(get_db)):
    obj = IntakeRequest(**payload.model_dump())
    db.add(obj); db.flush()
    write_audit_log(db, action='intake_created', entity_type='intake_request', entity_id=obj.id, description='Intake request created')
    db.commit(); db.refresh(obj)
    return obj


@router.put('/intake/{id}')
def update_intake(id: int, payload: IntakeUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, IntakeRequest, id)
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    write_audit_log(db, action='intake_updated', entity_type='intake_request', entity_id=obj.id, description='Intake request updated', user=current_user)
    db.commit(); db.refresh(obj)
    return obj


@router.get('/visits')
def list_visits(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(Visit).order_by(Visit.scheduled_start.asc()).all()


@router.post('/visits')
def create_visit(payload: VisitCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = Visit(**payload.model_dump())
    db.add(obj); db.flush()
    write_audit_log(db, action='visit_created', entity_type='visit', entity_id=obj.id, description='Visit created', user=current_user)
    db.commit(); db.refresh(obj)
    return obj


@router.get('/visits/{id}')
def get_visit(id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return get_or_404(db, Visit, id)


@router.put('/visits/{id}')
def update_visit(id: int, payload: VisitUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, Visit, id)
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    write_audit_log(db, action='visit_updated', entity_type='visit', entity_id=obj.id, description='Visit updated', user=current_user)
    db.commit(); db.refresh(obj)
    return obj


@router.delete('/visits/{id}')
def delete_visit(id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, Visit, id)
    write_audit_log(db, action='visit_deleted', entity_type='visit', entity_id=obj.id, description='Visit deleted', user=current_user)
    db.delete(obj); db.commit()
    return {"ok": True}


@router.get('/schedule/calendar')
def schedule_calendar(start: datetime | None = Query(default=None), end: datetime | None = Query(default=None), caregiver_id: int | None = None, client_id: int | None = None, status: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    query = db.query(Visit)
    if start:
        query = query.filter(Visit.scheduled_end >= start)
    if end:
        query = query.filter(Visit.scheduled_start <= end)
    if caregiver_id:
        query = query.filter(Visit.caregiver_id == caregiver_id)
    if client_id:
        query = query.filter(Visit.client_id == client_id)
    if status:
        query = query.filter(Visit.status == status)
    visits = query.order_by(Visit.scheduled_start.asc()).all()
    conflicts = _detect_conflicts(db, start=start, end=end)
    return [_calendar_visit_payload(db, visit, conflicts) for visit in visits]


@router.post('/schedule/visits')
def schedule_create_visit(payload: VisitCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = Visit(**payload.model_dump())
    db.add(obj); db.flush()
    _assert_no_severe_conflicts(db, obj)
    db.commit(); db.refresh(obj)
    return _calendar_visit_payload(db, obj, _detect_conflicts(db, visit=obj))


@router.put('/schedule/visits/{visit_id}')
def schedule_update_visit(visit_id: int, payload: VisitUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, Visit, visit_id)
    _copy_visit_fields(obj, payload.model_dump())
    db.flush()
    _assert_no_severe_conflicts(db, obj)
    db.commit(); db.refresh(obj)
    return _calendar_visit_payload(db, obj, _detect_conflicts(db, visit=obj))


@router.delete('/schedule/visits/{visit_id}')
def schedule_delete_visit(visit_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, Visit, visit_id)
    db.delete(obj); db.commit()
    return {"ok": True}


@router.post('/schedule/visits/{visit_id}/move')
def schedule_move_visit(visit_id: int, payload: VisitMove, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    obj = get_or_404(db, Visit, visit_id)
    old_start, old_end = obj.scheduled_start, obj.scheduled_end
    obj.scheduled_start = payload.scheduled_start
    obj.scheduled_end = payload.scheduled_end
    db.flush()
    try:
        _assert_no_severe_conflicts(db, obj)
    except HTTPException:
        obj.scheduled_start = old_start
        obj.scheduled_end = old_end
        db.rollback()
        raise
    db.commit(); db.refresh(obj)
    return _calendar_visit_payload(db, obj, _detect_conflicts(db, visit=obj))


@router.post('/schedule/recurring')
def schedule_create_recurring(payload: RecurringVisitCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if payload.scheduled_end <= payload.scheduled_start:
        raise HTTPException(status_code=400, detail='Visit end time must be after start time')
    if payload.recurrence_end_date < payload.scheduled_start.date():
        raise HTTPException(status_code=400, detail='Recurrence end date must be after the first visit')
    group_id = str(uuid.uuid4())
    visits = []
    current_start = payload.scheduled_start
    current_end = payload.scheduled_end
    delta = _recurrence_delta(payload.recurrence_rule)
    index = 0
    while current_start.date() <= payload.recurrence_end_date and len(visits) < 370:
        data = payload.model_dump()
        data.update({
            "scheduled_start": current_start,
            "scheduled_end": current_end,
            "recurrence_group_id": group_id,
            "generated_from_recurring": index > 0,
        })
        visit = Visit(**data)
        db.add(visit); db.flush()
        _assert_no_severe_conflicts(db, visit)
        visits.append(visit)
        index += 1
        if payload.recurrence_rule == "monthly":
            current_start = _add_month(current_start)
            current_end = _add_month(current_end)
        else:
            current_start = current_start + delta
            current_end = current_end + delta
    db.commit()
    return [_calendar_visit_payload(db, visit, _detect_conflicts(db, visit=visit)) for visit in visits]


@router.get('/schedule/conflicts')
def schedule_conflicts(start: datetime | None = Query(default=None), end: datetime | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return _detect_conflicts(db, start=start, end=end)


@router.get('/schedule/daily-summary')
def schedule_daily_summary(day: date | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    target = day or date.today()
    start = datetime.combine(target, time.min)
    end = datetime.combine(target, time.max)
    visits = db.query(Visit).filter(Visit.scheduled_start >= start, Visit.scheduled_start <= end).order_by(Visit.scheduled_start.asc()).all()
    conflicts = _detect_conflicts(db, start=start, end=end)
    upcoming = [v for v in visits if v.scheduled_start >= datetime.utcnow() and v.status in ['scheduled', 'in_progress']][:5]
    caregiver_ids = {v.caregiver_id for v in visits}
    return {
        "date": target.isoformat(),
        "total_visits": len(visits),
        "completed_visits": len([v for v in visits if v.status == 'completed']),
        "missed_visits": len([v for v in visits if v.status == 'missed']),
        "caregivers_on_shift": len(caregiver_ids),
        "upcoming_visits": [_calendar_visit_payload(db, v, conflicts) for v in upcoming],
        "unresolved_conflicts": conflicts,
    }


@router.get('/schedule/upcoming-reminders')
def schedule_upcoming_reminders(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    now = datetime.utcnow()
    reminders = []
    upcoming = db.query(Visit).filter(Visit.status == 'scheduled', Visit.scheduled_start >= now, Visit.scheduled_start <= now + timedelta(hours=2)).order_by(Visit.scheduled_start.asc()).all()
    for visit in upcoming:
        minutes = max(0, int((visit.scheduled_start - now).total_seconds() // 60))
        reminders.append({
            "type": "upcoming_visit",
            "visit_id": visit.id,
            "message": f"Visit for {_client_name(db, visit.client_id)} starts in {minutes} minutes.",
        })
    overdue = db.query(Visit).filter(Visit.status == 'scheduled', Visit.scheduled_start < now, Visit.scheduled_end >= now).order_by(Visit.scheduled_start.asc()).all()
    for visit in overdue:
        reminders.append({
            "type": "overdue_check_in",
            "visit_id": visit.id,
            "message": f"{_caregiver_name(db, visit.caregiver_id)} has not checked in for {_client_name(db, visit.client_id)}.",
        })
    missed = db.query(Visit).filter(Visit.status == 'scheduled', Visit.scheduled_end < now).order_by(Visit.scheduled_end.asc()).limit(10).all()
    for visit in missed:
        reminders.append({
            "type": "missed_visit",
            "visit_id": visit.id,
            "message": f"Visit for {_client_name(db, visit.client_id)} is past its scheduled end time.",
        })
    return reminders


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
def caregiver_visits(caregiver_id: int | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(require_caregiver_or_admin)):
    query = db.query(Visit).order_by(Visit.scheduled_start.asc())
    if current_user.role == 'caregiver':
        if current_user.caregiver_id is None:
            return []
        caregiver_id = current_user.caregiver_id
    if caregiver_id:
        query = query.filter(Visit.caregiver_id == caregiver_id)
    visits = query.all()
    return [_visit_payload(db, v) for v in visits]


@router.get('/caregiver/visits/{visit_id}')
def caregiver_visit_detail(visit_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_caregiver_or_admin)):
    visit = get_or_404(db, Visit, visit_id)
    _ensure_caregiver_visit_access(current_user, visit)
    return _visit_payload(db, visit)


@router.post('/caregiver/visits/{visit_id}/check-in')
def caregiver_check_in(visit_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(require_caregiver_or_admin)):
    visit = get_or_404(db, Visit, visit_id)
    _ensure_caregiver_visit_access(current_user, visit)
    if visit.status != 'scheduled':
        raise HTTPException(status_code=400, detail='Visit cannot be checked in from current status')
    visit.checked_in_at = datetime.utcnow()
    visit.status = 'in_progress'
    visit.check_in_location = payload.get('location')
    write_audit_log(db, action='visit_check_in', entity_type='visit', entity_id=visit.id, description='Caregiver checked in', user=current_user)
    db.commit(); db.refresh(visit)
    return _visit_payload(db, visit)


@router.post('/caregiver/visits/{visit_id}/check-out')
def caregiver_check_out(visit_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(require_caregiver_or_admin)):
    visit = get_or_404(db, Visit, visit_id)
    _ensure_caregiver_visit_access(current_user, visit)
    if not visit.checked_in_at:
        raise HTTPException(status_code=400, detail='Visit must be checked in before checking out')
    visit.checked_out_at = datetime.utcnow()
    visit.status = 'completed'
    visit.check_out_location = payload.get('location')
    if visit.mileage_start is not None and visit.mileage_end is not None:
        visit.mileage_total = max(0, visit.mileage_end - visit.mileage_start)
    write_audit_log(db, action='visit_check_out', entity_type='visit', entity_id=visit.id, description='Caregiver checked out', user=current_user)
    db.commit(); db.refresh(visit)
    return _visit_payload(db, visit)


@router.post('/caregiver/visits/{visit_id}/notes')
def caregiver_notes(visit_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(require_caregiver_or_admin)):
    visit = get_or_404(db, Visit, visit_id)
    _ensure_caregiver_visit_access(current_user, visit)
    visit.caregiver_notes = payload.get('caregiver_notes', '')
    db.commit(); db.refresh(visit)
    return _visit_payload(db, visit)


@router.put('/caregiver/visits/{visit_id}/tasks')
def caregiver_tasks(visit_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(require_caregiver_or_admin)):
    visit = get_or_404(db, Visit, visit_id)
    _ensure_caregiver_visit_access(current_user, visit)
    tasks = payload.get('task_checklist', DEFAULT_TASK_CHECKLIST)
    visit.task_checklist = json.dumps(tasks)
    db.commit(); db.refresh(visit)
    return _visit_payload(db, visit)


@router.put('/caregiver/visits/{visit_id}/mileage')
def caregiver_mileage(visit_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(require_caregiver_or_admin)):
    visit = get_or_404(db, Visit, visit_id)
    _ensure_caregiver_visit_access(current_user, visit)
    visit.mileage_start = payload.get('mileage_start')
    visit.mileage_end = payload.get('mileage_end')
    if visit.mileage_start is not None and visit.mileage_end is not None:
        visit.mileage_total = max(0, visit.mileage_end - visit.mileage_start)
    db.commit(); db.refresh(visit)
    return _visit_payload(db, visit)


@router.get('/caregiver/alerts/missed-check-ins')
def missed_checkins(caregiver_id: int | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(require_caregiver_or_admin)):
    query = db.query(Visit).filter(Visit.status == 'scheduled', Visit.scheduled_start < datetime.utcnow(), Visit.checked_in_at.is_(None))
    if current_user.role == 'caregiver':
        caregiver_id = current_user.caregiver_id
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
def family_client(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    client = _ensure_client(db, client_id)
    _ensure_family_client_access(current_user, client_id)
    return _family_client_payload(db, client)


@router.get('/family/client/{client_id}/visits/upcoming')
def family_upcoming_visits(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    _ensure_client(db, client_id)
    _ensure_family_client_access(current_user, client_id)
    visits = (
        db.query(Visit)
        .filter(Visit.client_id == client_id, Visit.status.in_(['scheduled', 'in_progress']))
        .order_by(Visit.scheduled_start.asc())
        .limit(10)
        .all()
    )
    return [_visit_payload(db, visit) for visit in visits]


@router.get('/family/client/{client_id}/visits/completed')
def family_completed_visits(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    _ensure_client(db, client_id)
    _ensure_family_client_access(current_user, client_id)
    visits = (
        db.query(Visit)
        .filter(Visit.client_id == client_id, Visit.status == 'completed')
        .order_by(Visit.scheduled_start.desc())
        .limit(10)
        .all()
    )
    return [_visit_payload(db, visit) for visit in visits]


@router.get('/family/client/{client_id}/notes')
def family_notes(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    _ensure_client(db, client_id)
    _ensure_family_client_access(current_user, client_id)
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
def family_contacts(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    _ensure_client(db, client_id)
    _ensure_family_client_access(current_user, client_id)
    return db.query(FamilyContact).filter(FamilyContact.client_id == client_id).order_by(FamilyContact.is_primary.desc(), FamilyContact.last_name.asc()).all()


@router.post('/family/client/{client_id}/contacts')
def create_family_contact(client_id: int, payload: FamilyContactCreate, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    _ensure_client(db, client_id)
    _ensure_family_client_access(current_user, client_id)
    contact = FamilyContact(client_id=client_id, **payload.model_dump())
    if contact.is_primary:
        db.query(FamilyContact).filter(FamilyContact.client_id == client_id).update({FamilyContact.is_primary: False})
    db.add(contact); db.flush()
    write_audit_log(db, action='family_contact_created', entity_type='family_contact', entity_id=contact.id, description='Family contact created', user=current_user)
    db.commit(); db.refresh(contact)
    return contact


@router.put('/family/contacts/{contact_id}')
def update_family_contact(contact_id: int, payload: FamilyContactUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    contact = get_or_404(db, FamilyContact, contact_id)
    _ensure_family_client_access(current_user, contact.client_id)
    data = payload.model_dump()
    if data.get('is_primary'):
        db.query(FamilyContact).filter(FamilyContact.client_id == contact.client_id, FamilyContact.id != contact.id).update({FamilyContact.is_primary: False})
    for key, value in data.items():
        setattr(contact, key, value)
    write_audit_log(db, action='family_contact_updated', entity_type='family_contact', entity_id=contact.id, description='Family contact updated', user=current_user)
    db.commit(); db.refresh(contact)
    return contact


@router.delete('/family/contacts/{contact_id}')
def delete_family_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    contact = get_or_404(db, FamilyContact, contact_id)
    _ensure_family_client_access(current_user, contact.client_id)
    write_audit_log(db, action='family_contact_deleted', entity_type='family_contact', entity_id=contact.id, description='Family contact deleted', user=current_user)
    db.delete(contact); db.commit()
    return {"ok": True}


@router.get('/family/client/{client_id}/messages')
def family_messages(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    _ensure_client(db, client_id)
    _ensure_family_client_access(current_user, client_id)
    return db.query(FamilyMessage).filter(FamilyMessage.client_id == client_id).order_by(FamilyMessage.created_at.desc()).all()


@router.post('/family/client/{client_id}/messages')
def create_family_message(client_id: int, payload: FamilyMessageCreate, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    _ensure_client(db, client_id)
    _ensure_family_client_access(current_user, client_id)
    message = FamilyMessage(client_id=client_id, status='new', **payload.model_dump())
    db.add(message); db.flush()
    write_audit_log(db, action='family_message_submitted', entity_type='family_message', entity_id=message.id, description='Family message submitted', user=current_user)
    db.commit(); db.refresh(message)
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
def family_timeline(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_family_or_admin)):
    _ensure_client(db, client_id)
    _ensure_family_client_access(current_user, client_id)
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
