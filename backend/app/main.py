# -*- coding: utf-8 -*-
"""
Aplicação FastAPI mínima com ciclo de vida via lifespan.

- Startup: garante que o database existe e prepara o engine.
- Shutdown: libera conexões do SQLAlchemy.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv          # ⟵ adiciona isso
from app.core.database import Database

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()                       # ⟵ carrega backend/.env (ou .env na raiz)
    Database.initialize()
    try:
        yield
    finally:
        Database.dispose()

app = FastAPI(title="LeadLab Starter", lifespan=lifespan)

@app.get("/health", summary="Healthcheck")
def health():
    """Retorna status básico da API."""
    return {"status": "ok"}
