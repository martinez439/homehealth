from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException
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
