from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from io import BytesIO



from db.database import get_db
from auth.dependencies import get_current_user
from db.files import get
from db.export import export_csv, export_notion, export_to_pdf

router = APIRouter(
    prefix="/export",
    tags=["export"],
)

@router.get("/csv/{file_id}")
def download_csv(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    try:
        csv_data = export_csv(str(file_id), current_user.username, db)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=action_items_{file_id}.csv"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/pdf/{file_id}")
def download_pdf(
    file_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    pdf_bytes = export_to_pdf(file_id, current_user.username, db)
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=summary_{file_id}.pdf"
    })

@router.post("/notion/{file_id}")
def export_notion_route(
    file_id: UUID,
    token: str,
    database_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = export_notion(
        file_id=str(file_id),
        username=current_user.username,
        db=db,
        token=token,
        database_id=database_id
    )
    return result
