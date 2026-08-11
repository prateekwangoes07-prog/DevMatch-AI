# DevMatch AI
"Intelligent Developer Allocation & Client Management Platform"

DevMatch AI is a production-oriented platform designed to orchestrate and optimize developer allocation and client relationships. This repository contains the Phase 1 project foundation.

## Technology Stack

- **Frontend:** Next.js (TypeScript, Tailwind CSS, shadcn/ui)
- **Backend:** FastAPI (Python, SQLAlchemy 2.0 Async, Pydantic, Alembic)
- **Database:** PostgreSQL 16
- **Infrastructure:** Docker & Docker Compose

## Quick Start (Development)

1. Make sure you have Docker and Docker Compose installed.
2. Copy the environment files:
   - `cp backend/.env.example backend/.env`
   - `cp frontend/.env.example frontend/.env`
3. Spin up the development services:
   ```bash
   docker compose up --build
   ```
4. Access the applications:
   - Frontend: `http://localhost:3000`
   - Backend API Docs: `http://localhost:8000/docs`
   - PostgreSQL: `localhost:5432`

## Project Structure

- `backend/`: FastAPI application code, Dockerfile, configurations, and alembic migrations.
- `frontend/`: Next.js frontend code and Docker configuration.
- `docs/`: Technical specifications and project rules.
