from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Caregiver, Client, IntakeRequest, Visit, VisitNote
from app.schemas.schemas import CaregiverCreate, ClientCreate, IntakeCreate, VisitCreate, VisitNoteCreate

router = APIRouter()

def _create_and_list(router, model, schema, path):
    @router.post(path)
    def create(payload: schema, db: Session = Depends(get_db)):
        obj = model(**payload.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj
    @router.get(path)
    def list_all(db: Session = Depends(get_db)):
        return db.query(model).all()

_create_and_list(router, IntakeRequest, IntakeCreate, '/intake')
_create_and_list(router, Client, ClientCreate, '/clients')
_create_and_list(router, Caregiver, CaregiverCreate, '/caregivers')
_create_and_list(router, Visit, VisitCreate, '/visits')
_create_and_list(router, VisitNote, VisitNoteCreate, '/notes')

@router.get('/family/{client_id}')
def family_view(client_id: int, db: Session = Depends(get_db)):
    visits = db.query(Visit).filter(Visit.client_id == client_id).all()
    return {'client_id': client_id, 'visits': visits}
