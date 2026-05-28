from fastapi import Request
from sqlalchemy.orm import Session

from app.models.models import AuditLog, User


def write_audit_log(db: Session, *, action: str, entity_type: str, entity_id: int | None = None, description: str = "", user: User | None = None, request: Request | None = None, actor_email: str | None = None, actor_role: str | None = None) -> AuditLog:
    log = AuditLog(
        user_id=user.id if user else None,
        actor_email=user.email if user else actor_email,
        actor_role=user.role if user else actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent")[:255] if request else None,
    )
    db.add(log)
    return log
