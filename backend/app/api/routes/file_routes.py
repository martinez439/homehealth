from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.audit import write_audit_log
from app.auth import require_admin
from app.core_config import get_settings
from app.db.database import get_db
from app.models.models import FileAttachment, User
from app.schemas.schemas import FileAttachmentRead

router = APIRouter(prefix="/files", tags=["files"])
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx"}


def _safe_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type is not allowed")
    return ext


@router.post("/upload", response_model=FileAttachmentRead)
def upload_file(
    upload: UploadFile = File(...),
    owner_type: str = Form("admin"),
    owner_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    settings = get_settings()
    ext = _safe_extension(upload.filename or "")
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid.uuid4().hex}.{ext}"
    target = settings.upload_dir / stored_filename
    max_bytes = settings.max_upload_mb * 1024 * 1024
    size = 0
    with target.open("wb") as buffer:
        while chunk := upload.file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                buffer.close()
                target.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_mb} MB limit")
            buffer.write(chunk)
    # Future production storage hook: replace this local write with S3 or DigitalOcean Spaces and keep only provider object keys in storage_path.
    attachment = FileAttachment(
        owner_type=owner_type,
        owner_id=owner_id,
        uploaded_by_user_id=current_user.id,
        original_filename=Path(upload.filename or "upload").name,
        stored_filename=stored_filename,
        content_type=upload.content_type or "application/octet-stream",
        file_size=size,
        storage_path=str(target),
    )
    db.add(attachment); db.flush()
    write_audit_log(db, action="file_uploaded", entity_type="file_attachment", entity_id=attachment.id, description=attachment.original_filename, user=current_user)
    db.commit(); db.refresh(attachment)
    return attachment


@router.get("/{file_id}")
def get_file(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    attachment = db.get(FileAttachment, file_id)
    if not attachment or attachment.is_deleted:
        raise HTTPException(status_code=404, detail="File not found")
    path = Path(attachment.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file missing")
    return FileResponse(path, media_type=attachment.content_type, filename=attachment.original_filename)


@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    attachment = db.get(FileAttachment, file_id)
    if not attachment or attachment.is_deleted:
        raise HTTPException(status_code=404, detail="File not found")
    attachment.is_deleted = True
    Path(attachment.storage_path).unlink(missing_ok=True)
    write_audit_log(db, action="file_deleted", entity_type="file_attachment", entity_id=attachment.id, description=attachment.original_filename, user=current_user)
    db.commit()
    return {"ok": True}
