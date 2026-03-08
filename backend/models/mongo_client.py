import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


class MongoStore:
    def __init__(self) -> None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "intelli_credit")
        self.client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        self.db = self.client[db_name]

    def ping(self) -> bool:
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def create_company(self, payload: dict) -> str:
        result = self.db.companies.insert_one(payload)
        return str(result.inserted_id)

    def get_company(self, company_id: str):
        from bson import ObjectId

        return self.db.companies.find_one({"_id": ObjectId(company_id)})

    def add_document(self, company_id: str, file_path: str, document_type: str) -> str:
        result = self.db.documents.insert_one(
            {
                "company_id": company_id,
                "file_path": file_path,
                "document_type": document_type,
                "uploaded_at": datetime.now(timezone.utc),
            }
        )
        return str(result.inserted_id)

    def list_documents(self, company_id: str) -> list[dict]:
        return list(self.db.documents.find({"company_id": company_id}))

    def save_financial_metrics(self, payload: dict) -> str:
        result = self.db.financial_metrics.insert_one(payload)
        return str(result.inserted_id)

    def save_legal_case(self, payload: dict) -> str:
        result = self.db.legal_cases.insert_one(payload)
        return str(result.inserted_id)

    def save_risk_score(self, payload: dict) -> str:
        result = self.db.risk_scores.insert_one(payload)
        return str(result.inserted_id)


store = MongoStore()
