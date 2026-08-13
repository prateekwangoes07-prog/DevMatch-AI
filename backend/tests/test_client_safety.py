"""
Phase 6 Safety Integration Tests
---------------------------------
1. Inactive client cannot create a CustomerRequest (HTTP 400).
2. Inactive client cannot receive a developer allocation (HTTP 400).
3. Active client works normally for both operations.
4. Client with a Project cannot be physically deleted (DB RESTRICT).
5. Client with a CustomerRequest cannot be physically deleted (DB RESTRICT).
"""
import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.client import Client
from app.models.developer import Developer
from app.models.project import Project
from app.models.customer_request import CustomerRequest
from app.models.enums import UserRole, DeveloperRole
from app.dependencies.auth import require_admin
from app.main import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _setup_admin(db_session, email: str) -> User:
    admin = User(
        name="Safety Test Admin",
        email=email,
        password_hash="hashed",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


async def _setup_client(db_session, email: str, status: str = "active") -> Client:
    client = Client(
        name="Safety Test Client",
        company="Safety Co",
        email=email,
        required_role=DeveloperRole.AI_ML,
        status=status,
    )
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    return client


async def _setup_developer(db_session, email: str, is_active: bool = True) -> Developer:
    dev = Developer(
        name="Safety Test Dev",
        email=email,
        role=DeveloperRole.AI_ML,
        is_active=is_active,
    )
    db_session.add(dev)
    await db_session.commit()
    await db_session.refresh(dev)
    return dev


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_inactive_client_cannot_create_customer_request(db_session):
    """Inactive client → CustomerRequest creation must return HTTP 400."""
    from app.db.session import get_db

    async def override_get_db():
        yield db_session

    # Clean up previous runs
    await db_session.execute(delete(CustomerRequest))
    await db_session.execute(delete(User).filter(User.email == "admin_safety1@example.com"))
    await db_session.execute(delete(Client).filter(Client.email == "inactive_client1@example.com"))
    await db_session.commit()

    admin = await _setup_admin(db_session, "admin_safety1@example.com")
    inactive_client = await _setup_client(db_session, "inactive_client1@example.com", status="inactive")

    async def override_require_admin():
        return admin

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_require_admin

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/customer-requests", json={
            "client_id": str(inactive_client.id),
            "required_role": "AI_ML"
        })
        assert res.status_code == 400, f"Expected 400 for inactive client, got {res.status_code}: {res.text}"
        assert "inactive" in res.json()["detail"].lower()

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_inactive_client_cannot_receive_allocation(db_session):
    """Inactive client → developer allocation must return HTTP 400."""
    from app.db.session import get_db

    async def override_get_db():
        yield db_session

    await db_session.execute(delete(Project))
    await db_session.execute(delete(User).filter(User.email == "admin_safety2@example.com"))
    await db_session.execute(delete(Client).filter(Client.email == "inactive_client2@example.com"))
    await db_session.execute(delete(Developer).filter(Developer.email == "dev_safety2@example.com"))
    await db_session.commit()

    admin = await _setup_admin(db_session, "admin_safety2@example.com")
    inactive_client = await _setup_client(db_session, "inactive_client2@example.com", status="inactive")
    dev = await _setup_developer(db_session, "dev_safety2@example.com")

    async def override_require_admin():
        return admin

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_require_admin

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(f"/developers/{dev.id}/allocate", json={
            "client_id": str(inactive_client.id),
            "project_name": "Safety Test Project"
        })
        assert res.status_code == 400, f"Expected 400 for inactive client allocation, got {res.status_code}: {res.text}"
        assert "inactive" in res.json()["detail"].lower()

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_active_client_can_create_customer_request(db_session):
    """Active client → CustomerRequest creation must succeed (HTTP 201)."""
    from app.db.session import get_db

    async def override_get_db():
        yield db_session

    await db_session.execute(delete(CustomerRequest))
    await db_session.execute(delete(User).filter(User.email == "admin_safety3@example.com"))
    await db_session.execute(delete(Client).filter(Client.email == "active_client3@example.com"))
    await db_session.commit()

    admin = await _setup_admin(db_session, "admin_safety3@example.com")
    active_client = await _setup_client(db_session, "active_client3@example.com", status="active")

    async def override_require_admin():
        return admin

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_require_admin

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/customer-requests", json={
            "client_id": str(active_client.id),
            "required_role": "AI_ML"
        })
        assert res.status_code == 201, f"Expected 201 for active client, got {res.status_code}: {res.text}"

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_client_with_project_cannot_be_physically_deleted(db_session):
    """
    Client with an existing Project must NOT be physically deletable.
    The DB RESTRICT constraint must raise an IntegrityError.
    """
    await db_session.execute(delete(Project))
    await db_session.execute(delete(Client).filter(Client.email == "restrict_client4@example.com"))
    await db_session.execute(delete(Developer).filter(Developer.email == "dev_restrict4@example.com"))
    await db_session.commit()

    client = await _setup_client(db_session, "restrict_client4@example.com")
    dev = await _setup_developer(db_session, "dev_restrict4@example.com")
    client_uuid = client.id  # capture before any delete attempt

    project = Project(
        client_id=client_uuid,
        developer_id=dev.id,
        name="Safety Test Project",
        status="active",
    )
    db_session.add(project)
    await db_session.commit()

    # Attempt physical delete of client — must fail
    with pytest.raises(IntegrityError):
        await db_session.execute(
            delete(Client).filter(Client.id == client_uuid)
        )
        await db_session.commit()

    await db_session.rollback()

    # Client must still exist — use text() to avoid expired ORM attribute access
    from sqlalchemy import text
    result = await db_session.execute(
        text("SELECT id FROM clients WHERE id = :cid"),
        {"cid": str(client_uuid)}
    )
    assert result.scalar_one_or_none() is not None, "Client should still exist after failed delete"


@pytest.mark.anyio
async def test_client_with_customer_request_cannot_be_physically_deleted(db_session):
    """
    Client with an existing CustomerRequest must NOT be physically deletable.
    The DB RESTRICT constraint must raise an IntegrityError.
    """
    await db_session.execute(delete(CustomerRequest))
    await db_session.execute(delete(Client).filter(Client.email == "restrict_client5@example.com"))
    await db_session.commit()

    client = await _setup_client(db_session, "restrict_client5@example.com")
    client_uuid = client.id  # capture before any delete attempt

    req = CustomerRequest(
        client_id=client_uuid,
        required_role=DeveloperRole.AI_ML,
    )
    db_session.add(req)
    await db_session.commit()

    with pytest.raises(IntegrityError):
        await db_session.execute(
            delete(Client).filter(Client.id == client_uuid)
        )
        await db_session.commit()

    await db_session.rollback()

    from sqlalchemy import text
    result = await db_session.execute(
        text("SELECT id FROM clients WHERE id = :cid"),
        {"cid": str(client_uuid)}
    )
    assert result.scalar_one_or_none() is not None, "Client should still exist after failed delete"
