"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: reverie.py
Description: This is the main program for running generative agent simulations
that defines the ReverieServer class. This class maintains and records all  
states related to the simulation. The primary mode of interaction for those  
running the simulation should be through the open_server function, which  
enables the simulator to input command-line prompts for running and saving  
the simulation, among other tasks.

Release note (June 14, 2023) -- Reverie implements the core simulation 
mechanism described in my paper entitled "Generative Agents: Interactive 
Simulacra of Human Behavior." If you are reading through these lines after 
having read the paper, you might notice that I use older terms to describe 
generative agents and their cognitive modules here. Most notably, I use the 
term "personas" to refer to generative agents, "associative memory" to refer 
to the memory stream, and "reverie" to refer to the overarching simulation 
framework.
"""
import json
import numpy
import datetime
import pickle
import time
import math
import os
import shutil
import traceback
from queue import Queue

from selenium import webdriver

from global_methods import *
# from utils import *
from maze import *
from persona.persona import *
from vector_db import *#
from institution import *#
from memorynode import *

global_rs = None#???
command_queue = Queue()

global_offline_mode = False ##false means online

def return_rs():
  global global_rs
  print('lg:',global_rs)
  return global_rs

##############################################################################
#                                  REVERIE                                   #
##############################################################################

class ReverieServer: 
  def __init__(self, 
               fork_sim_code,
               sim_code):
    # FORKING FROM A PRIOR SIMULATION:
    # <fork_sim_code> indicates the simulation we are forking from. 
    # Interestingly, all simulations must be forked from some initial 
    # simulation, where the first simulation is "hand-crafted".
    self.fork_sim_code = fork_sim_code
    fork_folder = f"{fs_storage}/{self.fork_sim_code}"

    # <sim_code> indicates our current simulation. The first step here is to 
    # copy everything that's in <fork_sim_code>, but edit its 
    # reverie/meta/json's fork variable. 
    self.sim_code = sim_code
    sim_folder = f"{fs_storage}/{self.sim_code}"
    copyanything(fork_folder, sim_folder)

    with open(f"{sim_folder}/reverie/meta.json") as json_file:  
      reverie_meta = json.load(json_file)

    with open(f"{sim_folder}/reverie/meta.json", "w") as outfile: 
      reverie_meta["fork_sim_code"] = fork_sim_code
      outfile.write(json.dumps(reverie_meta, indent=2))

    # LOADING REVERIE'S GLOBAL VARIABLES
    # The start datetime of the Reverie: 
    # <start_datetime> is the datetime instance for the start datetime of 
    # the Reverie instance. Once it is set, this is not really meant to 
    # change. It takes a string date in the following example form: 
    # "June 25, 2022"
    # e.g., ...strptime(June 25, 2022, "%B %d, %Y")
    self.start_time = datetime.datetime.strptime(
                        f"{reverie_meta['start_date']}, 00:00:00",  
                        "%B %d, %Y, %H:%M:%S")
    # <curr_time> is the datetime instance that indicates the game's current
    # time. This gets incremented by <sec_per_step> amount everytime the world
    # progresses (that is, everytime curr_env_file is recieved). 
    self.curr_time = datetime.datetime.strptime(reverie_meta['curr_time'], 
                                                "%B %d, %Y, %H:%M:%S")
    # <sec_per_step> denotes the number of seconds in game time that each 
    # step moves foward. 
    self.sec_per_step = reverie_meta['sec_per_step']
    self.sec_per_step = 60#lg#x6#报错
    self.sec_per_step = 600#lg#x10#？？？
    self.sec_per_step = 3600#lg#x6
    # self.sec_per_step = 86400#lg#x24
    # self.sec_per_step = 172800#lg#x2
    
    # <maze> is the main Maze instance. Note that we pass in the maze_name
    # (e.g., "double_studio") to instantiate Maze. 
    # e.g., Maze("double_studio")
    if global_offline_mode:
      self.maze = OfflineMaze(reverie_meta['maze_name'])
    else:
      self.maze = OnlineMaze(reverie_meta['maze_name'])
    
    # <step> denotes the number of steps that our game has taken. A step here
    # literally translates to the number of moves our personas made in terms
    # of the number of tiles. 
    self.step = reverie_meta['step']

    # SETTING UP PERSONAS IN REVERIE
    # <personas> is a dictionary that takes the persona's full name as its 
    # keys, and the actual persona instance as its values.
    # This dictionary is meant to keep track of all personas who are part of
    # the Reverie instance. 
    # e.g., ["Isabella Rodriguez"] = Persona("Isabella Rodriguezs")
    self.personas = dict()
    # <personas_tile> is a dictionary that contains the tile location of
    # the personas (!-> NOT px tile, but the actual tile coordinate).
    # The tile take the form of a set, (row, col). 
    # e.g., ["Isabella Rodriguez"] = (58, 39)
    if global_offline_mode:
      self.personas_tile = dict()
    
    # # <persona_convo_match> is a dictionary that describes which of the two
    # # personas are talking to each other. It takes a key of a persona's full
    # # name, and value of another persona's full name who is talking to the 
    # # original persona. 
    # # e.g., dict["Isabella Rodriguez"] = ["Maria Lopez"]
    # self.persona_convo_match = dict()
    # # <persona_convo> contains the actual content of the conversations. It
    # # takes as keys, a pair of persona names, and val of a string convo. 
    # # Note that the key pairs are *ordered alphabetically*. 
    # # e.g., dict[("Adam Abraham", "Zane Xu")] = "Adam: baba \n Zane:..."
    # self.persona_convo = dict()

    # Loading in all personas. 
    init_env_file = f"{sim_folder}/environment/{str(self.step)}.json"
    init_env = json.load(open(init_env_file))
    for persona_name in reverie_meta['persona_names']: 
      persona_folder = f"{sim_folder}/personas/{persona_name}"
      if global_offline_mode:
        p_x = init_env[persona_name]["x"]
        p_y = init_env[persona_name]["y"]
        curr_persona = GaPersona(persona_name, persona_folder)

        self.personas[persona_name] = curr_persona
        self.personas_tile[persona_name] = (p_x, p_y)
        self.maze.tiles[p_y][p_x]["events"].add(curr_persona.scratch
                                                .get_curr_event_and_desc())
      else:
        curr_persona = DaiPersona(persona_name, persona_folder)
        self.personas[persona_name] = curr_persona

    # REVERIE SETTINGS PARAMETERS:  
    # <server_sleep> denotes the amount of time that our while loop rests each
    # cycle; this is to not kill our machine. 
    self.server_sleep = 0.1

    # SIGNALING THE FRONTEND SERVER: 
    # curr_sim_code.json contains the current simulation code, and
    # curr_step.json contains the current step of the simulation. These are 
    # used to communicate the code and step information to the frontend. 
    # Note that step file is removed as soon as the frontend opens up the 
    # simulation. 
    curr_sim_code = dict()
    curr_sim_code["sim_code"] = self.sim_code
    with open(f"{fs_temp_storage}/curr_sim_code.json", "w") as outfile: 
      outfile.write(json.dumps(curr_sim_code, indent=2))
    
    curr_step = dict()
    curr_step["step"] = self.step
    with open(f"{fs_temp_storage}/curr_step.json", "w") as outfile: 
      outfile.write(json.dumps(curr_step, indent=2))
    
    self.tag = False#case
    self.maze.planning_cycle = 2#extend planning cycle
    self.maze.last_planning_day = None#extend planning cycle
    self.maze.need_stagely_planning = True#extend planning cycle


  def save(self): 
    """
    Save all Reverie progress -- this includes Reverie's global state as well
    as all the personas.  

    INPUT
      None
    OUTPUT 
      None
      * Saves all relevant data to the designated memory directory
    """
    # <sim_folder> points to the current simulation folder.
    sim_folder = f"{fs_storage}/{self.sim_code}"

    # Save Reverie meta information.
    reverie_meta = dict() 
    reverie_meta["fork_sim_code"] = self.fork_sim_code
    reverie_meta["start_date"] = self.start_time.strftime("%B %d, %Y")
    reverie_meta["curr_time"] = self.curr_time.strftime("%B %d, %Y, %H:%M:%S")
    reverie_meta["sec_per_step"] = self.sec_per_step
    reverie_meta["maze_name"] = self.maze.maze_name
    reverie_meta["persona_names"] = list(self.personas.keys())
    reverie_meta["step"] = self.step
    reverie_meta_f = f"{sim_folder}/reverie/meta.json"
    with open(reverie_meta_f, "w") as outfile: 
      outfile.write(json.dumps(reverie_meta, indent=2))

    # Save the personas.
    for persona_name, persona in self.personas.items(): 
      save_folder = f"{sim_folder}/personas/{persona_name}/bootstrap_memory"
      persona.save(save_folder)


  def start_path_tester_server(self): 
    """
    Starts the path tester server. This is for generating the spatial memory
    that we need for bootstrapping a persona's state. 

    To use this, you need to open server and enter the path tester mode, and
    open the front-end side of the browser. 

    INPUT 
      None
    OUTPUT 
      None
      * Saves the spatial memory of the test agent to the path_tester_env.json
        of the temp storage. 
    """
    def print_tree(tree): 
      def _print_tree(tree, depth):
        dash = " >" * depth

        if type(tree) == type(list()): 
          if tree:
            print (dash, tree)
          return 

        for key, val in tree.items(): 
          if key: 
            print (dash, key)
          _print_tree(val, depth+1)
      
      _print_tree(tree, 0)

    # <curr_vision> is the vision radius of the test agent. Recommend 8 as 
    # our default. 
    curr_vision = 8
    # <s_mem> is our test spatial memory. 
    s_mem = dict()

    # The main while loop for the test agent. 
    while (True): 
      try: 
        curr_dict = {}
        tester_file = fs_temp_storage + "/path_tester_env.json"
        if check_if_file_exists(tester_file): 
          with open(tester_file) as json_file: 
            curr_dict = json.load(json_file)
            os.remove(tester_file)
          
          # Current camera location
          curr_sts = self.maze.sq_tile_size
          curr_camera = (int(math.ceil(curr_dict["x"]/curr_sts)), 
                         int(math.ceil(curr_dict["y"]/curr_sts))+1)
          curr_tile_det = self.maze.access_tile(curr_camera)

          # Initiating the s_mem
          world = curr_tile_det["world"]
          if curr_tile_det["world"] not in s_mem: 
            s_mem[world] = dict()

          # Iterating throughn the nearby tiles.
          nearby_tiles = self.maze.get_nearby_tiles(curr_camera, curr_vision)
          for i in nearby_tiles: 
            i_det = self.maze.access_tile(i)
            if (curr_tile_det["sector"] == i_det["sector"] 
                and curr_tile_det["arena"] == i_det["arena"]): 
              if i_det["sector"] != "": 
                if i_det["sector"] not in s_mem[world]: 
                  s_mem[world][i_det["sector"]] = dict()
              if i_det["arena"] != "": 
                if i_det["arena"] not in s_mem[world][i_det["sector"]]: 
                  s_mem[world][i_det["sector"]][i_det["arena"]] = list()
              if i_det["game_object"] != "": 
                if (i_det["game_object"] 
                    not in s_mem[world][i_det["sector"]][i_det["arena"]]):
                  s_mem[world][i_det["sector"]][i_det["arena"]] += [
                                                         i_det["game_object"]]

        # Incrementally outputting the s_mem and saving the json file. 
        print ("= " * 15)
        out_file = fs_temp_storage + "/path_tester_out.json"
        with open(out_file, "w") as outfile: 
          outfile.write(json.dumps(s_mem, indent=2))
        print_tree(s_mem)

      except:
        pass

      time.sleep(self.server_sleep * 10)


  def start_server(self, int_counter): 
    """
    The main backend server of Reverie. 
    This function retrieves the environment file from the frontend to 
    understand the state of the world, calls on each personas to make 
    decisions based on the world state, and saves their moves at certain step
    intervals. 
    INPUT
      int_counter: Integer value for the number of steps left for us to take
                   in this iteration. 
    OUTPUT 
      None
    """
    # <sim_folder> points to the current simulation folder.
    sim_folder = f"{fs_storage}/{self.sim_code}"

    # When a persona arrives at a game object, we give a unique event
    # to that object. 
    # e.g., ('double studio[...]:bed', 'is', 'unmade', 'unmade')
    # Later on, before this cycle ends, we need to return that to its 
    # initial state, like this: 
    # e.g., ('double studio[...]:bed', None, None, None)
    # So we need to keep track of which event we added. 
    # <game_obj_cleanup> is used for that. 
    game_obj_cleanup = dict()

    # The main while loop of Reverie. 
    n = 1
    while (True): 
      # Done with this iteration if <int_counter> reaches 0. 
      if int_counter == 0: 
        break
      
      if global_offline_mode:
        # <curr_env_file> file is the file that our frontend outputs. When the
        # frontend has done its job and moved the personas, then it will put a 
        # new environment file that matches our step count. That's when we run 
        # the content of this for loop. Otherwise, we just wait. 
        curr_env_file = f"{sim_folder}/environment/{self.step}.json"
        if check_if_file_exists(curr_env_file):
          # If we have an environment file, it means we have a new perception
          # input to our personas. So we first retrieve it.
          try: 
            # Try and save block for robustness of the while loop.
            with open(curr_env_file) as json_file:
              new_env = json.load(json_file)
              env_retrieved = True
          except: 
            pass
        
          if env_retrieved: 
            # This is where we go through <game_obj_cleanup> to clean up all 
            # object actions that were used in this cylce. 
            for key, val in game_obj_cleanup.items(): 
              # We turn all object actions to their blank form (with None). 
              self.maze.turn_event_from_tile_idle(key, val)
            # Then we initialize game_obj_cleanup for this cycle. 
            game_obj_cleanup = dict()

            # We first move our personas in the backend environment to match 
            # the frontend environment. 
            for persona_name, persona in self.personas.items(): 
              # <curr_tile> is the tile that the persona was at previously. 
              curr_tile = self.personas_tile[persona_name]
              # <new_tile> is the tile that the persona will move to right now,
              # during this cycle. 
              new_tile = (new_env[persona_name]["x"], 
                          new_env[persona_name]["y"])

              # We actually move the persona on the backend tile map here. 
              self.personas_tile[persona_name] = new_tile
              self.maze.remove_subject_events_from_tile(persona.name, curr_tile)
              self.maze.add_event_from_tile(persona.scratch
                                          .get_curr_event_and_desc(), new_tile)

              # Now, the persona will travel to get to their destination. *Once*
              # the persona gets there, we activate the object action.
              if not persona.scratch.planned_path: 
                # We add that new object action event to the backend tile map. 
                # At its creation, it is stored in the persona's backend. 
                game_obj_cleanup[persona.scratch
                                .get_curr_obj_event_and_desc()] = new_tile
                self.maze.add_event_from_tile(persona.scratch
                                      .get_curr_obj_event_and_desc(), new_tile)
                # We also need to remove the temporary blank action for the 
                # object that is currently taking the action. 
                blank = (persona.scratch.get_curr_obj_event_and_desc()[0], 
                        None, None, None)
                self.maze.remove_event_from_tile(blank, new_tile)

            # Then we need to actually have each of the personas perceive and
            # move. The movement for each of the personas comes in the form of
            # x y coordinates where the persona will move towards. e.g., (50, 34)
            # This is where the core brains of the personas are invoked. 
            movements = {"persona": dict(), 
                        "meta": dict()}
            for persona_name, persona in self.personas.items(): 
              # <next_tile> is a x,y coordinate. e.g., (58, 9)
              # <pronunciatio> is an emoji. e.g., "\ud83d\udca4"
              # <description> is a string description of the movement. e.g., 
              #   writing her next novel (editing her novel) 
              #   @ double studio:double studio:common room:sofa
              # next_tile, pronunciatio, description = persona.move(
              next_tile, pronunciatio, description = persona.single_workflow(
                self.maze, self.personas, self.personas_tile[persona_name], 
                self.curr_time)
              movements["persona"][persona_name] = {}
              movements["persona"][persona_name]["movement"] = next_tile
              movements["persona"][persona_name]["pronunciatio"] = pronunciatio
              movements["persona"][persona_name]["description"] = description
              movements["persona"][persona_name]["chat"] = (persona
                                                            .scratch.chat)

            # Include the meta information about the current stage in the 
            # movements dictionary. 
            movements["meta"]["curr_time"] = (self.curr_time 
                                              .strftime("%B %d, %Y, %H:%M:%S"))

            # We then write the personas' movements to a file that will be sent 
            # to the frontend server. 
            # Example json output: 
            # {"persona": {"Maria Lopez": {"movement": [58, 9]}},
            #  "persona": {"Klaus Mueller": {"movement": [38, 12]}}, 
            #  "meta": {curr_time: <datetime>}}
            ###---lg---###
            exist_move_file = f"{sim_folder}/movement/"
            if not os.path.exists(exist_move_file):
              os.makedirs(exist_move_file)
            ###---lg---###
            curr_move_file = f"{sim_folder}/movement/{self.step}.json"
            with open(curr_move_file, "w") as outfile: 
              outfile.write(json.dumps(movements, indent=2))
          

            # After this cycle, the world takes one step forward, and the 
            # current time moves by <sec_per_step> amount. 
            self.step += 1
            self.curr_time += datetime.timedelta(seconds=self.sec_per_step)

            int_counter -= 1
      
      else: # online
        for persona_name, persona in self.personas.items():
          for node in self.maze.get_memories():
            if node.name == persona_name:
              node.new_or_old = False
          print("\n\n\n★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ "+persona_name+" 第"+str(n)+"轮"+" ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★")
          persona.single_workflow(self.maze, self.curr_time)
                
        n += 1
        self.step += 1
        self.curr_time += datetime.timedelta(seconds=self.sec_per_step)
        print("❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ next step ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤")
        int_counter -= 1
          
      # Sleep so we don't burn our machines. 
      time.sleep(self.server_sleep)


  def open_server(self): 
    """
    Open up an interactive terminal prompt that lets you run the simulation 
    step by step and probe agent state. 

    INPUT 
      None
    OUTPUT
      None
    """
    global command_queue
    print ("Note: The agents in this simulation package are computational")
    print ("constructs powered by generative agents architecture and LLM. We")
    print ("clarify that these agents lack human-like agency, consciousness,")
    print ("and independent decision-making.\n---")

    # <sim_folder> points to the current simulation folder.
    sim_folder = f"{fs_storage}/{self.sim_code}"

    while True: 
      # sim_command = input("Enter option: ")
      print("Enter option: ")
      sim_command = command_queue.get()
      print(sim_command)
      sim_command = sim_command.strip()
      ret_str = ""

      try: 
        if sim_command.lower() in ["f", "fin", "finish", "save and finish"]: 
          # Finishes the simulation environment and saves the progress. 
          # Example: fin
          self.save()
          break

        elif sim_command.lower() == "start path tester mode": 
          # Starts the path tester and removes the currently forked sim files.
          # Note that once you start this mode, you need to exit out of the
          # session and restart in case you want to run something else. 
          shutil.rmtree(sim_folder) 
          self.start_path_tester_server()

        elif sim_command.lower() == "exit": 
          # Finishes the simulation environment but does not save the progress
          # and erases all saved data from current simulation. 
          # Example: exit 
          shutil.rmtree(sim_folder) 
          break 

        elif sim_command.lower() == "save": 
          # Saves the current simulation progress. 
          # Example: save
          self.save()

        elif sim_command[:3].lower() == "run": # base_the_ville_n25
          # Runs the number of steps specified in the prompt.
          # Example: run 1000
          int_count = int(sim_command.split()[-1])
          rs.start_server(int_count)

        elif ("print persona schedule" 
              in sim_command[:22].lower()): 
          # Print the decomposed schedule of the persona specified in the 
          # prompt.
          # Example: print persona schedule Isabella Rodriguez
          ret_str += (self.personas[" ".join(sim_command.split()[-2:])]
                      .scratch.get_str_daily_schedule_summary())

        elif ("print all persona schedule" 
              in sim_command[:26].lower()): 
          # Print the decomposed schedule of all personas in the world. 
          # Example: print all persona schedule
          for persona_name, persona in self.personas.items(): 
            ret_str += f"{persona_name}\n"
            ret_str += f"{persona.scratch.get_str_daily_schedule_summary()}\n"
            ret_str += f"---\n"

        elif ("print hourly org persona schedule" 
              in sim_command.lower()): 
          # Print the hourly schedule of the persona specified in the prompt.
          # This one shows the original, non-decomposed version of the 
          # schedule.
          # Ex: print persona schedule Isabella Rodriguez
          ret_str += (self.personas[" ".join(sim_command.split()[-2:])]
                      .scratch.get_str_daily_schedule_hourly_org_summary())

        elif ("print persona current tile" 
              in sim_command[:26].lower()): 
          # Print the x y tile coordinate of the persona specified in the 
          # prompt. 
          # Ex: print persona current tile Isabella Rodriguez
          ret_str += str(self.personas[" ".join(sim_command.split()[-2:])]
                      .scratch.curr_tile)

        elif ("print persona chatting with buffer" 
              in sim_command.lower()): 
          # Print the chatting with buffer of the persona specified in the 
          # prompt.
          # Ex: print persona chatting with buffer Isabella Rodriguez
          curr_persona = self.personas[" ".join(sim_command.split()[-2:])]
          for p_n, count in curr_persona.scratch.chatting_with_buffer.items(): 
            ret_str += f"{p_n}: {count}"

        elif ("print persona associative memory (event)" 
              in sim_command.lower()):
          # Print the associative memory (event) of the persona specified in
          # the prompt
          # Ex: print persona associative memory (event) Isabella Rodriguez
          ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
          ret_str += (self.personas[" ".join(sim_command.split()[-2:])]
                                       .a_mem.get_str_seq_events())

        elif ("print persona associative memory (thought)" 
              in sim_command.lower()): 
          # Print the associative memory (thought) of the persona specified in
          # the prompt
          # Ex: print persona associative memory (thought) Isabella Rodriguez
          ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
          ret_str += (self.personas[" ".join(sim_command.split()[-2:])]
                                       .a_mem.get_str_seq_thoughts())

        elif ("print persona associative memory (chat)" 
              in sim_command.lower()): 
          # Print the associative memory (chat) of the persona specified in
          # the prompt
          # Ex: print persona associative memory (chat) Isabella Rodriguez
          ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
          ret_str += (self.personas[" ".join(sim_command.split()[-2:])]
                                       .a_mem.get_str_seq_chats())

        elif ("print persona spatial memory" 
              in sim_command.lower()): 
          # Print the spatial memory of the persona specified in the prompt
          # Ex: print persona spatial memory Isabella Rodriguez
          self.personas[" ".join(sim_command.split()[-2:])].s_mem.print_tree()

        elif ("print current time" 
              in sim_command[:18].lower()): 
          # Print the current time of the world. 
          # Ex: print current time
          ret_str += f'{self.curr_time.strftime("%B %d, %Y, %H:%M:%S")}\n'
          ret_str += f'steps: {self.step}'

        elif ("print tile event" 
              in sim_command[:16].lower()): 
          # Print the tile events in the tile specified in the prompt 
          # Ex: print tile event 50, 30
          cooordinate = [int(i.strip()) for i in sim_command[16:].split(",")]
          for i in self.maze.access_tile(cooordinate)["events"]: 
            ret_str += f"{i}\n"

        elif ("print tile details" 
              in sim_command.lower()): 
          # Print the tile details of the tile specified in the prompt 
          # Ex: print tile event 50, 30
          cooordinate = [int(i.strip()) for i in sim_command[18:].split(",")]
          for key, val in self.maze.access_tile(cooordinate).items(): 
            ret_str += f"{key}: {val}\n"

        elif ("call -- analysis" 
              in sim_command.lower()): 
          # Starts a stateless chat session with the agent. It does not save 
          # anything to the agent's memory. 
          # Ex: call -- analysis Isabella Rodriguez
          persona_name = sim_command[len("call -- analysis"):].strip() #Do you support Isabella Rodriguez as mayor?
          # self.personas[persona_name].open_convo_session("analysis")#Do you want to run for mayor in the local election?
          self.personas[persona_name].open_convo_session("analysis", self.maze.vbase)#Do you want to run for mayor in the local election?

        elif ("call -- load history" 
              in sim_command.lower()): 
          curr_file = maze_assets_loc + "/" + sim_command[len("call -- load history"):].strip() 
          # call -- load history the_ville/agent_history_init_n3.csv #必须要在run之后执行

          rows = read_file_to_list(curr_file, header=True, strip_trail=True)[1]
          clean_whispers = []
          for row in rows: 
            agent_name = row[0].strip() 
            whispers = row[1].split(";")
            whispers = [whisper.strip() for whisper in whispers]
            for whisper in whispers: 
              clean_whispers += [[agent_name, whisper]]

          load_history_via_whisper(self.personas, clean_whispers)
        
        elif ("call -- run spp" #插入spp模块。
              in sim_command.lower()): 
          self.maze.institution = DaiInstitution()
          # args = vars(parse_args())
          # model_name = args['model']
          
          # if model_name in gpt_configs:
          #     args['gpt_config'] = gpt_configs[model_name] # our configs
          # else:
          #     args['gpt_config'] = default_gpt_config
          #     args['gpt_config']['engine'] = model_name
          
          # # overwrite temperature and top_p
          # args['gpt_config']['temperature'] = args['temperature']
          # args['gpt_config']['top_p'] = args['top_p']
          # print("run args:", args)
          # Is_or_Not_Institution = input("Is_or_Not_Institution, Enter Input (yes or no): ")
          print("Is_or_Not_Institution, Enter Input (yes or no): ")
          Is_or_Not_Institution = command_queue.get()
          print(Is_or_Not_Institution)
          if Is_or_Not_Institution == 'yes':
            self.maze.content = "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."
            # self.maze.policy = run(args, case=self.maze.content)
            self.maze.policy = self.maze.institution.run(case=self.maze.content)
          else:
            # run(args, case=None)#
            self.maze.institution.run(case=None)#
        
        elif ("init dk" #初始化向量数据库。
              in sim_command.lower()): 
          #Initialize domain knowledge
          content = "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."
          # self.maze.vbase = Storage(content=content)
          self.maze.vbase = Storage(case=content)
          query = "nuclear"
          texts = self.maze.vbase.get_texts(query, 2)
          print("################################")
          print(texts)
          print("################################")
        
        elif ("call -- load case" #将事件广播给每个智能体。
              in sim_command.lower()): 
          curr_file = maze_assets_loc + "/" + sim_command[len("call -- load case"):].strip() 
          # call -- load case the_ville/agent_history_init_n3.csv

          rows = read_file_to_list(curr_file, header=True, strip_trail=True)[1]
          clean_whispers = []
          # Your_content = input("Input your content: ")
          print("Input your content: ")
          Your_content = command_queue.get()
          print(Your_content)
          for row in rows: 
            agent_name = row[0].strip() 
            # whispers = row[1].split(";")
            whispers = ["Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."]#case
            whispers = [Your_content]#
            whispers = [whisper.strip() for whisper in whispers]
            for whisper in whispers: 
              clean_whispers += [[agent_name, whisper]]

          load_history_via_whisper(self.personas, clean_whispers)
          self.tag = True#case
        
        elif ("call -- release policy" #将政策发布到所有智能体。
              in sim_command.lower()): 
          if self.tag == True:
            curr_file = maze_assets_loc + "/" + sim_command[len("call -- release policy"):].strip() 
            # call -- release policy the_ville/agent_history_init_n3.csv

            rows = read_file_to_list(curr_file, header=True, strip_trail=True)[1]
            clean_whispers = []
            policy = "The policy is as follows: " + self.maze.policy[0]
            for row in rows: 
              agent_name = row[0].strip() 
              # whispers = row[1].split(";")
              whispers = [policy]#
              whispers = [whisper.strip() for whisper in whispers]
              for whisper in whispers: 
                clean_whispers += [[agent_name, whisper]]

            load_history_via_whisper(self.personas, clean_whispers)
          else:
            print("<---There is no case.--->")
        
        elif ("call -- load weibo"  # 将事件广播给每个智能体。
              in sim_command.lower()):
          # tyn
          # truth = input("Input your content: ")
          truth = "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."

          # s, p, o = generate_action_event_triple_new(truth)
          s="日本"
          p="排放"
          o="核废水"
          description = truth


          #创建一个memory_node
          memory_node = MemoryNode("public",s, p, o, description, True)         

          self.maze.add_memory(memory_node)

        print (ret_str)

      except:
        traceback.print_exc()
        print ("Error.")
        pass

################SPP###############
# # import os
# # import json
# import argparse
# from models import OpenAIWrapper
# from tasks import get_task
# # import time


# SLEEP_RATE = 30 # sleep between calls


# def output_log_jsonl(log_file, all_logs):
#     with open(log_file, "w") as f:
#         for log in all_logs:
#             f.write(json.dumps(log) + "\n")

# def _post_process_raw_response(task, raw_output_batch, method):
#     unwrapped_output_batch = []
#     if_success_batch = []
#     for output in raw_output_batch:
#         unwrapped_output, if_success_flag = task.prompt_unwrap(output, method)
#         unwrapped_output_batch.append(unwrapped_output)
#         if_success_batch.append(if_success_flag)
#     return unwrapped_output_batch, if_success_batch

# def _run_task(task_name, gpt, task, i, method, num_generation, args):#
#     if task_name in ['trivia_creative_writing', 'logic_grid_puzzle']:
#         # get prompt
#         prompt = task.get_input_prompt(i, method=method)
#         # get raw response
#         raw_output_batch, raw_response_batch = gpt.run(prompt=prompt, n=num_generation)
#         if raw_output_batch == [] or raw_response_batch == []: # handle exception
#             return {}    
#         # get parsed response, and the success flags (whether or not the parsing is success) (standard prompt always success)
#         unwrapped_output_batch, if_success_batch = _post_process_raw_response(task, raw_output_batch, method)
#         # compute automatic metric (different for each task), e.g., if the output contains all the answers
#         test_output_infos = [task.test_output(i, output) for output in unwrapped_output_batch]
#         # log output
#         log_output = {
#             "idx": i,
#             "raw_response": raw_response_batch,
#             "unwrapped_output": unwrapped_output_batch,
#             "parsing_success_flag": if_success_batch,
#             "test_output_infos": test_output_infos
#         }
#     elif task_name in ['institution']:
#       # get prompt
#         prompt = task.get_input_prompt(i, method=method)
#         # get raw response
#         raw_output_batch, raw_response_batch = gpt.run(prompt=prompt, n=num_generation)
#         if raw_output_batch == [] or raw_response_batch == []: # handle exception
#             return {}    
#         # get parsed response, and the success flags (whether or not the parsing is success) (standard prompt always success)
#         unwrapped_output_batch, if_success_batch = _post_process_raw_response(task, raw_output_batch, method)
#         # print policy
#         print('################---Policy begin---################')
#         print(unwrapped_output_batch)
#         print('################---Policy end---################')
#         # log output
#         log_output = {
#             "raw_response": raw_response_batch,
#             "unwrapped_output": unwrapped_output_batch,
#             "parsing_success_flag": if_success_batch
#         }
#         return log_output#
#     elif task_name == 'codenames_collaborative':
#         # get spymaster hint word
#         spymaster_prompt = task.get_input_prompt(i, method=method, role='spymaster')
#         raw_spymaster_output, raw_response_spymaster = gpt.run(prompt=spymaster_prompt, n=1)
#         # raw_spymaster_output, raw_response_spymaster = gpt.run(prompt=spymaster_prompt, n=1, system_message="You are an AI assistant that plays the Spymaster role in Codenames.")
#         if raw_spymaster_output == [] or raw_response_spymaster == []: # handle exception
#             return {}
#         spymaster_output, if_success_batch_spymaster = _post_process_raw_response(task, raw_spymaster_output, method)
#         hint_word = spymaster_output[0].replace(".", "").strip()
#         print(f"\tidx: {i} | done spymaster, hint word: {hint_word}")
#         # sleep before calling guesser
#         time.sleep(SLEEP_RATE)
#         # get guesser result
#         guesser_prompt = task.get_input_prompt(i, method=method, role='guesser', hint_word=hint_word)
#         raw_guesser_output, raw_response_batch_guesser = gpt.run(prompt=guesser_prompt, n=num_generation)
#         # raw_guesser_output, raw_response_batch_guesser = gpt.run(prompt=guesser_prompt, n=num_generation, system_message="You are an AI assistant that plays the Guesser role in Codenames.")
#         if raw_guesser_output == [] or raw_response_batch_guesser == []: # handle exception
#             return {}
#         guesser_output_batch, if_success_batch_guesser = _post_process_raw_response(task, raw_guesser_output, method)
#         # compute automatic metric (different for each task), e.g., if the output contains all the answers
#         test_output_infos = [task.test_output(i, output) for output in guesser_output_batch]
#         # log output
#         log_output = {
#             "idx": i,
#             "raw_response_spymaster": raw_response_spymaster,
#             "raw_response_guesser": raw_response_batch_guesser,
#             "spymaster_output": spymaster_output,
#             "guesser_output": guesser_output_batch,
#             "hint_word": hint_word,
#             "parsing_success_flag_spymaster": if_success_batch_spymaster,
#             "parsing_success_flag_guesser": if_success_batch_guesser,
#             "test_output_infos": test_output_infos
#         }
#     else:
#         raise NotImplementedError(f"task {task_name} not implemented; please choose from ['trivia_creative_writing', 'logic_grid_puzzle', 'codenames_collaborative']")

#     # log everything else that is related
#     log_output.update(args)
#     log_output.update({"task_data":task.get_input(i)})
#     return log_output

# def run(args, case):
#     # get configs
#     gpt_config = args['gpt_config']
#     task_name = args['task']
#     method = args['method']
#     start_idx, end_idx = args['task_start_index'], args['task_end_index']
#     task_data_file = args['task_data_file']
#     num_generation = args['num_generation']

#     additional_output_note = args['additional_output_note']
#     system_message = args['system_message']
#     print(f"setting default system message: {system_message}")
    
#     # setup gpt api
#     gpt = OpenAIWrapper(config=gpt_config, system_message=system_message)

#     # setup log file
#     if system_message == "":
#         log_file = f"logs/{task_name}/{task_data_file}__method-{method}_model-{gpt_config['model']}_temp-{gpt_config['temperature']}_topp-{gpt_config['top_p']}_start{start_idx}-end{end_idx}{additional_output_note}__without_sys_mes.jsonl"
#     else:
#         log_file = f"logs/{task_name}/{task_data_file}__method-{method}_model-{gpt_config['model']}_temp-{gpt_config['temperature']}_topp-{gpt_config['top_p']}_start{start_idx}-end{end_idx}{additional_output_note}__with_sys_mes.jsonl"
#     # if system_message == "":
#     #     log_file = f"logs/{task_name}/{task_data_file}__method-{method}_engine-{gpt_config['engine']}_temp-{gpt_config['temperature']}_topp-{gpt_config['top_p']}_start{start_idx}-end{end_idx}{additional_output_note}__without_sys_mes.jsonl"
#     # else:
#     #     log_file = f"logs/{task_name}/{task_data_file}__method-{method}_engine-{gpt_config['engine']}_temp-{gpt_config['temperature']}_topp-{gpt_config['top_p']}_start{start_idx}-end{end_idx}{additional_output_note}__with_sys_mes.jsonl"
    
#     os.makedirs(os.path.dirname(log_file), exist_ok=True)

#     ###---Institution begin---###
#     if case is not None:
#       task = get_task("institution", file=case)
#       log_output = _run_task("institution", gpt, task, 0, method, num_generation, args)#
#       return log_output["unwrapped_output"]
#     ###---Institution end---###
    
#     # setup task
#     task = get_task(task_name, file=task_data_file)
    
#     all_logs = []
#     print("start running ... log file:", log_file)

#     print()
#     start = max(start_idx, 0)
#     end = min(end_idx, len(task))
#     print("total num of instances:", end - start)
#     for i in range(start, end):
#         log_output = _run_task(task_name, gpt, task, i, method, num_generation, args)#
#         all_logs.append(log_output)
#         print("\tidx:", i, "done | usage so far:", gpt.compute_gpt_usage())
#         # output log at each iteration
#         output_log_jsonl(log_file, all_logs)
#         # sleep
#         time.sleep(SLEEP_RATE)



# # TODO: add your custom model config here:
# gpt_configs = {
#     "gpt4-32k": {
#         "engine": "gpt-4-32k",#《可以自己命名》
#         "temperature": 0.0,
#         "max_tokens": 5000,
#         "top_p": 1.0,
#         "frequency_penalty": 0.0,
#         "presence_penalty": 0.0,
#         "stop": None
#     },
#     "gpt3.5": {
#         # "engine": "gpt-35-turbo",#《可以自己命名》
#         "model": "gpt-3.5-turbo",#《可以自己命名》
#         "temperature": 0.0,
#         "max_tokens": 2000,
#         "top_p": 1.0,
#         "frequency_penalty": 0.0,
#         "presence_penalty": 0.0,
#         "stop": None
#     },
#     "llama2": {
#         # "engine": "gpt-35-turbo",#《可以自己命名》
#         "model": "Llama-2-7b-chat-hf",#《可以自己命名》
#         # "model": "gpt-3.5-turbo",#《可以自己命名》
#         "temperature": 0.0,
#         "max_tokens": 2000,
#         "top_p": 1.0,
#         "frequency_penalty": 0.0,
#         "presence_penalty": 0.0,
#         "stop": None
#     },
#     "vicuna": {
#         # "engine": "gpt-35-turbo",#《可以自己命名》
#         # "model": "vicuna-13b-v1.5",#《可以自己命名》
#         "model": "vicuna-13b-v1.5-16k",#《可以自己命名》
#         # "model": "vicuna-33b-v1.3",#《可以自己命名》
#         # "model": "gpt-3.5-turbo",#《可以自己命名》
#         "temperature": 0.0,
#         "max_tokens": 2000,
#         "top_p": 1.0,
#         "frequency_penalty": 0.0,
#         "presence_penalty": 0.0,
#         "stop": None
#     }
# }

# default_gpt_config = {
#     "engine": None,
#     "temperature": 0.0,
#     "max_tokens": 5000,
#     "top_p": 1.0,
#     "frequency_penalty": 0.0,
#     "presence_penalty": 0.0,
#     "stop": None
# }

# def parse_args():
#     model_choices = list(gpt_configs.keys())
#     args = argparse.ArgumentParser()
#     # args.add_argument('--model', type=str, choices=model_choices, required=True)
#     # args.add_argument('--method', type=str, choices=['standard','cot','spp','spp_profile', 'spp_fixed_persona'], required=True)
#     # args.add_argument('--task', type=str, choices=['trivia_creative_writing', 'logic_grid_puzzle', 'codenames_collaborative'], required=True)
#     # args.add_argument('--task_data_file', type=str, required=True)
#     # args.add_argument('--task_start_index', type=int, required=True)
#     # args.add_argument('--task_end_index', type=int, required=True)
#     # args.add_argument('--num_generation', type=int, default=1)
#     # args.add_argument('--additional_output_note', type=str, default="")
#     # args.add_argument('--temperature', type=float, default=0.0)
#     # args.add_argument('--top_p', type=float, default=1.0)
#     # args.add_argument('--system_message', type=str, default="")
#     # args.add_argument('--model', type=str, default="llama2")
#     args.add_argument('--model', type=str, default="vicuna")
#     # args.add_argument('--model', type=str, default="gpt3.5")#20231108#3
#     args.add_argument('--method', type=str, default='spp')
#     args.add_argument('--task', type=str, default='trivia_creative_writing')
#     args.add_argument('--task_data_file', type=str, default="trivia_creative_writing_100_n_5.jsonl")
#     args.add_argument('--task_start_index', type=int, default=66)
#     args.add_argument('--task_end_index', type=int, default=68)
#     args.add_argument('--num_generation', type=int, default=1)
#     args.add_argument('--additional_output_note', type=str, default="")
#     args.add_argument('--temperature', type=float, default=0.0)
#     args.add_argument('--top_p', type=float, default=1.0)
#     args.add_argument('--system_message', type=str, default="")
    
#     args = args.parse_args()
#     return args
################SPP###############

def start_sim(forked_sim_name, new_sim_name):
  global rs
  rs = ReverieServer(forked_sim_name, new_sim_name)
  global_rs = rs#
  rs.open_server()

if __name__ == '__main__':
  # rs = ReverieServer("base_the_ville_isabella_maria_klaus", 
  #                    "July1_the_ville_isabella_maria_klaus-step-3-1")
  # rs = ReverieServer("July1_the_ville_isabella_maria_klaus-step-3-20", 
  #                    "July1_the_ville_isabella_maria_klaus-step-3-21")
  # rs.open_server()

  origin = input("Enter the name of the forked simulation: ").strip()
  target = input("Enter the name of the new simulation: ").strip()

  rs = ReverieServer(origin, target)
  global_rs = rs#
  rs.open_server()

#自动加载初始化文件未找到。

#test1

#test2

#test3

#test4
