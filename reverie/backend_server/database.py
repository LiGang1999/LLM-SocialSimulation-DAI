import os
from typing import Optional
import datetime # Added for timestamp
from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime, ForeignKey # Added Integer, Text, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import hashlib
import logging

logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)


# Database configuration from environment
DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

# Create async engine
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """User model for PostgreSQL database"""

    __tablename__ = "users"

    username = Column(String(50), primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20), nullable=False)
    institution = Column(String(100), nullable=False)
    hashed_password = Column(String(100), nullable=False)
    disabled = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False, nullable=False) # Add is_admin field

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_email_hash(email: str) -> str:
        """Generate consistent hash from email for storage folder naming"""
        return hashlib.sha256(email.encode()).hexdigest()


class Feedback(Base):
    """Feedback model for PostgreSQL database"""

    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_username = Column(String(50), ForeignKey("users.username"), nullable=False)
    feedback_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency to get database session"""
    async with async_session() as session:
        yield session
