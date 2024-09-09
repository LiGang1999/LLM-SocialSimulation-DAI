import asyncio
import json
import os
import threading
import time
from collections import OrderedDict
from datetime import datetime
from queue import Queue
from typing import Any, Dict, List, Optional

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils import config
from utils.logs import L

from reverie import LLMConfig, PersonaConfig, Reverie, ReverieConfig, start_sim

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


BASE_TEMPLATES = [
    "base_the_villie_isabella_maria_klaus",
    "base_the_villie_isabella_maria_klaus_online",
    "base_the_villie_n25",
]

STORAGE_PATH = config.storage_path
TEMP_STORAGE_PATH = config.temp_storage_path

# Utility functions (load_json_file, save_json_file, parse_llm_config, parse_persona_configs, parse_public_events)


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
        api_base=llm_config_data.get("api_base", config.openai_api_base),
        api_key=llm_config_data.get("api_key", config.openai_api_key),
        engine=llm_config_data.get("engine", ""),
        tempreature=float(llm_config_data.get("temperature", 1.0)),
        max_tokens=int(llm_config_data.get("max_tokens", 512)),
        top_p=float(llm_config_data.get("top_p", 0.7)),
        frequency_penalty=float(llm_config_data.get("frequency_penalty", 0.0)),
        presence_penalty=float(llm_config_data.get("presence_penalty", 0.0)),
        stream=llm_config_data.get("stream", False),
    )


def parse_persona_configs(personas_data: List[Dict[str, Any]]) -> Dict[str, PersonaConfig]:
    return {
        persona.get("name", ""): PersonaConfig(
            name=persona.get("name", ""),
            daily_plan_req=persona.get("daily_plan_req", ""),
            first_name=persona.get("first_name", ""),
            last_name=persona.get("last_name", ""),
            age=int(persona.get("age", 0)),
            innate=persona.get("innate", ""),
            learned=persona.get("learned", ""),
            currently=persona.get("currently", ""),
            lifestyle=persona.get("lifestyle", ""),
            living_area=persona.get("living_area", ""),
            bibliography=persona.get("bibliography", ""),
        )
        for persona in personas_data
    }


def parse_public_events(
    events_data: List[Dict[str, Any]], personas: List[str]
) -> List[Dict[str, Any]]:
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
    def __init__(self, template_sim_code, sim_config: ReverieConfig):
        self.initialized = False
        self.last_accessed = datetime.now()
        self.running = False
        self.active_websockets = {}
        self.ws_lock = threading.Lock()
        self.reverie = Reverie(template_sim_code=template_sim_code, sim_config=sim_config)
        self.template_sim_code = template_sim_code
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
                except Exception:
                    disconnected_sockets.append(ws_id)

            # Remove disconnected WebSockets
            for ws_id in disconnected_sockets:
                self.active_websockets.pop(ws_id, None)

            return bool(self.active_websockets)

    def message_sender_loop(self):
        with self.ws_lock:
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
            self.running = False
            self.message_sender_thread.join(timeout=5)  # Wait for the thread to finish
            # Close all active WebSockets
            for websocket in self.active_websockets.values():
                asyncio.run(websocket.close())
            self.active_websockets.clear()


class ReveriePool:
    def __init__(self, max_instances: int = 1000):
        self.max_instances = max_instances
        self.pool: OrderedDict[str, ReverieInstance] = OrderedDict()
        self.lock = threading.Lock()

    def get_or_create(
        self, session_id: str, template_sim_code: str, sim_config: ReverieConfig
    ) -> ReverieInstance:
        with self.lock:
            if session_id in self.pool:
                reverie = self.pool.pop(session_id)
                self.pool[session_id] = reverie
            else:
                if len(self.pool) >= self.max_instances:
                    _, oldest_reverie = self.pool.popitem(last=False)
                    oldest_reverie.shutdown()  # Shutdown the removed instance
                reverie = ReverieInstance(template_sim_code, sim_config)
                self.pool[session_id] = reverie
            return reverie

    def remove(self, session_id: str) -> None:
        with self.lock:
            if session_id in self.pool:
                reverie = self.pool.pop(session_id)
                reverie.shutdown()  # Shutdown the removed instance

    def get(self, session_id: str) -> ReverieInstance | None:
        with self.lock:
            if session_id in self.pool:
                # Move accessed item to the end (most recently used)
                reverie = self.pool.pop(session_id)
                self.pool[session_id] = reverie
                return reverie
            return None

    def __len__(self) -> int:
        with self.lock:
            return len(self.pool)


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
    history: List[Dict[str, Any]] = []
    content: str


