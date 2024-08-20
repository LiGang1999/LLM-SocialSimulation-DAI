from django.http import HttpResponse, JsonResponse
from reverie import start_sim, command_queue
import threading
import os


def start(request):
    fork = request.GET.get("fork")
    new = request.GET.get("new")
    thread = threading.Thread(target=start_sim, args=(fork, new))
    thread.start()
    return HttpResponse("success")


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
        if "test" not in dir and "sim" not in dir:
            result_envs.append(dir)
    return JsonResponse(safe=False, data={"envs": result_envs})
