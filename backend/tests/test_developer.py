import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from app.models.user import User
from app.models.developer import Developer
from app.models.project import Project
from app.models.client import Client
from app.models.enums import UserRole, DeveloperRole
from app.main import app

@pytest.mark.anyio
async def test_developer_management_flow(db_session):
    from app.db.session import get_db
    from app.dependencies.auth import get_current_user
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Clean up leftover test users/developers first
    from sqlalchemy import delete
    await db_session.execute(delete(User).filter(User.email == "admin_devs@example.com"))
    await db_session.execute(delete(Developer).filter(Developer.email == "john.doe@example.com"))
    await db_session.commit()

    # Create an Admin user in DB for auth mocks
    admin_user = User(
        name="Admin Test User",
        email="admin_devs@example.com",
        password_hash="some_hashed_pass",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)

    # Helper dependency override to simulate logged-in Admin
    async def override_get_current_user_admin():
        return admin_user

    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 1. Admin can create developer
            dev_data = {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+123456789",
                "role": "AI_ML"
            }
            res_create = await ac.post("/developers", json=dev_data)
            assert res_create.status_code == 201
            created_dev = res_create.json()
            assert created_dev["name"] == "John Doe"
            assert created_dev["email"] == "john.doe@example.com"
            assert created_dev["role"] == "AI_ML"
            assert created_dev["is_active"] is True
            assert created_dev["active_project_count"] == 0
            
            # 4. Developer email uniqueness works
            res_dup = await ac.post("/developers", json=dev_data)
            assert res_dup.status_code == 400
            assert "already registered" in res_dup.json()["detail"].lower()

            # 5. Admin can list developers
            res_list = await ac.get("/developers")
            assert res_list.status_code == 200
            dev_list = res_list.json()
            assert len(dev_list) >= 1
            assert any(d["email"] == "john.doe@example.com" for d in dev_list)

            # 6. Admin can retrieve a developer
            dev_id = created_dev["id"]
            res_get = await ac.get(f"/developers/{dev_id}")
            assert res_get.status_code == 200
            assert res_get.json()["name"] == "John Doe"

            # Check 404 for non-existent and invalid UUID
            res_not_found = await ac.get(f"/developers/{uuid.uuid4()}")
            assert res_not_found.status_code == 404
            res_invalid_uuid = await ac.get("/developers/not-a-valid-uuid")
            assert res_invalid_uuid.status_code == 404

            # 7. Admin can update a developer
            update_data = {
                "name": "John Updated",
                "role": "DEVOPS"
            }
            res_update = await ac.patch(f"/developers/{dev_id}", json=update_data)
            assert res_update.status_code == 200
            assert res_update.json()["name"] == "John Updated"
            assert res_update.json()["role"] == "DEVOPS"

            # 8. Admin can deactivate a developer (soft-delete)
            res_delete = await ac.delete(f"/developers/{dev_id}")
            assert res_delete.status_code == 200
            assert res_delete.json()["is_active"] is False

            # 9. Deactivated developer remains in database
            result = await db_session.execute(
                select(Developer).filter(Developer.id == uuid.UUID(dev_id))
            )
            db_dev = result.scalar_one_or_none()
            assert db_dev is not None
            assert db_dev.is_active is False

            # 10. Active project count is returned correctly
            # Reactivate developer for project count check
            db_dev.is_active = True
            await db_session.commit()

            # Create a mock client
            client = Client(
                name="Client Name",
                company="Test Client Co",
                email="client@example.com",
                phone="999888777",
                required_role=DeveloperRole.AI_ML
            )
            db_session.add(client)
            await db_session.commit()
            await db_session.refresh(client)

            # Assign an active project
            project_active = Project(
                client_id=client.id,
                developer_id=db_dev.id,
                name="Project Alpha",
                status="active"
            )
            # Assign an inactive project
            project_inactive = Project(
                client_id=client.id,
                developer_id=db_dev.id,
                name="Project Beta",
                status="completed"
            )
            db_session.add_all([project_active, project_inactive])
            await db_session.commit()

            res_get_project_count = await ac.get(f"/developers/{dev_id}")
            assert res_get_project_count.status_code == 200
            assert res_get_project_count.json()["active_project_count"] == 1

            # Clean up projects and client
            await db_session.delete(project_active)
            await db_session.delete(project_inactive)
            await db_session.delete(client)
            await db_session.delete(db_dev)
            await db_session.commit()

        # Clean up admin user
        await db_session.delete(admin_user)
        await db_session.commit()

    finally:
        app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_developer_authorization_and_unauthenticated(db_session):
    from app.db.session import get_db
    from app.dependencies.auth import get_current_user
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        # Test 2 & 11: Unauthenticated request fails
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res_unauth = await ac.get("/developers")
            assert res_unauth.status_code == 401

            res_unauth_post = await ac.post("/developers", json={})
            assert res_unauth_post.status_code == 401

        # Test 3 & 11: Non-admin fails
        async def override_get_current_user_non_admin():
            return User(
                name="Staff User",
                email="staff@example.com",
                password_hash="some_hashed_pass",
                role="NON_ADMIN",
                is_active=True
            )

        app.dependency_overrides[get_current_user] = override_get_current_user_non_admin

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res_non_admin = await ac.get("/developers")
            assert res_non_admin.status_code == 403

            res_non_admin_post = await ac.post("/developers", json={
                "name": "Jane",
                "email": "jane@example.com",
                "role": "DEVOPS"
            })
            assert res_non_admin_post.status_code == 403

    finally:
        app.dependency_overrides.clear()
