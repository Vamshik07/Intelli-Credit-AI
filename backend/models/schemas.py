from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    name: str
    industry: str
    cin: str
    incorporation_date: str | None = None


class CompanyOut(CompanyCreate):
    id: str = Field(alias="_id")


class DocumentOut(BaseModel):
    id: str = Field(alias="_id")
    company_id: str
    file_path: str
    document_type: str
    uploaded_at: datetime


class AnalysisRequest(BaseModel):
    company_id: str
    primary_insights: list[str] = Field(default_factory=list)
    credit_officer_observations: str = ""


class RiskBreakdown(BaseModel):
    financial_score: float
    legal_score: float
    promoter_score: float
    operational_score: float
    industry_score: float
    final_score: float
    recommendation: str


class AnalysisResult(BaseModel):
    company_id: str
    risk: RiskBreakdown
    recommendation: dict[str, Any]
    reasons: list[str]
    cam_docx_path: str
    cam_pdf_path: str


class ApiMessage(BaseModel):
    message: str
