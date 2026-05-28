# Home Health MVP Foundation

## Frontend
- React + Vite + React Router
- Set `VITE_API_URL` to backend URL

```bash
cd frontend
npm install
npm run dev
```

## Backend
- FastAPI + SQLAlchemy + PostgreSQL

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
