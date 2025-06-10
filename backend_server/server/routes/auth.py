import os
import secrets
import time
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend_server.database import User as DBUser
from backend_server.database import get_db
from backend_server.server.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_user,
    validate_username,
    verify_sso_signature,
)
from backend_server.server.schemas import SSOLoginRequest, Token, User, UserCreate
from backend_server.utils import get_password_hash, get_user_hash
from backend_server.utils.config import storage_path

router = APIRouter()

user_templates_path = os.path.join(storage_path, "user_templates")


@router.post("/register", response_model=User)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if username already exists
    existing_user = await get_user(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Validate username
    is_valid, error_message = validate_username(user_data.username)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

    hashed_password = get_password_hash(user_data.password)

    # Create new user in database
    new_user = DBUser(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
        institution=user_data.institution,
        hashed_password=hashed_password,
        disabled=False,
        is_admin=False,  # Default to False for new registrations
        is_sso=False,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Create user's template directory
    user_template_dir = os.path.join(user_templates_path, get_user_hash(user_data.username))
    os.makedirs(user_template_dir, exist_ok=True)

    return User(
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        disabled=new_user.disabled,
        is_admin=new_user.is_admin,
        is_sso=new_user.is_sso,
    )


@router.post("/ssologin")
async def sso_login(sso_data: SSOLoginRequest, db: AsyncSession = Depends(get_db)):
    """SSO login endpoint"""
    # Verify signature
    if not verify_sso_signature(sso_data.appId, sso_data.username, sso_data.time, sso_data.sign):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SSO signature",
        )

    # Check if timestamp is not too old (e.g., within 5 minutes)
    try:
        request_time = int(sso_data.time)
        current_time = int(time.time())
        if abs(current_time - request_time) > 300:  # 5 minutes
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="SSO request expired",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time format",
        )

    # Get or create user
    user = await get_user(db, sso_data.username)
    if not user:
        # Create a new user for SSO login
        # Generate a random password (user won't use it for SSO)
        random_password = secrets.token_urlsafe(32)
        hashed_password = get_password_hash(random_password)

        new_user = DBUser(
            username=sso_data.username,
            email=f"{sso_data.username}@zjgsu.edu.cn",  # Default email for SSO users
            full_name=sso_data.username,  # Default to username
            phone="",  # Empty phone for SSO users
            institution="zjgsu",  # Mark as SSO user
            hashed_password=hashed_password,
            disabled=False,
            is_admin=False,
            is_sso=True,
        )

        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            user = new_user

            # Create user's template directory
            user_template_dir = os.path.join(user_templates_path, get_user_hash(sso_data.username))
            os.makedirs(user_template_dir, exist_ok=True)
        except IntegrityError:
            await db.rollback()
            # Try to get the user again in case of race condition
            user = await get_user(db, sso_data.username)
            if not user:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    # Create response with token in body
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})

    # Set cookie with the same token
    response.set_cookie(
        key="auth_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
    )

    return response


@router.get("/ssologin")
async def sso_login_get(appId: str, username: str, time: str, sign: str, db: AsyncSession = Depends(get_db)):
    """SSO login endpoint for GET requests (redirect from portal)"""
    # Use the same logic as POST
    sso_data = SSOLoginRequest(appId=appId, username=username, time=time, sign=sign)
    return await sso_login(sso_data, db)


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    # Create response with token in body
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})

    # Set cookie with the same token
    response.set_cookie(
        key="auth_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
    )

    return response


@router.post("/logout")
async def logout():
    """Clear auth cookie on logout"""
    response = JSONResponse(content={"status": "success"})

    # Clear the auth cookie by setting it to expire immediately
    response.set_cookie(
        key="auth_token",
        value="",
        httponly=True,
        max_age=0,
        expires=0,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
    )

    return response


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
