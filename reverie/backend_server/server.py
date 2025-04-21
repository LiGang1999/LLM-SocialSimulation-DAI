import asyncio
import json
import os
import threading
import time
import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from queue import Queue
from typing import Any, Dict, List, Optional, Tuple, Union
from dacite import from_dict

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, APIRouter, status
from reverie.backend_server.persona.profile.generate_profile import generate_scratch_profile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import PyJWTError

from pydantic import BaseModel, ValidationError, EmailStr
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from utils import config, check_if_dir_exists, get_password_hash, get_user_hash
from utils.config import BASE_TEMPLATES
from utils.logs import L
from contextlib import asynccontextmanager


from reverie import LLMConfig, Reverie, ReverieConfig, ScratchData, StageInfo
from database import User as DBUser, get_db, init_db

# Security configuration
SECRET_KEY = "8f42a73d98f3118bcc9dd52fc4e53fce983e5f7f7acfeffeeb67a49e47f66673"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600


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


class UserInDB(User):
    hashed_password: str


# User storage paths
USER_TEMPLATES_PATH = os.path.join(config.storage_path, "user_templates")
os.makedirs(USER_TEMPLATES_PATH, exist_ok=True)

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


def is_template_public(sim_code: str) -> bool:
    """Check if template is in public directory"""
    public_path = os.path.join(STORAGE_PATH, "public_templates", sim_code)
    return os.path.exists(public_path)


def user_owns_template(username: str, sim_code: str) -> bool:
    """Check if user owns this private template"""
    user_hash = get_user_hash(username)
    user_path = os.path.join(STORAGE_PATH, "user_templates", user_hash, sim_code)
    return os.path.exists(user_path)


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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


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
            hashed_password=user.hashed_password,
        )

    return _get_current_user


async def get_current_active_user(current_user: User = Depends(get_current_user())):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

router = APIRouter(prefix="/api")


# Authentication endpoints
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
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Create user's template directory
    user_template_dir = os.path.join(USER_TEMPLATES_PATH, get_user_hash(user_data.username))
    os.makedirs(user_template_dir, exist_ok=True)

    return User(
        username=new_user.username, email=new_user.email, full_name=new_user.full_name, disabled=new_user.disabled
    )


from fastapi.responses import JSONResponse


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


STORAGE_PATH = config.storage_path
TEMP_STORAGE_PATH = config.temp_storage_path


# Utility functions (unchanged)
def load_json_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        L.error(f"Invalid JSON in file: {file_path}")
        return {}
    except FileNotFoundError:
        L.error(f"File not found: {file_path}")
        return {}


def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    with open(file_path, "w") as f:
        json.dump(data, f)


def parse_llm_config(llm_config_data: Dict[str, Any]) -> LLMConfig:
    return LLMConfig(
        # base_url=llm_config_data.get("base_url", config.openai_api_base), # 不再提供api
        # api_key=llm_config_data.get("api_key", config.openai_api_key), # 不再提供api
        base_url=llm_config_data.get("base_url", ""),
        api_key=llm_config_data.get("api_key", ""),
        model=llm_config_data.get("model", ""),
        tempreature=float(llm_config_data.get("temperature", 1.0)),
        max_tokens=int(llm_config_data.get("max_tokens", 512)),
        top_p=float(llm_config_data.get("top_p", 0.7)),
        frequency_penalty=float(llm_config_data.get("frequency_penalty", 0.0)),
        presence_penalty=float(llm_config_data.get("presence_penalty", 0.0)),
        stream=llm_config_data.get("stream", False),
    )


def parse_persona_configs(personas_data: List[Dict[str, Any]]) -> Dict[str, ScratchData]:
    return {persona["name"]: ScratchData(**persona) for persona in personas_data}


def parse_public_events(events_data: List[Dict[str, Any]], personas: List[str]) -> List[Dict[str, Any]]:
    return [
        {
            "name": event.get("name", ""),
            "access_list": (
                [name.strip() for name in event.get("access_list", "").strip().split(",")]
                if event.get("access_list")
                else personas
            ),
            "websearch": event.get("websearch", ""),
            "policy": event.get("policy", ""),
            "description": event.get("description", ""),
        }
        for event in events_data
    ]


