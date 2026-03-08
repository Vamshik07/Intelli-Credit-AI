from bson import ObjectId
from fastapi import APIRouter, HTTPException

from backend.models.mongo_client import store
from backend.models.schemas import CompanyCreate


router = APIRouter(tags=["company"])


def _serialize_company(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.post("/api/company/create")
def create_company(payload: CompanyCreate):
    if not store.ping():
        raise HTTPException(
            status_code=503,
            detail="Database unavailable: MongoDB is disconnected. Start MongoDB and retry.",
        )

    try:
        company_id = store.create_company(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create company: {exc}")

    return {"company_id": company_id}


@router.get("/api/company/stats")
def get_company_stats():
    if not store.ping():
        raise HTTPException(
            status_code=503,
            detail="Database unavailable: MongoDB is disconnected. Start MongoDB and retry.",
        )

    records = list(store.db.risk_scores.find({}, {"company_id": 1, "recommendation": 1, "created_at": 1}))

    # Keep only the latest decision per company so repeated analyses do not overcount.
    latest_by_company: dict[str, dict] = {}
    for record in records:
        company_id = str(record.get("company_id", "")).strip()
        if not company_id:
            continue

        current = latest_by_company.get(company_id)
        if not current:
            latest_by_company[company_id] = record
            continue

        current_created_at = current.get("created_at")
        record_created_at = record.get("created_at")
        if record_created_at and (not current_created_at or record_created_at > current_created_at):
            latest_by_company[company_id] = record

    accepted = 0
    rejected = 0
    for record in latest_by_company.values():
        recommendation = str(record.get("recommendation", "")).strip().lower()
        if "reject" in recommendation:
            rejected += 1
        elif "approve" in recommendation:
            accepted += 1

    return {
        "total_applications": len(latest_by_company),
        "accepted": accepted,
        "rejected": rejected,
    }


@router.get("/api/company/{company_id}")
def get_company(company_id: str):
    try:
        doc = store.db.companies.find_one({"_id": ObjectId(company_id)})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid company id: {exc}")

    if not doc:
        raise HTTPException(status_code=404, detail="Company not found")

    return _serialize_company(doc)
