# Home Health MVP Foundation

React + Vite frontend and FastAPI backend for concierge home health operations.

## Phase 5 production-readiness foundation

Phase 5 adds JWT authentication, admin/caregiver/family role gates, audit logging, secure local file-upload foundations, Alembic migrations, PostgreSQL support through `DATABASE_URL`, backup scripts/docs, Docker files, CI, CORS configuration, security headers, and safer production error responses.

> Privacy note: This app includes privacy-minded safeguards but is not automatically HIPAA compliant without proper hosting, BAAs, policies, encryption, access controls, and operational procedures.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` when the backend is not at `http://localhost:8000`.

## Backend local development

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python reset_db.py
python -m uvicorn app.main:app --reload --port 8000
```

Expected reset output:

```text
Local SQLite database reset complete.
```

Demo users seeded for local development:

- `admin@example.com` / `password123`
- `caregiver@example.com` / `password123`
- `family@example.com` / `password123`

## Environment

Copy `backend/.env.example` and set real staging/production values. `DATABASE_URL` is optional locally and defaults to SQLite. In production, set a PostgreSQL URL such as `postgresql+psycopg2://user:password@host:5432/dbname`.

Important variables:

- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- `CORS_ORIGINS=https://your-frontend.example`
- `MAX_UPLOAD_MB=10`
- `ENVIRONMENT=production`

## Migrations

Local/staging/production migrations use Alembic:

```bash
cd backend
alembic upgrade head
```

`reset_db.py` remains available for local SQLite resets only.

## Backups

Local SQLite backup:

```bash
cd backend
python scripts/backup_sqlite.py
```

PostgreSQL backup and restore examples are documented in `docs/backup-postgres.md`.

## Deployment

Backend production command:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend build command:

```bash
cd frontend
npm install && npm run build
```

Optional local full-stack containers:

```bash
docker compose up --build
```

CI is defined in `.github/workflows/ci.yml` and performs backend dependency install/import checks plus frontend install/build checks.
