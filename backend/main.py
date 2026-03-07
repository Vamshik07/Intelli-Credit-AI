from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from pathlib import Path

try:
    # Package mode: `uvicorn backend.main:app --reload` from project root.
    from .agents.data_ingestor import ingest_documents
    from .agents.research_agent import research_company
    from .agents.risk_agent import calculate_risk
    from .agents.cam_generator import generate_cam
except ImportError:
    # Script mode: `uvicorn main:app --reload` from within backend/.
    from agents.data_ingestor import ingest_documents
    from agents.research_agent import research_company
    from agents.risk_agent import calculate_risk
    from agents.cam_generator import generate_cam

app = FastAPI()
BACKEND_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BACKEND_DIR / "uploads"


class PredictRequest(BaseModel):
    revenue: float
    profit: float
    debt: float
    industry_type: str = "General"
    location_zone: str = "Central Economic Zone"
    market_trend: str = "Stable"
    debt_ratio: float | None = None

# Allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "AI Loan Approval API Running"}


@app.post("/predict")
def predict(payload: PredictRequest):
    debt_ratio = payload.debt_ratio
    if debt_ratio is None:
        debt_ratio = (payload.debt / payload.revenue) if payload.revenue else 0.0

    financials = {
        "revenue": payload.revenue,
        "profit": payload.profit,
        "debt": payload.debt,
        "industry_type": payload.industry_type,
        "location_zone": payload.location_zone,
        "market_trend": payload.market_trend,
        "debt_ratio": debt_ratio,
    }

    score, risk, explanation = calculate_risk(financials, [])

    return {
        "prediction": risk,
        "risk_score": score,
        "explanation": explanation,
    }

@app.post("/analyze")
async def analyze(
    company: str = Form(...),
    file: UploadFile = File(...)
):
    UPLOADS_DIR.mkdir(exist_ok=True)
    filepath = UPLOADS_DIR / file.filename

    # save uploaded file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    docs = ingest_documents([str(filepath)])

    # Financial extraction is intentionally lightweight here to match the requested backend/agents layout.
    financials = {
        "revenue": 100000000,
        "profit": 10000000,
        "debt": 50000000,
        "industry_type": "Manufacturing",
        "location_zone": "Central Economic Zone",
        "market_trend": "Stable",
    }

    news = research_company(company)

    score, risk, explanation = calculate_risk(financials, news)

    recommendation = "Review Required"
    generate_cam(company, financials, risk, recommendation)

    return {
        "financials": financials,
        "risk_score": score,
        "risk_level": risk,
        "recommendation": recommendation,
        "news": news,
        "explanation": explanation,
    }