"""AI endpoints using only caller-supplied article text."""

from fastapi import APIRouter, HTTPException

from Backend.Logic.ai_service import AIInputError, AIModelError
from Backend.Presentation.dependencies import AIServiceDep
from Backend.Presentation.schemas.ai import AIResponse, AskRequest, SummarizeRequest


router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/summarize", response_model=AIResponse)
def summarize(body: SummarizeRequest, service: AIServiceDep):
    try:
        return service.summarize(
            article_text=body.article_text,
            language=body.language,
            source_url=str(body.source_url) if body.source_url else None,
        )
    except AIInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except AIModelError as exc:
        raise HTTPException(status_code=503, detail="AI model unavailable or invalid response") from exc


@router.post("/ask", response_model=AIResponse)
def ask(body: AskRequest, service: AIServiceDep):
    try:
        return service.ask(
            article_text=body.article_text,
            question=body.question,
            language=body.language,
            source_url=str(body.source_url) if body.source_url else None,
        )
    except AIInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except AIModelError as exc:
        raise HTTPException(status_code=503, detail="AI model unavailable or invalid response") from exc
