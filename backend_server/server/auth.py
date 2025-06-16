import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_server.database import User as DBUser
from backend_server.database import get_db
from backend_server.server.schemas import TokenData, User, UserInDB
from backend_server.utils import get_password_hash, get_user_hash

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
SSO_APP_SECRETS = json.loads(os.environ["SSO_APP_SECRETS"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

# Invalid usernames
INVALID_USERNAMES = [
    "admin",
    "administrator",
    "root",
    "system",
    "superuser",
    "user",
    "guest",
    "anonymous",
    "moderator",
    "support",
    "help",
    "webmaster",
    "postmaster",
    "hostmaster",
    "info",
    "mail",
    "ftp",
    "www",
    "test",
]

# Windows reserved device names
WINDOWS_RESERVED_NAMES = [
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
]


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate a username to ensure it can be used as a valid folder name in both Linux and Windows
    and doesn't contain disallowed strings.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check against invalid username list
    if username.lower() in INVALID_USERNAMES:
        return False, f"Username '{username}' is reserved and cannot be used"

    # Check if username is . or ..
    if username in [".", ".."]:
        return False, "Username cannot be '.' or '..'"

    # Check if username is a Windows reserved name
    if username.upper() in WINDOWS_RESERVED_NAMES:
        return False, f"Username '{username}' is a reserved system name"

    # Check for invalid characters
    invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    for char in invalid_chars:
        if char in username:
            return False, f"Username cannot contain '{char}'"

    # Check for control characters
    if any(ord(char) < 32 for char in username):
        return False, "Username cannot contain control characters"

    # Check maximum length (Windows path component limitation)
    if len(username) > 255:
        return False, "Username cannot exceed 255 characters"

    # Check if username starts or ends with space or period
    if username.startswith(" ") or username.endswith(" ") or username.endswith("."):
        return False, "Username cannot start or end with a space, or end with a period"

    return True, ""


async def get_user(db: AsyncSession, username: str) -> Optional[DBUser]:
    """Get user from database"""
    result = await db.execute(select(DBUser).where(DBUser.username == username))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """Authenticate user against database"""
    user = await get_user(db, username)
    if not user:
        return False
    if not DBUser.verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(required: bool = True):
    async def _get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        if not required and not token:
            return None

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        if not token:
            raise credentials_exception
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except PyJWTError:
            raise credentials_exception
        user = await get_user(db, username=token_data.username)
        if user is None:
            raise credentials_exception
        return UserInDB(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            disabled=user.disabled,
            is_admin=user.is_admin,
            is_sso=user.is_sso,
            hashed_password=user.hashed_password,
        )

    return _get_current_user


async def get_current_active_user(current_user: User = Depends(get_current_user())):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_sso_signature(app_id: str, username: str, time: str, sign: str) -> bool:
    """Verify SSO signature"""
    # Get the app secret
    app_secret = SSO_APP_SECRETS.get(app_id)
    if not app_secret:
        return False

    # Construct the string to hash
    string_to_hash = f"appId={app_id}&appSecret={app_secret}&username={username}&time={time}"

    # Calculate MD5 hash
    calculated_sign = hashlib.md5(string_to_hash.encode()).hexdigest()

    # Compare signatures (case-insensitive)
    return calculated_sign.lower() == sign.lower()
