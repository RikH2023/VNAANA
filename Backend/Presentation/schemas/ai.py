"""Request and response contracts for article-only AI endpoints."""

from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator

from Backend.Logic.ai_service import MAX_ARTICLE_CHARS, MAX_QUESTION_CHARS


class SummarizeRequest(BaseModel):
    article_text: str = Field(min_length=1, max_length=MAX_ARTICLE_CHARS)
    source_url: AnyHttpUrl | None = None
    language: Literal["en", "nl"]

    @field_validator("article_text")
    @classmethod
    def article_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("article_text must not be blank")
        return value


class AskRequest(SummarizeRequest):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_CHARS)

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question must not be blank")
        return value


class AIResponse(BaseModel):
    text: str
    sources: list[str]
    uncertainty: str
    status: Literal["answered", "insufficient_information"]
