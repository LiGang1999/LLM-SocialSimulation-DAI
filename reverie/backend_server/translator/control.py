from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from reverie import start_sim, command_queue
import threading
import json
from os import listdir

def start(request):
    fork = request.GET.get("fork")
    new = request.GET.get("new")
    model = request.GET.get("model")
    thread = threading.Thread(target=start_sim, args=(fork, new, model))
    thread.start()
    return HttpResponse("success")

def add_command(request):
    command = request.GET.get("command")
    command_queue.put(command)
    return HttpResponse("success")

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
  return [ path_to_dir+"/"+filename 
           for filename in filenames if filename.endswith( suffix ) ]

def get_persona(request):
    print("Get personas...")
    with open('/home/lj/code/mine/llm-ss-dai-0624/environment/frontend_server/temp_storage/curr_sim_code.json') as json_file:  
        sim_code = json.load(json_file)["sim_code"]
    persona_names = []
    persona_names_set = set()
    for i in find_filenames(f"/home/lj/code/mine/llm-ss-dai-0624/environment/frontend_server/storage/{sim_code}/personas", ""): 
        x = i.split("/")[-1].strip()
        if x[0] != ".": 
            persona_names += [[x, x.replace(" ", "_")]]
            persona_names_set.add(x)
    print(persona_names_set)
    return JsonResponse({'personas': list(persona_names_set)}, status=200, safe=False)
    