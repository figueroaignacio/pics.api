# Pics API

A production-ready REST API for a personal photography gallery, built with **FastAPI**, **SQLAlchemy 2.0 (async)**, and **PostgreSQL on Neon**. Images are stored on **Cloudflare Images** — this API manages only the metadata.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Package manager | uv |
| Database | PostgreSQL (Neon serverless) |
| ORM | SQLAlchemy 2.0 async |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Image hosting | Cloudflare Images |
| Server | Uvicorn |

---

## Project Structure

```
pics.api/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py       # GET /health
│   │   │   └── photos.py       # CRUD /photos
│   │   └── router.py           # Aggregated router
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── exceptions.py       # Custom exception classes
│   │   ├── logging.py          # Structured logging setup
│   │   └── responses.py        # JSON envelope helpers
│   ├── db/
│   │   ├── base.py             # SQLAlchemy DeclarativeBase
│   │   ├── engine.py           # Async engine factory
│   │   └── session.py          # AsyncSession + get_db dependency
│   ├── dependencies/
│   │   ├── database.py         # Re-exports get_db
│   │   └── pagination.py       # PaginationParams dependency
│   ├── models/
│   │   └── photo.py            # Photo SQLAlchemy model
│   ├── repositories/
│   │   └── photo_repository.py # DB access layer
│   ├── schemas/
│   │   └── photo.py            # Pydantic v2 schemas
│   ├── services/
│   │   └── photo_service.py    # Business logic layer
│   └── main.py                 # Application factory
├── migrations/
│   ├── versions/
│   │   └── 0001_initial.py     # Initial migration
│   ├── env.py                  # Async Alembic env
│   └── script.py.mako          # Migration file template
├── .env                        # Local secrets (git-ignored)
├── .env.example                # Safe-to-commit template
├── .gitignore
├── alembic.ini
└── pyproject.toml
```

---

## Getting Started

### 1. Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) installed (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A [Neon](https://neon.tech) PostgreSQL database
- A [Cloudflare Images](https://developers.cloudflare.com/images/) account

### 2. Clone & install dependencies

```bash
git clone <your-repo-url>
cd pics.api
uv sync
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your real values:

```dotenv
DATABASE_URL="postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require"
CLOUDFLARE_ACCOUNT_ID="..."
CLOUDFLARE_API_TOKEN="..."
CLOUDFLARE_IMAGES_DELIVERY_URL="https://imagedelivery.net/your-account-hash"
```

> **Note:** The app automatically converts `postgresql://` → `postgresql+asyncpg://` for you.

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

### 5. Start the development server

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/photos` | List photos (paginated, filterable) |
| `GET` | `/photos/{id}` | Get a single photo |
| `POST` | `/photos` | Create a new photo |
| `PATCH` | `/photos/{id}` | Partially update a photo |
| `DELETE` | `/photos/{id}` | Delete a photo |

### Query parameters for `GET /photos`

| Parameter | Type | Description |
|---|---|---|
| `page` | `int` | Page number (default: 1) |
| `size` | `int` | Items per page (default: 20, max: 100) |
| `category` | `string` | Filter by category (partial, case-insensitive) |
| `favorite` | `bool` | Filter by favourite status |
| `search` | `string` | Search by title (partial, case-insensitive) |

---

## Interactive Documentation

| URL | Tool |
|---|---|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |

---

## Response Format

All responses use a consistent JSON envelope:

**Success:**
```json
{
    "success": true,
    "message": "Photos retrieved successfully.",
    "data": { ... }
}
```

**Error:**
```json
{
    "success": false,
    "message": "Photo with id '...' was not found.",
    "errors": []
}
```

---

## Creating a Photo

Images must be uploaded to Cloudflare Images **before** calling this API. Then pass the resulting ID and URL:

```bash
curl -X POST http://localhost:8000/photos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Golden Hour at Patagonia",
    "cloudflare_image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "image_url": "https://imagedelivery.net/account/image-id/public",
    "category": "Landscape",
    "location": "Torres del Paine, Chile",
    "favorite": true
  }'
```

---

## Alembic — Creating New Migrations

After modifying a model, auto-generate a migration:

```bash
uv run alembic revision --autogenerate -m "add_new_column"
uv run alembic upgrade head
```

Roll back one step:

```bash
uv run alembic downgrade -1
```

---

## Architecture

```
Request → Route → Service → Repository → Database
                ↑               ↑
           Schemas          ORM Model
          (Pydantic)      (SQLAlchemy)
```

- **Routes** — zero business logic; inject service, return envelope
- **Services** — business rules, raise domain exceptions
- **Repositories** — pure DB access, return ORM instances
- **Schemas** — request validation (Pydantic v2) and response serialisation

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `CLOUDFLARE_ACCOUNT_ID` | ✅ | Cloudflare account ID |
| `CLOUDFLARE_API_TOKEN` | ✅ | Cloudflare API token |
| `CLOUDFLARE_IMAGES_DELIVERY_URL` | ✅ | Base delivery URL |
| `APP_ENV` | ❌ | `development` / `staging` / `production` (default: `development`) |
| `APP_NAME` | ❌ | Application name shown in docs |
| `CORS_ORIGINS` | ❌ | JSON array of allowed origins (default: `["*"]`) |
