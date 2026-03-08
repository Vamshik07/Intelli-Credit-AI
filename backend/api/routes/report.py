from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from backend.models.mongo_client import store


router = APIRouter(tags=["report"])


@router.get("/api/report/{company_id}")
def get_report(company_id: str):
    record = store.db.risk_scores.find_one(
        {"company_id": company_id},
        sort=[("created_at", -1)],
    )
    if not record:
        raise HTTPException(status_code=404, detail="No report found for company")

    record["_id"] = str(record["_id"])
    return record


@router.get("/api/report/{company_id}/download/{fmt}")
def download_report(company_id: str, fmt: str):
    record = store.db.risk_scores.find_one(
        {"company_id": company_id},
        sort=[("created_at", -1)],
    )
    if not record:
        raise HTTPException(status_code=404, detail="No report found for company")

    report_paths = record.get("report_paths", {})
    if fmt.lower() == "pdf":
        report_path = report_paths.get("pdf")
        media_type = "application/pdf"
    elif fmt.lower() == "docx":
        report_path = report_paths.get("docx")
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        raise HTTPException(status_code=400, detail="Unsupported report format")

    if not report_path:
        raise HTTPException(status_code=404, detail=f"{fmt.upper()} report path missing")

    path_obj = Path(report_path)
    if not path_obj.exists():
        raise HTTPException(status_code=404, detail=f"{fmt.upper()} report file not found")

    return FileResponse(
        path=path_obj,
        media_type=media_type,
        filename=path_obj.name,
    )
