# INTELLI-CREDIT AI

AI-powered corporate credit appraisal platform built with FastAPI, LangGraph orchestration, MongoDB persistence, and a React + Vite frontend.

## Quick Backend Command

Run from project root:

```bash
.venv\Scripts\activate
uvicorn backend.main:app --reload
```

Backend URL: `http://127.0.0.1:8000`

## Stack

Backend:
- FastAPI
- LangGraph
- PyMongo
- python-docx + reportlab
- pdfplumber + PyMuPDF + pytesseract
- Gemini + Groq (task-routed LLM usage)

Frontend:
- React 18
- Vite
- Tailwind CSS
- Axios

Data/ML:
- pandas
- scikit-learn
- joblib

## Architecture

Backend entrypoints:
- `backend/main.py` (compat shim)
- `backend/api/main.py` (actual FastAPI app)

Workflow:
- `backend/langgraph/workflow.py`
- Agent sequence: ingestion -> financial -> research -> litigation -> risk -> cam

Backend API routes:
- `backend/api/routes/company.py`
- `backend/api/routes/document.py`
- `backend/api/routes/analysis.py`
- `backend/api/routes/report.py`

Frontend app:
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/pages/CompanyRegistration.jsx`
- `frontend/src/pages/DocumentUpload.jsx`
- `frontend/src/pages/ObservationPage.jsx`
- `frontend/src/pages/AnalysisPage.jsx`
- `frontend/src/pages/ResultsPage.jsx`
- `frontend/src/pages/ReportPage.jsx`
- `frontend/src/components/*` (Navbar, Sidebar, upload, progress, risk, CAM download)
- `frontend/src/services/api.js`

Backend service modules:
- `backend/services/parser_service.py`
- `backend/services/research_service.py`
- `backend/services/risk_service.py`
- `backend/services/cam_service.py`
- `backend/services/llm_router.py`

## API Endpoints

- `GET /`
  - Service status and MongoDB connectivity indicator.

- `POST /api/company/create`
  - Create company profile.

- `GET /api/company/{company_id}`
  - Retrieve company profile.

- `POST /api/document/upload`
  - Multipart fields:
    - `company_id`
    - `document_type`
    - `files` (supports multiple)

- `POST /api/analysis/run`
  - Runs complete LangGraph credit workflow.

- `GET /api/report/{company_id}`
  - Fetch latest stored report record for the company.

- `GET /api/report/{company_id}/download/docx`
  - Download latest CAM as DOCX.

- `GET /api/report/{company_id}/download/pdf`
  - Download latest CAM as PDF.

## Analysis Output Contract

`POST /api/analysis/run` returns:
- `agent_workflow` (status for each LangGraph agent)
- `financial_data` (revenue, ebitda, net_profit, total_assets, total_debt)
- `research_insights` (industry trends, news signals, regulatory alerts)
- `risk_scores` (financial/legal/promoter/industry/operational strengths + weighted final score)
- `recommendation` (decision, recommended loan amount, suggested interest rate)
- `reasons` (explainable risk factors)
- `reports` (CAM DOCX/PDF paths)
- `database_record.risk_id`

## Environment Variables

Copy `.env.example` to `.env` and set:
- `MONGODB_URI`
- `MONGODB_DB_NAME`
- `GEMINI_API_KEY`
- `GROQ_API_KEY`

If MongoDB is unavailable, backend still starts and returns disconnected status from `GET /`.

## Setup

### 1. Python environment and backend deps

```bash
python -m venv .venv
.venv\Scripts\activate
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Frontend deps

```bash
cd frontend
npm install
cd ..
```

## Run Commands

### Backend only

```bash
.venv\Scripts\activate
uvicorn backend.main:app --reload
```

Backend default URL: `http://127.0.0.1:8000`

### Frontend only

```bash
cd frontend
npm run dev
```

Frontend default URL: `http://127.0.0.1:3000`

### Full stack (recommended)

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\run-dev.ps1
```

This starts backend and frontend together with automatic port handling.

### 3. Install helper script

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\install-all.ps1
```

## Train Model

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\train-model.ps1
```

Writes model artifact to `models/credit_model.pkl`.

## Notes

- Frontend is now Vite-only (`frontend/src/main.jsx`).
- Legacy CRA source files were removed.
- `google.generativeai` currently emits deprecation warnings; migrating to `google.genai` is recommended in a later update.
- Browser CORS errors during analysis can be a symptom of backend exceptions; current backend hardening now surfaces structured failure details where possible.
