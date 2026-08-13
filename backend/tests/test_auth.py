import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from jose import jwt
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import verify_password
from app.core.config import settings
from app.main import app

@pytest.mark.anyio
async def test_auth_flow(db_session):
    from app.db.session import get_db
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            signup_data = {
                "name": "Test Admin",
                "email": "admin_test@example.com",
                "password": "securepassword123"
            }

            # 1a. Signup fails with missing header
            res_no_hdr = await ac.post("/auth/signup", json=signup_data)
            assert res_no_hdr.status_code == 403  # Restricted access on missing header

            # 1b. Signup fails with invalid header
            res_bad_hdr = await ac.post(
                "/auth/signup",
                json=signup_data,
                headers={"X-Signup-Token": "wrong_token_123"}
            )
            assert res_bad_hdr.status_code == 403
            assert "restricted" in res_bad_hdr.json()["detail"].lower()

            # 1c. Successful signup with valid token header
            res = await ac.post(
                "/auth/signup",
                json=signup_data,
                headers={"X-Signup-Token": settings.SIGNUP_SECRET}
            )
            assert res.status_code == 201
            data = res.json()
            assert data["email"] == "admin_test@example.com"
            assert data["name"] == "Test Admin"
            assert data["role"] == "ADMIN"
            assert "password" not in data
            assert "password_hash" not in data

            # 2. Duplicate email rejected
            res_dup = await ac.post(
                "/auth/signup",
                json=signup_data,
                headers={"X-Signup-Token": settings.SIGNUP_SECRET}
            )
            assert res_dup.status_code == 400
            assert "already registered" in res_dup.json()["detail"].lower()

            # 3. Password is hashed in DB
            result = await db_session.execute(
                select(User).filter(User.email == "admin_test@example.com")
            )
            db_user = result.scalar_one()
            assert db_user.password_hash != "securepassword123"
            assert verify_password("securepassword123", db_user.password_hash)

            # 4. Successful login
            login_data = {
                "email": "admin_test@example.com",
                "password": "securepassword123"
            }
            res_login = await ac.post("/auth/login", json=login_data)
            assert res_login.status_code == 200
            login_res = res_login.json()
            assert "access_token" in login_res
            assert login_res["token_type"] == "bearer"
            token = login_res["access_token"]

            # 5. Wrong password rejected
            wrong_login = {
                "email": "admin_test@example.com",
                "password": "wrongpassword"
            }
            res_wrong = await ac.post("/auth/login", json=wrong_login)
            assert res_wrong.status_code == 401
            assert "incorrect" in res_wrong.json()["detail"].lower()

            # 5.5 Inactive user login rejected
            db_user.is_active = False
            await db_session.commit()
            
            res_inactive_login = await ac.post("/auth/login", json=login_data)
            assert res_inactive_login.status_code == 400
            assert "inactive user" in res_inactive_login.json()["detail"].lower()
            
            # Restore active status
            db_user.is_active = True
            await db_session.commit()

            # 6. Valid JWT allows /auth/me
            headers = {"Authorization": f"Bearer {token}"}
            res_me = await ac.get("/auth/me", headers=headers)
            assert res_me.status_code == 200
            me_data = res_me.json()
            assert me_data["email"] == "admin_test@example.com"
            assert "password_hash" not in me_data

            # 7. Invalid JWT rejected
            bad_headers = {"Authorization": "Bearer invalidtoken123"}
            res_bad = await ac.get("/auth/me", headers=bad_headers)
            assert res_bad.status_code == 401

            # 7.5 JWT non-UUID subject rejected
            from datetime import datetime, timezone, timedelta
            payload = {
                "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
                "sub": "not-a-valid-uuid"
            }
            bad_uuid_token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
            res_bad_uuid = await ac.get("/auth/me", headers={"Authorization": f"Bearer {bad_uuid_token}"})
            assert res_bad_uuid.status_code == 401

            # 8. Missing JWT rejected
            res_missing = await ac.get("/auth/me")
            assert res_missing.status_code == 401

            # 9. Inactive user profile access rejected
            db_user.is_active = False
            await db_session.commit()

            res_inactive = await ac.get("/auth/me", headers=headers)
            assert res_inactive.status_code == 400
            assert "inactive user" in res_inactive.json()["detail"].lower()

            # Restore active status
            db_user.is_active = True
            await db_session.commit()

            # 10. Admin authorization works
            from app.dependencies.auth import require_admin, get_current_user
            from fastapi import Depends
            
            @app.get("/test-admin-only-route")
            async def admin_only_route(current_user: User = Depends(require_admin)):
                return {"message": "success"}

            res_admin_ok = await ac.get("/test-admin-only-route", headers=headers)
            assert res_admin_ok.status_code == 200
            assert res_admin_ok.json() == {"message": "success"}

            # Test admin validation failure by overriding get_current_user
            async def override_get_current_user_non_admin():
                return User(
                    id=db_user.id,
                    name=db_user.name,
                    email=db_user.email,
                    role="NON_ADMIN",
                    is_active=True
                )
            
            app.dependency_overrides[get_current_user] = override_get_current_user_non_admin
            res_admin_fail = await ac.get("/test-admin-only-route", headers=headers)
            assert res_admin_fail.status_code == 403

            # Cleanup
            app.dependency_overrides[get_current_user] = override_get_db
            await db_session.delete(db_user)
            await db_session.commit()

    finally:
        app.dependency_overrides.clear()
