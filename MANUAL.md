# NUTrack — How to Run Everything

## Quick start (Docker, recommended)

### Prerequisites
- Docker Desktop installed and running
- `backend/.env` file present (see Environment Variables section below)

### Run all services

```bash
docker compose up --build
```

| Service   | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost:3000      |
| Backend   | http://localhost:8000      |
| API docs  | http://localhost:8000/docs |
| Postgres  | localhost:5434             |
| Redis     | localhost:6380             |
| RustFS S3 | http://localhost:9000      |
| RustFS UI | http://localhost:9001      |

On first start the backend automatically runs `alembic upgrade head` before starting uvicorn.

### Stop everything

```bash
docker compose down
```

### Stop and wipe the database

```bash
docker compose down -v
```

---

## Environment variables (`backend/.env`)

Copy and fill in the secrets. The file must live at `backend/.env`.

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:qwerty12345@db:5432/senior_project
SYNC_DATABASE_URL=postgresql+psycopg2://postgres:qwerty12345@db:5432/senior_project

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Google OAuth  (create at https://console.cloud.google.com)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# JWT
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# AWS S3 (optional, leave blank to disable file uploads)
AWS_ACCESS_KEY=rustfsadmin
AWS_SECRET_KEY=rustfsadmin
AWS_BUCKET_NAME=course-materials
AWS_REGION=us-east-1
AWS_ENDPOINT_URL=http://rustfs:9000
AWS_PUBLIC_ENDPOINT_URL=http://localhost:9000
AWS_S3_FORCE_PATH_STYLE=true
MATERIAL_UPLOAD_STAGING_DIR=/tmp/material_uploads
MATERIAL_PRESIGNED_URL_TTL_SECONDS=900

# OpenAI (optional)
OPENAI_API_KEY=

# Semester config
CURRENT_TERM=Spring
CURRENT_YEAR=2026
```

> When running locally (no Docker) change `@db:` → `@localhost:` and `redis://redis:` → `redis://localhost:` in the URLs.

---

## Running the backend locally (without Docker)

### Requirements
- Python 3.12+
- `uv` — install with `pip install uv` or `curl -Ls https://astral.sh/uv/install.sh | sh`
- Postgres and Redis running locally

### Steps

```bash
cd backend

# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start the dev server
uv run uvicorn --app-dir src nutrack.main:app --host 0.0.0.0 --port 8000 --reload --loop asyncio
```

### Run tests

```bash
cd backend
uv run pytest tests/ -v
```

---

## Running the frontend locally (without Docker)

### Requirements
- Node.js 20+

### Steps

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Frontend will be at http://localhost:3000.

The frontend talks to the backend via `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000/v1` if not set).

---

## Database migrations (Alembic)

All commands run from the `backend/` directory.

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Roll back one migration
uv run alembic downgrade -1

# Check current revision
uv run alembic current

# Show migration history
uv run alembic history

# Create a new migration (after changing SQLAlchemy models)
uv run alembic revision --autogenerate -m "describe your change"
```

---

## Project structure

```
senior_project/
├── docker-compose.yml
├── backend/
│   ├── .env                  # secrets (not committed)
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic/
│   │   └── versions/         # migration files
│   └── src/nutrack/
│       ├── main.py
│       ├── config.py
│       ├── auth/
│       ├── users/
│       ├── courses/
│       ├── enrollments/
│       └── ...
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
```

---

## Common issues

| Error | Fix |
|-------|-----|
| `Multiple head revisions` | Two migration branches exist. Update the newer migration's `down_revision` to point to the latest head, then re-run `alembic upgrade head`. |
| `backend_app exited with code 255` | Usually a migration error or missing `.env`. Check `docker compose logs backend`. |
| `connection refused` on Postgres | DB container not healthy yet. Wait a few seconds or run `docker compose up db` first. |
| Frontend can't reach backend | Set `NEXT_PUBLIC_API_URL=http://localhost:8000/v1` in `frontend/.env.local`. |
