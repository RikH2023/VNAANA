from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from Backend.config import get_settings

bearer_scheme=HTTPBearer(auto_error=False)

async def get_authenticated_subject(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> UUID:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Sign-in required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings = get_settings()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
                headers={
                    "apikey": settings.supabase_publishable_key,
                    "Authorization": f"Bearer {credentials.credentials}",
                },
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Authentication service is unavailable.",
        ) from exc

    if response.status_code in (401, 403):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="Authentication service could not verify the request.",
        )

    try:
        return UUID(response.json()["id"])
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Authentication service returned an unexpected response.",
        ) from exc


AuthenticatedSubject = Annotated[
    UUID,
    Depends(get_authenticated_subject),
]