def get_reverie_instance(sim_code: str):
    instance = reverie_pool.get(sim_code)
    if not instance:
        L.warning(f"Simulation with code {sim_code} not found")
        raise HTTPException(status_code=404, detail=f"Simulation with code {sim_code} not found")
    return instance


@app.post("/start")
async def start(sim_data: StartReq, background_tasks: BackgroundTasks):
    try:
        sim_code = sim_data.simCode
        template = sim_data.template
        llm_config = sim_data.llmConfig
        initial_rounds = sim_data.initialRounds

        if template.get("simCode") in BASE_TEMPLATES:
            raise HTTPException(status_code=400, detail="Cannot overwrite base template")

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
        )

        reverie_instance = reverie_pool.get_or_create(
            sim_code, template.get("simCode"), reverie_config
        )
        background_tasks.add_task(start_sim, template.get("simCode"), reverie_config)

        return {"status": "success", "message": "Simulation started"}

    except Exception as e:
        L.error(f"Error in start endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/publish_event/{sim_code}")
async def publish_event(sim_code: str, event: EventPublishReq):
    reverie_instance = get_reverie_instance(sim_code)
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


@app.get("/query_status/{sim_code}")
async def query_status(sim_code: str):
    instance = reverie_pool.get(sim_code)
    if not instance:
        return {"status": "terminated"}
    return {"status": "running" if instance.running else "started"}


@app.get("/add_command/{sim_code}")
async def add_command(sim_code: str, command: str):
    reverie_instance = get_reverie_instance(sim_code)
    if not command:
        L.warning("add_command: No command provided")
        raise HTTPException(status_code=400, detail="Missing command parameter")
    reverie_instance.handle_command(command)
    return {"status": "success"}


@app.get("/run/{sim_code}")
async def run(sim_code: str, count: int):
    reverie_instance = get_reverie_instance(sim_code)
    if not count:
        L.warning("run: No count provided")
        raise HTTPException(status_code=400, detail="Missing count parameter")
    q = reverie_instance.reverie.command_queue
    q.put(f"run {count}")
    return {"status": "success"}


@app.get("/get_persona/{sim_code}")
async def get_persona(sim_code: str):
    reverie_instance = get_reverie_instance(sim_code)
    personas_path = os.path.join(STORAGE_PATH, reverie_instance.template_sim_code, "personas")
    persona_names = set(
        name
        for name in os.listdir(personas_path)
        if os.path.isdir(os.path.join(personas_path, name)) and not name.startswith(".")
    )

    return {"personas": list(persona_names)}


@app.get("/personas_info/{sim_code}")
async def personas_info(sim_code: str):
    reverie_instance = get_reverie_instance(sim_code)
    personas_path = os.path.join(STORAGE_PATH, reverie_instance.template_sim_code, "personas")
    persona_names = set(
        name
        for name in os.listdir(personas_path)
        if os.path.isdir(os.path.join(personas_path, name)) and not name.startswith(".")
    )

    persona_info = []
    for persona in persona_names:
        scratch_file = os.path.join(personas_path, persona, "bootstrap_memory", "scratch.json")
        scratch_data = load_json_file(scratch_file)
        persona_info.append(
            {
                "name": scratch_data.get("name", ""),
                "first_name": scratch_data.get("first_name", ""),
                "last_name": scratch_data.get("last_name", ""),
                "age": scratch_data.get("age", ""),
                "innate": scratch_data.get("innate", ""),
                "learned": scratch_data.get("learned", ""),
                "currently": scratch_data.get("currently", ""),
                "lifestyle": scratch_data.get("lifestyle", ""),
                "living_area": scratch_data.get("living_area", ""),
                "act_event": scratch_data.get("act_event", ""),
            }
        )

    return {"personas": persona_info}


@app.post("/chat/{sim_code}")
async def chat(sim_code: str, chat_request: ChatReq):
    reverie_instance = get_reverie_instance(sim_code)
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


