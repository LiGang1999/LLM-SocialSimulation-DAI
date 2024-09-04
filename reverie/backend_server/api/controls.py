import json
import os
import threading
from typing import Dict, Any

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from typing import List

from reverie import LLMConfig, PersonaConfig, ReverieConfig, command_queue, start_sim
from utils import config
from utils.logs import L

BASE_TEMPLATES = [
    "base_the_villie_isabella_maria_klaus",
    "base_the_villie_isabella_maria_klaus_online",
    "base_the_villie_n25",
]

STORAGE_PATH = config.storage_path
TEMP_STORAGE_PATH = config.temp_storage_path


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


def parse_public_events(events_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "name": event.get("name", ""),
            "access_list": [
                name.strip() for name in event.get("access_list", "").strip().split(",")
            ],
            "websearch": event.get("websearch", ""),
            "policy": event.get("policy", ""),
            "description": event.get("description", ""),
        }
        for event in events_data
    ]


@csrf_exempt
@require_http_methods(["POST"])
def start(request):
    try:
        data = json.loads(request.body)
        L.debug(f"Received data: {data}")

        template_name = data.get("template")
        config_data = data.get("config", {})

        if not config_data.get("sim_code"):
            return JsonResponse({"error": "Missing sim_code in config"}, status=400)

        if not template_name or not config_data:
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        if template_name in BASE_TEMPLATES:
            return JsonResponse({"error": "Cannot overwrite base template"}, status=400)

        llm_config = parse_llm_config(config_data.get("llm_config", {}))
        persona_configs = parse_persona_configs(config_data.get("personas", []))
        public_events = parse_public_events(config_data.get("events", []))

        reverie_config = ReverieConfig(
            sim_code=config_data.get("sim_code", ""),
            sim_mode=config_data.get("sim_mode", ""),
            start_date=config_data.get("start_date", ""),
            curr_time=config_data.get("curr_time", ""),
            maze_name=config_data.get("maze_name", ""),
            step=int(config_data.get("step", 0)),
            llm_config=llm_config,
            persona_configs=persona_configs,
            public_events=public_events,
            direction=config_data.get("direction", ""),
        )

        thread = threading.Thread(target=start_sim, args=(template_name, reverie_config))
        thread.start()

        return JsonResponse({"status": "success", "message": "Simulation started"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        L.error(f"Error in start view: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def publish_event(request):
    try:
        data = json.loads(request.body)
        L.debug(f"Received data: {data}")

        event_description = data.get("description", "")
        event_websearch = data.get("websearch", "")
        event_policy = data.get("policy", "")
        event_access_list = [name.strip() for name in data.get("access_list", "").split(",")]

        command_queue.put("call -- with policy and websearch load online event")
        command_queue.put(event_description)
        command_queue.put(",".join(event_access_list))
        command_queue.put(event_policy)
        command_queue.put(event_websearch)

        return JsonResponse({"status": "success", "message": "Event published"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        L.error(f"Error in publish_event view: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


def fetch_template(request):
    env_name = request.GET.get("sim_code")
    if not env_name:
        return JsonResponse({"error": "Missing sim_code parameter"}, status=400)

    env_path = os.path.join(STORAGE_PATH, env_name)
    if not os.path.exists(env_path):
        return JsonResponse({"error": "Environment does not exist"}, status=404)

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

    return JsonResponse({"meta": env_meta, "personas": persona_info, "events": events})


def add_command(request):
    command = request.GET.get("command")
    if not command:
        return JsonResponse({"error": "Missing command parameter"}, status=400)
    command_queue.put(command)
    return HttpResponse("success")


def run(request):
    count = request.GET.get("count")
    if not count:
        return JsonResponse({"error": "Missing count parameter"}, status=400)
    command_queue.put(f"run {count}")
    return HttpResponse("success")


def fetch_templates(request):
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

    return JsonResponse({"envs": result_envs})


def get_persona(request):
    sim_code_file = os.path.join(TEMP_STORAGE_PATH, "curr_sim_code.json")
    sim_code_data = load_json_file(sim_code_file)
    sim_code = sim_code_data.get("sim_code")

    if not sim_code:
        return JsonResponse({"error": "Current simulation code not found"}, status=404)

    personas_path = os.path.join(STORAGE_PATH, sim_code, "personas")
    persona_names = set(
        name
        for name in os.listdir(personas_path)
        if os.path.isdir(os.path.join(personas_path, name)) and not name.startswith(".")
    )

    return JsonResponse({"personas": list(persona_names)})
