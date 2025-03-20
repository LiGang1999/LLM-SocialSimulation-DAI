"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: reverie.py
Description: This is the main program for running generative agent simulations
that defines the Reverie class. This class maintains and records all
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

import sys

import datetime
import json
import math
import os
import shutil
import threading
from dataclasses import asdict, dataclass, field, fields, replace
from queue import Queue
from typing import List, Optional, Tuple
import asyncio

from pydantic import BaseModel, Field, parse_obj_as
import traceback


# 然后是其他的导入语句
from maze import *
from persona.persona import *
from utils import *
from utils import config
from utils.config import *


# 获取当前文件所在的目录（backend_server）
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将 backend_server 目录添加到 Python 路径
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)


rs_lock = threading.Lock()


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
    base_url: str = config.openai_api_base
    api_key: str = config.openai_api_key
    model: str = ""
    tempreature: float = 1.0
    max_tokens: int = 512
    top_p: float = 0.7
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = False


class ScratchData(BaseModel):
    # Necessary fields
    name: str
    first_name: str
    last_name: str
    age: int
    lifestyle: str
    daily_plan_req: str
    innate: str
    learned: str
    living_area: str

    # Optional fields with default values
    vision_r: int = 8
    att_bandwidth: int = 8
    retention: int = 8
    curr_time: Optional[str] = None
    curr_tile: Optional[str] = None
    currently: str = ""
    concept_forget: int = 100
    daily_reflection_time: int = 180
    daily_reflection_size: int = 5
    overlap_reflect_th: int = 4
    kw_strg_event_reflect_th: int = 10
    kw_strg_thought_reflect_th: int = 9
    recency_w: int = 1
    relevance_w: int = 1
    importance_w: int = 1
    recency_decay: float = 0.99
    importance_trigger_max: int = 30  # very low poig score to cause reflection every online round!
    importance_trigger_curr: int = 30
    importance_ele_n: int = 0
    thought_count: int = 5
    daily_req: List[str] = Field(default_factory=list)
    f_daily_schedule: List[str] = Field(default_factory=list)
    f_daily_schedule_hourly_org: List[str] = Field(default_factory=list)
    act_address: Optional[str] = None
    act_start_time: Optional[str] = None
    act_duration: Optional[str] = None
    act_description: Optional[str] = None
    act_pronunciatio: Optional[str] = None
    act_event: Tuple[str, Optional[str], Optional[str]] = ("", None, None)
    act_obj_description: Optional[str] = None
    act_obj_pronunciatio: Optional[str] = None
    act_obj_event: Tuple[Optional[str], Optional[str], Optional[str]] = (None, None, None)
    chatting_with: Optional[str] = None
    chat: Optional[List[List[str]]] = None
    chatting_with_buffer: dict = Field(default_factory=dict)
    chatting_end_time: Optional[str] = None
    act_path_set: bool = False
    planned_path: List[str] = Field(default_factory=list)

    class Config:
        extra = "ignore"


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
    persona_configs: dict[str, ScratchData] = field(default_factory=dict)  # persona config
    public_events: List[dict] = field(default_factory=list)  # public events
    direction: str | None = ""  # The instruction of what the agents should do with each other
    initial_rounds: int | None = 0  # The number of initial rounds
    sec_per_step: int | None = 3600
    start_order: str | None = ""


def load_config_from_files(path: str) -> ReverieConfig:
    meta_file_path = f"{path}/reverie/meta.json"
    event_file_path = f"{path}/reverie/events.json"
    personas_folder_path = f"{path}/personas"

    # Load meta.json
    with open(meta_file_path, "r") as meta_file:
        meta_data = json.load(meta_file)

    # Load events.json
    if os.path.exists(event_file_path):
        with open(event_file_path, "r") as event_file:
            events_data = json.load(event_file)
    else:
        events_data = []

    # Initialize ReverieConfig
    cfg = ReverieConfig(
        sim_code=meta_data.get("template_sim_code", ""),
        sim_mode=meta_data.get("sim_mode"),
        start_date=meta_data.get("start_date"),
        curr_time=meta_data.get("curr_time"),
        maze_name=meta_data.get("maze_name"),
        step=meta_data.get("step", 0),
        public_events=events_data,
        direction=meta_data.get("description", ""),
        initial_rounds=0,  # You might want to add this to meta.json if needed
        sec_per_step=meta_data.get("sec_per_step", 3600),
        start_order=meta_data.get("start_order", ""),
    )

    # Load LLMConfig if present in meta_data
    if "llm_config" in meta_data:
        cfg.llm_config = LLMConfig(**meta_data["llm_config"])

    # Load persona configs
    cfg.persona_configs = {}
    for persona_name in meta_data.get("persona_names", []):
        scratch_file_path = f"{personas_folder_path}/{persona_name}/bootstrap_memory/scratch.json"
        with open(scratch_file_path, "r") as scratch_file:
            scratch_data = json.load(scratch_file)

        # Parse the JSON data into a ScratchData object
        persona_config = ScratchData.model_validate_json(json.dumps(scratch_data))
        cfg.persona_configs[persona_name] = persona_config

    return cfg


