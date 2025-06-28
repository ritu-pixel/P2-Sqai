import csv
import io
from typing import List, Dict
from sqlalchemy.orm import Session
from notion_client import Client

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from db.table import FileDB, FileStatus


def get_action_items(file_id: str, username: str, db: Session) -> List[Dict]:
    file = db.query(FileDB).filter_by(id=file_id, uploaded_by=username).first()

    if not file or file.status != FileStatus.summarized:
        raise ValueError("File not found, access denied, or not summarized yet.")

    action_items: List[dict] = file.summary.get("action_items", [])
    if not action_items:
        raise ValueError("No action items found in summary.")

    return action_items

def get_meet_summary(file_id: str, username: str, db: Session) -> str:
    file = db.query(FileDB).filter_by(id=file_id, uploaded_by=username).first()

    if not file or file.status != FileStatus.summarized:
        raise ValueError("File not found, access denied, or not summarized yet.")
    summary_text = file.summary.get("summary")
    if not summary_text:
        raise ValueError("Summary field is missing or empty.")

    return summary_text

def export_csv(file_id: str, username: str, db: Session) -> str:
    action_items = get_action_items(file_id, username, db)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["task", "assignee", "due_date", "category"])
    writer.writeheader()

    for item in action_items:
        writer.writerow({
            "task": item.get("task", ""),
            "assignee": item.get("assignee"),
            "due_date": item.get("due_date"),
            "category": item.get("category")
        })

    return output.getvalue()


def export_to_pdf(file_id: str, username: str, db: Session) -> bytes:
    action_items = get_action_items(file_id, username, db)

    if not action_items:
        raise ValueError("No action items found in summary.")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Meeting Summary - Action Items", styles["Title"]))
    elements.append(Paragraph(get_meet_summary(file_id, username, db), styles["BodyText"]))
    elements.append(Spacer(1, 12))

    data = [["Task", "Assignee", "Due Date", "Category"]]

    for item in action_items:
        data.append([
            item.get("task", ""),
            item.get("assignee", ""),
            item.get("due_date", ""),
            item.get("category", "")
        ])

    table = Table(data, colWidths=[150, 100, 100, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
    ]))

    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()


def export_notion(file_id: str, username: str, db: Session, token: str, database_id: str) -> dict:
    action_items = get_action_items(file_id, username, db)

    notion = Client(auth=token)
    results = []

    for item in action_items:
        try:
            result = notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Task": {
                        "title": [{"text": {"content": item.get("task", "No Task")}}]
                    },
                    "Assignee": {
                        "rich_text": [{"text": {"content": item.get("assignee", "")}}]
                    },
                    "Due Date": {
                        "date": {"start": item.get("due_date")} if item.get("due_date") else None
                    },
                    "Category": {
                        "select": {"name": item.get("category")} if item.get("category") else None
                    }
                }
            )
            results.append({"success": True, "id": result["id"]})
        except Exception as e:
            results.append({"success": False, "error": str(e)})

    return {"results": results}
