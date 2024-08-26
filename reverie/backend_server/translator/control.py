import json
import os
import threading
from os import listdir

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from reverie import ReverieConfig, command_queue, start_sim


@csrf_exempt
@require_http_methods(["POST"])
def start(request):
    try:
        data = json.loads(request.body)
        template = data.get("template")
        config = data.get("config")

        if not template or not config:
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # Convert the config dictionary to ReverieConfig object
        config = ReverieConfig(**config)

        thread = threading.Thread(target=start_sim, args=(template, config))
        thread.start()

        return JsonResponse({"status": "success", "message": "Simulation started"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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
