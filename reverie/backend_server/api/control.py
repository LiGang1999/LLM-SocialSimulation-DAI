import json
import os
import threading
from os import listdir

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from reverie import LLMConfig, PersonaConfig, ReverieConfig, command_queue, start_sim


@csrf_exempt
@require_http_methods(["POST"])
def start(request):
    try:
        data = json.loads(request.body)
        template_name = data.get("template")
        config_data = data.get("config")

        if not template_name or not config_data:
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # Parsing the LLMConfig from config_data if available
        llm_config_data = config_data.get("llm_config", {})
        llm_config = LLMConfig(
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

        # Parsing PersonaConfig objects from the "personas" key in config_data
        personas_data = config_data.get("personas", {})
        persona_configs = {
            name: PersonaConfig(
                name=persona.get("name", ""),
                daily_plan_req=persona.get("daily_plan_req", ""),
                first_name=persona.get("first_name", ""),
                last_name=persona.get("last_name", ""),
                age=int(persona.get("age", 0)),
                learned=persona.get("learned", ""),
                currently=persona.get("currently", ""),
                lifestyle=persona.get("lifestyle", ""),
                living_area=persona.get("living_area", ""),
                bibliography=persona.get("bibliography", ""),
            )
            for name, persona in personas_data.items()
        }

        # Parsing public events from config_data
        public_events = config_data.get("events", [])

        # Building the ReverieConfig object
        config = ReverieConfig(
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

        # Starting the simulation in a new thread
        thread = threading.Thread(target=start_sim, args=(template_name, config))
        thread.start()

        return JsonResponse({"status": "success", "message": "Simulation started"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_env_info(request):
    env_name = request.GET.get("env_name")
    storage_folder = "../../environment/frontend_server/storage"
    if env_name:
        # load environment meat information
        with open(f"{storage_folder}/{env_name}/reverie/meta.json", "r") as f:
            env_meta = json.load(f)
        persona_names = env_meta["persona_names"]
        persona_info = {}
        for persona in persona_names:
            persona_scratch_file = (
                f"{storage_folder}/{env_name}/personas/{persona}/bootstrap_memory/scratch.json"
            )
            f2 = open(persona_scratch_file, "r")
            scratch = json.load(f2)
            persona_info[persona] = {
                "name": scratch["name"],
                "first_name": scratch["first_name"],
                "last_name": scratch["last_name"],
                "age": scratch["age"],
                "innate": scratch["innate"],
                "learned": scratch["learned"],
                "currently": scratch["currently"],
                "lifestyle": scratch["lifestyle"],
                "living_area": scratch["living_area"],
                "bibliography": "",  # WIP
            }

    return JsonResponse(safe=False, data={"meta": env_meta, "personas": persona_info})


def add_command(request):
    command = request.GET.get("command")
    command_queue.put(command)
    return HttpResponse("success")


def list_envs(request):
    # list all folders under environment/frontend_server/storage
    storage_folder = "../../environment/frontend_server/storage"
    envs = os.listdir(storage_folder)
    result_envs = []
    for dir in envs:
        if "test" not in dir and "sim" not in dir and "July" not in dir:
            result_envs.append(dir)
    return JsonResponse(safe=False, data={"envs": result_envs})


def find_filenames(path_to_dir, suffix=".csv"):
    """
    Given a directory, find all files that ends with the provided suffix and
    returns their paths.
    ARGS:
      path_to_dir: Path to the current directory
      suffix: The target suffix.
    RETURNS:
      A list of paths to all files in the directory.
    """
    filenames = listdir(path_to_dir)
    return [path_to_dir + "/" + filename for filename in filenames if filename.endswith(suffix)]


def get_persona(request):
    # This implementation is a pile of shit
    print("Get personas...")
    storage_path = "../../environment/frontend_server/storage"
    temp_storage_path = "../../environment/frontend_server/temp_storage"
    with open(f"{temp_storage_path}/curr_sim_code.json") as json_file:
        sim_code = json.load(json_file)["sim_code"]
    persona_names = []
    persona_names_set = set()
    for i in find_filenames(f"{storage_path}/{sim_code}/personas", ""):
        x = i.split("/")[-1].strip()
        if x[0] != ".":
            persona_names += [[x, x.replace(" ", "_")]]
            persona_names_set.add(x)
    print(persona_names_set)
    return JsonResponse({"personas": list(persona_names_set)}, status=200, safe=False)
