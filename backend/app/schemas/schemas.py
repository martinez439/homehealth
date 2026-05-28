from datetime import datetime
from pydantic import BaseModel

class RoleMixin(BaseModel):
    allowed_roles: list[str] = ['admin', 'caregiver', 'family']

class ClientBase(BaseModel): full_name: str; status: str='pending'
class ClientCreate(ClientBase): pass
class ClientRead(ClientBase): id: int; created_at: datetime; updated_at: datetime
class CaregiverBase(BaseModel): full_name: str; certification: str=''
class CaregiverCreate(CaregiverBase): pass
class CaregiverRead(CaregiverBase): id: int; created_at: datetime; updated_at: datetime
class IntakeBase(BaseModel): client_name: str; phone: str=''; care_needs: str=''
class IntakeCreate(IntakeBase): pass
class IntakeRead(IntakeBase): id: int; created_at: datetime; updated_at: datetime
class VisitBase(BaseModel): client_id: int; caregiver_id: int; status: str='scheduled'
class VisitCreate(VisitBase): pass
class VisitRead(VisitBase): id: int; created_at: datetime; updated_at: datetime
class VisitNoteBase(BaseModel): visit_id: int; note: str
class VisitNoteCreate(VisitNoteBase): pass
class VisitNoteRead(VisitNoteBase): id: int; created_at: datetime; updated_at: datetime
