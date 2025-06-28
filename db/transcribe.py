from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from db.table import FileDB, FileStatus
from models.models import transcribe_audio, summarize_transcript
from utils.file_utils import decrypt_to_temp_path

class TranscriptResponse(BaseModel):
    file_id: UUID
    transcribed_text: str
    summary: Optional[dict] = None

    class Config:
        from_attributes = True

def transcribe_and_summarize(file: FileDB, db: Session, current_user: str) -> TranscriptResponse:
    # if file_obj.status == FileStatus.summarized:
    #     return TranscriptResponse(
    #         file_id=file_obj.id,
    #         transcribed_text=file_obj.transcribed_text,
    #         summary=file_obj.summary
    #     )
    audio_path = decrypt_to_temp_path(
        encrypted_path=file.storage_path,
        current_user=current_user,
        content_type=file.content_type,
    )

    transcript = transcribe_audio(audio_path)
    file.transcribed_text = transcript
    file.status = FileStatus.transcribed
    db.commit()

    summary = summarize_transcript(file.transcribed_text)
    file.summary = summary
    if not summary or summary.get("error"):
        db.commit()
        return TranscriptResponse(
            file_id=file.id,
            transcribed_text=file.transcribed_text,
             summary =file.summary
        )

    file.status = FileStatus.summarized
    db.commit()
    return TranscriptResponse(
        file_id=file.id,
        transcribed_text=file.transcribed_text,
        summary=file.summary
    )
