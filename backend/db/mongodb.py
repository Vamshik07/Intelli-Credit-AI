from datetime import datetime, timezone
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

try:
    from pymongo import MongoClient
except Exception:  # pragma: no cover
    MongoClient = None


class MongoDBClient:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DB_NAME", "intelli_credit_ai")
        self.enabled = False
        self.reason = "MongoDB client not initialized"
        self._client = None
        self._db = None

        if MongoClient is None:
            self.reason = "pymongo is not installed"
            return

        try:
            self._client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            self._client.admin.command("ping")
            self._db = self._client[self.db_name]
            self.enabled = True
            self.reason = "connected"
        except Exception as exc:
            self.enabled = False
            self.reason = f"connection failed: {exc}"

    def health(self):
        return {
            "enabled": self.enabled,
            "db_name": self.db_name,
            "reason": self.reason,
        }

    def insert_event(self, collection_name, payload):
        if not self.enabled:
            return {"stored": False, "reason": self.reason}

        document = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }

        try:
            result = self._db[collection_name].insert_one(document)
            return {
                "stored": True,
                "collection": collection_name,
                "id": str(result.inserted_id),
            }
        except Exception as exc:
            return {"stored": False, "reason": str(exc), "collection": collection_name}


mongo_client = MongoDBClient()


def store_prediction(payload, response):
    return mongo_client.insert_event(
        "predictions",
        {
            "request": payload,
            "response": response,
        },
    )


def store_analysis(payload, response):
    return mongo_client.insert_event(
        "analyses",
        {
            "request": payload,
            "response": response,
        },
    )


def store_simulation(payload, response):
    return mongo_client.insert_event(
        "simulations",
        {
            "request": payload,
            "response": response,
        },
    )


def store_cam_generation(payload, response):
    return mongo_client.insert_event(
        "cam_reports",
        {
            "request": payload,
            "response": response,
        },
    )
