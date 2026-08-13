import pytest
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from app.models.user import User
from app.models.developer import Developer
from app.models.client import Client
from app.models.project import Project
from app.models.enums import UserRole, DeveloperRole
from app.main import app

@pytest.mark.anyio
async def test_developer_availability_and_allocation(db_session):
    from app.db.session import get_db
    from app.dependencies.auth import get_current_user
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Clean up leftover test users/developers first
    from sqlalchemy import delete
    await db_session.execute(delete(User).filter(User.email == "admin_alloc@example.com"))
    await db_session.execute(delete(Client).filter(Client.email.in_(["c1@example.com", "c2@example.com", "c3@example.com", "c4@example.com"])))
    await db_session.execute(delete(Developer).filter(Developer.email.in_(["d1@example.com", "d2@example.com"])))
    await db_session.commit()

    # Create admin user
    admin_user = User(
        name="Admin Alloc User",
        email="admin_alloc@example.com",
        password_hash="pass",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)
    await db_session.commit()

    async def override_get_current_user_admin():
        return admin_user

    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Create active AI_ML developer
            dev = Developer(
                name="AI ML Dev",
                email="d1@example.com",
                phone="111",
                role=DeveloperRole.AI_ML,
                is_active=True
            )
            # Create inactive AI_ML developer
            inactive_dev = Developer(
                name="Inactive Dev",
                email="d2@example.com",
                phone="222",
                role=DeveloperRole.AI_ML,
                is_active=False
            )
            db_session.add_all([dev, inactive_dev])
            await db_session.commit()
            await db_session.refresh(dev)
            await db_session.refresh(inactive_dev)

            # Create clients
            client1 = Client(
                name="Client 1", company="C1", email="c1@example.com", phone="12", required_role=DeveloperRole.AI_ML
            )
            client2 = Client(
                name="Client 2", company="C2", email="c2@example.com", phone="34", required_role=DeveloperRole.AI_ML
            )
            client_wrong_role = Client(
                name="Client 3", company="C3", email="c3@example.com", phone="56", required_role=DeveloperRole.DEVOPS
            )
            db_session.add_all([client1, client2, client_wrong_role])
            await db_session.commit()
            await db_session.refresh(client1)
            await db_session.refresh(client2)
            await db_session.refresh(client_wrong_role)

            # 1. Active AI/ML developer with 0 projects -> available
            res_avail = await ac.get("/developers/available?required_role=AI_ML")
            assert res_avail.status_code == 200
            avail_list = res_avail.json()
            assert any(d["id"] == str(dev.id) for d in avail_list)
            assert not any(d["id"] == str(inactive_dev.id) for d in avail_list) # 4. Inactive -> unavailable

            # 5. Wrong role -> unavailable
            res_avail_devops = await ac.get("/developers/available?required_role=DEVOPS")
            assert res_avail_devops.status_code == 200
            assert not any(d["id"] == str(dev.id) for d in res_avail_devops.json())

            # 7. Allocation succeeds when developer has 0 projects
            alloc_data1 = {
                "client_id": str(client1.id),
                "project_name": "Project Alpha"
            }
            res_alloc1 = await ac.post(f"/developers/{dev.id}/allocate", json=alloc_data1)
            assert res_alloc1.status_code == 201
            assert res_alloc1.json()["project_name"] == "Project Alpha"
            db_session.expire(dev)

            # 2. Active AI/ML developer with 1 active project -> available
            res_avail_1 = await ac.get("/developers/available?required_role=AI_ML")
            dev_entry = next(d for d in res_avail_1.json() if d["id"] == str(dev.id))
            assert dev_entry["active_project_count"] == 1
            assert dev_entry["available"] is True

            # 8. Allocation succeeds when developer has 1 active project
            alloc_data2 = {
                "client_id": str(client2.id),
                "project_name": "Project Beta"
            }
            res_alloc2 = await ac.post(f"/developers/{dev.id}/allocate", json=alloc_data2)
            assert res_alloc2.status_code == 201
            db_session.expire(dev)

            # 3. Active AI/ML developer with 2 active projects -> unavailable
            res_avail_2 = await ac.get("/developers/available?required_role=AI_ML")
            assert not any(d["id"] == str(dev.id) for d in res_avail_2.json())

            # 9. Allocation fails when developer already has 2 active projects
            client4 = Client(
                name="Client 4", company="C4", email="c4@example.com", phone="78", required_role=DeveloperRole.AI_ML
            )
            db_session.add(client4)
            await db_session.commit()
            await db_session.refresh(client4)

            alloc_data3 = {
                "client_id": str(client4.id),
                "project_name": "Project Gamma"
            }
            res_alloc3 = await ac.post(f"/developers/{dev.id}/allocate", json=alloc_data3)
            assert res_alloc3.status_code == 400
            assert "maximum active projects" in res_alloc3.json()["detail"].lower()

            # 6. Completed/non-active projects do not count
            # Set Project Alpha status to completed
            result_proj = await db_session.execute(
                select(Project).filter(Project.name == "Project Alpha")
            )
            p_alpha = result_proj.scalar_one()
            p_alpha.status = "completed"
            await db_session.commit()
            db_session.expire(dev)

            # Now active project count is 1 again, so available!
            res_avail_3 = await ac.get("/developers/available?required_role=AI_ML")
            assert any(d["id"] == str(dev.id) for d in res_avail_3.json())

            # 10. Allocation fails for inactive developer
            res_alloc_inactive = await ac.post(f"/developers/{inactive_dev.id}/allocate", json=alloc_data1)
            assert res_alloc_inactive.status_code == 400
            assert "inactive" in res_alloc_inactive.json()["detail"].lower()

            # 11. Allocation fails for role mismatch
            alloc_data_wrong = {
                "client_id": str(client_wrong_role.id),
                "project_name": "Project Delta"
            }
            res_alloc_wrong_role = await ac.post(f"/developers/{dev.id}/allocate", json=alloc_data_wrong)
            assert res_alloc_wrong_role.status_code == 400
            assert "role" in res_alloc_wrong_role.json()["detail"].lower()

            # 12. Allocation fails for nonexistent developer
            res_alloc_nonexistent = await ac.post(f"/developers/{uuid.uuid4()}/allocate", json=alloc_data1)
            assert res_alloc_nonexistent.status_code == 404

            # Cleanup
            await db_session.delete(p_alpha)
            # Find and delete other projects
            proj_list = await db_session.execute(select(Project))
            for p in proj_list.scalars().all():
                await db_session.delete(p)
            await db_session.delete(dev)
            await db_session.delete(inactive_dev)
            await db_session.delete(client1)
            await db_session.delete(client2)
            await db_session.delete(client_wrong_role)
            await db_session.delete(client4)
            await db_session.commit()

        # Clean up admin user
        await db_session.delete(admin_user)
        await db_session.commit()

    finally:
        app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_non_admin_availability_and_allocation_protections(db_session):
    from app.db.session import get_db
    from app.dependencies.auth import get_current_user
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Create transient non-admin user mock
    async def override_get_current_user_non_admin():
        return User(
            name="Non Admin User",
            email="non_admin@example.com",
            password_hash="pass",
            role="STAFF",
            is_active=True
        )

    app.dependency_overrides[get_current_user] = override_get_current_user_non_admin

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 13. Non-admin cannot access availability endpoint -> 403
            res_avail = await ac.get("/developers/available?required_role=AI_ML")
            assert res_avail.status_code == 403

            # 14. Non-admin cannot allocate -> 403
            res_alloc = await ac.post(f"/developers/{uuid.uuid4()}/allocate", json={
                "client_id": str(uuid.uuid4()),
                "project_name": "New Project"
            })
            assert res_alloc.status_code == 403

    finally:
        app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_allocation_concurrency_safe(db_session):
    from app.db.session import SessionLocal
    from fastapi import HTTPException
    
    # Clean up leftover data using main session
    from sqlalchemy import delete
    await db_session.execute(delete(User).filter(User.email == "admin_race@example.com"))
    await db_session.execute(delete(Client).filter(Client.email.in_(["race_c1@example.com", "race_c2@example.com", "race_c3@example.com"])))
    await db_session.execute(delete(Developer).filter(Developer.email.in_(["race_d1@example.com", "race_d2@example.com"])))
    await db_session.commit()

    # Insert test data
    dev1 = Developer(
        name="Race Dev 1",
        email="race_d1@example.com",
        phone="999",
        role=DeveloperRole.AI_ML,
        is_active=True
    )
    dev2 = Developer(
        name="Race Dev 2",
        email="race_d2@example.com",
        phone="888",
        role=DeveloperRole.AI_ML,
        is_active=True
    )
    client1 = Client(
        name="Race Client 1",
        company="C1",
        email="race_c1@example.com",
        phone="12",
        required_role=DeveloperRole.AI_ML
    )
    client2 = Client(
        name="Race Client 2",
        company="C2",
        email="race_c2@example.com",
        phone="34",
        required_role=DeveloperRole.AI_ML
    )
    client3 = Client(
        name="Race Client 3",
        company="C3",
        email="race_c3@example.com",
        phone="56",
        required_role=DeveloperRole.AI_ML
    )
    db_session.add_all([dev1, dev2, client1, client2, client3])
    await db_session.commit()
    await db_session.refresh(dev1)
    await db_session.refresh(dev2)
    await db_session.refresh(client1)
    await db_session.refresh(client2)
    await db_session.refresh(client3)

    # Put dev1 at 1 active project initially
    init_proj = Project(
        client_id=client1.id,
        developer_id=dev1.id,
        name="Init Proj",
        status="active"
    )
    db_session.add(init_proj)
    await db_session.commit()

    from app.services.allocation_service import AllocationService

    # --- Test Case A: Developer maximum-2 active project safety ---
    async def allocate_dev1_c2():
        async with SessionLocal() as session:
            try:
                await AllocationService.allocate_developer(session, dev1.id, client2.id, "Proj C2")
                return ("SUCCESS", 201, None)
            except HTTPException as e:
                return ("ERROR", e.status_code, e.detail)

    async def allocate_dev1_c3():
        async with SessionLocal() as session:
            try:
                await AllocationService.allocate_developer(session, dev1.id, client3.id, "Proj C3")
                return ("SUCCESS", 201, None)
            except HTTPException as e:
                return ("ERROR", e.status_code, e.detail)

    res_a1, res_a2 = await asyncio.gather(allocate_dev1_c2(), allocate_dev1_c3())
    results_a = [res_a1, res_a2]
    
    success_a = [r for r in results_a if r[0] == "SUCCESS"]
    error_a = [r for r in results_a if r[0] == "ERROR"]
    
    assert len(success_a) == 1
    assert len(error_a) == 1
    assert error_a[0][1] == 400
    assert "maximum active projects" in error_a[0][2].lower()

    # --- Test Case B: Client one active project safety (partial unique index) ---
    await db_session.execute(delete(Project))
    await db_session.commit()

    async def allocate_c1_to_dev1():
        async with SessionLocal() as session:
            try:
                await AllocationService.allocate_developer(session, dev1.id, client1.id, "Dev1 Proj")
                return ("SUCCESS", 201, None)
            except HTTPException as e:
                return ("ERROR", e.status_code, e.detail)

    async def allocate_c1_to_dev2():
        async with SessionLocal() as session:
            try:
                await AllocationService.allocate_developer(session, dev2.id, client1.id, "Dev2 Proj")
                return ("SUCCESS", 201, None)
            except HTTPException as e:
                return ("ERROR", e.status_code, e.detail)

    res_b1, res_b2 = await asyncio.gather(allocate_c1_to_dev1(), allocate_c1_to_dev2())
    results_b = [res_b1, res_b2]

    success_b = [r for r in results_b if r[0] == "SUCCESS"]
    error_b = [r for r in results_b if r[0] == "ERROR"]

    assert len(success_b) == 1
    assert len(error_b) == 1
    assert error_b[0][1] == 400
    assert "already has an active project assignment" in error_b[0][2].lower()

    # Clean up
    await db_session.execute(delete(Project))
    await db_session.delete(dev1)
    await db_session.delete(dev2)
    await db_session.delete(client1)
    await db_session.delete(client2)
    await db_session.delete(client3)
    await db_session.commit()


