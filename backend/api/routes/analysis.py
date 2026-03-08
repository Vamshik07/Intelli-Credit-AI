from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.langgraph.workflow import AGENT_WORKFLOW_SEQUENCE, run_credit_workflow
from backend.models.mongo_client import store
from backend.models.schemas import AnalysisRequest


router = APIRouter(tags=["analysis"])


@router.post("/api/analysis/run")
def run_analysis(payload: AnalysisRequest):
    try:
        company = store.get_company(payload.company_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid company id: {exc}")

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company["_id"] = str(company["_id"])
    documents = store.list_documents(payload.company_id)
    for doc in documents:
        doc["_id"] = str(doc["_id"])

    state = {
        "company": company,
        "documents": documents,
        "primary_insights": payload.primary_insights,
        "credit_officer_observations": payload.credit_officer_observations,
    }

    try:
        result = run_credit_workflow(state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline failed: {exc}")

    financial = result.get("financial_metrics", {})
    risk = result.get("risk", {})
    recommendation = result.get("recommendation", {})
    litigation = result.get("litigation", {})
    reports = result.get("reports", {})

    store.save_financial_metrics(
        {
            "company_id": payload.company_id,
            "year": datetime.now(timezone.utc).year,
            "revenue": financial.get("revenue", 0.0),
            "profit": financial.get("net_profit", 0.0),
            "assets": financial.get("total_assets", 0.0),
            "liabilities": financial.get("total_debt", 0.0),
            "debt": financial.get("total_debt", 0.0),
        }
    )

    for signal in litigation.get("signals", []):
        store.save_legal_case(
            {
                "company_id": payload.company_id,
                "court": "Unknown",
                "status": signal,
                "amount": 0.0,
            }
        )

    risk_record_id = store.save_risk_score(
        {
            "company_id": payload.company_id,
            "financial_score": risk.get("financial_score", 0.0),
            "legal_score": risk.get("legal_score", 0.0),
            "industry_score": risk.get("industry_score", 0.0),
            "promoter_score": risk.get("promoter_score", 0.0),
            "final_score": risk.get("final_score", 0.0),
            "recommendation": risk.get("recommendation", "Loan Rejected"),
            "loan_terms": recommendation,
            "reasons": risk.get("reasons", []),
            "report_paths": reports,
            "created_at": datetime.now(timezone.utc),
        }
    )

    agent_workflow = []
    for agent_key, label in AGENT_WORKFLOW_SEQUENCE:
        status = "completed"
        if agent_key == "financial_agent" and not financial:
            status = "warning"
        if agent_key == "research_agent" and not result.get("research", {}):
            status = "warning"
        if agent_key == "cam_agent" and not reports:
            status = "warning"

        agent_workflow.append({"agent": agent_key, "label": label, "status": status})

    return {
        "company_id": payload.company_id,
        "agent_workflow": agent_workflow,
        "financial_data": {
            "revenue": financial.get("revenue", 0.0),
            "ebitda": financial.get("ebitda", 0.0),
            "net_profit": financial.get("net_profit", 0.0),
            "total_assets": financial.get("total_assets", 0.0),
            "total_debt": financial.get("total_debt", 0.0),
        },
        "research_insights": {
            "industry_trends": result.get("research", {}).get("analysis", ""),
            "news_signals": result.get("research", {}).get("headlines", []),
            "regulatory_alerts": result.get("litigation", {}).get("signals", []),
        },
        "risk_scores": {
            "financial_strength": risk.get("financial_score", 0.0),
            "legal_strength": risk.get("legal_score", 0.0),
            "promoter_strength": risk.get("promoter_score", 0.0),
            "industry_strength": risk.get("industry_score", 0.0),
            "operational_strength": risk.get("operational_score", 0.0),
            "weighted_final_score": risk.get("final_score", 0.0),
        },
        "risk": risk,
        "recommendation": recommendation,
        "reasons": risk.get("reasons", []),
        "reports": {
            "cam_docx_path": reports.get("docx"),
            "cam_pdf_path": reports.get("pdf"),
            **reports,
        },
        "explainability": {
            "summary": "Loan decision is derived from financial, legal, promoter, industry, and operational components with primary-insight penalty adjustments.",
            "reasons": risk.get("reasons", []),
            "components": risk.get("components", {}),
            "inputs_used": {
                "document_count": len(documents),
                "news_headline_count": len(result.get("research", {}).get("headlines", [])),
                "litigation_signals": result.get("litigation", {}).get("signals", []),
            },
        },
        "database_record": {
            "collection": "risk_scores",
            "risk_id": risk_record_id,
        },
    }
