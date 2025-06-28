from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict

from db.database import get_db
from auth.dependencies import get_current_user
from db.files import get as get_file
from db.export import get_action_items
from db.transcribe import transcribe_and_summarize, TranscriptResponse

router = APIRouter(
    prefix="/transcribe",
    tags=["transcription"],
)

@router.get("/{file_id}", response_model=TranscriptResponse)
def generate_transcription_and_summary(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    file = get_file(file_id, current_user.username, db)
    if not file:
        raise HTTPException(status_code=404, detail="File not found or access denied")

    return transcribe_and_summarize(file, db, current_user.username)

@router.get("/items/{file_id}", response_model=List[Dict])
def list_action_items(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_action_items(file_id, current_user.username, db)