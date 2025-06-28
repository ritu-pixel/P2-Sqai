import os
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional

from db.table import UserDB, FileDB, FileStatus
from auth.encryption import encrypt_bytes, get_user_fernet_key

UPLOAD_DIR = "encrypted_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    storage_path: str
    uploaded_at: datetime
    transcribed_text: Optional[str] = None
    summary: Optional[dict] = None
    uploaded_by: str
    status: FileStatus

    class Config:
        from_attributes = True

def save(file, username: str, db: Session):
    import uuid
    file_id = str(uuid.uuid4())
    raw_data = file.file.read()
    encrypted = encrypt_bytes(raw_data, get_user_fernet_key(username))

    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.bin")
    with open(file_path, "wb") as f:
        f.write(encrypted)

    record = FileDB(
        id=file_id,
        filename=file.filename,
        content_type=file.content_type,
        storage_path=file_path,
        uploaded_by=username,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
def get(file_id: str, username: str, db: Session):
    return (
        db.query(FileDB)
        .join(FileDB.uploader)
        .filter(FileDB.id == file_id, UserDB.username == username)
        .first()
    )

def get_all(username: str, db: Session, status: Optional[FileStatus] = None):
    query = (
        db.query(FileDB)
        .join(FileDB.uploader)
        .filter(UserDB.username == username)
    )
    if status:
        query = query.filter(FileDB.status == status)
    return query.all()

def remove(file_id: str, username: str, db: Session):
    file_record = db.query(FileDB).filter_by(id=file_id, uploaded_by=username).first()
    if not file_record:
        return False
    if os.path.exists(file_record.storage_path):
        os.remove(file_record.storage_path)
    db.delete(file_record)
    db.commit()
    return True
