from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate, UserOut, UserLogin, Token
from app.dependencies.auth import get_current_user
from app.core.config import settings

router = APIRouter()

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    x_signup_token: str | None = Header(None, alias="X-Signup-Token")
):
    # Validate environment-controlled signup secret
    if not x_signup_token or x_signup_token != settings.SIGNUP_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signups are restricted. Invalid signup token."
        )

    # 1. Check duplicate email
    result = await db.execute(select(User).filter(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Hash password and create admin user
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password,
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login(login_in: UserLogin, db: AsyncSession = Depends(get_db)):
    # 1. Retrieve user
    result = await db.execute(select(User).filter(User.email == login_in.email))
    user = result.scalar_one_or_none()
    
    # 2. Verify password (do not reveal if email exists or not)
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2.5 Block inactive users
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # 3. Create access token
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)

@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user
