from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(TimestampMixin, Base):
    __tablename__='users'; id: Mapped[int]=mapped_column(primary_key=True)
    email: Mapped[str]=mapped_column(String(255), unique=True); role: Mapped[str]=mapped_column(String(50), default='caregiver')

class Client(TimestampMixin, Base):
    __tablename__='clients'; id: Mapped[int]=mapped_column(primary_key=True)
    full_name: Mapped[str]=mapped_column(String(255)); status: Mapped[str]=mapped_column(String(50), default='pending')

class Caregiver(TimestampMixin, Base):
    __tablename__='caregivers'; id: Mapped[int]=mapped_column(primary_key=True)
    full_name: Mapped[str]=mapped_column(String(255)); certification: Mapped[str]=mapped_column(String(100), default='')

class IntakeRequest(TimestampMixin, Base):
    __tablename__='intake_requests'; id: Mapped[int]=mapped_column(primary_key=True)
    client_name: Mapped[str]=mapped_column(String(255)); phone: Mapped[str]=mapped_column(String(40), default=''); care_needs: Mapped[str]=mapped_column(Text, default='')

class Visit(TimestampMixin, Base):
    __tablename__='visits'; id: Mapped[int]=mapped_column(primary_key=True)
    client_id: Mapped[int]=mapped_column(ForeignKey('clients.id')); caregiver_id: Mapped[int]=mapped_column(ForeignKey('caregivers.id'))
    status: Mapped[str]=mapped_column(String(40), default='scheduled')

class VisitNote(TimestampMixin, Base):
    __tablename__='visit_notes'; id: Mapped[int]=mapped_column(primary_key=True)
    visit_id: Mapped[int]=mapped_column(ForeignKey('visits.id')); note: Mapped[str]=mapped_column(Text)

class FamilyContact(TimestampMixin, Base):
    __tablename__='family_contacts'; id: Mapped[int]=mapped_column(primary_key=True)
    client_id: Mapped[int]=mapped_column(ForeignKey('clients.id')); full_name: Mapped[str]=mapped_column(String(255)); relationship: Mapped[str]=mapped_column(String(120), default='')

class AuditLog(Base):
    __tablename__='audit_logs'; id: Mapped[int]=mapped_column(primary_key=True)
    actor_user_id: Mapped[int|None]=mapped_column(ForeignKey('users.id'), nullable=True)
    action: Mapped[str]=mapped_column(String(255)); entity_type: Mapped[str]=mapped_column(String(120)); entity_id: Mapped[str]=mapped_column(String(120)); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
