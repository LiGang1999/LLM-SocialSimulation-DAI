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

import asyncio
import datetime
import json
import math
import os
import pickle
import shutil
import threading
import time
import traceback
from dataclasses import asdict, dataclass, field, fields, replace
from queue import Queue

import numpy
from institution import *
from maze import *
from memorynode import *
from persona.persona import *
from selenium import webdriver
from utils import *
from utils import config
from utils.config import *
from vector_db import *

rs = None
rs_lock = threading.Lock()


def get_rs():
    with rs_lock:
        return rs


def set_rs(new_rs):
    global rs
    with rs_lock:
        rs = new_rs


command_queue = Queue()
online_relation = Queue()

BASE_TEMPLATES = [
    "base_the_villie_isabella_maria_klaus",
    "base_the_villie_isabella_maria_klaus_online",
    "base_the_villie_n25",
]


##############################################################################
#                                  REVERIE                                   #
##############################################################################


def from_dict(cls, input_dict):
    # Initialize with default values
    obj = cls()
    # Update with the values from input_dict
    return replace(
        obj,
        **{key: value for key, value in input_dict.items() if key in {f.name for f in fields(cls)}},
    )


@dataclass
class EventInfo:
    description: str = ""
    websearch: str = ""
    policy: str = ""  # TODO: the policy and websearch should be two lists
    access_list: list[str] = field(default_factory=list)


@dataclass
class LLMConfig:
    api_base: str = config.openai_api_base
    api_key: str = config.openai_api_key
    engine: str = ""
    tempreature: float = 1.0
    max_tokens: int = 512
    top_p: float = 0.7
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = False


@dataclass
class PersonaConfig:
    name: str = ""
    daily_plan_req: str = ""
    first_name: str = ""
    last_name: str = ""
    age: int = 0
    innate: str = ""
    learned: str = ""
    currently: str = ""
    lifestyle: str = ""
    living_area: str = ""
    bibliography: str = ""  # This one is additional field


# The data class representing the meta information of a simulation.
# Passed as an argument when creating a new simulation
# If a field is none, it will be inherited from the forking template
@dataclass
class ReverieConfig:
    sim_code: str = ""  # current simulation code
    sim_mode: str | None = ""  # simulation mode.
    start_date: str | None = ""  # simulation start date
    curr_time: str | None = ""  # simulation current time
    maze_name: str | None = ""  # map name
    step: int | None = 0  # current steps
    llm_config: LLMConfig | None = field(default_factory=LLMConfig)  # llm config
    persona_configs: dict[str, PersonaConfig] = field(default_factory=dict)  # persona config
    public_events: List[dict] = field(default_factory=list)  # public events
    direction: str | None = ""  # The instruction of what the agents should do with each other
    initial_rounds: int | None = 0  # The number of initial rounds


