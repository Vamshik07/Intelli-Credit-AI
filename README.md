## Intelli Credit AI

Run backend (FastAPI) and frontend (React) together with one command from the project root.

### One-time setup

```bash
npm run install:all
```

### Start both services

```bash
npm run dev
```

Services:
- Frontend: `http://localhost:3000`
- Backend: auto-selected local port (prefers `http://127.0.0.1:8000`, falls back to a free port automatically)

### Notes

- The backend command uses the workspace virtual environment at `.venv/Scripts/python.exe`.
- The frontend receives the backend URL automatically through `REACT_APP_API_BASE_URL`.
- If `.venv` does not exist, create it first and install backend dependencies:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## Credit Model Features

The model now uses broad, low-overfit supplementary signals along with core financial inputs:

- `location_zone` (high-level region/economic zone, not exact city)
- `industry_type`
- `debt_ratio`
- `market_trend`
- `revenue`, `profit`, `debt`

To retrain with this feature set:

```bash
c:/Users/VAMSHI/OneDrive/Desktop/intelli-credit-ai/.venv/Scripts/python.exe train_model.py
```

## Currency UX

- Frontend auto-detects likely user currency from browser locale.
- Live FX rates are fetched from `open.er-api.com` and cached for 4 hours in browser storage.
- Users can manually switch display currency.
- Values are normalized before scoring, so backend predictions remain consistent.
