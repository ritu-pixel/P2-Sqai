from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from db.files import (
    save,
    remove,
    get,
    get_all,
    FileResponse
)
from db.table import FileStatus
from auth.dependencies import get_current_user

router = APIRouter(prefix="/file", tags=["file"])

@router.post("/upload", response_model=FileResponse)
async def upload_route(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    if file.content_type not in ["audio/mpeg", "audio/wav", "audio/x-m4a"]:
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    saved = save(file, current_user.username, db)
    return saved

@router.get("/", response_model=List[FileResponse])
def list_all_route(
    status: Optional[FileStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    files = get_all(current_user.username, db, status)
    return files

@router.get("/{file_id}", status_code=status.HTTP_200_OK)
def list_one_route(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    file_record = get(file_id, current_user.username, db)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found or access denied")
    return file_record

@router.delete("/{file_id}", status_code=status.HTTP_200_OK)
def delete_route(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    success = remove(file_id, current_user.username, db)
    if not success:
        raise HTTPException(status_code=404, detail="File not found or access denied")
    return {"message": f"File {file_id} deleted successfully."}
