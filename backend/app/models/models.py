from __future__ import annotations

from datetime import datetime, time

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)




class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(40), default="admin", index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=True)
    caregiver_id: Mapped[int] = mapped_column(ForeignKey("caregivers.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_email: Mapped[str] = mapped_column(String(255), nullable=True)
    actor_role: Mapped[str] = mapped_column(String(40), nullable=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str] = mapped_column(String(120), index=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    ip_address: Mapped[str] = mapped_column(String(120), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class FileAttachment(TimestampMixin, Base):
    __tablename__ = "file_attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_type: Mapped[str] = mapped_column(String(80), default="admin")
    owner_id: Mapped[int] = mapped_column(Integer, nullable=True)
    uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True)
    content_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    storage_path: Mapped[str] = mapped_column(String(500))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class Client(TimestampMixin, Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    date_of_birth: Mapped[datetime] = mapped_column(Date, nullable=True)
    phone: Mapped[str] = mapped_column(String(40))
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(String(255), default="")
    city: Mapped[str] = mapped_column(String(120), default="")
    state: Mapped[str] = mapped_column(String(50), default="")
    zip_code: Mapped[str] = mapped_column(String(20), default="")
    care_level: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(40), default="active")
    notes: Mapped[str] = mapped_column(Text, default="")


class Caregiver(TimestampMixin, Base):
    __tablename__ = "caregivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(40), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    certification: Mapped[str] = mapped_column(String(100), default="")
    availability_notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="available")
    notes: Mapped[str] = mapped_column(Text, default="")


class IntakeRequest(TimestampMixin, Base):
    __tablename__ = "intake_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(40), default="")
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(120), default="")
    care_needs: Mapped[str] = mapped_column(Text, default="")
    preferred_schedule: Mapped[str] = mapped_column(String(120), default="")
    urgency: Mapped[str] = mapped_column(String(40), default="normal")
    status: Mapped[str] = mapped_column(String(40), default="new")
    notes: Mapped[str] = mapped_column(Text, default="")


class Visit(TimestampMixin, Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    caregiver_id: Mapped[int] = mapped_column(ForeignKey("caregivers.id"))
    scheduled_start: Mapped[datetime] = mapped_column(DateTime)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(40), default="scheduled")
    service_type: Mapped[str] = mapped_column(String(120), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    checked_in_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    checked_out_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    check_in_location: Mapped[str] = mapped_column(String(255), nullable=True)
    check_out_location: Mapped[str] = mapped_column(String(255), nullable=True)
    mileage_start: Mapped[float] = mapped_column(Float, nullable=True)
    mileage_end: Mapped[float] = mapped_column(Float, nullable=True)
    mileage_total: Mapped[float] = mapped_column(Float, nullable=True)
    task_checklist: Mapped[str] = mapped_column(Text, default="[]")
    caregiver_notes: Mapped[str] = mapped_column(Text, default="")
    missed_alert_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_group_id: Mapped[str] = mapped_column(String(80), nullable=True)
    recurrence_rule: Mapped[str] = mapped_column(String(40), nullable=True)
    recurrence_end_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    generated_from_recurring: Mapped[bool] = mapped_column(Boolean, default=False)


class CaregiverAvailability(TimestampMixin, Base):
    __tablename__ = "caregiver_availability"

    id: Mapped[int] = mapped_column(primary_key=True)
    caregiver_id: Mapped[int] = mapped_column(ForeignKey("caregivers.id"))
    day_of_week: Mapped[int] = mapped_column(Integer)
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=True)
    end_time: Mapped[time] = mapped_column(Time, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class FamilyContact(TimestampMixin, Base):
    __tablename__ = "family_contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    relationship: Mapped[str] = mapped_column(String(100), default="")
    phone: Mapped[str] = mapped_column(String(40), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    receives_updates: Mapped[bool] = mapped_column(Boolean, default=True)


class FamilyMessage(TimestampMixin, Base):
    __tablename__ = "family_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    sender_name: Mapped[str] = mapped_column(String(200))
    sender_email: Mapped[str] = mapped_column(String(255), nullable=True)
    message_type: Mapped[str] = mapped_column(String(60), default="general_question")
    subject: Mapped[str] = mapped_column(String(255), default="")
    message: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="new")
