from uuid import UUID

from Backend.database import SessionLocal
from Backend.Dal.models import Provider


provider_id = UUID("768f0319-a5dc-5056-9f27-1afc9f71f2aa")

print("1. Opening session")

db = SessionLocal()

try:
    print("2. Before query")

    provider = db.get(Provider, provider_id)

    print("3. After query")
    print("Provider:", provider)

finally:
    db.close()
    print("4. Session closed")