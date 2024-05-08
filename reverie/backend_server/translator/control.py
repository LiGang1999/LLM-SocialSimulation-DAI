from django.http import HttpResponse, JsonResponse
from reverie import start_sim, command_queue
import threading

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