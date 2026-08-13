import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete
from app.models.user import User
from app.models.client import Client
from app.models.enums import UserRole
from app.dependencies.auth import require_admin
from app.main import app

@pytest.mark.anyio
async def test_client_management_flow(db_session):
    from app.db.session import get_db
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Clean up leftover test users/clients first
    await db_session.execute(delete(User).filter(User.email == "admin_clients@example.com"))
    await db_session.execute(delete(Client).filter(Client.email.in_(["c1@example.com", "c2@example.com"])))
    await db_session.commit()

    # Create admin user
    admin_user = User(
        name="Admin Client Manager",
        email="admin_clients@example.com",
        password_hash="some_hashed_pass",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)

    # Helper dependency overrides
    async def override_require_admin():
        return admin_user

    async def override_require_admin_forbidden():
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not enough permissions")

    transport = ASGITransport(app=app)
    
    # Test 7: Non-admin cannot manage clients
    app.dependency_overrides[require_admin] = override_require_admin_forbidden
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/clients")
        assert res.status_code == 403

        res_post = await ac.post("/clients", json={
            "name": "C1", "company": "Co1", "email": "c1@example.com", "required_role": "AI_ML"
        })
        assert res_post.status_code == 403

    # Switch to Admin
    app.dependency_overrides[require_admin] = override_require_admin
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test 1: Admin can create client
        client_data = {
            "name": "Client One",
            "company": "Company One",
            "email": "c1@example.com",
            "phone": "123456",
            "requirement": "Need AI help",
            "required_role": "AI_ML"
        }
        res_create = await ac.post("/clients", json=client_data)
        assert res_create.status_code == 201
        created_client = res_create.json()
        assert created_client["name"] == "Client One"
        assert created_client["status"] == "active"
        client_id = created_client["id"]

        # Test 2: Duplicate email is rejected
        res_dup = await ac.post("/clients", json={
            "name": "Client Two",
            "company": "Company Two",
            "email": "c1@example.com",
            "required_role": "AI_ML"
        })
        assert res_dup.status_code == 400

        # Test 3: Admin can retrieve client
        res_get = await ac.get(f"/clients/{client_id}")
        assert res_get.status_code == 200
        assert res_get.json()["email"] == "c1@example.com"

        # Test 8: Invalid UUID is handled safely
        res_invalid_uuid = await ac.get("/clients/invalid-uuid-string")
        assert res_invalid_uuid.status_code == 404

        # Test 4: Admin can update client
        res_update = await ac.patch(f"/clients/{client_id}", json={
            "name": "Client One Updated",
            "company": "Company One Updated"
        })
        assert res_update.status_code == 200
        assert res_update.json()["name"] == "Client One Updated"

        # Test 5 & 6: Admin can deactivate client, remains in db
        res_delete = await ac.delete(f"/clients/{client_id}")
        assert res_delete.status_code == 200
        assert res_delete.json()["status"] == "inactive"

        # Verify client is still in DB (just status is inactive)
        result_db = await db_session.execute(select(Client).filter(Client.id == uuid.UUID(client_id)))
        db_client = result_db.scalar_one_or_none()
        assert db_client is not None
        assert db_client.status == "inactive"

    # Cleanup overrides
    app.dependency_overrides.clear()