class ReverieInstance:
    # ReverieInstance definition (unchanged)
    def __init__(self, username, template_config, sim_config: ReverieConfig):
        self.initialized = False
        self.last_accessed = datetime.now()
        self.active_websockets = {}
        self.ws_lock = threading.Lock()
        self.reverie = Reverie(username, template_config, sim_config=sim_config)
        self.template_sim_code = template_config["template_sim_code"]
        self.sim_config = sim_config
        # more code for ReverieInstance is omitted

        self.message_sender_thread = threading.Thread(target=self.message_sender_loop, daemon=True)
        self.message_sender_thread.start()

    async def send_message_to_websockets(self, message):
        with self.ws_lock:
            if not self.active_websockets:
                return False

            disconnected_sockets = []
            for ws_id, websocket in self.active_websockets.items():
                try:
                    await websocket.send_text(message)
                except PyJWTError:
                    disconnected_sockets.append(ws_id)
                except Exception:
                    disconnected_sockets.append(ws_id)

            # Remove disconnected WebSockets
            for ws_id in disconnected_sockets:
                self.active_websockets.pop(ws_id, None)

            return bool(self.active_websockets)

    def message_sender_loop(self):
        while True:
            if not self.reverie.message_queue.empty() and self.active_websockets:
                message = self.reverie.message_queue.get()
                success = asyncio.run(self.send_message_to_websockets(message))
                if not success:
                    # If no active WebSockets, put the message back in the queue
                    self.reverie.message_queue.put(message)
            else:
                # Sleep briefly to avoid busy-waiting
                time.sleep(0.1)

    def shutdown(self):
        with self.ws_lock:
            self.message_sender_thread.join(timeout=5)  # Wait for the thread to finish
            # Close all active WebSockets
            for websocket in self.active_websockets.values():
                asyncio.run(websocket.close())
            self.active_websockets.clear()


class ReveriePool:
    # ReveriePool definition (unchanged)
    def __init__(self, max_instances: int = 1000):
        self.max_instances = max_instances
        self.pool: OrderedDict[str, OrderedDict[str, ReverieInstance]] = OrderedDict()
        self.lock = threading.Lock()

    def get_or_create(
        self, sim_code: str, username: str, template_config: Dict, sim_config: ReverieConfig
    ) -> ReverieInstance:
        with self.lock:
            if username not in self.pool:
                self.pool[username] = OrderedDict()

            if sim_code in self.pool[username]:
                # Move accessed item to the end (most recently used)
                reverie = self.pool[username].pop(sim_code)
                self.pool[username][sim_code] = reverie
            else:
                # Check total instance count before creating a new one
                total_instances = sum(len(user_pool) for user_pool in self.pool.values())
                if total_instances >= self.max_instances:
                    # Find and remove the oldest instance across all users
                    oldest_user = None
                    oldest_sim_code = None
                    oldest_time = datetime.now()

                    for user, user_pool in self.pool.items():
                        if user_pool:
                            # The first item in OrderedDict is the oldest
                            first_sim_code, first_reverie = next(iter(user_pool.items()))
                            if first_reverie.last_accessed < oldest_time:
                                oldest_time = first_reverie.last_accessed
                                oldest_user = user
                                oldest_sim_code = first_sim_code

                    if oldest_user and oldest_sim_code:
                        oldest_reverie = self.pool[oldest_user].pop(oldest_sim_code)
                        oldest_reverie.shutdown()
                        if not self.pool[oldest_user]:
                            self.pool.pop(oldest_user) # Remove user if no more instances

                reverie = ReverieInstance(username, template_config, sim_config)
                self.pool[username][sim_code] = reverie
            return reverie

    def remove(self, username: str, sim_code: str) -> None:
        with self.lock:
            if username in self.pool and sim_code in self.pool[username]:
                reverie = self.pool[username].pop(sim_code)
                reverie.shutdown()  # Shutdown the removed instance
                if not self.pool[username]:
                    self.pool.pop(username) # Remove user if no more instances

    def get(self, username: str, sim_code: str) -> ReverieInstance | None:
        with self.lock:
            if username in self.pool and sim_code in self.pool[username]:
                # Move accessed item to the end (most recently used)
                reverie = self.pool[username].pop(sim_code)
                self.pool[username][sim_code] = reverie
                return reverie
            return None

    def __len__(self) -> int:
        with self.lock:
            return sum(len(user_pool) for user_pool in self.pool.values())