def bootstrap_persona(path: str, config: PersonaConfig):

    def update_scratch_json(path: str, config: PersonaConfig):
        scratch_file_path = os.path.join(path, "bootstrap_memory/scratch.json")

        # Load the existing scratch.json
        with open(scratch_file_path, "r") as f:
            scratch_data = json.load(f)

        # Update the fields with the values from PersonaConfig
        scratch_data["daily_plan_req"] = config.daily_plan_req
        scratch_data["name"] = config.name
        scratch_data["first_name"] = config.first_name
        scratch_data["last_name"] = config.last_name
        scratch_data["age"] = config.age
        scratch_data["learned"] = config.learned
        scratch_data["currently"] = config.currently
        scratch_data["lifestyle"] = config.lifestyle
        scratch_data["living_area"] = config.living_area

        # Save the updated scratch.json
        with open(scratch_file_path, "w") as f:
            json.dump(scratch_data, f, indent=4)

    # Define the required directory structure
    directories = ["bootstrap_memory", "bootstrap_memory/associative_memory"]

    # Define the required files with their default content
    files = {
        "bootstrap_memory/associative_memory/embeddings.json": {},
        "bootstrap_memory/associative_memory/kw_strength.json": {},
        "bootstrap_memory/associative_memory/nodes.json": {},
        "bootstrap_memory/scratch.json": {
            "vision_r": 8,
            "att_bandwidth": 8,
            "retention": 8,
            "curr_time": None,
            "curr_tile": None,
            "daily_plan_req": "",
            "name": "",
            "first_name": "",
            "last_name": "",
            "age": 0,
            "innate": "kind, inquisitive, passionate",
            "learned": "",
            "currently": "",
            "lifestyle": "",
            "living_area": "",
            "concept_forget": 100,
            "daily_reflection_time": 180,
            "daily_reflection_size": 5,
            "overlap_reflect_th": 4,
            "kw_strg_event_reflect_th": 10,
            "kw_strg_thought_reflect_th": 9,
            "recency_w": 1,
            "relevance_w": 1,
            "importance_w": 1,
            "recency_decay": 0.99,
            "importance_trigger_max": 150,
            "importance_trigger_curr": 150,
            "importance_ele_n": 0,
            "thought_count": 5,
            "daily_req": [],
            "f_daily_schedule": [],
            "f_daily_schedule_hourly_org": [],
            "act_address": None,
            "act_start_time": None,
            "act_duration": None,
            "act_description": None,
            "act_pronunciatio": None,
            "act_event": [None, None, None],
            "act_obj_description": None,
            "act_obj_pronunciatio": None,
            "act_obj_event": [config.name, None, None],
            "chatting_with": None,
            "chat": None,
            "chatting_with_buffer": {},
            "chatting_end_time": None,
            "act_path_set": False,
            "planned_path": [],
        },
        "bootstrap_memory/spatial_memory.json": {},
    }

    ensure_directories(path, directories)
    ensure_files_with_default_content(path, files)
    update_scratch_json(path, config)


