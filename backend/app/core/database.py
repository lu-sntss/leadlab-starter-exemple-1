# -*- coding: utf-8 -*-
"""
Database bootstrap para o LeadLab Starter.

Responsabilidades:
- Ler DATABASE_URL do ambiente (PostgreSQL).
- Conectar no DB administrativo ("postgres") e criar o DB-alvo se não existir.
- Expor um engine pronto para uso pela aplicação.
- Liberar conexões no shutdown.
"""

from __future__ import annotations
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url, URL
from sqlalchemy.exc import OperationalError

log = logging.getLogger(__name__)

DEFAULT_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/leadlab"


class Database:
    """Gerencia a inicialização e acesso ao banco de dados."""
    engine = None  # SQLAlchemy Engine para o DB-alvo

    @staticmethod
    def _safe_url_str(url: URL) -> str:
        """String da URL sem expor senha (para logs/prints)."""
        try:
            return url.render_as_string(hide_password=True)
        except Exception:
            return str(url).replace(url.password or "", "*****") if getattr(url, "password", None) else str(url)

    @staticmethod
    def _get_urls() -> tuple[URL, URL, str]:
        """
        Resolve as URLs de conexão administrativa e de aplicação.

        Returns:
            (admin_url, app_url, db_name): URLs e nome do DB alvo.
        """
        app_url = make_url(os.getenv("DATABASE_URL", DEFAULT_URL))
        db_name = app_url.database or "leadlab"
        admin_url = app_url.set(database="postgres")  # DB administrativo padrão

        safe_app = Database._safe_url_str(app_url)
        print(f"[DB] ✅ DATABASE_URL resolvida: {safe_app}")
        print(f"[DB] 🎯 Database alvo: {db_name}")

        return admin_url, app_url, db_name

    @classmethod
    def ensure_database(cls) -> None:
        """
        Garante que o database alvo exista. Se não existir, cria.

        Observação:
            - CREATE DATABASE precisa de AUTOCOMMIT (fora de transação).
        """
        admin_url, app_url, db_name = cls._get_urls()

        # Engine administrativo (db=postgres) com AUTOCOMMIT
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        safe_admin = cls._safe_url_str(admin_url)

        with admin_engine.connect() as conn:
            print(f"[DB] 🔌 Conectado ao DB administrativo: {safe_admin}")
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            ).scalar() is not None

            if not exists:
                log.info("Criando database '%s'…", db_name)
                conn.execute(text(f'CREATE DATABASE "{db_name}" ENCODING \'UTF8\' TEMPLATE template1'))
                log.info("Database '%s' criado com sucesso.", db_name)
                print(f"[DB]  Database criado: {db_name}")
            else:
                print(f"[DB]  Database já existe: {db_name}")

        admin_engine.dispose()
        print("[DB]  Conexão administrativa liberada.")

        # Cria o engine do DB-alvo e testa conexão
        cls.engine = create_engine(app_url, pool_pre_ping=True)
        safe_app = cls._safe_url_str(app_url)
        print(f"[DB] 🛠️ Engine do aplicativo criado: {safe_app}")

        try:
            with cls.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("[DB] ✅ Teste de conexão ao DB-alvo: OK")
        except OperationalError as e:
            log.error("Falha ao conectar no DB-alvo: %s", e)
            raise

    @classmethod
    def initialize(cls) -> None:
        """Ponto único de inicialização do banco (idempotente)."""
        if cls.engine is None:
            print("[DB]  Inicializando Database…")
            cls.ensure_database()
            print("[DB]  Database pronto para uso.")

    @classmethod
    def dispose(cls) -> None:
        """Fecha conexões do engine no shutdown."""
        if cls.engine is not None:
            cls.engine.dispose()
            cls.engine = None
            print("[DB] 👋 Engine fechado e conexões liberadas.")