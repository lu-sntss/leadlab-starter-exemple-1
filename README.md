# LeadLab Starter

Monorepo: FastAPI (backend) + React/Vite (frontend) + shared.

## Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1  |  Linux/Mac: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
leadlab check-db     # testa conexão
leadlab init-db      # cria tabelas
leadlab run          # http://localhost:8000