class ReverieServer:
    BASE_TEMPLATES = [
        "base_the_villie_isabella_maria_klaus",
        "base_the_villie_isabella_maria_klaus_online",
        "base_the_villie_n25",
    ]

    def __init__(self, template_sim_code, sim_config: ReverieConfig):
        # Check if all required fields in sim_config are populated
        missing_fields = []

        self.is_running = False

        for field_name, field_value in vars(sim_config).items():
            if field_value is None or (isinstance(field_value, str) and field_value == ""):
                missing_fields.append(field_name)

        if missing_fields:
            L.error(f"Missing required fields in sim_config: {', '.join(missing_fields)}")
            # You can raise an exception here if necessary:
            # raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        self.template_sim_code = template_sim_code
        template_folder = f"{storage_path}/{self.template_sim_code}"

        self.sim_code = sim_config.sim_code
        sim_folder = f"{storage_path}/{self.sim_code}"

        if check_if_dir_exists(sim_folder):
            if self.template_sim_code in BASE_TEMPLATES:
                L.error(
                    f"Cannot overwrite base template {self.template_sim_code}. Operation aborted."
                )
            else:
                L.warning(
                    f"Simulation {sim_folder} exists. It will be overwritten by the new environment."
                )
                removeanything(sim_folder)

        copyanything(template_folder, sim_folder)

        self.sim_mode = sim_config.sim_mode

        reverie_meta = {}
        # reverie_meta is loaded from the meta.json file in the simulation folder. This is only for backward compatibility

        with open(f"{sim_folder}/reverie/meta.json", "r") as infile:
            reverie_meta = json.load(infile)
        reverie_meta["curr_time"] = sim_config.curr_time
        reverie_meta["step"] = sim_config.step
        reverie_meta["persona_names"] = [
            persona.name for persona in sim_config.persona_configs.values()
        ]
        reverie_meta["maze_name"] = sim_config.maze_name
        reverie_meta["sim_mode"] = sim_config.sim_mode
        reverie_meta["start_date"] = sim_config.start_date
        reverie_meta["llm_config"] = asdict(sim_config.llm_config)

        # This one should be called sim_code, but call it template_sim_code to maintain backward compatability
        reverie_meta["template_sim_code"] = sim_config.sim_code
        self.storage_home = f"{storage_path}/{self.sim_code}"

        # check fields for reverie_meta

        if "sim_mode" not in reverie_meta:
            reverie_meta["sim_mode"] = "offline"

        with open(f"{sim_folder}/reverie/meta.json", "w") as outfile:
            outfile.write(json.dumps(reverie_meta, indent=2))

        # LOADING REVERIE'S GLOBAL VARIABLES
        # Whether the reverie runs in offline mode or online mode

        # The start datetime of the Reverie:
        # <start_datetime> is the datetime instance for the start datetime of
        # the Reverie instance. Once it is set, this is not really meant to
        # change. It takes a string date in the following example form:
        # "June 25, 2022"
        # e.g., ...strptime(June 25, 2022, "%B %d, %Y")
        self.start_time = datetime.datetime.strptime(
            f"{reverie_meta['start_date']}, 00:00:00", "%B %d, %Y, %H:%M:%S"
        )
        # <curr_time> is the datetime instance that indicates the game's current
        # time. This gets incremented by <sec_per_step> amount everytime the world
        # progresses (that is, everytime curr_env_file is recieved).
        self.curr_time = datetime.datetime.strptime(
            reverie_meta["curr_time"], "%B %d, %Y, %H:%M:%S"
        )
        # <sec_per_step> denotes the number of seconds in game time that each
        # step moves foward.
        self.sec_per_step = reverie_meta["sec_per_step"]  # 不能大于最大计划周期！！！
        self.sec_per_step = 60  # lg#x6#报错
        self.sec_per_step = 600  # lg#x10#？？？
        self.sec_per_step = 3600  # lg#x6
        # self.sec_per_step = 86400#lg#x24
        # self.sec_per_step = 172800#lg#x2

        # <maze> is the main Maze instance. Note that we pass in the maze_name
        # (e.g., "double_studio") to instantiate Maze.
        # e.g., Maze("double_studio")
        self.is_offline_mode = reverie_meta["sim_mode"] == "offline"
        if self.is_offline_mode:
            self.maze = OfflineMaze(reverie_meta["maze_name"])
        else:
            self.maze = OnlineMaze(reverie_meta["maze_name"])

        # <step> denotes the number of steps that our game has taken. A step here
        # literally translates to the number of moves our personas made in terms
        # of the number of tiles.
        self.step = reverie_meta["step"]

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
        if self.is_offline_mode:
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

        # Loading in all personas. Either from the simulation config or from files.
        # For each persona in the PersonaConfig:
        # 1. If it is a newly created persona, create the folder and files for it.
        # 2. If it is an existing persona, we should update the persona information accordingly.
        for name, persona in sim_config.persona_configs.items():
            bootstrap_persona(f"{self.storage_home}/{name}", persona)

        init_env_file = f"{sim_folder}/environment/{str(self.step)}.json"
        init_env = json.load(open(init_env_file))
        for persona_name in reverie_meta["persona_names"]:
            persona_folder = f"{sim_folder}/personas/{persona_name}"
            if self.is_offline_mode:
                p_x = init_env[persona_name]["x"]
                p_y = init_env[persona_name]["y"]
                curr_persona = GaPersona(persona_name, persona_folder)

                self.personas[persona_name] = curr_persona
                self.personas_tile[persona_name] = (p_x, p_y)
                self.maze.tiles[p_y][p_x]["events"].add(
                    curr_persona.scratch.get_curr_event_and_desc()
                )
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
        with open(f"{temp_storage_path}/curr_sim_code.json", "w") as outfile:
            outfile.write(json.dumps(curr_sim_code, indent=2))

        curr_step = dict()
        curr_step["step"] = self.step
        with open(f"{temp_storage_path}/curr_step.json", "w") as outfile:
            outfile.write(json.dumps(curr_step, indent=2))

        self.tag = False  # case
        self.maze.planning_cycle = 1  # extend planning cycle
        self.maze.last_planning_day = self.curr_time + datetime.timedelta(
            days=-1
        )  # extend planning cycle
        self.maze.need_stagely_planning = True  # extend planning cycle

        # Load all online events
        self.is_running = True
        if self.sim_mode == "online":
            for event in sim_config.public_events:
                self.load_online_event(
                    event_desc=event["description"],
                    policy=event["policy"],
                    websearch=event["websearch"],
                    access_list=event["access_list"],
                )
        self.is_running = False

    # def is_running(self):
    # return self.is_running

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
        sim_folder = f"{storage_path}/{self.sim_code}"

        # Save Reverie meta information.
        reverie_meta = dict()
        reverie_meta["template_sim_code"] = self.template_sim_code
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
                        print(dash, tree)
                    return

                for key, val in tree.items():
                    if key:
                        print(dash, key)
                    _print_tree(val, depth + 1)

            _print_tree(tree, 0)

        # <curr_vision> is the vision radius of the test agent. Recommend 8 as
        # our default.
        curr_vision = 8
        # <s_mem> is our test spatial memory.
        s_mem = dict()

        # The main while loop for the test agent.
        while True:
            try:
                curr_dict = {}
                tester_file = temp_storage_path + "/path_tester_env.json"
                if check_if_file_exists(tester_file):
                    with open(tester_file) as json_file:
                        curr_dict = json.load(json_file)
                        os.remove(tester_file)

                    # Current camera location
                    curr_sts = self.maze.sq_tile_size
                    curr_camera = (
                        int(math.ceil(curr_dict["x"] / curr_sts)),
                        int(math.ceil(curr_dict["y"] / curr_sts)) + 1,
                    )
                    curr_tile_det = self.maze.access_tile(curr_camera)

                    # Initiating the s_mem
                    world = curr_tile_det["world"]
                    if curr_tile_det["world"] not in s_mem:
                        s_mem[world] = dict()

                    # Iterating throughn the nearby tiles.
                    nearby_tiles = self.maze.get_nearby_tiles(curr_camera, curr_vision)
                    for i in nearby_tiles:
                        i_det = self.maze.access_tile(i)
                        if (
                            curr_tile_det["sector"] == i_det["sector"]
                            and curr_tile_det["arena"] == i_det["arena"]
                        ):
                            if i_det["sector"] != "":
                                if i_det["sector"] not in s_mem[world]:
                                    s_mem[world][i_det["sector"]] = dict()
                            if i_det["arena"] != "":
                                if i_det["arena"] not in s_mem[world][i_det["sector"]]:
                                    s_mem[world][i_det["sector"]][i_det["arena"]] = list()
                            if i_det["game_object"] != "":
                                if (
                                    i_det["game_object"]
                                    not in s_mem[world][i_det["sector"]][i_det["arena"]]
                                ):
                                    s_mem[world][i_det["sector"]][i_det["arena"]] += [
                                        i_det["game_object"]
                                    ]

                # Incrementally outputting the s_mem and saving the json file.
                print("= " * 15)
                out_file = temp_storage_path + "/path_tester_out.json"
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
        sim_folder = f"{storage_path}/{self.sim_code}"
        self.is_running = True

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
        while True:
            # Done with this iteration if <int_counter> reaches 0.
            if int_counter == 0:
                break

            if self.is_offline_mode:
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
                            new_tile = (new_env[persona_name]["x"], new_env[persona_name]["y"])

                            # We actually move the persona on the backend tile map here.
                            self.personas_tile[persona_name] = new_tile
                            self.maze.remove_subject_events_from_tile(persona.name, curr_tile)
                            self.maze.add_event_from_tile(
                                persona.scratch.get_curr_event_and_desc(), new_tile
                            )

                            # Now, the persona will travel to get to their destination. *Once*
                            # the persona gets there, we activate the object action.
                            if not persona.scratch.planned_path:
                                # We add that new object action event to the backend tile map.
                                # At its creation, it is stored in the persona's backend.
                                game_obj_cleanup[persona.scratch.get_curr_obj_event_and_desc()] = (
                                    new_tile
                                )
                                self.maze.add_event_from_tile(
                                    persona.scratch.get_curr_obj_event_and_desc(), new_tile
                                )
                                # We also need to remove the temporary blank action for the
                                # object that is currently taking the action.
                                blank = (
                                    persona.scratch.get_curr_obj_event_and_desc()[0],
                                    None,
                                    None,
                                    None,
                                )
                                self.maze.remove_event_from_tile(blank, new_tile)

                        # Then we need to actually have each of the personas perceive and
                        # move. The movement for each of the personas comes in the form of
                        # x y coordinates where the persona will move towards. e.g., (50, 34)
                        # This is where the core brains of the personas are invoked.
                        movements = {"persona": dict(), "meta": dict()}
                        for persona_name, persona in self.personas.items():
                            # <next_tile> is a x,y coordinate. e.g., (58, 9)
                            # <pronunciatio> is an emoji. e.g., "\ud83d\udca4"
                            # <description> is a string description of the movement. e.g.,
                            #   writing her next novel (editing her novel)
                            #   @ double studio:double studio:common room:sofa
                            # next_tile, pronunciatio, description = persona.move(
                            next_tile, pronunciatio, description = persona.single_workflow(
                                self.maze,
                                self.personas,
                                self.personas_tile[persona_name],
                                self.curr_time,
                            )
                            movements["persona"][persona_name] = {}
                            movements["persona"][persona_name]["movement"] = next_tile
                            movements["persona"][persona_name]["pronunciatio"] = pronunciatio
                            movements["persona"][persona_name]["description"] = description
                            movements["persona"][persona_name]["chat"] = persona.scratch.chat

                        # Include the meta information about the current stage in the
                        # movements dictionary.
                        movements["meta"]["curr_time"] = self.curr_time.strftime(
                            "%B %d, %Y, %H:%M:%S"
                        )

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

            else:  # online
                for persona_name, persona in self.personas.items():
                    # for node in self.maze.get_memories():
                    #   if node.name == persona_name:
                    #     node.new_or_old = False
                    print(
                        "\n\n\n★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ "
                        + persona_name
                        + " 第"
                        + str(n)
                        + "轮"
                        + " ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★"
                    )
                    persona.single_workflow(self.maze, self.curr_time)

                n += 1
                self.step += 1
                self.curr_time += datetime.timedelta(seconds=self.sec_per_step)
                print("❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ next step ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤")
                int_counter -= 1

            # Sleep so we don't burn our machines.
            time.sleep(self.server_sleep)

    def load_online_event(self, event_desc="", policy="", websearch="", access_list=[]):
        s, p, o = generate_action_event_triple_new(event_desc)
        # TODO 只用spo来完整表示一个事件是远远不够的
        description = event_desc
        event_id = len(self.maze.events)
        L.debug(f"Adding event: {event_desc}, {policy} {websearch} {access_list}")

        memory_node = MemoryNode("public", s, p, o, description, True)
        self.maze.add_event(event_id, access_list)
        self.maze.add_memory_to_event(event_id, memory_node)

        if policy:
            self.maze.add_events_policy(event_id, policy)
        if websearch:
            self.maze.add_events_websearch(event_id, websearch)

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
        print("Note: The agents in this simulation package are computational")
        print("constructs powered by generative agents architecture and LLM. We")
        print("clarify that these agents lack human-like agency, consciousness,")
        print("and independent decision-making.\n---")

        # <sim_folder> points to the current simulation folder.
        sim_folder = f"{storage_path}/{self.sim_code}"

        while True:
            # sim_command = input("Enter option: ")
            print("Enter option: ")
            self.is_running = False
            sim_command = command_queue.get()
            self.is_running = True
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

                elif sim_command[:3].lower() == "run":  # base_the_ville_n25
                    # Runs the number of steps specified in the prompt.
                    # Example: run 1000
                    int_count = int(sim_command.split()[-1])
                    rs.start_server(int_count)

                elif "print persona schedule" in sim_command[:22].lower():
                    # Print the decomposed schedule of the persona specified in the
                    # prompt.
                    # Example: print persona schedule Isabella Rodriguez
                    ret_str += self.personas[
                        " ".join(sim_command.split()[-2:])
                    ].scratch.get_str_daily_schedule_summary()

                elif "print all persona schedule" in sim_command[:26].lower():
                    # Print the decomposed schedule of all personas in the world.
                    # Example: print all persona schedule
                    for persona_name, persona in self.personas.items():
                        ret_str += f"{persona_name}\n"
                        ret_str += f"{persona.scratch.get_str_daily_schedule_summary()}\n"
                        ret_str += f"---\n"

                elif "print hourly org persona schedule" in sim_command.lower():
                    # Print the hourly schedule of the persona specified in the prompt.
                    # This one shows the original, non-decomposed version of the
                    # schedule.
                    # Ex: print persona schedule Isabella Rodriguez
                    ret_str += self.personas[
                        " ".join(sim_command.split()[-2:])
                    ].scratch.get_str_daily_schedule_hourly_org_summary()

                elif "print persona current tile" in sim_command[:26].lower():
                    # Print the x y tile coordinate of the persona specified in the
                    # prompt.
                    # Ex: print persona current tile Isabella Rodriguez
                    persona = self.personas[" ".join(sim_command.split()[-2:])]
                    ret_str += str(persona.scratch.curr_tile)
                    ret_str += "\n" + repr(
                        self.maze.access_tile(persona.scratch.curr_tile)["sector"]
                    )

                elif "print persona chatting with buffer" in sim_command.lower():
                    # Print the chatting with buffer of the persona specified in the
                    # prompt.
                    # Ex: print persona chatting with buffer Isabella Rodriguez
                    curr_persona = self.personas[" ".join(sim_command.split()[-2:])]
                    for p_n, count in curr_persona.scratch.chatting_with_buffer.items():
                        ret_str += f"{p_n}: {count}"

                elif "print persona associative memory (event)" in sim_command.lower():
                    # Print the associative memory (event) of the persona specified in
                    # the prompt
                    # Ex: print persona associative memory (event) Isabella Rodriguez
                    ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
                    ret_str += self.personas[
                        " ".join(sim_command.split()[-2:])
                    ].a_mem.get_str_seq_events()

                elif "print persona associative memory (thought)" in sim_command.lower():
                    # Print the associative memory (thought) of the persona specified in
                    # the prompt
                    # Ex: print persona associative memory (thought) Isabella Rodriguez
                    ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
                    ret_str += self.personas[
                        " ".join(sim_command.split()[-2:])
                    ].a_mem.get_str_seq_thoughts()

                elif "print persona associative memory (chat)" in sim_command.lower():
                    # Print the associative memory (chat) of the persona specified in
                    # the prompt
                    # Ex: print persona associative memory (chat) Isabella Rodriguez
                    ret_str += f'{self.personas[" ".join(sim_command.split()[-2:])]}\n'
                    ret_str += self.personas[
                        " ".join(sim_command.split()[-2:])
                    ].a_mem.get_str_seq_chats()

                elif "print persona spatial memory" in sim_command.lower():
                    # Print the spatial memory of the persona specified in the prompt
                    # Ex: print persona spatial memory Isabella Rodriguez
                    self.personas[" ".join(sim_command.split()[-2:])].s_mem.print_tree()

                elif "print current time" in sim_command[:18].lower():
                    # Print the current time of the world.
                    # Ex: print current time
                    ret_str += f'{self.curr_time.strftime("%B %d, %Y, %H:%M:%S")}\n'
                    ret_str += f"steps: {self.step}"

                elif "print tile event" in sim_command[:16].lower():
                    # Print the tile events in the tile specified in the prompt
                    # Ex: print tile event 50, 30
                    cooordinate = [int(i.strip()) for i in sim_command[16:].split(",")]
                    for i in self.maze.access_tile(cooordinate)["events"]:
                        ret_str += f"{i}\n"

                elif "print tile details" in sim_command.lower():
                    # Print the tile details of the tile specified in the prompt
                    # Ex: print tile event 50, 30
                    cooordinate = [int(i.strip()) for i in sim_command[18:].split(",")]
                    for key, val in self.maze.access_tile(cooordinate).items():
                        ret_str += f"{key}: {val}\n"
                elif "print llm stats" in sim_command.lower():
                    # Print the LLM stats
                    L.print_stats()

                elif "call -- analysis" in sim_command.lower():
                    # Starts a stateless chat session with the agent. It does not save
                    # anything to the agent's memory.
                    # Ex: call -- analysis Isabella Rodriguez
                    persona_name = sim_command[len("call -- analysis") :].strip()
                    # Do you support Isabella Rodriguez as mayor?
                    # self.personas[persona_name].open_convo_session("analysis")#Do you want to run for mayor in the local election?
                    self.personas[persona_name].open_convo_session(
                        "analysis", self.maze.vbase, command_queue
                    )
                    # Do you want to run for mayor in the local election?

                elif "call -- chat to persona" in sim_command.lower():
                    persona_name = sim_command[len("call -- chat to persona") :].strip()
                    payload = json.loads(command_queue.get())
                    mode = payload.get("mode", "analysis")
                    prev_msgs = payload.get("prev_msgs", [])
                    msg = payload.get("msg", "")

                    retval = self.personas[persona_name].chat_to_persona(
                        mode, self.maze.vbase, prev_msgs, msg
                    )
                    event_trigger(
                        "chat_to_persona", {"mode": mode, "persona": persona_name, "reply": retval}
                    )

                elif "call -- whisper" in sim_command.lower():
                    # Starts a stateless chat session with the agent. It does not save
                    # anything to the agent's memory.
                    # Ex: call -- whisper Isabella Rodriguez
                    persona_name = sim_command[len("call -- whisper") :].strip()
                    self.personas[persona_name].open_convo_session(
                        "whisper", self.maze.vbase, command_queue
                    )

                elif "call -- load history" in sim_command.lower():
                    curr_file = (
                        maze_assets_loc + "/" + sim_command[len("call -- load history") :].strip()
                    )
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

                elif "call -- run spp" in sim_command.lower():  # 插入spp模块。
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
                    if Is_or_Not_Institution == "yes":
                        # self.maze.content = "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."
                        # self.maze.policy = run(args, case=self.maze.content)
                        self.maze.content = "Marine biologists at the Oceanic Institute of Marine Sciences made a groundbreaking discovery this week, uncovering a previously unknown species of bioluminescent jellyfish in the depths of the Pacific Ocean. The newly identified species, named Aurelia noctiluca, emits a mesmerizing blue-green glow, illuminating the dark ocean depths where it resides."
                        self.maze.policy = self.maze.institution.run(case=self.maze.content)
                    else:
                        # run(args, case=None)#
                        self.maze.institution.run(case=None)  #

                elif "init dk" in sim_command.lower():  # 初始化向量数据库。
                    # Initialize domain knowledge
                    content = "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."
                    # self.maze.vbase = Storage(content=content)
                    # FIX: who told you to write like this?
                    self.maze.vbase = Storage(case=content)
                    query = "nuclear"
                    texts = self.maze.vbase.get_texts(query, 2)
                    print("################################")
                    print(texts)
                    print("################################")

                elif "call -- load case" in sim_command.lower():  # 将事件广播给每个智能体。
                    curr_file = (
                        maze_assets_loc + "/" + sim_command[len("call -- load case") :].strip()
                    )
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
                        whispers = [
                            "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."
                        ]  # case
                        whispers = [Your_content]  #
                        whispers = [whisper.strip() for whisper in whispers]
                        for whisper in whispers:
                            clean_whispers += [[agent_name, whisper]]

                    load_history_via_whisper(self.personas, clean_whispers)
                    self.tag = True  # case

                elif "call -- release policy" in sim_command.lower():  # 将政策发布到所有智能体。
                    if self.tag == True:
                        curr_file = (
                            maze_assets_loc
                            + "/"
                            + sim_command[len("call -- release policy") :].strip()
                        )
                        # call -- release policy the_ville/agent_history_init_n3.csv

                        rows = read_file_to_list(curr_file, header=True, strip_trail=True)[1]
                        clean_whispers = []
                        policy = "The policy is as follows: " + self.maze.policy[0]
                        for row in rows:
                            agent_name = row[0].strip()
                            # whispers = row[1].split(";")
                            whispers = [policy]  #
                            whispers = [whisper.strip() for whisper in whispers]
                            for whisper in whispers:
                                clean_whispers += [[agent_name, whisper]]

                        load_history_via_whisper(self.personas, clean_whispers)
                    else:
                        print("<---There is no case.--->")
                elif "call -- zjy test 1" in sim_command.lower():
                    commands = [
                        "call -- load online event",
                        "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters.",
                        "Isabella Rodriguez",
                        "call -- load online event",
                        "Marine biologists at the Oceanic Institute of Marine Sciences made a groundbreaking discovery this week, uncovering a previously unknown species of bioluminescent jellyfish in the depths of the Pacific Ocean. The newly identified species, named Aurelia noctiluca, emits a mesmerizing blue-green glow, illuminating the dark ocean depths where it resides.",
                        "Isabella Rodriguez, Klaus Mueller, Maria Lopez",
                        "run 2",
                    ]
                    for cmd in commands:
                        command_queue.put(cmd)
                elif "call -- load online event" in sim_command.lower():  # 将事件广播给每个智能体。
                    # tyn
                    word_command = command_queue.get().strip()
                    names = command_queue.get().strip()

                    self.load_online_event(
                        event_desc=word_command,
                        access_list=[name.strip() for name in names.split(",")],
                    )

                elif (
                    "call -- with policy load online event" in sim_command.lower()
                ):  # 将事件广播给每个智能体。
                    # tyn
                    # truth = input("Input your content: ")
                    # truth = "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."
                    word_command = command_queue.get().strip()
                    names = command_queue.get().strip()
                    policy = command_queue.get().strip()

                    self.load_online_event(
                        event_desc=word_command,
                        access_list=[name.strip() for name in names.split(",")],
                        policy=policy,
                    )

                elif (
                    "call -- with websearch load online event" in sim_command.lower()
                ):  # 将事件广播给每个智能体。
                    word_command = command_queue.get().strip()
                    names = command_queue.get().strip()
                    websearch = command_queue.get().strip()

                    self.load_online_event(
                        event_desc=word_command,
                        access_list=[name.strip() for name in names.split(",")],
                        websearch=websearch,
                    )
                elif (
                    "call -- with policy and websearch load online event" in sim_command.lower()
                ):  # 将事件广播给每个智能体。
                    word_command = command_queue.get().strip()
                    names = command_queue.get().strip()
                    policy = command_queue.get().strip()
                    websearch = command_queue.get().strip()

                    self.load_online_event(
                        event_desc=word_command,
                        access_list=[name.strip() for name in names.split(",")],
                        policy=policy,
                        websearch=websearch,
                    )

            except Exception as e:
                traceback.print_exc()
                L.error(f"Error during command execution: {e}")
                pass


def start_sim(template_sim_name: str, sim_config: ReverieConfig):
    new_rs = ReverieServer(template_sim_name, sim_config)
    set_rs(new_rs)
    new_rs.start_server(sim_config.initial_rounds)
    new_rs.open_server()


if __name__ == "__main__":

    origin = input("Enter the name of the forked simulation: ").strip()
    target = input("Enter the name of the new simulation: ").strip()

    rs = ReverieServer(origin, target)
    rs.open_server()
