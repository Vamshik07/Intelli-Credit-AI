from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.analysis import router as analysis_router
from backend.api.routes.company import router as company_router
from backend.api.routes.document import router as document_router
from backend.api.routes.report import router as report_router
from backend.models.mongo_client import store


app = FastAPI(title="INTELLI-CREDIT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {
        "message": "INTELLI-CREDIT API running",
        "mongodb": "connected" if store.ping() else "disconnected",
    }


app.include_router(company_router)
app.include_router(document_router)
app.include_router(analysis_router)
app.include_router(report_router)