@app.get("/persona_detail/{sim_code}")
async def persona_detail(sim_code: str, agent_name: str):
    reverie_instance = get_reverie_instance(sim_code)
    persona_path = os.path.join(
        STORAGE_PATH, reverie_instance.template_sim_code, "personas", agent_name
    )
    scratch_file = os.path.join(persona_path, "bootstrap_memory", "scratch.json")
    # Actually the scratch data should be loaded from ReverieInstance
    scratch_data = load_json_file(scratch_file)

    persona_detail = {
        "curr_time": scratch_data.get("curr_time"),
        "curr_tile": scratch_data.get("curr_tile"),
        "daily_plan_req": scratch_data.get("daily_plan_req", ""),
        "name": scratch_data.get("name", ""),
        "first_name": scratch_data.get("first_name", ""),
        "last_name": scratch_data.get("last_name", ""),
        "age": scratch_data.get("age"),
        "innate": scratch_data.get("innate", ""),
        "learned": scratch_data.get("learned", ""),
        "currently": scratch_data.get("currently", ""),
        "lifestyle": scratch_data.get("lifestyle", ""),
        "living_area": scratch_data.get("living_area", ""),
        "daily_req": scratch_data.get("daily_req", []),
        "f_daily_schedule": scratch_data.get("f_daily_schedule", []),
        "f_daily_schedule_hourly_org": scratch_data.get("f_daily_schedule_hourly_org", []),
        "act_address": scratch_data.get("act_address"),
        "act_start_time": scratch_data.get("act_start_time"),
        "act_duration": scratch_data.get("act_duration"),
        "act_description": scratch_data.get("act_description"),
        "act_pronunciatio": scratch_data.get("act_pronunciatio"),
        "act_event": scratch_data.get("act_event", [None, None, None]),
        "act_obj_description": scratch_data.get("act_obj_description"),
        "act_obj_pronunciatio": scratch_data.get("act_obj_pronunciatio"),
        "act_obj_event": scratch_data.get("act_obj_event", [None, None, None]),
        "chatting_with": scratch_data.get("chatting_with"),
        "chat": scratch_data.get("chat"),
        "chatting_with_buffer": scratch_data.get("chatting_with_buffer", {}),
        "chatting_end_time": scratch_data.get("chatting_end_time"),
        "act_path_set": scratch_data.get("act_path_set", False),
        "planned_path": scratch_data.get("planned_path", []),
        "avatar": scratch_data.get("avatar"),
        "plan": scratch_data.get("plan", []),
        "memory": scratch_data.get("memory", []),
        "bibliography": scratch_data.get("bibliography", ""),
    }

    return persona_detail


@app.get("/fetch_templates")
async def fetch_templates():
    envs = [
        dir
        for dir in os.listdir(STORAGE_PATH)
        if os.path.isdir(os.path.join(STORAGE_PATH, dir))
        and "test" not in dir
        and "sim" not in dir
        and "July" not in dir
    ]

    result_envs = []
    for dir in envs:
        template_meta_file = os.path.join(STORAGE_PATH, dir, "reverie", "meta.json")
        template_meta = load_json_file(template_meta_file)
        if template_meta:
            result_envs.append(template_meta)

    return {"envs": result_envs}


@app.get("/fetch_template")
async def fetch_template(sim_code: str):
    if not sim_code:
        raise HTTPException(status_code=400, detail="Missing sim_code parameter")

    env_path = os.path.join(STORAGE_PATH, sim_code)
    if not os.path.exists(env_path):
        raise HTTPException(status_code=404, detail="Environment does not exist")

    meta_file = os.path.join(env_path, "reverie", "meta.json")
    env_meta = load_json_file(meta_file)

    persona_names = env_meta.get("persona_names", [])
    persona_info = {}
    for persona in persona_names:
        scratch_file = os.path.join(
            env_path, "personas", persona, "bootstrap_memory", "scratch.json"
        )
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

    return {"meta": env_meta, "personas": persona_info, "events": events}


@app.websocket("/ws/message/{sim_code}")
async def websocket_endpoint(websocket: WebSocket, sim_code: str):
    reverie_instance = get_reverie_instance(sim_code)
    await websocket.accept()

    websocket_id = id(websocket)

    try:
        with threading.Lock():
            reverie_instance.active_websockets[websocket_id] = websocket

        while True:
            # Wait for messages (if needed)
            await websocket.receive_text()
            # Process the received data if necessary

    except WebSocketDisconnect:
        pass
    finally:
        with threading.Lock():
            reverie_instance.active_websockets.pop(websocket_id, None)


if __name__ == "__main__":
    import argparse
    import sys

    import uvicorn

    parser = argparse.ArgumentParser(description="Run the FastAPI server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=11544, help="Port to bind to")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()

    if args.dev:
        uvicorn.run("__main__:app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run(app, host=args.host, port=args.port)
