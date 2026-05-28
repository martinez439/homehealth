from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

VisitStatus = Literal["scheduled", "in_progress", "completed", "missed"]


class ClientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    phone: str
    email: str | None = None
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    care_level: str = ""
    status: str = "active"
    notes: str = ""


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientRead(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaregiverBase(BaseModel):
    first_name: str
    last_name: str
    phone: str = ""
    email: str = ""
    certification: str = ""
    availability_notes: str = ""
    status: str = "available"
    notes: str = ""


class CaregiverCreate(CaregiverBase):
    pass


class CaregiverUpdate(CaregiverBase):
    pass


class CaregiverRead(CaregiverBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IntakeBase(BaseModel):
    client_name: str
    phone: str = ""
    email: str | None = None
    city: str = ""
    care_needs: str = ""
    preferred_schedule: str = ""
    urgency: str = "normal"
    status: str = "new"
    notes: str = ""


class IntakeCreate(IntakeBase):
    pass


class IntakeUpdate(IntakeBase):
    pass


class IntakeRead(IntakeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VisitBase(BaseModel):
    client_id: int
    caregiver_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    status: VisitStatus = "scheduled"
    service_type: str = ""
    notes: str = ""


class VisitCreate(VisitBase):
    pass


class VisitUpdate(VisitBase):
    pass


class VisitRead(VisitBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
