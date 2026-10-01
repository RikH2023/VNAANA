# VNAANA API

FastAPI backend for VNAANA, split into three layers:

```
VNAANA/
├── requirements.txt
├── .env.example             # copy to .env (stays in this folder)
├── README.md
└── Backend/
    ├── main.py              # creates the app, registers routers + error handlers
    ├── config.py            # settings from env / .env
    ├── presentation/        # HTTP only
    │   ├── routers/         # users.py, stories.py, articles.py
    │   ├── schemas/         # Pydantic request/response models
    │   ├── dependencies.py  # session -> service wiring
    │   └── error_handlers.py # logic errors -> HTTP status codes
    ├── logic/               # business rules, no HTTP and no SQL
    │   ├── user_service.py
    │   ├── story_service.py
    │   ├── article_service.py
    │   └── exceptions.py
    └── dal/                 # database only
        ├── database.py      # engine, SessionLocal, get_db
        ├── models/          # maps each existing table (9 tables)
        └── repositories/    # all queries live here
```

A request goes **router → service → repository → database**. A layer only
talks to the layer directly below it.

The API does **not** create or migrate the database. The schema is made
separately; the models in `dal/models/` only map onto those tables, so their
table and column names must match it.

## Run it

Run everything from the `VNAANA` folder (not from inside `Backend`), so the
`Backend.` imports and the `.env` file are found:

```bash
python -m venv .venv && .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env          # set DATABASE_URL to the existing database
uvicorn Backend.main:app --reload
```

Swagger docs: http://localhost:8000/docs

## Endpoints

| Method | Path | What it does |
|---|---|---|
| POST | /users | Create user (consent defaults to false) |
| GET / PATCH / DELETE | /users/{id} | Read, update profile, erase (also deletes events + tags) |
| PUT | /users/{id}/consent | Set analytics consent, stamps consent_updated_at |
| GET / PUT | /users/{id}/tags | Read / replace interests |
| POST / GET | /users/{id}/events | Log / list engagement events (403 without consent) |
| GET | /stories | List, `?status=` (default published), `?tag_id=`, `limit`, `offset` |
| POST | /stories | Create story |
| GET / PATCH | /stories/{id} | Detail with tags + articles / update |
| PUT | /stories/{id}/tags | Replace tags with relevance scores |
| POST | /stories/{id}/articles | Link article (one primary per story) |
| DELETE | /stories/{id}/articles/{article_id} | Unlink article |
| GET | /articles | List, `?provider_id=`, `?language=`, `limit`, `offset` |
| POST | /articles | Ingest: 201 if new, 200 if the canonical_url already existed |
| GET | /articles/{id} | Detail incl. provider |

## Supabase database setup

The project uses a PostgreSQL database hosted by Supabase. SQLAlchemy handles database access, while Alembic manages changes to the database structure.

### Local environment

Create .env file if it does not exist in the Backend/.env
Add the connection URL that has been provided that has the following format:
```ini
DATABASE_URL="postgresql+psycopg://postgres.PROJECT_REFERENCE:URL_ENCODED_PASSWORD@POOLER_HOST:5432/postgres?sslmode=require"
```
The `.env` file is private and must not be committed.

### Install dependencies

From the project root, activate the virtual environment and install the project dependencies. The database setup requires SQLAlchemy, Alembic, psycopg, and python-dotenv.

### Test the connection

Run this command from the project root:
```powershell
python -m alembic current
```
A successful connection displays the current migration revision. Connection or authentication errors normally mean the URL, password, or pooler settings need to be checked.

### Synchronize the database

After pulling new code, apply migrations that other developers have added:
```powershell
python -m alembic upgrade head
```

This updates the database to the latest committed schema version.

Do not use `Base.metadata.create_all()` because Alembic manages the database structure.

### Making a database change

When changing a table:

1. Update the relevant SQLAlchemy model.
2. Generate a migration:

```powershell
python -m alembic revision --autogenerate -m "describe the change"
```
3. Review the generated file in `Backend/dal/migrations/versions`.
4. Check that it does not contain unexpected table or column deletions.
5. Commit both the model changes and migration file.
6. Apply the migration:

```powershell
python -m alembic upgrade head
```
Coordinate database changes with the team so that two developers do not create conflicting migrations at the same time.

### Important files

- `Backend/.env`: private database connection settings
- `Backend/dal/database.py`: SQLAlchemy connection configuration
- `Backend/dal/models/`: database models
- `Backend/dal/models/base.py`: shared SQLAlchemy Base
- `Backend/dal/migrations/`: Alembic configuration and migration history
- `Backend/dal/migrations/versions/`: individual database changes
- `alembic.ini`: Alembic project configuration

Never commit passwords, completed connection URLs, service-role keys, or other Supabase secrets.