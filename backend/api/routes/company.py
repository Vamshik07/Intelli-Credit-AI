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


@router.get("/api/company/{company_id}")
def get_company(company_id: str):
    try:
        doc = store.db.companies.find_one({"_id": ObjectId(company_id)})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid company id: {exc}")

    if not doc:
        raise HTTPException(status_code=404, detail="Company not found")

    return _serialize_company(doc)
