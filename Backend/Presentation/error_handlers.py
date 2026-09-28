"""Turns logic-layer errors into HTTP responses."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from Backend.logic.exceptions import ConflictError, ConsentRequiredError, DomainError, NotFoundError

_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    ConsentRequiredError: status.HTTP_403_FORBIDDEN,
}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        code = _STATUS_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=code, content={"detail": exc.message})
