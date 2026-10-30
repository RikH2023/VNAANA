"""Runs one scoring pass of the "For you" algorithm (design doc D11).

Run (from the VNAANA folder):  python -m Backend.run_algorithm

Meant to run once an hour. Hosting is out of scope, so for now that means
running it by hand or with a local scheduler (Windows Task Scheduler / cron).

Like run_news_gathering.py this is a composition root: the one place outside
the API that plugs DAL implementations into the Logic layer.
"""

from Backend.database import SessionLocal
from Backend.Dal.repositories.algorithm_repository import AlgorithmRepository
from Backend.Dal.repositories.user_repository import UserRepository
from Backend.Logic.algorithm_service import AlgorithmService


def main() -> None:
    db = SessionLocal()

    try:
        service = AlgorithmService(
            algorithm=AlgorithmRepository(db),
            users=UserRepository(db),
        )

        scored = service.run_scoring()

        # One commit for the whole run: if anything fails, every user keeps
        # their previous scores instead of ending up half updated.
        db.commit()

        print(f"Scored {scored} user(s).")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
