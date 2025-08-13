import json
import os
import threading
import traceback
from typing import Any, Dict, List

import jwt
from dacite import from_dict
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from jwt.exceptions import PyJWTError
from pydantic import ValidationError
from pydantic_core import PydanticUndefined
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_server.database import Provider as DBProvider
from backend_server.database import get_db
from backend_server.reverie import ReverieConfig, ScratchData, StageInfo
from backend_server.server.auth import get_current_active_user, get_user
from backend_server.server.reverie_manager import ReveriePool
from backend_server.server.schemas import ChatReq, EventPublishReq, StartReq, User
from backend_server.server.utils import get_user_providers
from backend_server.utils import check_if_dir_exists, config
from backend_server.utils.config import BASE_TEMPLATES
from backend_server.utils.llm import LLMConfig
from backend_server.utils.logs import L

router = APIRouter()

reverie_pool = ReveriePool()
STORAGE_PATH = config.storage_path


def is_template_public(sim_code: str) -> bool:
    """Check if template is in public directory"""
    public_path = os.path.join(STORAGE_PATH, "public_templates", sim_code)
    return os.path.exists(public_path)


def user_owns_template(username: str, sim_code: str) -> bool:
    """Check if user owns this private template"""
    from backend_server.utils import get_user_hash

    user_hash = get_user_hash(username)
    user_path = os.path.join(STORAGE_PATH, "user_templates", user_hash, sim_code)
    return os.path.exists(user_path)


def parse_persona_configs(personas_data: List[Dict[str, Any]]) -> Dict[str, ScratchData]:
    parsed_personas: Dict[str, ScratchData] = {}
    for persona_config_original in personas_data:
        persona_name = persona_config_original.get("name")
        if not persona_name:
            L.warning("Persona data missing 'name', skipping.")
            continue

        # Attempt to parse with the original configuration first
        try:
            instance = ScratchData(**persona_config_original)
            parsed_personas[persona_name] = instance
        except ValidationError as e:
            L.warning(
                f"Validation error for persona '{persona_name}'. Errors: {e.errors()}. Attempting to apply defaults."
            )

            # If validation fails, create a copy to modify with defaults
            corrected_config = persona_config_original.copy()

            for error_detail in e.errors():
                # error_detail['loc'] is a tuple representing the path to the field
                # e.g., ('simple_field',) or ('nested_object', 'field_in_nested')
                if not error_detail["loc"]:
                    L.warning(
                        f"Validation error for persona '{persona_name}' without specific field location: {error_detail['msg']}. Skipping this error's handling."
                    )
                    continue

                # Assuming errors are for top-level fields of ScratchData for simplicity
                field_key = str(error_detail["loc"][0])

                # Check if the field exists in the model's fields
                if field_key not in ScratchData.model_fields:
                    L.warning(
                        f"Field '{field_key}' from validation error for persona '{persona_name}' not found in ScratchData.model_fields."
                    )
                    continue

                field_info = ScratchData.model_fields[field_key]

                applied_default = False
                # Check if the field has an explicit default value
                if field_info.default is not PydanticUndefined:
                    corrected_config[field_key] = field_info.default
                    L.info(
                        f"Applied default value for field '{field_key}' in persona '{persona_name}'. Original error: {error_detail['type']}:{error_detail['msg']}."
                    )
                    applied_default = True
                # Else, check if the field has a default_factory
                elif field_info.default_factory is not None:
                    default_value = field_info.default_factory()
                    corrected_config[field_key] = default_value
                    L.info(
                        f"Applied default_factory generated value for field '{field_key}' in persona '{persona_name}'. Original error: {error_detail['type']}:{error_detail['msg']}."
                    )
                    applied_default = True

                if not applied_default:
                    L.warning(
                        f"Field '{field_key}' in persona '{persona_name}' failed validation (type: {error_detail['type']}, msg: {error_detail['msg']}) but has no default value or factory. Original value was '{persona_config_original.get(field_key)}'. This field may cause validation to fail again."
                    )

            try:
                # Attempt to validate again with the corrected configuration
                instance = ScratchData(**corrected_config)
                parsed_personas[persona_name] = instance
                L.info(f"Successfully parsed persona '{persona_name}' after applying defaults for validated fields.")
            except ValidationError as e2:
                L.error(
                    f"Failed to parse persona '{persona_name}' even after attempting to apply defaults. Final errors: {e2.errors()}. Skipping this persona."
                )

    return parsed_personas


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


def get_reverie_instance(username: str, sim_code: str):
    instance = reverie_pool.get(username, sim_code)
    if not instance:
        L.warning(f"Simulation with code {sim_code} for user {username} not found")
        raise HTTPException(status_code=404, detail=f"Simulation with code {sim_code} for user {username} not found")
    return instance


