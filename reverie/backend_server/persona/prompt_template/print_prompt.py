"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: print_prompt.py
Description: For printing prompts when the setting for verbose is set to True.
"""

import sys

sys.path.append("../")

import datetime
import json
import random

import numpy
from global_methods import *
from persona.prompt_template.gpt_structure import *
from utils.config import *

##############################################################################
#                    PERSONA Chapter 1: Prompt Structures                    #
##############################################################################


def print_run_prompts(
    prompt_template=None, persona=None, gpt_param=None, prompt_input=None, prompt=None, output=None
):
    # Deprecated. Use logging instead.
    return
    print(f"=== {prompt_template}")
    print("~~~ persona    ---------------------------------------------------")
    print(persona.name, "\n")
    print("~~~ gpt_param ----------------------------------------------------")
    print(gpt_param, "\n")
    print("~~~ prompt_input    ----------------------------------------------")
    print(prompt_input, "\n")
    print("~~~ prompt    ----------------------------------------------------")
    print(prompt, "\n")
    print("~~~ output    ----------------------------------------------------")
    print(output, "\n")
    print("=== END ==========================================================")
    print("\n\n\n")


# tyn
def print_run_prompts_new(
    prompt_template=None, gpt_param=None, prompt_input=None, prompt=None, output=None
):
    # Deprecated. Use logging instead.
    return
    print(f"=== {prompt_template}")
    print("~~~ gpt_param ----------------------------------------------------")
    print(gpt_param, "\n")
    print("~~~ prompt_input    ----------------------------------------------")
    print(prompt_input, "\n")
    print("~~~ prompt    ----------------------------------------------------")
    print(prompt, "\n")
    print("~~~ output    ----------------------------------------------------")
    print(output, "\n")
    print("=== END ==========================================================")
    print("\n\n\n")
