import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete
from app.models.user import User
from app.models.client import Client
from app.models.developer import Developer
from app.models.project import Project
from app.models.customer_request import CustomerRequest
from app.models.enums import UserRole, DeveloperRole, ApprovalStatus
from app.dependencies.auth import require_admin
from app.main import app

@pytest.mark.anyio
async def test_customer_request_flow(db_session):
    from app.db.session import get_db
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Clean up stale data
    await db_session.execute(delete(User).filter(User.email == "admin_reqs@example.com"))
    await db_session.execute(delete(CustomerRequest))
    await db_session.execute(delete(Project))
    await db_session.execute(delete(Client).filter(Client.email == "req_client@example.com"))
    await db_session.execute(delete(Developer).filter(Developer.email.in_(["dev_req1@example.com", "dev_req2@example.com"])))
    await db_session.commit()

    # Create admin
    admin_user = User(
        name="Admin Request Manager",
        email="admin_reqs@example.com",
        password_hash="some_hashed_pass",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)

    # Create client
    client = Client(
        name="Request Client",
        company="Req Co",
        email="req_client@example.com",
        required_role=DeveloperRole.AI_ML,
        status="active"
    )
    db_session.add(client)

    # Create matching active developer
    active_dev = Developer(
        name="Active AI ML Dev",
        email="dev_req1@example.com",
        role=DeveloperRole.AI_ML,
        is_active=True
    )
    # Create inactive developer
    inactive_dev = Developer(
        name="Inactive AI ML Dev",
        email="dev_req2@example.com",
        role=DeveloperRole.AI_ML,
        is_active=False
    )
    db_session.add(active_dev)
    db_session.add(inactive_dev)
    await db_session.commit()
    await db_session.refresh(client)
    await db_session.refresh(active_dev)
    await db_session.refresh(inactive_dev)

    # Helper dependency overrides
    async def override_require_admin():
        return admin_user

    async def override_require_admin_forbidden():
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not enough permissions")

    transport = ASGITransport(app=app)

    # Test 11: Non-admin cannot manage requests
    app.dependency_overrides[require_admin] = override_require_admin_forbidden
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/customer-requests")
        assert res.status_code == 403

    # Switch to admin
    app.dependency_overrides[require_admin] = override_require_admin
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test 3: Request requires existing client
        res_fail_client = await ac.post("/customer-requests", json={
            "client_id": str(uuid.uuid4()),
            "required_role": "AI_ML"
        })
        assert res_fail_client.status_code == 404

        # Test 4: Invalid developer is rejected
        res_fail_dev_exists = await ac.post("/customer-requests", json={
            "client_id": str(client.id),
            "required_role": "AI_ML",
            "recommended_developer_id": str(uuid.uuid4())
        })
        assert res_fail_dev_exists.status_code == 404

        # Test 5: Inactive developer is rejected
        res_fail_inactive = await ac.post("/customer-requests", json={
            "client_id": str(client.id),
            "required_role": "AI_ML",
            "recommended_developer_id": str(inactive_dev.id)
        })
        assert res_fail_inactive.status_code == 400

        # Test 6: Developer role mismatch is rejected
        res_fail_role = await ac.post("/customer-requests", json={
            "client_id": str(client.id),
            "required_role": "DEVOPS", # mismatch
            "recommended_developer_id": str(active_dev.id)
        })
        assert res_fail_role.status_code == 400

        # Test 1 & 2 & 7: Admin can create request, starts as PENDING, matching developer works
        res_create = await ac.post("/customer-requests", json={
            "client_id": str(client.id),
            "required_role": "AI_ML",
            "recommended_developer_id": str(active_dev.id)
        })
        assert res_create.status_code == 201
        created_req = res_create.json()
        assert created_req["approval_status"] == ApprovalStatus.PENDING
        req_id = created_req["id"]

        # Test 10: Invalid approval transition is rejected (cannot change to PENDING)
        res_fail_pending = await ac.patch(f"/customer-requests/{req_id}/approval", json={
            "approval_status": "PENDING"
        })
        assert res_fail_pending.status_code == 400

        # Test 9: PENDING -> REJECTED works
        res_reject = await ac.patch(f"/customer-requests/{req_id}/approval", json={
            "approval_status": "REJECTED"
        })
        assert res_reject.status_code == 200
        assert res_reject.json()["approval_status"] == ApprovalStatus.REJECTED

        # Test 10: Cannot transition once approved/rejected
        res_fail_re_approve = await ac.patch(f"/customer-requests/{req_id}/approval", json={
            "approval_status": "APPROVED"
        })
        assert res_fail_re_approve.status_code == 400

        # Test 8: PENDING -> APPROVED works (on a new request)
        res_create2 = await ac.post("/customer-requests", json={
            "client_id": str(client.id),
            "required_role": "AI_ML"
        })
        req_id2 = res_create2.json()["id"]
        res_approve = await ac.patch(f"/customer-requests/{req_id2}/approval", json={
            "approval_status": "APPROVED"
        })
        assert res_approve.status_code == 200
        assert res_approve.json()["approval_status"] == ApprovalStatus.APPROVED

    app.dependency_overrides.clear()