@router.get("/user_providers")
async def user_providers(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    # get the providers mapping for current user
    result = await db.execute(select(DBProvider).where(DBProvider.username == current_user.username))
    providers = result.scalars().all()
    provider_configs = {
        provider.usage: {
            "kind": provider.kind,
            "base_url": provider.base_url,
            "api_key": provider.api_key,
            "model": provider.model,
            "temperature": provider.temperature,
            "max_tokens": provider.max_tokens,
            "top_p": provider.top_p,
            "frequency_penalty": provider.frequency_penalty,
            "presence_penalty": provider.presence_penalty,
            "stream": provider.stream,
        }
        for provider in providers
    }
    return provider_configs


@router.post("/user_providers")
async def update_user_providers(
    providers: Dict[str, LLMConfig],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # get the providers mapping for current user
    result = await db.execute(select(DBProvider).where(DBProvider.username == current_user.username))
    existing_providers = result.scalars().all()
    existing_providers_map = {p.usage: p for p in existing_providers}

    for usage, cfg in providers.items():
        if usage in existing_providers_map:
            # Update existing provider
            provider = existing_providers_map[usage]
            provider.kind = cfg["kind"]
            provider.base_url = cfg["base_url"]
            provider.api_key = cfg["api_key"]
            provider.model = cfg["model"]
            provider.temperature = cfg["temperature"]
            provider.max_tokens = cfg["max_tokens"]
            provider.top_p = cfg["top_p"]
            provider.frequency_penalty = cfg["frequency_penalty"]
            provider.presence_penalty = cfg["presence_penalty"]
            provider.stream = cfg["stream"]
        else:
            # Create new provider
            provider = DBProvider(
                username=current_user.username,
                usage=usage,
                kind=cfg["kind"],
                base_url=cfg["base_url"],
                api_key=cfg["api_key"],
                model=cfg["model"],
                temperature=cfg["temperature"],
                max_tokens=cfg["max_tokens"],
                top_p=cfg["top_p"],
                frequency_penalty=cfg["frequency_penalty"],
                presence_penalty=cfg["presence_penalty"],
                stream=cfg["stream"],
            )
            db.add(provider)

    await db.commit()
    return {"status": "success"}


@router.post("/start")
async def start(
    sim_data: StartReq, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    try:
        sim_code = sim_data.simCode
        template = sim_data.template
        template_sim_code = template.get("simCode")
        initial_rounds = sim_data.initialRounds

        # Check if user is allowed to use the template
        if template_sim_code:
            if not is_template_public(template_sim_code) and not user_owns_template(
                current_user.username, template_sim_code
            ):
                raise HTTPException(status_code=403, detail="You don't have access to the specified template")

        is_public = is_template_public(template_sim_code)
        from backend_server.utils import get_user_hash

        user_hash = get_user_hash(current_user.username)

        if sim_code in BASE_TEMPLATES:
            raise HTTPException(status_code=400, detail="Cannot overwrite base template")
        # Forbid overwriting existing template for now
        sim_folder = f"{STORAGE_PATH}/user_templates/{user_hash}/{sim_code}"
        if check_if_dir_exists(sim_folder):
            raise HTTPException(status_code=400, detail="Simulation already exists")
        L.debug(f"Persona configs: {template.get('personas', [])}")
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

        L.debug(f"starting simulation. providers: {sim_data.providers}")

        # Start a new thread to run the open_server method
        thread = threading.Thread(
            target=reverie_instance.reverie.open_server,
            args=(
                reverie_instance,
                current_user,
                sim_data.providers,
            ),
        )
        thread.start()

        return {"status": "success", "message": "Simulation started"}
    except Exception as e:
        L.error(f"Error in start endpoint: {str(e)}\n{traceback.format_exc()}")
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


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, sim_code: str, token: str, db: AsyncSession = Depends(get_db)):
    # Authenticate websocket connections with token parameter
    if token:
        try:
            from backend_server.server.auth import ALGORITHM, SECRET_KEY

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user = await get_user(db, username)
            if not username or user is None:
                await websocket.close(code=1008)  # Policy violation
                return
        except PyJWTError:
            await websocket.close(code=1008)  # JWT Authentication failed
            return
        except Exception:
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


@router.get("/summary")
async def get_summary(
    sim_code: str, current_user: User = Depends(get_current_active_user), providers: dict = Depends(get_user_providers)
):
    reverie_instance = get_reverie_instance(current_user.username, sim_code)
    try:
        summary = reverie_instance.reverie.generate_summary_from_action_log(providers["chat"])
        return {"summary": summary}
    except Exception as e:
        L.error(f"Error in get_summary endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