reverie_pool = ReveriePool()


class StartReq(BaseModel):
    simCode: str
    template: Dict[str, Any]
    llmConfig: Dict[str, Any]
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


def get_reverie_instance(username: str, sim_code: str):
    instance = reverie_pool.get(username, sim_code)
    if not instance:
        L.warning(f"Simulation with code {sim_code} for user {username} not found")
        raise HTTPException(status_code=404, detail=f"Simulation with code {sim_code} for user {username} not found")
    return instance


# Protected endpoints (require authentication)
@router.post("/start")
async def start(sim_data: StartReq, current_user: User = Depends(get_current_active_user)):
    try:
        sim_code = sim_data.simCode
        template = sim_data.template
        template_sim_code = template.get("simCode")
        llm_config = sim_data.llmConfig
        initial_rounds = sim_data.initialRounds

        # Check if user is allowed to use the template
        if template_sim_code:
            if not is_template_public(template_sim_code) and not user_owns_template(
                current_user.username, template_sim_code
            ):
                raise HTTPException(status_code=403, detail="You don't have access to the specified template")

        is_public = is_template_public(template_sim_code)
        user_hash = get_user_hash(current_user.username)

        if sim_code in BASE_TEMPLATES:
            raise HTTPException(status_code=400, detail="Cannot overwrite base template")
        # Forbid overwriting existing template for now
        sim_folder = f"{STORAGE_PATH}/user_templates/{user_hash}/{sim_code}"
        if check_if_dir_exists(sim_folder):
            raise HTTPException(status_code=400, detail="Simulation already exists")
        parsed_llm_config = parse_llm_config(llm_config)
        persona_configs = parse_persona_configs(template.get("personas", []))
        public_events = parse_public_events(
            template.get("events", []), [persona.name for persona in persona_configs.values()]
        )

        reverie_config = ReverieConfig(
            sim_code=sim_code,
            sim_mode=template.get("meta", {}).get("sim_mode", ""),
            start_date=template.get("meta", {}).get("start_date", ""),
            curr_time=template.get("meta", {}).get("curr_time", ""),
            maze_name=template.get("meta", {}).get("maze_name", ""),
            step=int(template.get("meta", {}).get("step", 0)),
            llm_config=parsed_llm_config,
            persona_configs=persona_configs,
            public_events=public_events,
            direction=template.get("meta", {}).get("direction", ""),
            initial_rounds=initial_rounds or 0,
            workflow={
                key: from_dict(data_class=StageInfo, data=value) for key, value in template.get("workflow", {}).items()
            },
        )
        reverie_instance = reverie_pool.get_or_create(
            sim_code,
            current_user.username,
            {"is_public": is_public, "template_sim_code": template.get("simCode")},
            reverie_config,
        )

        # Start a new thread to run the open_server method
        thread = threading.Thread(target=reverie_instance.reverie.open_server, args=(reverie_instance,))
        thread.start()

        return {"status": "success", "message": "Simulation started"}
    except Exception as e:
        L.error(f"Error in start endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish_events")
