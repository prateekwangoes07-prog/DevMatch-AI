# API Guide: DevMatch AI

FastAPI will serve the REST endpoints under `/api/v1`. 

## Router Structure (Planned)

All routers will be registered under `app/api/v1/endpoints/`:

- `/auth`: Sign-up, login (setting HttpOnly JWT cookies), logout.
- `/requests`: Customer/client request intake and status updates.
- `/developers`: List, search, and update developer profiles/skills.
- `/allocations`: Recommended match lookup, approvals, and assignments.

## Design Rules

1. **Schemas (Pydantic):** All input and output request payloads must map to Pydantic schemas for verification and strict typing.
2. **Dependency Injection:** Database sessions, current authenticated user instances, and services must be injected using FastAPI `Depends`.
3. **Repository Pattern:** Direct SQL queries (via SQLAlchemy 2.0 async) must be isolated within the `repositories/` directory rather than directly in controllers or routers.
