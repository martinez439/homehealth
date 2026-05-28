from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel

VisitStatus = Literal["scheduled", "in_progress", "completed", "missed"]
RecurrenceRule = Literal["daily", "weekly", "biweekly", "monthly"]


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
    recurrence_group_id: str | None = None
    recurrence_rule: str | None = None
    recurrence_end_date: date | None = None
    generated_from_recurring: bool = False


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


class VisitMove(BaseModel):
    scheduled_start: datetime
    scheduled_end: datetime


class RecurringVisitCreate(VisitBase):
    recurrence_rule: RecurrenceRule
    recurrence_end_date: date


class CaregiverAvailabilityBase(BaseModel):
    day_of_week: int
    available: bool = True
    start_time: time | None = None
    end_time: time | None = None
    notes: str = ""


class CaregiverAvailabilityCreate(CaregiverAvailabilityBase):
    pass


class CaregiverAvailabilityUpdate(CaregiverAvailabilityBase):
    pass


class CaregiverAvailabilityRead(CaregiverAvailabilityBase):
    id: int
    caregiver_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

FamilyMessageType = Literal[
    "general_question",
    "schedule_request",
    "care_update_request",
    "billing_question",
    "other",
]
FamilyMessageStatus = Literal["new", "reviewed", "resolved"]


class FamilyContactBase(BaseModel):
    first_name: str
    last_name: str
    relationship: str = ""
    phone: str = ""
    email: str = ""
    is_primary: bool = False
    receives_updates: bool = True


class FamilyContactCreate(FamilyContactBase):
    pass


class FamilyContactUpdate(FamilyContactBase):
    pass


class FamilyContactRead(FamilyContactBase):
    id: int
    client_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FamilyMessageBase(BaseModel):
    sender_name: str
    sender_email: str | None = None
    message_type: FamilyMessageType = "general_question"
    subject: str
    message: str


class FamilyMessageCreate(FamilyMessageBase):
    pass


class FamilyMessageUpdate(FamilyMessageBase):
    status: FamilyMessageStatus = "new"


class FamilyMessageRead(FamilyMessageBase):
    id: int
    client_id: int
    status: FamilyMessageStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