def bootstrap_persona(path: str, config: ScratchData):
    def update_scratch_json(path: str, config: ScratchData):
        scratch_file_path = os.path.join(path, "bootstrap_memory/scratch.json")
        # Load the existing scratch.json
        with open(scratch_file_path, "r") as f:
            scratch_data = json.load(f)

        # Update all fields from the Person model
        for field, value in config.dict().items():
            if field in scratch_data:
                scratch_data[field] = value

        # Save the updated scratch.json
        with open(scratch_file_path, "w") as f:
            json.dump(scratch_data, f, indent=4)

    # Define the required directory structure
    directories = ["bootstrap_memory"]

    # Define the required files with their default content
    files = {
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
            "importance_trigger_max": 30,
            "importance_trigger_curr": 30,
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


class Reverie:
    def __init__(self, template_sim_code, sim_config: ReverieConfig, reverie_storage_path=""):
        # Check if all required fields in sim_config are populated
        missing_fields = []

        self.is_running = False
        self.command_queue = Queue()  # User command input queue
        self.message_queue = Queue()

        if not reverie_storage_path:
            reverie_storage_path = storage_path
        self.storage_path = reverie_storage_path

        # L.info(f"Initializing Reverie with template {template_sim_code} and config {sim_config}")

        self.sim_config = sim_config

        for field_name, field_value in vars(sim_config).items():
            if field_value is None or (isinstance(field_value, str) and field_value == ""):
                missing_fields.append(field_name)

        if missing_fields:
            L.error(f"Missing required fields in sim_config: {', '.join(missing_fields)}")
            # You can raise an exception here if necessary:
            # raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        self.template_sim_code = template_sim_code
        template_folder = f"{self.storage_path}/{self.template_sim_code}"

        self.sim_code = sim_config.sim_code
        sim_folder = f"{self.storage_path}/{self.sim_code}"

        if check_if_dir_exists(sim_folder):
            if self.sim_code in BASE_TEMPLATES:
                L.error(f"Cannot overwrite base template {self.template_sim_code}. Operation aborted.")
            else:
                L.warning(f"Simulation {sim_folder} exists. It will be overwritten by the new environment.")
                removeanything(sim_folder)

        copyanything(template_folder, sim_folder)

        try:
            self.sim_mode = sim_config.sim_mode

            reverie_meta = {}
            # reverie_meta is loaded from the meta.json file in the simulation folder. This is only for backward compatibility

            with open(f"{sim_folder}/reverie/meta.json", "r") as infile:
                reverie_meta = json.load(infile)
            reverie_meta["curr_time"] = sim_config.curr_time
            reverie_meta["step"] = sim_config.step
            reverie_meta["persona_names"] = [persona.name for persona in sim_config.persona_configs.values()]
            reverie_meta["maze_name"] = sim_config.maze_name
            reverie_meta["sim_mode"] = sim_config.sim_mode
            reverie_meta["start_date"] = sim_config.start_date
            reverie_meta["llm_config"] = asdict(sim_config.llm_config)

            # This one should be called sim_code, but call it template_sim_code to maintain backward compatability
            reverie_meta["template_sim_code"] = sim_config.sim_code
            self.storage_home = f"{self.storage_path}/{self.sim_code}"

            # check fields for reverie_meta

            if "sim_mode" not in reverie_meta:
                reverie_meta["sim_mode"] = "offline"

            with open(f"{sim_folder}/reverie/meta.json", "w") as outfile:
                outfile.write(json.dumps(reverie_meta, indent=2))

            # SAVING EVENTS INTO STORAGE
            events = sim_config.public_events
            with open(f"{sim_folder}/reverie/events.json", "w") as outfile:
                outfile.write(json.dumps(events, indent=2))

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
            self.curr_time = datetime.datetime.strptime(reverie_meta["curr_time"], "%B %d, %Y, %H:%M:%S")
            # <sec_per_step> denotes the number of seconds in game time that each
            # step moves foward.
            self.sec_per_step = reverie_meta["sec_per_step"]  # 不能大于最大计划周期！！！

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
            if not self.is_offline_mode:
                self.workflow_config = {
                    "plan": {
                        "task": "Decide whether the agent should vote on a policy proposal.",
                        "output_format": {
                            "reasoning": "Step-by-step reasoning...",
                            "decision": "The decision made.",
                        },
                    },
                    "execute": {
                        "task": "Execute the agent's plan.",
                        "output_format": {
                            "reasoning": "Step-by-step reasoning...",
                            "execution": "The action to take.",
                        },
                    },
                }
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
            # For each persona in the ScratchData:
            # 1. If it is a newly created persona, create the folder and files for it.
            # 2. If it is an existing persona, we should update the persona information accordingly.
            for name, persona in sim_config.persona_configs.items():
                bootstrap_persona(f"{self.storage_home}/personas/{name}", persona)

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
                    self.maze.tiles[p_y][p_x]["events"].add(curr_persona.scratch.get_curr_event_and_desc())
                else:
                    curr_persona = DaiPersona(persona_name, persona_folder)
                    self.personas[persona_name] = curr_persona

            self.personas_positions = {}
            if self.is_offline_mode:
                for persona_name in self.personas:
                    initial_tile = self.personas_tile[persona_name]
                    self.personas_positions[persona_name] = {
                        "x": initial_tile[0],
                        "y": initial_tile[1],
                        "pronunciatio": "",  # Initialize if needed
                        "description": "",  # Initialize if needed
                    }

            # REVERIE SETTINGS PARAMETERS:
            # <server_sleep> denotes the amount of time that our while loop rests each
            # cycle; this is to not kill our machine.

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
            self.maze.last_planning_day = self.curr_time + datetime.timedelta(days=-1)  # extend planning cycle
            self.maze.need_stagely_planning = True  # extend planning cycle

            self.command_queue.put(f"{sim_config.start_order} {sim_config.initial_rounds}")

            self.interested = False  # Whether current run is interested. If calls to large language model is generated in current run ,then current run is 'interested'.
        except Exception as e:
            L.error(f"Error during reverie initialization: {e}")
            if self.sim_code not in BASE_TEMPLATES:
                removeanything(f"{self.storage_path}/{self.sim_code}")
            raise e

    def handle_command(self, payload):
        self.command_queue.put(payload)

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
        sim_folder = f"{self.storage_path}/{self.sim_code}"

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
                        if curr_tile_det["sector"] == i_det["sector"] and curr_tile_det["arena"] == i_det["arena"]:
                            if i_det["sector"] != "":
                                if i_det["sector"] not in s_mem[world]:
                                    s_mem[world][i_det["sector"]] = dict()
                            if i_det["arena"] != "":
                                if i_det["arena"] not in s_mem[world][i_det["sector"]]:
                                    s_mem[world][i_det["sector"]][i_det["arena"]] = list()
                            if i_det["game_object"] != "":
                                if i_det["game_object"] not in s_mem[world][i_det["sector"]][i_det["arena"]]:
                                    s_mem[world][i_det["sector"]][i_det["arena"]] += [i_det["game_object"]]

                # Incrementally outputting the s_mem and saving the json file.
                print("= " * 15)
                out_file = temp_storage_path + "/path_tester_out.json"
                with open(out_file, "w") as outfile:
                    outfile.write(json.dumps(s_mem, indent=2))
                print_tree(s_mem)

            except:
                pass

    def start_server(self, int_counter, agents=None, do_skip=False):
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
        sim_folder = f"{self.storage_path}/{self.sim_code}"

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
            self.interested = False
            # Done with this iteration if <int_counter> reaches 0.
            if int_counter == 0:
                break

            if self.is_offline_mode:
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
                    new_tile = (
                        self.personas_positions[persona_name]["x"],
                        self.personas_positions[persona_name]["y"],
                    )

                    # We actually move the persona on the backend tile map here.
                    self.personas_tile[persona_name] = new_tile
                    self.maze.remove_subject_events_from_tile(persona.name, curr_tile)
                    self.maze.add_event_from_tile(persona.scratch.get_curr_event_and_desc(), new_tile)

                    # Now, the persona will travel to get to their destination. *Once*
                    # the persona gets there, we activate the object action.
                    if not persona.scratch.planned_path:
                        # We add that new object action event to the backend tile map.
                        # At its creation, it is stored in the persona's backend.
                        game_obj_cleanup[persona.scratch.get_curr_obj_event_and_desc()] = new_tile
                        self.maze.add_event_from_tile(persona.scratch.get_curr_obj_event_and_desc(), new_tile)
                        # We also need to remove the temporary blank action for the
                        # object that is currently taking the action.
                        blank = (persona.scratch.get_curr_obj_event_and_desc()[0], None, None, None)
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
                        self.maze, self.personas, self.personas_tile[persona_name], self.curr_time
                    )
                    print(self.curr_time, next_tile, pronunciatio, description)
                    # move the persona position by one tile
                    self.personas_tile[persona_name] = next_tile
                    self.personas_positions[persona_name] = {
                        "x": next_tile[0],
                        "y": next_tile[1],
                        "pronunciatio": pronunciatio,
                        "description": description,
                    }
                    movements["persona"][persona_name] = {}
                    movements["persona"][persona_name]["movement"] = next_tile
                    movements["persona"][persona_name]["pronunciatio"] = pronunciatio
                    movements["persona"][persona_name]["description"] = description
                    movements["persona"][persona_name]["chat"] = persona.scratch.chat

                # Include the meta information about the current stage in the
                # movements dictionary.
                movements["meta"]["curr_time"] = self.curr_time.strftime("%B %d, %Y, %H:%M:%S")

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

                # Write positions to positions.json
                positions_file = f"{self.storage_home}/positions.json"
                with open(positions_file, "w") as f:
                    json.dump(self.personas_positions, f, indent=2)

                # After this cycle, the world takes one step forward, and the
                # current time moves by <sec_per_step> amount.
                self.step += 1
                self.curr_time += datetime.timedelta(seconds=self.sec_per_step)
                if (not do_skip) or self.interested:
                    int_counter -= 1

            else:  # online mode
                # If participating_agents is not provided, default to all personas.
                if agents is None:
                    agents = self.personas

                # set plan
                for persona_name, persona in agents.items():
                    persona.set_workflow_stage_config(self.workflow_config)

                # Iterate over the participating agents
                for persona_name, persona in agents.items():
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
                if (not do_skip) or self.interested:
                    int_counter -= 1

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

    def custom_run(self, sim_command):
        # Parses the command to extract the number of steps and the included/excluded agents.
        # Example: custom-run 1 lisa candy -> only 'lisa' and 'candy' participate in 1 step.
        # Example: custom-run 7 no candy -> everyone except 'candy' participates in 7 steps.
        # Example: custom-run 1 -> all agents participate in 1 step.

        # Split the command into parts
        parts = sim_command.split()
        print("Parts of the command:", parts)

        # Parse the number of steps
        int_count = int(parts[1])

        # Determine participating agents
        if len(parts) == 2:  # No specific agents mentioned, include all agents
            participating_agents = self.personas
        elif parts[2].lower() == "no":  # Exclusion case
            excluded_agents = [agent.lower() for agent in parts[3:]]  # Excluded agents
            participating_agents = {
                persona_name: persona
                for persona_name, persona in self.personas.items()
                if persona_name.lower() not in excluded_agents
            }
        else:  # Inclusion case
            included_agents = [agent.lower() for agent in parts[2:]]  # Included agents
            participating_agents = {
                persona_name: persona
                for persona_name, persona in self.personas.items()
                if persona_name.lower() in included_agents
            }

        # Execute the simulation with the filtered agents
        self.start_server(int_count, participating_agents)

    def open_server(self, reverie_instance):
        """
        Open up an interactive terminal prompt that lets you run the simulation
        step by step and probe agent state.

        INPUT
          None
        OUTPUT
          None
        """
        print("Note: The agents in this simulation package are computational")
        print("constructs powered by generative agents architecture and LLM. We")
        print("clarify that these agents lack human-like agency, consciousness,")
        print("and independent decision-making.\n---")

        # <sim_folder> points to the current simulation folder.
        sim_folder = f"{self.storage_path}/{self.sim_code}"

        # set instance to thread local storage
        thread_local.reverie_instance = reverie_instance
        thread_local.reverie_local = self
        # Load all online events
        self.is_running = True
        if self.sim_mode == "online":
            for event in self.sim_config.public_events:
                self.load_online_event(
                    event_desc=event["description"],
                    policy=event["policy"],
                    websearch=event["websearch"],
                    access_list=event["access_list"],
                )
        self.is_running = False

        while True:
            # sim_command = input("Enter option: ")
            print("Enter option: ")
            self.is_running = False
            sim_command = self.command_queue.get()
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

                elif "custom-run legislative_council" in sim_command.lower():
                    int_count = int(sim_command.split()[-1])
                    self.workflow_config = {
                        "plan": {
                            "task": "分析并决定在讨论推动创新科技产业发展的政策框架时需要考量的关键方面。",
                            "output_format": {
                                "reasoning": "首先，我会考虑……（详细说明推理过程）。其次，我会……。此外，我会……。公众和同行的意见也很重要……。最后，我会回顾……。注意逐步推理需要考虑的因素，例如政策支持的全面性与可行性、财政投入的效率与透明度、区域合作的深度与广度、科技产业发展的长期可持续性、政策实施的公平性等。",
                                "decision": "需要关注的关键方面列表，例如方面1、方面2、方面3、方面4等。",
                            },
                        },
                        "execute": {
                            "task": "明确关于推动创新科技产业发展的政策框架的立场。",
                            "output_format": {
                                "reasoning": "首先，我会分析……（详细说明推理过程）。其次，我会……。此外，我会……。最后，我会回顾……。注意逐步推理需要考虑的因素。",
                                "execution": "支持/反对",
                            },
                        },
                    }

                    commands = "custom-run " + str(int_count)

                    self.custom_run(commands)

                elif "custom-run legislative_council_life" in sim_command.lower():
                    int_count = int(sim_command.split()[-1])
                    self.workflow_config = {
                        "plan": {
                            "task": "分析并决定在讨论维持生命治疗预作决定条例草案时需要考量的关键方面。",
                            "output_format": {
                                "reasoning": "首先，我会考虑……（详细说明推理过程）。其次，我会……。此外，我会……。公众和同行的意见也很重要……。最后，我会回顾……。注意逐步推理需要考虑的因素，例如条文是否明确、政策目标的达成可能性、法律保障的可操作性、电子化的实现风险与益处、公众教育的充分性等。",
                                "decision": "需要关注的关键方面列表，例如方面1、方面2、方面3、方面4等。",
                            },
                        },
                        "execute": {
                            "task": "针对维持生命治疗预作决定条例草案提出意见和问题，第一人称对话口吻，简体，每一个问题内的字数要多（充分描述问题），分点明确。",
                            "output_format": {
                                "reasoning": "首先，我会考虑……（详细说明推理过程）。其次，我会……。此外，我会……。最后，我会回顾……。注意逐步推理需要考虑的因素。",
                                "execution": "说出具体的修改建议或意见，例如问题1的详细内容和对为什么提这个问题的解释、问题2的详细内容和对为什么提这个问题的解释等。",
                            },
                        },
                    }

                    commands = "custom-run " + str(int_count)

                    self.custom_run(commands)

                elif "custom-run shbz" in sim_command.lower():
                    int_count = int(sim_command.split()[-1])

                    self.workflow_config = {
                        "plan": {
                            "task": "基于你的背景(年龄、职业、性格、生活现状、生活经历等)分析你对西湖益联保的认知和态度。请考虑：1)你的医疗保障需求 2)你的收入和支付能力 3)你对西湖益联保的了解程度 4)你的健康状况和就医经历 5)你对医疗费用的承受能力",
                            "output_format": {
                                "reasoning": "从以下几个方面逐步分析：1. 个人基本情况(年龄、职业、收入、家庭状况等) 2. 医疗保险参保情况(基本医保、商业保险等) 3. 就医和医疗支出经历 4. 对西湖益联保的认知和态度 5. 参保决策的影响因素",
                                "decision": "总结对西湖益联保的整体态度和参保意愿",
                            },
                        },
                        "execute": {
                            "task": "请以问卷形式回答以下问题(注意要符合你的身份背景和语气)：\n"
                            # + "第一部分：西湖益联保参保情况\n"
                            # + "19. 您是否参加了西湖益联保？\n"
                            # + "20. 您参保后是否获得过理赔？如果是，请回答：\n"
                            # + "    (1) 理赔情况您是否满意？如不满意，原因是什么？\n"
                            # + "    (2) 获得的赔付数额是多少元？占总体医疗费用的比例是多少？基本医疗报销支付金额是多少元？经过各类保险报销后个人自付费用是多少元？\n\n"
                            # + "第二部分：认知与了解\n"
                            # + "21. 您对西湖益联保的了解程度是？(非常了解/了解/一般/不太了解/不了解)\n"
                            # + "22. 您了解西湖益联保的途径是？(可多选：政府部门宣传/就职企业推广/社区宣传/保险公司推广/网络信息/家人或朋友推荐/其他)\n"
                            # + "23. 对于西湖益联保您会重点关注哪方面的信息？(可多选：参保条件/保费/运行模式/报销额度/免赔责任/保障范围/免赔额度/免赔疾病范围)\n"
                            # + "24. 对于西湖益联保的保费，您能接受的范围是？(<50元/年/50~100元/年/101~150元/年/151~200元/年/>200元/年)\n\n"
                            + "第一部分：参保意愿\n"
                            + "25. 您为自己购买西湖益联保的意愿是？(非常愿意/愿意/一般/不愿意/非常不愿意)\n"
                            + "26. 您为父母购买西湖益联保的意愿是？(非常愿意/愿意/一般/不愿意/非常不愿意)\n"
                            + "27. 您为子女购买西湖益联保的意愿是？(非常愿意/愿意/一般/不愿意/非常不愿意)\n",
                            # + "28. 您愿意为自己和家人购买西湖益联保的原因是？(可多选：保费便宜/认为基本医疗保险可能不够/报销额度大/保障覆盖范围广/政府背书/有身边人推荐/身边有人因参加益联保化解了高额医疗费用风险)\n\n"
                            # + "第四部分：后续意向\n"
                            # + "29. 您是否会继续参加西湖益联保？(肯定会/可能会/不确定/可能不会/肯定不会)\n"
                            # + "30. 您是否会向身边人推荐参加西湖益联保？(是/否)\n"
                            # + "31. 您不愿意参加西湖益联保的原因是？(可多选：基本医疗保险已经足够/已参加了其他地区的普惠型商业补充医疗保险/对西湖益联保不够信任/已购入其他类型的商业医疗保险/西湖益联保的保费较贵/西湖益联保的理赔项目用不到/参保流程繁琐/其他原因)\n"
                            # + "32. 您对西湖益联保还有什么看法和建议？",
                            "output_format": {
                                "reasoning": "基于计划阶段的分析，结合个人背景和经历，详细回答每个问题",
                                "execution": "用第一人称口吻，按照问卷的部分依次作答。回答要真实自然，符合角色身份特征，并体现个人的真实想法和具体经历。对于选择题要明确选择选项，对于开放性问题要详细说明原因。",
                            },
                        },
                    }

                    commands = "custom-run " + str(int_count)

                    self.custom_run(commands)

                elif "custom-run base_the_ville_isabella_maria_klaus_online" in sim_command.lower():
                    int_count = int(sim_command.split()[-1])
                    self.workflow_config = {
                        "plan": {
                            "task": "分析并决定在讨论该新闻时需要考量的关键方面。",
                            "output_format": {
                                "reasoning": "首先，我会考虑……（详细说明推理过程）。其次，我会……。此外，我会……。公众和同行的意见也很重要……。最后，我会回顾……。注意逐步推理需要考虑的因素，例如条文是否明确、政策目标的达成可能性、法律保障的可操作性、电子化的实现风险与益处、公众教育的充分性等。",
                                "decision": "需要关注的关键方面列表，例如方面1、方面2、方面3、方面4等。",
                            },
                        },
                        "execute": {
                            "task": "针对该新闻你将发表什么言论，第一人称对话口吻，简体。",
                            "output_format": {
                                "reasoning": "首先，我会考虑……（详细说明推理过程）。其次，我会……。此外，我会……。最后，我会回顾……。注意逐步推理需要考虑的因素。",
                                "execution": "说出具体的修改建议或意见，例如问题1的详细内容和对为什么提这个问题的解释、问题2的详细内容和对为什么提这个问题的解释等。",
                            },
                        },
                    }

                    commands = "custom-run " + str(int_count)

                    self.custom_run(commands)

                elif "custom-run dragon_tv_demo" in sim_command.lower():
                    int_count = int(sim_command.split()[-1])
                    self.workflow_config = {
                        "plan": {
                            "task": "基于你的背景(年龄、职业、性格、生活现状、生活经历等)分析你对讨论的事件的态度和认知。请考虑:1)你对这个事件的看法2)你的工作/学习是否需要用到AI 3)你是否有使用AI的经验 4)你对新技术的接受程度 5)你的生活方式是否适合AI城市",
                            "output_format": {
                                "reasoning": "从个人背景、AI接触经验、生活需求等方面逐步分析对所讨论的事件的看法，AI城市与传统城市两种环境。AI城市全面整合了先进的人工智能技术，在交通、城市建筑设施、教育、医疗等方面都深度融入了人工智能技术，清洁能源与核能为主要能源供给方式，城市自动化程度高。传统城市仅有少量的工智能技术，实际应用很少。在交通、城市建筑设施、教育、医疗等方面都以人工和机械为主，化石能源与少量清洁能源为主要能源供给方式，城市自动化程度低。",
                                "decision": "发表对正在讨论的事件的看法，描述个人使用AI的经历和体验",
                            },
                        },
                        "execute": {
                            "task": "从自身的角度，用符合你的口吻详细说明你对这个事件、以及其中AI和传统的操作模式的看法(200字以上)，",
                            "output_format": {
                                "reasoning": "基于计划阶段的分析,发表对事件的看法",
                                "execution": "用符合你的语气发表你对正在讨论的事件的看法",
                            },
                        },
                    }

                    commands = "custom-run " + str(int_count)

                    self.custom_run(commands)

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
                    self.start_server(int_count)

                elif sim_command[:10].lower() == "custom-run":
                    self.custom_run(sim_command)

                elif sim_command[:4].lower() == "skip":  # base_the_ville_n25
                    # Runs the number of steps specified in the prompt.
                    # Example: run 1000
                    int_count = int(sim_command.split()[-1])
                    self.start_server(int_count, None, True)

                elif "print persona scratch" in sim_command[:21].lower():
                    importance_trigger_curr = self.personas[
                        " ".join(sim_command.split()[-2:])
                    ].scratch.get_str_summary()
                    ret_str = f"importance_trigger_curr: {importance_trigger_curr}"

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
                    ret_str += "\n" + repr(self.maze.access_tile(persona.scratch.curr_tile)["sector"])

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
                    ret_str += f"{self.personas[' '.join(sim_command.split()[-2:])]}\n"
                    ret_str += self.personas[" ".join(sim_command.split()[-2:])].a_mem.get_str_seq_events()

                elif "print persona associative memory (thought)" in sim_command.lower():
                    # Print the associative memory (thought) of the persona specified in
                    # the prompt
                    # Ex: print persona associative memory (thought) Isabella Rodriguez
                    ret_str += f"{self.personas[' '.join(sim_command.split()[-2:])]}\n"
                    thoughts = self.personas[" ".join(sim_command.split()[-2:])].a_mem.get_thoughts()
                    for count, event in enumerate(thoughts):
                        ret_str += f"Thought {count}: {event.spo_summary()} -- {event.description}\n"

                elif "print persona associative memory (chat)" in sim_command.lower():
                    # Print the associative memory (chat) of the persona specified in
                    # the prompt
                    # Ex: print persona associative memory (chat) Isabella Rodriguez
                    ret_str += f"{self.personas[' '.join(sim_command.split()[-2:])]}\n"
                    ret_str += self.personas[" ".join(sim_command.split()[-2:])].a_mem.get_str_seq_chats()

                elif "print persona spatial memory" in sim_command.lower():
                    # Print the spatial memory of the persona specified in the prompt
                    # Ex: print persona spatial memory Isabella Rodriguez
                    self.personas[" ".join(sim_command.split()[-2:])].s_mem.print_tree()

                elif "print current time" in sim_command[:18].lower():
                    # Print the current time of the world.
                    # Ex: print current time
                    ret_str += f"{self.curr_time.strftime('%B %d, %Y, %H:%M:%S')}\n"
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
                # elif "call -- analysis" in sim_command.lower():
                #     # Starts a stateless chat session with the agent. It does not save
                #     # anything to the agent's memory.
                #     # Ex: call -- analysis Isabella Rodriguez
                #     persona_name = sim_command[len("call -- analysis") :].strip()
                #     # Do you support Isabella Rodriguez as mayor?
                #     # self.personas[persona_name].open_convo_session("interview")#Do you want to run for mayor in the local election?
                #     vbase = getattr(self.maze, "vbase", None)
                #     response = self.personas[persona_name].open_convo_session(
                #         "interview", vbase, self.command_queue
                #     )

                #     print(f"完整回答:\n{response}")
                #     # Do you want to run for mayor in the local election?
                elif "call -- survey" in sim_command.lower():
                    # 在这里对每个persona 逐个采访
                    print("\n输入问卷文件：")
                    filename = self.command_queue.get()
                    filename = f"{self.storage_path}/{self.sim_code}/{filename}"
                    with open(filename, "r") as f:
                        questions = json.load(f)
                    responses = {}

                    # Create async task wrapper
                    async def _run_concurrent_surveys():
                        # Create survey tasks for all personas
                        tasks = [
                            asyncio.create_task(self.personas[name].run_survey(questions)) for name in self.personas
                        ]
                        # Run concurrently and collect results
                        results = await asyncio.gather(*tasks)
                        # Match results with names
                        return {name: result for name, result in zip(self.personas.keys(), results)}

                    # Run the async surveys
                    responses = asyncio.run(_run_concurrent_surveys())

                    # Print and save results
                    for name, response in responses.items():
                        print(f"\n=== {name} 的回答 ===")
                        print(response)
                        print("==========")

                    with open("survey_log.txt", "w", encoding="utf-8") as f:
                        json.dump(responses, f, ensure_ascii=False, indent=2)

                elif "call -- analysis" in sim_command.lower():
                    persona_name = sim_command[len("call -- analysis") :].strip()
                    vbase = getattr(self.maze, "vbase", None)

                    # 创建一个变量来存储对话内容
                    conversation_history = []

                    try:
                        while True:
                            print("\n请输入您的问题(输入 end_convo 结束对话):")
                            question = self.command_queue.get()

                            if question.lower() == "end_convo":
                                break

                            response = self.personas[persona_name].chat_to_persona(
                                "interview", vbase, conversation_history, question
                            )

                            print(f"\n=== {persona_name}的回答 ===")
                            print(response)
                            print("===================")

                            conversation_history.append(("interviewer", question))
                            conversation_history.append((persona_name, response))

                            # 保存到文件
                            with open("interview_log.txt", "a", encoding="utf-8") as f:
                                f.write(f"\nQ: {question}\n")
                                f.write(f"A: {response}\n")
                                f.write("-------------------\n")

                    except Exception as e:
                        print(f"对话过程中出现错误: {str(e)}")
                        traceback.print_exc()

                elif "call -- chat to persona" in sim_command.lower():
                    persona_name = sim_command[len("call -- chat to persona") :].strip()
                    payload = json.loads(self.command_queue.get())
                    mode = payload.get("mode", "interview")
                    prev_msgs = payload.get("prev_msgs", [])
                    msg = payload.get("msg", "")

                    retval = self.personas[persona_name].chat_to_persona(
                        mode, None if self.sim_mode == "online" else self.maze.vbase, prev_msgs, msg
                    )
                    event_trigger("chat_to_persona", {"mode": mode, "persona": persona_name, "reply": retval})

                elif "call -- whisper" in sim_command.lower():
                    # Starts a stateless chat session with the agent. It does not save
                    # anything to the agent's memory.
                    # Ex: call -- whisper Isabella Rodriguez
                    persona_name = sim_command[len("call -- whisper") :].strip()
                    self.personas[persona_name].open_convo_session("whisper", self.maze.vbase, self.command_queue)

                elif "call -- load history" in sim_command.lower():
                    curr_file = maze_assets_loc + "/" + sim_command[len("call -- load history") :].strip()
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
                    #     args['gpt_config']['model'] = model_name

                    # # overwrite temperature and top_p
                    # args['gpt_config']['temperature'] = args['temperature']
                    # args['gpt_config']['top_p'] = args['top_p']
                    # print("run args:", args)
                    # Is_or_Not_Institution = input("Is_or_Not_Institution, Enter Input (yes or no): ")
                    print("Is_or_Not_Institution, Enter Input (yes or no): ")
                    Is_or_Not_Institution = self.command_queue.get()
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
                    curr_file = maze_assets_loc + "/" + sim_command[len("call -- load case") :].strip()
                    # call -- load case the_ville/agent_history_init_n3.csv

                    rows = read_file_to_list(curr_file, header=True, strip_trail=True)[1]
                    clean_whispers = []
                    # Your_content = input("Input your content: ")
                    print("Input your content: ")
                    Your_content = self.command_queue.get()
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
                        curr_file = maze_assets_loc + "/" + sim_command[len("call -- release policy") :].strip()
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

                elif "call --  test 1" in sim_command.lower():
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
                        self.command_queue.put(cmd)

                elif "call -- load online event" in sim_command.lower():  # 将事件广播给每个智能体。
                    #
                    word_command = self.command_queue.get().strip()
                    names = self.command_queue.get().strip()

                    self.load_online_event(
                        event_desc=word_command,
                        access_list=[name.strip() for name in names.split(",")],
                    )

                elif "call -- with policy load online event" in sim_command.lower():  # 将事件广播给每个智能体。
                    #
                    # truth = input("Input your content: ")
                    # truth = "Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters."
                    word_command = self.command_queue.get().strip()
                    names = self.command_queue.get().strip()
                    policy = self.command_queue.get().strip()

                    self.load_online_event(
                        event_desc=word_command,
                        access_list=[name.strip() for name in names.split(",")],
                        policy=policy,
                    )

                elif "call -- with websearch load online event" in sim_command.lower():  # 将事件广播给每个智能体。
                    word_command = self.command_queue.get().strip()
                    names = self.command_queue.get().strip()
                    websearch = self.command_queue.get().strip()

                    self.load_online_event(
                        event_desc=word_command,
                        access_list=[name.strip() for name in names.split(",")],
                        websearch=websearch,
                    )
                elif (
                    "call -- with policy and websearch load online event" in sim_command.lower()
                ):  # 将事件广播给每个智能体。
                    word_command = self.command_queue.get().strip()
                    names = self.command_queue.get().strip()
                    policy = self.command_queue.get().strip()
                    websearch = self.command_queue.get().strip()

                    self.load_online_event(
                        event_desc=word_command,
                        access_list=[name.strip() for name in names.split(",")],
                        policy=policy,
                        websearch=websearch,
                    )
                elif "call -- new load online event" in sim_command.lower():
                    word_command = self.command_queue.get().strip()
                    json_data = json.loads(word_command)
                    self.load_online_event(
                        event_desc=json_data.get("event_desc", ""),
                        access_list=json_data.get("access_list", []),
                        policy=json_data.get("policy", ""),
                        websearch=json_data.get("websearch", ""),
                    )

                L.info(f"Command result: {ret_str}")

            except Exception as e:
                traceback.print_exc()
                L.error(f"Error during command execution: {e}")
                pass


def start_sim(template_sim_name: str, sim_config: ReverieConfig):
    new_rs = Reverie(template_sim_name, sim_config)
    # set_rs(new_rs)
    # new_rs.start_server(sim_config.initial_rounds)
    new_rs.command_queue.put(f"run {sim_config.initial_rounds}")
    return new_rs
    # new_rs.open_server()
    # return new_rs


if __name__ == "__main__":
    import threading

    template_sim_code = input("Enter the name of the forked simulation: ").strip()
    sim_code = input("Enter the name of the new simulation: ").strip()

    # Create a default ReverieConfig
    cfg = load_config_from_files(f"{storage_path}/{template_sim_code}")
    cfg.sim_code = sim_code
    cfg.llm_config = LLMConfig(base_url=openai_api_base, api_key=openai_api_key, model=override_gpt_param["model"])

    rs = Reverie(template_sim_code, cfg)

    # Define a function to read from stdin and put commands into the command_queue
    def stdin_reader():
        while True:
            try:
                command = input()
                rs.handle_command(command)
            except EOFError:
                break

    # Start the stdin reader thread
    input_thread = threading.Thread(target=stdin_reader)
    input_thread.daemon = True
    input_thread.start()

    # Start processing commands
    rs.open_server(None)
