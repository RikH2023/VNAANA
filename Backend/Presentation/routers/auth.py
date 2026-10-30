from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from Backend.Presentation.auth import AuthenticatedSubject

router = APIRouter(prefix="/auth", tags=["Authentication"])

class AuthIdentityRead(BaseModel):
    auth_provider: str
    auth_subject: UUID

@router.get("/me", response_model=AuthIdentityRead)
async def get_my_identity(subject: AuthenticatedSubject,) -> AuthIdentityRead:
    return AuthIdentityRead(auth_provider="supabase", auth_subject=subject,)