async def publish_event(event: EventPublishReq, sim_code: str, current_user: User = Depends(get_current_active_user)):
    reverie_instance = get_reverie_instance(current_user.username, sim_code)
    try:
        event_access_list = [name.strip() for name in event.access_list.split(",")]
        q = reverie_instance.reverie.command_queue

        q.put("call -- with policy and websearch load online event")
        q.put(event.description)
        q.put(",".join(event_access_list))
        q.put(event.policy)
        q.put(event.websearch)

        return {"status": "success", "message": "Event published"}

    except Exception as e:
        L.error(f"Error in publish_event endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def query_status(sim_code: str, current_user: User = Depends(get_current_active_user)):
    instance = reverie_pool.get(current_user.username, sim_code)
    if not instance:
        return {"status": "terminated"}
    return {
        "status": "running" if instance.reverie.is_running else "started",
        "connections": [ws for ws in instance.active_websockets],
    }


@router.get("/command")
async def add_command(sim_code: str, command: str, current_user: User = Depends(get_current_active_user)):
    reverie_instance = get_reverie_instance(current_user.username, sim_code)
    if not command:
        L.warning("add_command: No command provided")
        raise HTTPException(status_code=400, detail="Missing command parameter")
    reverie_instance.reverie.command_queue.put(command)
    return {"status": "success"}


@router.get("/run")
async def run(sim_code: str, count: int, current_user: User = Depends(get_current_active_user)):
    reverie_instance = get_reverie_instance(current_user.username, sim_code)
    if not count:
        L.warning("run: No count provided")
        raise HTTPException(status_code=400, detail="Missing count parameter")
    q = reverie_instance.reverie.command_queue
    # special treatment for cases
    if sim_code in [
        "dragon_tv_demo",
        "shbz",
        "legislative_council_life",
        "legislative_council",
        "legislative_council_life_demo",
    ]:
        q.put(f"cusom-run {sim_code} {count}")
    else:
        q.put(f"run {count}")
    L.debug(list(q.queue))
    return {"status": "success"}


@router.post("/chat")
async def chat(chat_request: ChatReq, sim_code: str, current_user: User = Depends(get_current_active_user)):
    reverie_instance = get_reverie_instance(current_user.username, sim_code)
    try:
        q = reverie_instance.reverie.command_queue
        q.put(f"call -- chat to persona {chat_request.agent_name}")
        q.put(
            json.dumps(
                {
                    "mode": chat_request.type,
                    "prev_msgs": chat_request.history,
                    "msg": chat_request.content,
                }
            )
        )
        return {"status": "success"}
    except Exception as e:
        L.warning(f"Error processing chat request: {e}")
        raise HTTPException(status_code=404, detail="Invalid simulation or persona")


@router.post("/generate_profile")
async def generate_profile(profile_req: ProfileReq, current_user: User = Depends(get_current_active_user)):
    """Generate a profile based on a description"""
    try:
        profile = await generate_scratch_profile(profile_req.description)
        return profile
    except Exception as e:
        L.error(f"Error generating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating profile: {str(e)}")


# Public endpoints (no authentication required)
@router.get("/get_persona/{sim_code}")
async def get_persona(sim_code: str, current_user: User = Depends(get_current_active_user)):
    reverie_instance = get_reverie_instance(current_user.username, sim_code)
    personas_path = os.path.join(STORAGE_PATH, reverie_instance.template_sim_code, "personas")
    persona_names = set(
        name
        for name in os.listdir(personas_path)
        if os.path.isdir(os.path.join(personas_path, name)) and not name.startswith(".")
    )

    return {"personas": list(persona_names)}


@router.get("/personas_info")
async def personas_info(sim_code: str, current_user: User = Depends(get_current_active_user)):
    reverie_instance = get_reverie_instance(current_user.username, sim_code)
    r = reverie_instance.reverie
    persona_info = []

    try:
        for persona_name, persona in r.personas.items():
            scratch = persona.scratch
            persona_info.append(
                {
                    "name": persona_name,
                    "first_name": scratch.first_name,
                    "last_name": scratch.last_name,
                    "age": scratch.age,
                    "innate": scratch.innate,
                    "learned": scratch.learned,
                    "currently": scratch.currently,
                    "lifestyle": scratch.lifestyle,
                    "living_area": scratch.living_area,
                    "act_event": scratch.act_event,
                }
            )
    except ValidationError as e:
        L.warning(f"Error parsing persona {persona}: {e}")

    return {"personas": persona_info}


@router.get("/persona_detail")
async def persona_detail(sim_code: str, agent_name: str, current_user: User = Depends(get_current_active_user)):
    r = get_reverie_instance(current_user.username, sim_code)
    r = r.reverie
    persona_path = os.path.join(STORAGE_PATH, r.template_sim_code, "personas", agent_name)
    scratch = r.personas[agent_name].scratch
    scratch_data = vars(scratch)

    try:
        person = ScratchData(**scratch_data)
        persona_detail = person.dict()
    except ValidationError as e:
        L.warning(f"Error parsing persona {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing persona data for {agent_name}")

    return {"scratch": persona_detail, "a_mem": {}, "s_mem": {}}


def get_public_templates():
    """Get list of available public templates"""
    public_path = os.path.join(STORAGE_PATH, "public_templates")
    public_templates = []
    if os.path.exists(public_path):
        public_dirs = [dir for dir in os.listdir(public_path) if os.path.isdir(os.path.join(public_path, dir))]
        for dir in public_dirs:
            template_meta_file = os.path.join(public_path, dir, "reverie", "meta.json")
            template_meta = load_json_file(template_meta_file)
            if template_meta:
                hidden = template_meta.get("hidden", True)
                if not hidden:
                    public_templates.append(template_meta)

    # Sort templates
    def sort_key(env):
        sim_code = env.get("template_sim_code", "")
        return (0 if "online" in sim_code.lower() else 1, sim_code)

    public_templates.sort(key=sort_key)
    return public_templates


@router.get("/fetch_templates")
async def fetch_templates(current_user: User = Depends(get_current_user(False), use_cache=False)):
    # Get public templates
    public_templates = get_public_templates()

    # If user is not authenticated, return only public templates
    if current_user is None:
        return {"public_templates": public_templates, "user_templates": []}

    # Get user templates from storage_path/{user_hash}/
    user_hash = get_user_hash(current_user.username)
    user_path = os.path.join(STORAGE_PATH, "user_templates", user_hash)
    user_templates = []
    if os.path.exists(user_path):
        user_dirs = [dir for dir in os.listdir(user_path) if os.path.isdir(os.path.join(user_path, dir))]
        for dir in user_dirs:
            template_meta_file = os.path.join(user_path, dir, "reverie", "meta.json")
            template_meta = load_json_file(template_meta_file)
            if template_meta:
                user_templates.append(template_meta)

    # Sort user templates
    def sort_key(env):
        sim_code = env.get("template_sim_code", "")
        return (0 if "online" in sim_code.lower() else 1, sim_code)

    user_templates.sort(key=sort_key)

    return {"public_templates": public_templates, "user_templates": user_templates}


@router.delete("/delete_template")
async def delete_template(sim_code: str, current_user: User = Depends(get_current_active_user)):
    """Delete a user template"""
    if not sim_code:
        raise HTTPException(status_code=400, detail="Missing sim_code parameter")

    # Check if template is public (can't delete public templates)
    if is_template_public(sim_code):
        raise HTTPException(status_code=403, detail="Cannot delete public templates")

    # Check if user owns the template
    if not user_owns_template(current_user.username, sim_code):
        raise HTTPException(status_code=403, detail="You don't own this template")

    # Delete the template directory
    user_hash = get_user_hash(current_user.username)
    template_path = os.path.join(STORAGE_PATH, "user_templates", user_hash, sim_code)

    try:
        if os.path.exists(template_path):
            import shutil

            shutil.rmtree(template_path)
            return {"status": "success", "message": "Template deleted"}
        else:
            raise HTTPException(status_code=404, detail="Template not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch_template")
async def fetch_template(sim_code: str, current_user: User = Depends(get_current_active_user)):
    if not sim_code:
        raise HTTPException(status_code=400, detail="Missing sim_code parameter")

    # Check if the template is accessible to the user
    # First, check if it's a public template
    if is_template_public(sim_code):
        env_path = os.path.join(STORAGE_PATH, "public_templates", sim_code)
    # Then check if it's owned by the user
    elif user_owns_template(current_user.username, sim_code):
        user_hash = get_user_hash(current_user.username)
        env_path = os.path.join(STORAGE_PATH, "user_templates", user_hash, sim_code)
    else:
        # Template doesn't exist or user doesn't have access
        raise HTTPException(status_code=403, detail="Template not found or access denied")

    meta_file = os.path.join(env_path, "reverie", "meta.json")
    env_meta = load_json_file(meta_file)

    persona_names = env_meta.get("persona_names", [])
    persona_info = {}
    for persona in persona_names:
        scratch_file = os.path.join(env_path, "personas", persona, "bootstrap_memory", "scratch.json")
        scratch_data = load_json_file(scratch_file)
        persona_info[persona] = {
            "name": scratch_data.get("name", ""),
            "first_name": scratch_data.get("first_name", ""),
            "last_name": scratch_data.get("last_name", ""),
            "age": scratch_data.get("age", 0),
            "daily_plan_req": scratch_data.get("daily_plan_req", ""),
            "innate": scratch_data.get("innate", ""),
            "learned": scratch_data.get("learned", ""),
            "currently": scratch_data.get("currently", ""),
            "lifestyle": scratch_data.get("lifestyle", ""),
            "living_area": scratch_data.get("living_area", ""),
            "bibliography": "",  # WIP
        }

    events_file = os.path.join(env_path, "reverie", "events.json")
    events = load_json_file(events_file)
    workflow = env_meta.get("workflow", {})

    return {"meta": env_meta, "personas": persona_info, "events": events, "workflow": workflow}


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, sim_code: str, token: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    # Authenticate websocket connections with token parameter
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user = await get_user(db, username)
            if not username or user is None:
                await websocket.close(code=1008)  # Policy violation
                return
        except PyJWTError as e:
            await websocket.close(code=1008)  # JWT Authentication failed
            return
        except Exception as e:
            await websocket.close(code=1008)  # General authentication failure
            return
    else:
        await websocket.close(code=1008)  # General authentication failure
        return

    reverie_instance = get_reverie_instance(username, sim_code)
    if not reverie_instance:
        L.warning(f"No reverie instance found for sim_code: {sim_code} for user {username}")
        await websocket.close(code=1003)  # Can't accept
        return

    await websocket.accept()
    websocket_id = id(websocket)

    try:
        with reverie_instance.ws_lock:
            reverie_instance.active_websockets[websocket_id] = websocket

        while True:
            # Wait for messages (if needed)
            await websocket.receive_text()
            # Process the received data if necessary

    except WebSocketDisconnect:
        pass
    finally:
        with reverie_instance.ws_lock:
            reverie_instance.active_websockets.pop(websocket_id, None)


app.include_router(router)


@router.get("/sessions")
async def list_sessions(current_user: User = Depends(get_current_active_user)):
    """
    Returns the list of sim_code for all running reverie instances under the current user.
    """
    user_sessions = []
    with reverie_pool.lock:
        if current_user.username in reverie_pool.pool:
            user_sessions = list(reverie_pool.pool[current_user.username].keys())
    return {"sessions": user_sessions}


if __name__ == "__main__":
    import argparse
    import sys

    import uvicorn

    parser = argparse.ArgumentParser(description="Run the FastAPI server")
    # parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    # parser.add_argument("--port", type=int, default=11544, help="Port to bind to")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()
    host = os.environ.get("LISTEN_ADDRESS", "0.0.0.0")
    port = int(os.environ.get("BACKEND_PORT", 11544))

    if args.dev:
        uvicorn.run("__main__:app", host=host, port=port, reload=True)
    else:
        uvicorn.run(app, host=host, port=port)
