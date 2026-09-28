"""Engine and session setup. This is the only place that knows the connection string."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from Backend.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, echo=settings.sql_echo, pool_pre_ping=True)

# expire_on_commit=False: objects keep their values after commit, so the
# presentation layer can still serialise them without extra queries.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """One session per request. Rolls back anything that wasn't committed."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
