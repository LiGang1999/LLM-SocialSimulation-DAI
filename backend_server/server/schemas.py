from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, EmailStr


# User management
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    phone: str
    institution: str


class User(UserBase):
    disabled: Optional[bool] = False
    is_admin: Optional[bool] = False
    is_sso: Optional[bool] = False


class UserInDB(User):
    hashed_password: str


class SSOLoginRequest(BaseModel):
    appId: str
    username: str
    time: str
    sign: str


# API Request/Response Models
class StartReq(BaseModel):
    simCode: str
    template: Dict[str, Any]
    initialRounds: Optional[int] = 0


class EventPublishReq(BaseModel):
    description: str
    websearch: str
    policy: str
    access_list: str


class ChatReq(BaseModel):
    agent_name: str
    type: str
    history: List[Tuple[str, str]] = []
    content: str


class ProfileReq(BaseModel):
    description: str


class ProfilePlanReq(BaseModel):
    scenario: str
    request: str
    agent_count: int


class ProfilesReq(BaseModel):
    plan: Dict[str, str]


class FeedbackCreate(BaseModel):
    username: str
    feedback: str


class FeedbackAdminResponse(BaseModel):
    id: int
    user_username: str
    user_email: EmailStr
    feedback_text: str
    timestamp: datetime


class ProviderBase(BaseModel):
    usage: str
    model: str
    api_key: str
    base_url: Optional[str] = None
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = 512
    top_p: Optional[float] = 0.7
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stream: Optional[bool] = False


class ProviderCreate(ProviderBase):
    pass


class Provider(ProviderBase):
    username: str

    class Config:
        from_attributes = True
