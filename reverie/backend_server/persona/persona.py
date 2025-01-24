"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: persona.py
Description: Defines the Persona class that powers the agents in Reverie. 

Note (May 1, 2023) -- this is effectively GenerativeAgent class. Persona was
the term we used internally back in 2022, taking from our Social Simulacra 
paper.
"""

import datetime
import math
import random
import sys

sys.path.append("../")

from persona.cognitive_modules.converse import *
from persona.cognitive_modules.execute import *
from persona.cognitive_modules.perceive import *
from persona.cognitive_modules.plan import *
from persona.cognitive_modules.reflect import *
from persona.cognitive_modules.retrieve import *
from persona.memory_structures.associative_memory import *
from persona.memory_structures.scratch import *
from persona.memory_structures.spatial_memory import *
from persona.workflow import *
from utils import *
from utils.logs import L
from persona.cognitive_modules.converse import open_convo_session


class Persona:
    def __init__(self):
        self.workflow = None

    def single_workflow(self):
        pass


class GaPersona(Persona):
    def __init__(self, name, folder_mem_saved=False):
        super().__init__()
        # PERSONA BASE STATE
        # <name> is the full name of the persona. This is a unique identifier for
        # the persona within Reverie.
        self.name = name

        self.workflow = GaWorkFlow()  #

        # PERSONA MEMORY
        # If there is already memory in folder_mem_saved, we load that. Otherwise,
        # we create new memory instances.
        # <s_mem> is the persona's spatial memory.
        f_s_mem_saved = f"{folder_mem_saved}/bootstrap_memory/spatial_memory.json"
        self.s_mem = MemoryTree(f_s_mem_saved)

        # <s_mem> is the persona's associative memory.
        f_a_mem_saved = f"{folder_mem_saved}/bootstrap_memory"
        self.a_mem = AssociativeMemory(f_a_mem_saved)
        # <scratch> is the persona's scratch (short term memory) space.
        scratch_saved = f"{folder_mem_saved}/bootstrap_memory/scratch.json"
        self.scratch = Scratch(scratch_saved)

    def single_workflow(self, maze, personas, curr_tile, curr_time):
        return self.workflow.work(self, maze, personas, curr_tile, curr_time)

    def save(self, save_folder):
        """
        Save persona's current state (i.e., memory).

        INPUT:
          save_folder: The folder where we wil be saving our persona's state.
        OUTPUT:
          None
        """
        # Spatial memory contains a tree in a json format.
        # e.g., {"double studio":
        #         {"double studio":
        #           {"bedroom 2":
        #             ["painting", "easel", "closet", "bed"]}}}
        f_s_mem = f"{save_folder}/spatial_memory.json"
        self.s_mem.save(f_s_mem)

        # Associative memory contains a csv with the following rows:
        # [event.type, event.created, event.expiration, s, p, o]
        # e.g., event,2022-10-23 00:00:00,,Isabella Rodriguez,is,idle
        self.a_mem.save(save_folder)

        # Scratch contains non-permanent data associated with the persona. When
        # it is saved, it takes a json form. When we load it, we move the values
        # to Python variables.
        f_scratch = f"{save_folder}/scratch.json"
        self.scratch.save(f_scratch)

    def open_convo_session(self, convo_mode, vbase, input_queue):
        open_convo_session(self, convo_mode, vbase, input_queue)

    def chat_to_persona(self, mode, vbase, prev_msgs, msg):
        return chat_to_persona(self, mode, vbase, prev_msgs, msg)


class DaiPersona(Persona):
    def __init__(self, name, folder_mem_saved=False):
        super().__init__()
        # PERSONA BASE STATE
        # <name> is the full name of the persona. This is a unique identifier for
        # the persona within Reverie.
        self.name = name

        self.workflow = DaiWorkFlow()  #
        self.read_positions = {}  # 存储每个智能体的读取位置

        # PERSONA MEMORY
        # If there is already memory in folder_mem_saved, we load that. Otherwise,
        # we create new memory instances.

        # <s_mem> is the persona's associative memory.
        f_a_mem_saved = f"{folder_mem_saved}/bootstrap_memory"
        self.a_mem = AssociativeMemory(f_a_mem_saved)
        # <scratch> is the persona's scratch (short term memory) space.
        scratch_saved = f"{folder_mem_saved}/bootstrap_memory/scratch.json"
        self.scratch = Scratch(scratch_saved)
        self.workflow_config = {
            "plan": {
                "task": "Decide whether the agent should vote on a policy proposal.",
                "output_format": {
                    "reasoning": "Step-by-step reasoning...",
                    "decision": "Yes or No",
                },
            },
            "execute": {
                "task": "Decide whether the agent should vote on a policy proposal.",
                "output_format": {
                    "reasoning": "Step-by-step reasoning...",
                    "decision": "Yes or No",
                },
            },
        }

    def get_workflow_stage_config(self):
        return self.workflow_config

    # 设置新的工作流配置
    def set_workflow_stage_config(self, workflow_config):
        self.workflow_config = workflow_config

    def single_workflow(self, maze, curr_time):
        self.workflow.work(self, maze, curr_time)

    def save(self, save_folder):
        """
        Save persona's current state (i.e., memory).

        INPUT:
          save_folder: The folder where we wil be saving our persona's state.
        OUTPUT:
          None
        """
        # Associative memory contains a csv with the following rows:
        # [event.type, event.created, event.expiration, s, p, o]
        # e.g., event,2022-10-23 00:00:00,,Isabella Rodriguez,is,idle
        self.a_mem.save(save_folder)

        # Scratch contains non-permanent data associated with the persona. When
        # it is saved, it takes a json form. When we load it, we move the values
        # to Python variables.
        f_scratch = f"{save_folder}/scratch.json"
        self.scratch.save(f_scratch)

    def chat_to_persona(self, mode, vbase, prev_msgs, msg):
        return chat_to_persona(self, mode, vbase, prev_msgs, msg)
    
    async def run_survey(self, questions):
        return await survey_persona(self, questions)

    def open_convo_session(self, convo_mode, vbase, input_queue):
        """
        打开一个会话session

        Args:
            convo_mode: 会话模式(interview/whisper等)
            vbase: 向量数据库
            input_queue: 命令队列
        """
        # from reverie.backend_server.persona.cognitive_modules.converse import open_convo_session

        from persona.cognitive_modules.converse import open_convo_session

        open_convo_session(self, convo_mode, vbase, input_queue)
