"""VNAANA API entry point.

Run:   (from the VNAANA folder) uvicorn Backend.main:app --reload
Docs:  http://localhost:8000/docs

Layers:
  presentation/  HTTP: routers, request/response schemas, error mapping
  logic/         business rules (services), no HTTP and no SQL
  dal/           database: models, session, repositories
"""
from fastapi import FastAPI

from Backend.presentation.error_handlers import register_error_handlers
from Backend.presentation.routers import articles, stories, users

app = FastAPI(
    title="VNAANA API",
    description="Backend for the Virtual News Anchor Against News Avoidance project.",
    version="0.1.0",
)

register_error_handlers(app)

app.include_router(users.router)
app.include_router(stories.router)
app.include_router(articles.router)
