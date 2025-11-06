from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
from app.core.config import settings

# Engine síncrono (simples e estável)
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    """Dependency FastAPI: fornece sessão e garante fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_all() -> None:
    """Cria todas as tabelas registradas em Base.metadata."""
    Base.metadata.create_all(bind=engine)
