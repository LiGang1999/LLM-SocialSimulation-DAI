"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: run_gpt_prompt.py
Description: Defines all run gpt prompt functions. These functions directly
interface with the safe_generate_response function.
"""

import ast
import datetime
import re
import sys

from persona.prompt_template.gpt_structure import *
from persona.prompt_template.print_prompt import *
from utils import *
from utils.llm_function import llm_function


def get_random_alphanumeric(i=6, j=6):
    """
    Returns a random alpha numeric strength that has the length of somewhere
    between i and j.

    INPUT:
      i: min_range for the length
      j: max_range for the length
    OUTPUT:
      an alpha numeric str with the length of somewhere between i and j.
    """
    k = random.randint(i, j)
    x = "".join(random.choices(string.ascii_letters + string.digits, k=k))
    return x


##############################################################################
# CHAPTER 1: Run GPT Prompt
##############################################################################
def run_gpt_prompt_wake_up_hour(persona, test_input=None, verbose=False):
    """
    Given the persona, returns an integer that indicates the hour when the
    persona wakes up.

    INPUT:
      persona: The Persona class instance
    OUTPUT:
      integer for the wake up hour.
    """
    persona_iss = persona.scratch.get_str_iss()
    lifestyle = persona.scratch.get_str_lifestyle()
    firstname = persona.scratch.get_str_firstname()

    @llm_function(is_chat=True, prompt_file="wake_up_hour.md")
    def get_wake_up_hour(persona_iss, lifestyle, firstname):
        # LLM function wrapper
        return {"time": "06:30"}

    try:
        time_str = get_wake_up_hour(persona_iss, lifestyle, firstname)["time"]
        hour, _ = time_str.split(":")
        return [int(hour)]
    except:
        return [6]


def run_gpt_prompt_wake_up_hour_old(persona, test_input=None, verbose=False):
    """
    Given the persona, returns an integer that indicates the hour when the
    persona wakes up.

    INPUT:
      persona: The Persona class instance
    OUTPUT:
      integer for the wake up hour.
    """

    def create_prompt_input(persona, test_input=None):
        if test_input:
            return test_input
        prompt_input = [
            persona.scratch.get_str_iss(),
            persona.scratch.get_str_lifestyle(),
            persona.scratch.get_str_firstname(),
        ]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = int(gpt_response.strip().lower().split("am")[0])
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt="")
        except:
            return False
        return True

    def get_fail_safe():
        fs = 8
        return fs

    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 5,
        "temperature": 0.8,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": ["\n"],
    }
    prompt_template = "persona/prompt_template/v2/wake_up_hour_v1.txt"
    prompt_input = create_prompt_input(persona, test_input)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()

    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_daily_plan(persona, wake_up_hour, test_input=None, verbose=False):
    """
    Basically the long term planning that spans a day. Returns a list of actions
    that the persona will take today. Usually comes in the following form:
    'wake up and complete the morning routine at 6:00 am',
    'eat breakfast at 7:00 am',..
    Note that the actions come without a period.

    INPUT:
      persona: The Persona class instance
    OUTPUT:
      a list of daily actions in broad strokes.
    """

    def create_prompt_input(persona, wake_up_hour, test_input=None):
        if test_input:
            return test_input
        prompt_input = []
        prompt_input += [persona.scratch.get_str_iss()]
        prompt_input += [persona.scratch.get_str_lifestyle()]
        prompt_input += [persona.scratch.get_str_curr_date_str()]
        prompt_input += [persona.scratch.get_str_firstname()]
        prompt_input += [f"{str(wake_up_hour)}:00 am"]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = []
        _cr = gpt_response.split(")")
        for i in _cr:
            if i[-1].isdigit():
                i = i[:-1].strip()
                if i[-1] == "." or i[-1] == ",":
                    cr += [i[:-1].strip()]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt="")
        except:
            return False
        return True

    def get_fail_safe():
        fs = [
            "wake up and complete the morning routine at 6:00 am",
            "eat breakfast at 7:00 am",
            "read a book from 8:00 am to 12:00 pm",
            "have lunch at 12:00 pm",
            "take a nap from 1:00 pm to 4:00 pm",
            "relax and watch TV from 7:00 pm to 8:00 pm",
            "go to bed at 11:00 pm",
        ]
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 500,
        "temperature": 1,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/daily_planning_v6.txt"
    prompt_input = create_prompt_input(persona, wake_up_hour, test_input)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()

    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )
    output = [f"wake up and complete the morning routine at {wake_up_hour}:00 am"] + output

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_daily_plan_directed_by_LTP(
    persona,
    wake_up_hour,
    extraprompt="exercise for two hours today.",
    test_input=None,
    verbose=False,
):
    """
    Basically the long term planning that spans a day. Returns a list of actions
    that the persona will take today. Usually comes in the following form:
    'wake up and complete the morning routine at 6:00 am',
    'eat breakfast at 7:00 am',..
    Note that the actions come without a period.

    INPUT:
      persona: The Persona class instance
    OUTPUT:
      a list of daily actions in broad strokes.
    """

    def create_prompt_input(persona, wake_up_hour, extraprompt=extraprompt, test_input=None):
        if test_input:
            return test_input
        prompt_input = []
        prompt_input += [persona.scratch.get_str_iss()]
        prompt_input += [persona.scratch.get_str_lifestyle()]
        prompt_input += [extraprompt]
        prompt_input += [persona.scratch.get_str_curr_date_str()]
        prompt_input += [persona.scratch.get_str_firstname()]
        prompt_input += [f"{str(wake_up_hour)}:00 am"]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = []
        _cr = gpt_response.split(")")
        for i in _cr:
            if i[-1].isdigit():
                i = i[:-1].strip()
                if i[-1] == "." or i[-1] == ",":
                    cr += [i[:-1].strip()]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt="")
        except:
            return False
        return True

    def get_fail_safe():
        fs = [
            "wake up and complete the morning routine at 6:00 am",
            "eat breakfast at 7:00 am",
            "read a book from 8:00 am to 12:00 pm",
            "have lunch at 12:00 pm",
            "take a nap from 1:00 pm to 4:00 pm",
            "relax and watch TV from 7:00 pm to 8:00 pm",
            "go to bed at 11:00 pm",
        ]
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 500,
        "temperature": 1,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    # prompt_template = "persona/prompt_template/v2/daily_planning_v6.txt"
    prompt_template = "persona/prompt_template/v2/daily_planning_v6_new.txt"
    prompt_input = create_prompt_input(persona, wake_up_hour, test_input)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()

    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )
    output = [f"wake up and complete the morning routine at {wake_up_hour}:00 am"] + output

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_stagely_plan(persona, maze):  # extend planning cycle
    def create_prompt_input(persona, maze):
        prompt_input = []
        prompt_input += [persona.scratch.get_str_iss()]
        prompt_input += [persona.scratch.get_str_firstname()]
        prompt_input += [(maze.last_planning_day + datetime.timedelta(days=1)).strftime("%A %B %d")]
        prompt_input += [
            (maze.last_planning_day + datetime.timedelta(days=maze.planning_cycle)).strftime(
                "%A %B %d"
            )
        ]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = []
        _cr = gpt_response.split(")")
        for i in _cr:
            if i[-1].isdigit():
                i = i[:-1].strip()
                if i[-1] == "." or i[-1] == ",":
                    cr += [i[:-1].strip()]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt="")
        except:
            return False
        return True

    def get_fail_safe():
        fs = [
            "exercise for two hours on the first day",
            "complete graduation thesis during the period",
        ]
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 500,
        "temperature": 1,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/stagely_planning.txt"
    prompt_input = create_prompt_input(persona, maze)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_generate_hourly_schedule(
    persona,
    curr_hour_str,
    p_f_ds_hourly_org,
    hour_str,
    intermission2=None,
    test_input=None,
    verbose=False,
):
    intended_schedule = ""
    for count, i in enumerate(persona.scratch.daily_req):
        intended_schedule += f"{str(count+1)}) {i}, "
    intended_schedule = intended_schedule[:-2]

    prior_schedule = ""
    if p_f_ds_hourly_org:
        prior_schedule = "\n"
        for count, i in enumerate(p_f_ds_hourly_org):
            prior_schedule += f"["
            prior_schedule += f" {persona.scratch.get_str_curr_date_str()} --"
            prior_schedule += f" {hour_str[count]}] Activity:"
            prior_schedule += f" {persona.scratch.get_str_firstname()}"
            prior_schedule += f" is {i}\n"

    @llm_function(
        is_chat=True, prompt_file="generate_hourly_schedule.md", failsafe={"activity": "asleep"}
    )
    def llm_generate_hourly_schedule(
        prior_sched, current_hour, intended_schedule, persona_iss, persona_name
    ):

        # example return value
        return {"activity": "doing something"}

    output = llm_generate_hourly_schedule(
        prior_schedule,
        curr_hour_str,
        intended_schedule,
        persona.scratch.get_str_iss(),
        persona.scratch.get_str_firstname(),
    )
    return [output["activity"]]


def run_gpt_prompt_generate_hourly_schedule_old(
    persona,
    curr_hour_str,
    p_f_ds_hourly_org,
    hour_str,
    intermission2=None,
    test_input=None,
    verbose=False,
):
    def create_prompt_input(
        persona, curr_hour_str, p_f_ds_hourly_org, hour_str, intermission2=None, test_input=None
    ):
        if test_input:
            return test_input
        schedule_format = ""
        for i in hour_str:
            schedule_format += f"[{persona.scratch.get_str_curr_date_str()} -- {i}]"
            schedule_format += f" Activity: [Fill in]\n"
        schedule_format = schedule_format[:-1]

        intermission_str = f"Here the originally intended hourly breakdown of"
        intermission_str += f" {persona.scratch.get_str_firstname()}'s schedule today: "
        for count, i in enumerate(persona.scratch.daily_req):
            intermission_str += f"{str(count+1)}) {i}, "
        intermission_str = intermission_str[:-2]

        prior_schedule = ""
        if p_f_ds_hourly_org:
            prior_schedule = "\n"
            for count, i in enumerate(p_f_ds_hourly_org):
                prior_schedule += f"[(ID:{get_random_alphanumeric()})"
                prior_schedule += f" {persona.scratch.get_str_curr_date_str()} --"
                prior_schedule += f" {hour_str[count]}] Activity:"
                prior_schedule += f" {persona.scratch.get_str_firstname()}"
                prior_schedule += f" is {i}\n"

        prompt_ending = f"[(ID:{get_random_alphanumeric()})"
        prompt_ending += f" {persona.scratch.get_str_curr_date_str()}"
        prompt_ending += f" -- {curr_hour_str}] Activity:"
        prompt_ending += f" {persona.scratch.get_str_firstname()} is"

        if intermission2:
            intermission2 = f"\n{intermission2}"

        prompt_input = []
        prompt_input += [schedule_format]
        prompt_input += [persona.scratch.get_str_iss()]

        prompt_input += [prior_schedule + "\n"]
        prompt_input += [intermission_str]
        if intermission2:
            prompt_input += [intermission2]
        else:
            prompt_input += [""]
        prompt_input += [prompt_ending]

        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = gpt_response.strip()
        if cr[-1] == ".":
            cr = cr[:-1]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt="")
        except:
            return False
        return True

    def get_fail_safe():
        fs = "asleep"
        return fs

    # # ChatGPT Plugin ===========================================================
    # def __chat_func_clean_up(gpt_response, prompt=""): ############
    #   cr = gpt_response.strip()
    #   if cr[-1] == ".":
    #     cr = cr[:-1]
    #   return cr

    # def __chat_func_validate(gpt_response, prompt=""): ############
    #   try: __func_clean_up(gpt_response, prompt="")
    #   except: return False
    #   return True

    # print ("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 10") ########
    # gpt_param = {"engine": "text-davinci-002", "max_tokens": 15,
    #              "temperature": 0, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    # prompt_template = "persona/prompt_template/v3_ChatGPT/generate_hourly_schedule_v2.txt" ########
    # prompt_input = create_prompt_input(persona,
    #                                    curr_hour_str,
    #                                    p_f_ds_hourly_org,
    #                                    hour_str,
    #                                    intermission2,
    #                                    test_input)  ########
    # prompt = generate_prompt(prompt_input, prompt_template)
    # example_output = "studying for her music classes" ########
    # special_instruction = "The output should ONLY include the part of the sentence that completes the last line in the schedule above." ########
    # fail_safe = get_fail_safe() ########
    # output = chat_safe_generate_response(prompt, example_output, special_instruction, 3, fail_safe,
    #                                         __chat_func_validate, __chat_func_clean_up, True)
    # if output != False:
    #   return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # # ChatGPT Plugin ===========================================================

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 100,
        "temperature": 0.5,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": "---",
    }
    prompt_template = "persona/prompt_template/v2/generate_hourly_schedule_v2.txt"
    prompt_input = create_prompt_input(
        persona, curr_hour_str, p_f_ds_hourly_org, hour_str, intermission2, test_input
    )
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()

    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_generate_daily_schedule(
    persona, curr_day_str, p_f_ds_daily_org, maze
):  # extend planning cycle
    def create_prompt_input(persona, curr_day_str, p_f_ds_daily_org, maze):
        schedule_format = ""
        for i in range(maze.planning_cycle):
            schedule_format += (
                f"[{(maze.last_planing_day+datetime.timedelta(days=i+1)).strftime('%A %B %d')}]"
            )
            schedule_format += f" Activity: [Fill in]\n"
        schedule_format = schedule_format[:-1]

        intermission_str = f"Here the originally intended daily breakdown of"
        intermission_str += f" {persona.scratch.get_str_firstname()}'s schedule from {(maze.last_planning_day+datetime.timedelta(days=1)).strftime('%A %B %d')} to {(maze.last_planning_day+datetime.timedelta(days=maze.planning_cycle)).strftime('%A %B %d')}: "
        for count, i in enumerate(persona.scratch.daily_req):
            intermission_str += f"{str(count+1)}) {i}, "
        intermission_str = intermission_str[:-2]

        prior_schedule = ""
        if p_f_ds_daily_org:
            prior_schedule = "\n"
            for count, i in enumerate(p_f_ds_daily_org):
                prior_schedule += f"[(ID:{get_random_alphanumeric()})"
                prior_schedule += f" {(maze.last_planing_day+datetime.timedelta(days=count+1)).strftime('%A %B %d')} --"
                prior_schedule += f" Activity:"
                prior_schedule += f" {persona.scratch.get_str_firstname()}"
                prior_schedule += f" intends to {i}\n"  #

        prompt_ending = f"[(ID:{get_random_alphanumeric()})"
        prompt_ending += f" {curr_day_str}"
        prompt_ending += f" -- Activity:"
        prompt_ending += f" {persona.scratch.get_str_firstname()} intends to"  #

        prompt_input = []
        prompt_input += [schedule_format]
        prompt_input += [persona.scratch.get_str_iss()]

        prompt_input += [prior_schedule + "\n"]
        prompt_input += [intermission_str]
        prompt_input += [prompt_ending]

        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = gpt_response.strip()
        if cr[-1] == ".":
            cr = cr[:-1]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt="")
        except:
            return False
        return True

    def get_fail_safe():
        fs = "asleep"
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 50,
        "temperature": 0.5,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": ["\n"],
    }
    prompt_template = "persona/prompt_template/v2/generate_daily_schedule.txt"
    prompt_input = create_prompt_input(persona, curr_day_str, p_f_ds_daily_org, maze)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_task_decomp(persona, task, duration, test_input=None, verbose=False):
    curr_f_org_index = persona.scratch.get_f_daily_schedule_hourly_org_index()
    all_indices = []
    all_indices += [curr_f_org_index]
    if curr_f_org_index + 1 <= len(persona.scratch.f_daily_schedule_hourly_org):
        all_indices += [curr_f_org_index + 1]
    if curr_f_org_index + 2 <= len(persona.scratch.f_daily_schedule_hourly_org):
        all_indices += [curr_f_org_index + 2]

    curr_time_range = ""

    summ_str = f'Today is {persona.scratch.curr_time.strftime("%B %d, %Y")}. '
    summ_str += f"From "
    for index in all_indices:
        if index < len(persona.scratch.f_daily_schedule_hourly_org):
            start_min = 0
            for i in range(index):
                start_min += persona.scratch.f_daily_schedule_hourly_org[i][1]
            end_min = start_min + persona.scratch.f_daily_schedule_hourly_org[index][1]
            start_time = datetime.datetime.strptime("00:00:00", "%H:%M:%S") + datetime.timedelta(
                minutes=start_min
            )
            end_time = datetime.datetime.strptime("00:00:00", "%H:%M:%S") + datetime.timedelta(
                minutes=end_min
            )
            start_time_str = start_time.strftime("%H:%M%p")
            end_time_str = end_time.strftime("%H:%M%p")
            summ_str += f"{start_time_str} ~ {end_time_str}, {persona.name} is planning on {persona.scratch.f_daily_schedule_hourly_org[index][0]}, "
            if curr_f_org_index + 1 == index:
                curr_time_range = f"{start_time_str} ~ {end_time_str}"
    summ_str = summ_str[:-2] + "."

    @llm_function(is_chat=True, prompt_file="task_decomp.md")
    def llm_task_decomp(
        commonset, surrounding_sched, first_name, curr_action, curr_time_range, cur_action_dur
    ):
        # TODO where to put the examples?
        return [
            {
                "subtask": "reviewing the kindergarten curriculum standards.",
                "duration": 15,
                "remaining": 165,
            },
            {"subtask": "brainstorming ideas for the lesson.", "duration": 30, "remaining": 135},
            {"subtask": "creating the lesson plan.", "duration": 30, "remaining": 105},
            {"subtask": "creating materials for the lesson.", "duration": 30, "remaining": 75},
            {"subtask": "taking a break.", "duration": 15, "remaining": 60},
            {"subtask": "reviewing the lesson plan.", "duration": 30, "remaining": 30},
            {
                "subtask": "making final changes to the lesson plan.",
                "duration": 15,
                "remaining": 15,
            },
            {"subtask": "printing the lesson plan.", "duration": 10, "remaining": 5},
            {"subtask": "putting the lesson plan in her bag.", "duration": 5, "remaining": 0},
        ]

    output = llm_task_decomp(
        persona.scratch.get_str_iss(),
        summ_str,
        persona.scratch.get_str_firstname(),
        task,
        curr_time_range,
        duration,
    )

    output = [(item["subtask"], item["duration"]) for item in output]
    fin_output = []
    time_sum = 0
    for i_task, i_duration in output:
        time_sum += i_duration
        if time_sum <= duration:
            fin_output += [[i_task, i_duration]]
        else:
            break
    ftime_sum = 0
    for fi_task, fi_duration in fin_output:
        ftime_sum += fi_duration

    fin_output[-1][1] += duration - ftime_sum
    output = fin_output

    task_decomp = output
    ret = []
    for decomp_task, duration in task_decomp:
        ret += [[f"{task} ({decomp_task})", duration]]
    return [ret]


def run_gpt_prompt_task_decomp_old(persona, task, duration, test_input=None, verbose=False):
    def create_prompt_input(persona, task, duration, test_input=None):
        """
        Today is Saturday June 25. From 00:00 ~ 06:00am, Maeve is
        planning on sleeping, 06:00 ~ 07:00am, Maeve is
        planning on waking up and doing her morning routinse,
        and from 07:00am ~08:00am, Maeve is planning on having breakfast.
        """

        curr_f_org_index = persona.scratch.get_f_daily_schedule_hourly_org_index()
        all_indices = []
        # if curr_f_org_index > 0:
        #   all_indices += [curr_f_org_index-1]
        all_indices += [curr_f_org_index]
        if curr_f_org_index + 1 <= len(persona.scratch.f_daily_schedule_hourly_org):
            all_indices += [curr_f_org_index + 1]
        if curr_f_org_index + 2 <= len(persona.scratch.f_daily_schedule_hourly_org):
            all_indices += [curr_f_org_index + 2]

        curr_time_range = ""

        print("DEBUG")
        print(persona.scratch.f_daily_schedule_hourly_org)
        print(all_indices)

        summ_str = f'Today is {persona.scratch.curr_time.strftime("%B %d, %Y")}. '
        summ_str += f"From "
        for index in all_indices:
            print("index", index)
            if index < len(persona.scratch.f_daily_schedule_hourly_org):
                start_min = 0
                for i in range(index):
                    start_min += persona.scratch.f_daily_schedule_hourly_org[i][1]
                end_min = start_min + persona.scratch.f_daily_schedule_hourly_org[index][1]
                start_time = datetime.datetime.strptime(
                    "00:00:00", "%H:%M:%S"
                ) + datetime.timedelta(minutes=start_min)
                end_time = datetime.datetime.strptime("00:00:00", "%H:%M:%S") + datetime.timedelta(
                    minutes=end_min
                )
                start_time_str = start_time.strftime("%H:%M%p")
                end_time_str = end_time.strftime("%H:%M%p")
                summ_str += f"{start_time_str} ~ {end_time_str}, {persona.name} is planning on {persona.scratch.f_daily_schedule_hourly_org[index][0]}, "
                if curr_f_org_index + 1 == index:
                    curr_time_range = f"{start_time_str} ~ {end_time_str}"
        summ_str = summ_str[:-2] + "."

        prompt_input = []
        prompt_input += [persona.scratch.get_str_iss()]
        prompt_input += [summ_str]
        # prompt_input += [persona.scratch.get_str_curr_date_str()]
        prompt_input += [persona.scratch.get_str_firstname()]
        prompt_input += [persona.scratch.get_str_firstname()]
        prompt_input += [task]
        prompt_input += [curr_time_range]
        prompt_input += [duration]
        prompt_input += [persona.scratch.get_str_firstname()]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print("TOODOOOOOO")
        print(gpt_response)
        print("-==- -==- -==- ")

        # TODO SOMETHING HERE sometimes fails... See screenshot
        # This function is deprecated. The new one works fine now.
        temp = [i.strip() for i in gpt_response.split("\n")]
        _cr = []
        cr = []
        for count, i in enumerate(temp):
            if count != 0:
                _cr += [" ".join([j.strip() for j in i.split(" ")][3:])]
            else:
                _cr += [i]
        for count, i in enumerate(_cr):
            k = [j.strip() for j in i.split("(duration in minutes:")]
            task = k[0]
            # print("lg")#
            # print(k)#
            # print(task)#
            # duration = int(k[1].split(",")[0].strip())#
            # print(duration)#
            # print("lg")#
            if task == "" or k[0] == k[-1]:  # lg#
                continue  # lg#
            if task[-1] == ".":
                # print("get there!")#
                task = task[:-1]
            print("lg")  #
            print(k[1])  #
            print("lg")  #
            k[1] = k[1].split(")")[0].strip()  # for vicuna-33b-v1.3.
            duration = int(k[1].split(",")[0].strip())
            # duration = int(k[1].split(")")[0].strip())#for vicuna-33b-v1.3.
            cr += [[task, duration]]

        total_expected_min = int(
            prompt.split("(total duration in minutes")[-1].split("):")[0].strip()
        )

        # TODO -- now, you need to make sure that this is the same as the sum of
        #         the current action sequence.
        # Solved by usin the new function.
        curr_min_slot = [["dummy", -1]]  # (task_name, task_index)
        for count, i in enumerate(cr):
            i_task = i[0]
            i_duration = i[1]

            i_duration -= i_duration % 5
            if i_duration > 0:
                for j in range(i_duration):
                    curr_min_slot += [(i_task, count)]
        curr_min_slot = curr_min_slot[1:]

        if len(curr_min_slot) > total_expected_min:
            last_task = curr_min_slot[60]
            for i in range(1, 6):
                curr_min_slot[-1 * i] = last_task
        elif len(curr_min_slot) < total_expected_min:
            last_task = curr_min_slot[-1]
            for i in range(total_expected_min - len(curr_min_slot)):
                curr_min_slot += [last_task]

        cr_ret = [["dummy", -1]]
        for task, task_index in curr_min_slot:
            if task != cr_ret[-1][0]:
                cr_ret += [[task, 1]]
            else:
                cr_ret[-1][1] += 1
        cr = cr_ret[1:]

        return cr

    def __func_validate(gpt_response, prompt=""):
        # TODO -- this sometimes generates error
        try:
            __func_clean_up(gpt_response)
        except:
            pass
            # return False
        return gpt_response

    def get_fail_safe():
        fs = ["asleep"]
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 1000,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/task_decomp_v3.txt"
    prompt_input = create_prompt_input(persona, task, duration)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()

    print("?????")
    print(prompt)
    output = safe_generate_response(
        prompt, gpt_param, 5, get_fail_safe(), __func_validate, __func_clean_up
    )

    # TODO THERE WAS A BUG HERE...
    # This is for preventing overflows...
    """
  File "/Users/joonsungpark/Desktop/Stanford/Projects/
  generative-personas/src_exploration/reverie_simulation/
  brain/get_next_action_v3.py", line 364, in run_gpt_prompt_task_decomp
  fin_output[-1][1] += (duration - ftime_sum)
  IndexError: list index out of range
  """

    print("IMPORTANT VVV DEBUG")

    # print (prompt_input)
    # print (prompt)
    print(output)

    fin_output = []
    time_sum = 0
    for i_task, i_duration in output:
        time_sum += i_duration
        # HM?????????
        # if time_sum < duration:
        if time_sum <= duration:
            fin_output += [[i_task, i_duration]]
        else:
            break
    ftime_sum = 0
    for fi_task, fi_duration in fin_output:
        ftime_sum += fi_duration

    # print ("for debugging... line 365", fin_output)
    fin_output[-1][1] += duration - ftime_sum
    output = fin_output

    task_decomp = output
    ret = []
    for decomp_task, duration in task_decomp:
        ret += [[f"{task} ({decomp_task})", duration]]
    output = ret

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_action_sector(action_description, persona, maze, test_input=None, verbose=False):
    act_world = f"{maze.access_tile(persona.scratch.curr_tile)['world']}"

    x1 = f"{act_world}:{persona.scratch.living_area.split(':')[1]}"
    x2 = f"{act_world}:{maze.access_tile(persona.scratch.curr_tile)['sector']}"

    # MAR 11 TEMP
    accessible_sector_str = persona.s_mem.get_str_accessible_sectors(act_world)
    curr = accessible_sector_str.split(", ")
    fin_accessible_sectors = []

    def house_and_owner(place: str, name: str):
        place = place.lower()
        name = name.lower()
        if "'s house" in place or "'s apartment" in place:
            if name in place:
                return True, True
            return True, False
        return False, False

    for i in curr:
        # TODO this check is incomplete. It should be 's house or 's apartment
        if "'s house" in i.lower() or "'s apartment" in i.lower():
            if persona.scratch.last_name.lower() in i.lower():
                fin_accessible_sectors += [i]
        else:
            fin_accessible_sectors += [i]
    accessible_sector_str = ", ".join(fin_accessible_sectors)
    # END MAR 11 TEMP

    action_description_1 = action_description
    action_description_2 = action_description
    if "(" in action_description:
        action_description_1 = action_description.split("(")[0].strip()
        action_description_2 = action_description.split("(")[-1][:-1]

    @llm_function(is_chat=True, prompt_file="action_location_sector.md")
    def llm_action_location_sector(
        persona_name,
        all_sectors,
        living_sector,
        living_sector_arenas,
        cur_sector,
        cur_sector_arenas,
        cur_action_coarse,
        cur_action_fine,
        daily_plan_req,
    ):
        return {"place": "some place"}

    L.debug(f"all sectors:{accessible_sector_str}")
    output = llm_action_location_sector(
        persona_name=persona.scratch.get_str_name(),
        all_sectors=accessible_sector_str,
        living_sector=persona.scratch.living_area.split(":")[1],
        living_sector_arenas=persona.s_mem.get_str_accessible_sector_arenas(x1),
        cur_sector=f"{maze.access_tile(persona.scratch.curr_tile)['sector']}",
        cur_sector_arenas=persona.s_mem.get_str_accessible_sector_arenas(x2),
        cur_action_coarse=action_description_1,
        cur_action_fine=action_description_2,
        daily_plan_req=persona.scratch.get_str_daily_plan_req(),
    )

    return [output["place"]]


def run_gpt_prompt_action_sector_old(
    action_description, persona, maze, test_input=None, verbose=False
):
    def create_prompt_input(action_description, persona, maze, test_input=None):
        act_world = f"{maze.access_tile(persona.scratch.curr_tile)['world']}"

        prompt_input = []

        prompt_input += [persona.scratch.get_str_name()]
        prompt_input += [persona.scratch.living_area.split(":")[1]]
        x = f"{act_world}:{persona.scratch.living_area.split(':')[1]}"
        prompt_input += [persona.s_mem.get_str_accessible_sector_arenas(x)]

        prompt_input += [persona.scratch.get_str_name()]
        prompt_input += [f"{maze.access_tile(persona.scratch.curr_tile)['sector']}"]
        x = f"{act_world}:{maze.access_tile(persona.scratch.curr_tile)['sector']}"
        prompt_input += [persona.s_mem.get_str_accessible_sector_arenas(x)]

        if persona.scratch.get_str_daily_plan_req() != "":
            prompt_input += [f"\n{persona.scratch.get_str_daily_plan_req()}"]
        else:
            prompt_input += [""]

        # MAR 11 TEMP
        accessible_sector_str = persona.s_mem.get_str_accessible_sectors(act_world)
        curr = accessible_sector_str.split(", ")
        fin_accessible_sectors = []
        for i in curr:
            if "'s house" in i:
                if persona.scratch.last_name in i:
                    fin_accessible_sectors += [i]
            else:
                fin_accessible_sectors += [i]
        accessible_sector_str = ", ".join(fin_accessible_sectors)
        # END MAR 11 TEMP

        prompt_input += [accessible_sector_str]

        action_description_1 = action_description
        action_description_2 = action_description
        if "(" in action_description:
            action_description_1 = action_description.split("(")[0].strip()
            action_description_2 = action_description.split("(")[-1][:-1]
        prompt_input += [persona.scratch.get_str_name()]
        prompt_input += [action_description_1]

        prompt_input += [action_description_2]
        prompt_input += [persona.scratch.get_str_name()]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cleaned_response = gpt_response.split("}")[0]
        return cleaned_response

    def __func_validate(gpt_response, prompt=""):
        if len(gpt_response.strip()) < 1:
            return False
        if "}" not in gpt_response:
            return False
        if "," in gpt_response:
            return False
        return True

    def get_fail_safe():
        fs = "kitchen"
        return fs

    # # ChatGPT Plugin ===========================================================
    # def __chat_func_clean_up(gpt_response, prompt=""): ############
    #   cr = gpt_response.strip()
    #   return cr

    # def __chat_func_validate(gpt_response, prompt=""): ############
    #   try:
    #     gpt_response = __func_clean_up(gpt_response, prompt="")
    #   except:
    #     return False
    #   return True

    # print ("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 20") ########
    # gpt_param = {"engine": "text-davinci-002", "max_tokens": 15,
    #              "temperature": 0, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    # prompt_template = "persona/prompt_template/v3_ChatGPT/action_location_sector_v2.txt" ########
    # prompt_input = create_prompt_input(action_description, persona, maze)  ########
    # prompt = generate_prompt(prompt_input, prompt_template)
    # example_output = "Johnson Park" ########
    # special_instruction = "The value for the output must contain one of the area options above verbatim (including lower/upper case)." ########
    # fail_safe = get_fail_safe() ########
    # output = chat_safe_generate_response(prompt, example_output, special_instruction, 3, fail_safe,
    #                                         __chat_func_validate, __chat_func_clean_up, True)
    # if output != False:
    #   return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # # ChatGPT Plugin ===========================================================

    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v1/action_location_sector_v1.txt"
    prompt_input = create_prompt_input(action_description, persona, maze)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )
    y = f"{maze.access_tile(persona.scratch.curr_tile)['world']}"
    x = [i.strip() for i in persona.s_mem.get_str_accessible_sectors(y).split(",")]
    if output not in x:
        # output = random.choice(x)
        output = persona.scratch.living_area.split(":")[1]

    print("DEBUG", random.choice(x), "------", output)

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_action_arena(
    action_description, persona, maze, act_world, act_sector, test_input=None, verbose=False
):
    # Firstly, the action_sector is generated via prompt. So we do not need the 'current action sector' thing.
    prompt_input = []
    # prompt_input += [persona.scratch.get_str_name()]
    # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["arena"]]
    # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["sector"]]
    x = f"{act_world}:{act_sector}"

    # TODO WHAT THE FUCK IS THIS ?
    # MAR 11 TEMP
    accessible_arena_str = persona.s_mem.get_str_accessible_sector_arenas(x)
    curr = accessible_arena_str.split(", ")
    fin_accessible_arenas = []
    for i in curr:
        if "'s room" in i:
            if persona.scratch.last_name in i:
                fin_accessible_arenas += [i]
        else:
            fin_accessible_arenas += [i]
    accessible_arena_str = ", ".join(fin_accessible_arenas)
    # END MAR 11 TEMP

    action_description_1 = action_description
    action_description_2 = action_description
    if "(" in action_description:
        action_description_1 = action_description.split("(")[0].strip()
        action_description_2 = action_description.split("(")[-1][:-1]

    @llm_function(is_chat=True, prompt_file="action_location_object.md")
    def llm_action_location_object(
        persona_name, curr_area, action_sector, arenas, large_action, small_action
    ):

        return {"place": "kitchen"}

    output = llm_action_location_object(
        persona_name=persona.scratch.get_str_name(),
        curr_area=act_sector,
        arenas=accessible_arena_str,
        action_sector=accessible_arena_str,
        large_action=action_description_1,
        small_action=action_description_2,
    )

    return [output["place"]]


def run_gpt_prompt_action_arena_old(
    action_description, persona, maze, act_world, act_sector, test_input=None, verbose=False
):
    def create_prompt_input(
        action_description, persona, maze, act_world, act_sector, test_input=None
    ):
        prompt_input = []
        # prompt_input += [persona.scratch.get_str_name()]
        # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["arena"]]
        # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["sector"]]
        prompt_input += [persona.scratch.get_str_name()]
        x = f"{act_world}:{act_sector}"
        prompt_input += [act_sector]

        # TODO WHAT THE FUCK IS THIS ?
        # MAR 11 TEMP
        accessible_arena_str = persona.s_mem.get_str_accessible_sector_arenas(x)
        curr = accessible_arena_str.split(", ")
        fin_accessible_arenas = []
        for i in curr:
            if "'s room" in i:
                if persona.scratch.last_name in i:
                    fin_accessible_arenas += [i]
            else:
                fin_accessible_arenas += [i]
        accessible_arena_str = ", ".join(fin_accessible_arenas)
        # END MAR 11 TEMP

        prompt_input += [accessible_arena_str]

        action_description_1 = action_description
        action_description_2 = action_description
        if "(" in action_description:
            action_description_1 = action_description.split("(")[0].strip()
            action_description_2 = action_description.split("(")[-1][:-1]
        prompt_input += [persona.scratch.get_str_name()]
        prompt_input += [action_description_1]

        prompt_input += [action_description_2]
        prompt_input += [persona.scratch.get_str_name()]

        prompt_input += [act_sector]

        prompt_input += [accessible_arena_str]
        # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["arena"]]
        # x = f"{maze.access_tile(persona.scratch.curr_tile)['world']}:{maze.access_tile(persona.scratch.curr_tile)['sector']}:{maze.access_tile(persona.scratch.curr_tile)['arena']}"
        # prompt_input += [persona.s_mem.get_str_accessible_arena_game_objects(x)]

        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cleaned_response = gpt_response.split("}")[0]
        return cleaned_response

    def __func_validate(gpt_response, prompt=""):
        if len(gpt_response.strip()) < 1:
            return False
        if "}" not in gpt_response:
            return False
        if "," in gpt_response:
            return False
        return True

    def get_fail_safe():
        fs = "kitchen"
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v1/action_location_object_vMar11.txt"
    prompt_input = create_prompt_input(action_description, persona, maze, act_world, act_sector)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )
    print(output)
    # y = f"{act_world}:{act_sector}"
    # x = [i.strip() for i in persona.s_mem.get_str_accessible_sector_arenas(y).split(",")]
    # if output not in x:
    #   output = random.choice(x)

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_action_game_object(
    action_description, persona, maze, temp_address, test_input=None, verbose=False
):
    if "(" in action_description:
        action_description = action_description.split("(")[-1][:-1]

    @llm_function(is_chat=True, prompt_file="action_object.md")
    def llm_action_object(action, objects):
        return {"object": "the most relevant object"}

    output = llm_action_object(
        action=action_description,
        objects=persona.s_mem.get_str_accessible_arena_game_objects(temp_address),
    )
    output = output["object"]
    x = [
        i.strip()
        for i in persona.s_mem.get_str_accessible_arena_game_objects(temp_address).split(",")
    ]
    if output not in x:
        output = random.choice(x)
    return [output]


def run_gpt_prompt_action_game_object_old(
    action_description, persona, maze, temp_address, test_input=None, verbose=False
):
    def create_prompt_input(action_description, persona, temp_address, test_input=None):
        prompt_input = []
        if "(" in action_description:
            action_description = action_description.split("(")[-1][:-1]

        prompt_input += [action_description]
        prompt_input += [persona.s_mem.get_str_accessible_arena_game_objects(temp_address)]
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        if len(gpt_response.strip()) < 1:
            return False
        return True

    def __func_clean_up(gpt_response, prompt=""):
        cleaned_response = gpt_response.strip()
        return cleaned_response

    def get_fail_safe():
        fs = "bed"
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v1/action_object_v2.txt"
    prompt_input = create_prompt_input(action_description, persona, temp_address, test_input)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    x = [
        i.strip()
        for i in persona.s_mem.get_str_accessible_arena_game_objects(temp_address).split(",")
    ]
    if output not in x:
        output = random.choice(x)

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_pronunciatio(action_description, persona, verbose=False):
    if "(" in action_description:
        action_description = action_description.split("(")[-1].split(")")[0]

    @llm_function(is_chat=True, prompt_file="generate_pronunciatio.md")
    def llm_generate_pronunciation(action_description):

        return {"emoji": "🛁🧖‍♀️"}

    response = llm_generate_pronunciation(action_description)["emoji"]
    return [response]


def run_gpt_prompt_pronunciatio_old(action_description, persona, verbose=False):
    def create_prompt_input(action_description):
        if "(" in action_description:
            action_description = action_description.split("(")[-1].split(")")[0]
        prompt_input = [action_description]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = gpt_response.strip()
        if len(cr) > 3:
            cr = cr[:3]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt="")
            if len(gpt_response) == 0:
                return False
        except:
            return False
        return True

    def get_fail_safe():
        fs = "😋"
        return fs

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        cr = gpt_response.strip()
        if len(cr) > 3:
            cr = cr[:3]
        return cr

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt="")
            if len(gpt_response) == 0:
                return False
        except:
            return False
        return True
        return True

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 4")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/generate_pronunciatio_v1.txt"  ########
    prompt_input = create_prompt_input(action_description)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "🛁🧖‍♀️"  ########
    special_instruction = "The value for the output must ONLY contain the emojis."  ########
    fail_safe = get_fail_safe()
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    # gpt_param = {"engine": "text-davinci-003", "max_tokens": 15,
    #              "temperature": 0, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": ["\n"]}
    # prompt_template = "persona/prompt_template/v2/generate_pronunciatio_v1.txt"
    # prompt_input = create_prompt_input(action_description)

    # prompt = generate_prompt(prompt_input, prompt_template)

    # fail_safe = get_fail_safe()
    # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
    #                                  __func_validate, __func_clean_up)

    # if debug or verbose:
    #   print_run_prompts(prompt_template, persona, gpt_param,
    #                     prompt_input, prompt, output)

    # return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_event_triple(action_description, persona, verbose=False):
    if "(" in action_description:
        action_description = action_description.split("(")[-1].split(")")[0]

    @llm_function(is_chat=True, prompt_file="generate_event_triple.md")
    def llm_generate_event_triple(persona_name, action):
        return {"subject": "Joon Park", "predicate": "brew", "object": "coffee"}

    output = llm_generate_event_triple(persona.name, action_description)
    return [(output["subject"], output["predicate"], output["object"])]


def run_gpt_prompt_event_triple_old(action_description, persona, verbose=False):
    def create_prompt_input(action_description, persona):
        if "(" in action_description:
            action_description = action_description.split("(")[-1].split(")")[0]
        prompt_input = [persona.name, action_description, persona.name]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = gpt_response.strip()
        cr = [i.strip() for i in cr.split(")")[0].split(",")]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            gpt_response = __func_clean_up(gpt_response, prompt="")
            if len(gpt_response) != 2:
                return False
        except:
            return False
        return True

    def get_fail_safe(persona):
        fs = (persona.name, "is", "idle")
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 30,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": ["\n"],
    }
    prompt_template = "persona/prompt_template/v2/generate_event_triple_v1.txt"
    prompt_input = create_prompt_input(action_description, persona)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe(persona)  ########
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )
    output = (persona.name, output[0], output[1])

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_event_triple_new(action_description, verbose=False):
    @llm_function(is_chat=True, prompt_file="generate_event_triple_new.md")
    def llm_generate_event_triple(action):
        return {"subject": "Joon Park", "predicate": "brew", "object": "coffee"}

    output = llm_generate_event_triple(action_description)
    return [(output["subject"], output["predicate"], output["object"])]


# tyn
def run_gpt_prompt_event_triple_new_old(action_description, verbose=False):
    def __func_clean_up(gpt_response, prompt=""):
        cr = gpt_response.strip()
        cr = [i.strip() for i in cr.split(")")[0].split(",")]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            gpt_response = __func_clean_up(gpt_response, prompt="")
            if len(gpt_response) != 3:
                return False
        except:
            return False
        return True

    def get_fail_safe():
        fs = ("none", "is", "idle")
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 200,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": ["\n"],
    }

    import os

    # 获取当前工作目录
    current_path = os.getcwd()

    # 输出当前工作目录
    print("当前工作目录:", current_path)
    prompt_template = "persona/prompt_template/v2/generate_event_triple_v2.txt"
    prompt_input = action_description
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()  ########
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )
    output = (output[0], output[1], output[2])

    if debug or verbose:
        print_run_prompts_new(prompt_template, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_act_obj_desc(act_game_object, act_desp, persona, verbose=False):
    @llm_function(is_chat=True, prompt_file="generate_obj_event.md")
    def llm_generate_obj_event(obj_name, persona_name, action):

        return {"state": "oven is being heated to cook breakfast"}

    output = llm_generate_obj_event(act_game_object, persona.name, act_desp)["state"]
    return [output]


def run_gpt_prompt_act_obj_desc_old(act_game_object, act_desp, persona, verbose=False):
    def create_prompt_input(act_game_object, act_desp, persona):
        prompt_input = [act_game_object, persona.name, act_desp, act_game_object, act_game_object]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = gpt_response.strip()
        if cr[-1] == ".":
            cr = cr[:-1]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            gpt_response = __func_clean_up(gpt_response, prompt="")
        except:
            return False
        return True

    def get_fail_safe(act_game_object):
        fs = f"{act_game_object} is idle"
        return fs

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        cr = gpt_response.strip()
        if cr[-1] == ".":
            cr = cr[:-1]
        return cr

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            gpt_response = __func_clean_up(gpt_response, prompt="")
        except:
            return False
        return True

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 6")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/generate_obj_event_v1.txt"  ########
    prompt_input = create_prompt_input(act_game_object, act_desp, persona)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "being fixed"  ########
    special_instruction = (
        "The output should ONLY contain the phrase that should go in <fill in>."  ########
    )
    fail_safe = get_fail_safe(act_game_object)  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    # print("-lg-")#
    # print(output)#
    # print("-lg-")#
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    # gpt_param = {"engine": "text-davinci-003", "max_tokens": 30,
    #              "temperature": 0, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": ["\n"]}
    # prompt_template = "persona/prompt_template/v2/generate_obj_event_v1.txt"
    # prompt_input = create_prompt_input(act_game_object, act_desp, persona)
    # prompt = generate_prompt(prompt_input, prompt_template)
    # fail_safe = get_fail_safe(act_game_object)
    # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
    #                                  __func_validate, __func_clean_up)

    # if debug or verbose:
    #   print_run_prompts(prompt_template, persona, gpt_param,
    #                     prompt_input, prompt, output)

    # return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_act_obj_event_triple(act_game_object, act_obj_desc, persona, verbose=False):
    @llm_function(is_chat=True, prompt_file="generate_event_triple.md")
    def llm_generate_event_triple(persona_name, action):
        return {"subject": "Joon Park", "predicate": "brew", "object": "coffee"}

    output = llm_generate_event_triple(act_game_object, act_obj_desc)
    output = (output["subject"], output["predicate"], output["object"])
    return [output]


def run_gpt_prompt_act_obj_event_triple_old(act_game_object, act_obj_desc, persona, verbose=False):
    def create_prompt_input(act_game_object, act_obj_desc):
        prompt_input = [act_game_object, act_obj_desc, act_game_object]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = gpt_response.strip()
        cr = [i.strip() for i in cr.split(")")[0].split(",")]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            gpt_response = __func_clean_up(gpt_response, prompt="")
            if len(gpt_response) != 2:
                return False
        except:
            return False
        return True

    def get_fail_safe(act_game_object):
        fs = (act_game_object, "is", "idle")
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 30,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": ["\n"],
    }
    prompt_template = "persona/prompt_template/v2/generate_event_triple_v1.txt"
    prompt_input = create_prompt_input(act_game_object, act_obj_desc)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe(act_game_object)
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )
    output = (act_game_object, output[0], output[1])

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_new_decomp_schedule(
    persona,
    main_act_dur,
    truncated_act_dur,
    start_time_hour,
    end_time_hour,
    inserted_act,
    inserted_act_dur,
    test_input=None,
    verbose=False,
):
    def create_prompt_input(
        persona,
        main_act_dur,
        truncated_act_dur,
        start_time_hour,
        end_time_hour,
        inserted_act,
        inserted_act_dur,
        test_input=None,
    ):
        persona_name = persona.name
        start_hour_str = start_time_hour.strftime("%H:%M %p")
        end_hour_str = end_time_hour.strftime("%H:%M %p")

        original_plan = ""
        for_time = start_time_hour
        for i in main_act_dur:
            original_plan += (
                f'{for_time.strftime("%H:%M")} ~ {(for_time + datetime.timedelta(minutes=int(i[1]))).strftime("%H:%M")} -- '
                + i[0]
            )
            original_plan += "\n"
            for_time += datetime.timedelta(minutes=int(i[1]))

        new_plan_init = ""
        for_time = start_time_hour
        for count, i in enumerate(truncated_act_dur):
            new_plan_init += (
                f'{for_time.strftime("%H:%M")} ~ {(for_time + datetime.timedelta(minutes=int(i[1]))).strftime("%H:%M")} -- '
                + i[0]
            )
            new_plan_init += "\n"
            if count < len(truncated_act_dur) - 1:
                for_time += datetime.timedelta(minutes=int(i[1]))

        new_plan_init += (for_time + datetime.timedelta(minutes=int(i[1]))).strftime("%H:%M") + " ~"

        prompt_input = [
            persona_name,
            start_hour_str,
            end_hour_str,
            original_plan,
            persona_name,
            inserted_act,
            inserted_act_dur,
            persona_name,
            start_hour_str,
            end_hour_str,
            end_hour_str,
            new_plan_init,
        ]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        new_schedule = prompt + " " + gpt_response.strip()
        new_schedule = new_schedule.split("The revised schedule:")[-1].strip()
        new_schedule = new_schedule.split("\n")

        ret_temp = []
        for i in new_schedule:
            ret_temp += [i.split(" -- ")]

        ret = []
        for time_str, action in ret_temp:
            start_time = time_str.split(" ~ ")[0].strip()
            end_time = time_str.split(" ~ ")[1].strip()
            delta = datetime.datetime.strptime(end_time, "%H:%M") - datetime.datetime.strptime(
                start_time, "%H:%M"
            )
            delta_min = int(delta.total_seconds() / 60)
            if delta_min < 0:
                delta_min = 0
            ret += [[action, delta_min]]

        return ret

    def __func_validate(gpt_response, prompt=""):
        try:
            gpt_response = __func_clean_up(gpt_response, prompt)
            dur_sum = 0
            for act, dur in gpt_response:
                dur_sum += dur
                if str(type(act)) != "<class 'str'>":
                    return False
                if str(type(dur)) != "<class 'int'>":
                    return False
            x = prompt.split("\n")[0].split("originally planned schedule from")[-1].strip()[:-1]
            x = [datetime.datetime.strptime(i.strip(), "%H:%M %p") for i in x.split(" to ")]
            delta_min = int((x[1] - x[0]).total_seconds() / 60)

            if int(dur_sum) != int(delta_min):
                return False

        except:
            return False
        return True

    def get_fail_safe(main_act_dur, truncated_act_dur):
        dur_sum = 0
        for act, dur in main_act_dur:
            dur_sum += dur

        ret = truncated_act_dur[:]
        ret += main_act_dur[len(ret) - 1 :]

        # If there are access, we need to trim...
        ret_dur_sum = 0
        count = 0
        over = None
        for act, dur in ret:
            ret_dur_sum += dur
            if ret_dur_sum == dur_sum:
                break
            if ret_dur_sum > dur_sum:
                over = ret_dur_sum - dur_sum
                break
            count += 1

        if over:
            ret = ret[: count + 1]
            ret[-1][1] -= over

        return ret

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 1000,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/new_decomp_schedule_v1.txt"
    prompt_input = create_prompt_input(
        persona,
        main_act_dur,
        truncated_act_dur,
        start_time_hour,
        end_time_hour,
        inserted_act,
        inserted_act_dur,
        test_input,
    )
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe(main_act_dur, truncated_act_dur)
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    # print ("* * * * output")
    # print (output)
    # print ('* * * * fail_safe')
    # print (fail_safe)

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_decide_to_talk(
    persona, target_persona, retrieved, test_input=None, verbose=False
):
    def create_prompt_input(init_persona, target_persona, retrieved, test_input=None):
        last_chat = init_persona.a_mem.get_last_chat(target_persona.name)
        last_chatted_time = ""
        last_chat_about = ""
        if last_chat:
            last_chatted_time = last_chat.created.strftime("%B %d, %Y, %H:%M:%S")
            last_chat_about = last_chat.description

        context = ""
        for c_node in retrieved["events"]:
            curr_desc = c_node.description.split(" ")
            curr_desc[2:3] = ["was"]
            curr_desc = " ".join(curr_desc)
            context += f"{curr_desc}. "
        context += "\n"
        for c_node in retrieved["thoughts"]:
            context += f"{c_node.description}. "

        curr_time = init_persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S %p")
        init_act_desc = init_persona.scratch.act_description
        if "(" in init_act_desc:
            init_act_desc = init_act_desc.split("(")[-1][:-1]

        if len(init_persona.scratch.planned_path) == 0 and "waiting" not in init_act_desc:
            init_p_desc = f"{init_persona.name} is already {init_act_desc}"
        elif "waiting" in init_act_desc:
            init_p_desc = f"{init_persona.name} is {init_act_desc}"
        else:
            init_p_desc = f"{init_persona.name} is on the way to {init_act_desc}"

        target_act_desc = target_persona.scratch.act_description
        if "(" in target_act_desc:
            target_act_desc = target_act_desc.split("(")[-1][:-1]

        if len(target_persona.scratch.planned_path) == 0 and "waiting" not in init_act_desc:
            target_p_desc = f"{target_persona.name} is already {target_act_desc}"
        elif "waiting" in init_act_desc:
            target_p_desc = f"{init_persona.name} is {init_act_desc}"
        else:
            target_p_desc = f"{target_persona.name} is on the way to {target_act_desc}"

        prompt_input = []
        prompt_input += [context]

        prompt_input += [curr_time]

        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        prompt_input += [last_chatted_time]
        prompt_input += [last_chat_about]

        prompt_input += [init_p_desc]
        prompt_input += [target_p_desc]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if gpt_response.split("Answer in yes or no:")[-1].strip().lower() in ["yes", "no"]:
                return True
            return False
        except:
            return False

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.split("Answer in yes or no:")[-1].strip().lower()

    def get_fail_safe():
        fs = "yes"
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 20,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/decide_to_talk_v2.txt"
    prompt_input = create_prompt_input(persona, target_persona, retrieved, test_input)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_decide_to_react(
    persona, target_persona, retrieved, test_input=None, verbose=False
):
    def create_prompt_input(init_persona, target_persona, retrieved, test_input=None):

        context = ""
        for c_node in retrieved["events"]:
            curr_desc = c_node.description.split(" ")
            curr_desc[2:3] = ["was"]
            curr_desc = " ".join(curr_desc)
            context += f"{curr_desc}. "
        context += "\n"
        for c_node in retrieved["thoughts"]:
            context += f"{c_node.description}. "

        curr_time = init_persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S %p")
        init_act_desc = init_persona.scratch.act_description
        if "(" in init_act_desc:
            init_act_desc = init_act_desc.split("(")[-1][:-1]
        if len(init_persona.scratch.planned_path) == 0:
            loc = ""
            if ":" in init_persona.scratch.act_address:
                loc = (
                    init_persona.scratch.act_address.split(":")[-1]
                    + " in "
                    + init_persona.scratch.act_address.split(":")[-2]
                )
            init_p_desc = f"{init_persona.name} is already {init_act_desc} at {loc}"
        else:
            loc = ""
            if ":" in init_persona.scratch.act_address:
                loc = (
                    init_persona.scratch.act_address.split(":")[-1]
                    + " in "
                    + init_persona.scratch.act_address.split(":")[-2]
                )
            init_p_desc = f"{init_persona.name} is on the way to {init_act_desc} at {loc}"

        target_act_desc = target_persona.scratch.act_description
        if "(" in target_act_desc:
            target_act_desc = target_act_desc.split("(")[-1][:-1]
        if len(target_persona.scratch.planned_path) == 0:
            loc = ""
            if ":" in target_persona.scratch.act_address:
                loc = (
                    target_persona.scratch.act_address.split(":")[-1]
                    + " in "
                    + target_persona.scratch.act_address.split(":")[-2]
                )
            target_p_desc = f"{target_persona.name} is already {target_act_desc} at {loc}"
        else:
            loc = ""
            if ":" in target_persona.scratch.act_address:
                loc = (
                    target_persona.scratch.act_address.split(":")[-1]
                    + " in "
                    + target_persona.scratch.act_address.split(":")[-2]
                )
            target_p_desc = f"{target_persona.name} is on the way to {target_act_desc} at {loc}"

        prompt_input = []
        prompt_input += [context]
        prompt_input += [curr_time]
        prompt_input += [init_p_desc]
        prompt_input += [target_p_desc]

        prompt_input += [init_persona.name]
        prompt_input += [init_act_desc]
        prompt_input += [target_persona.name]
        prompt_input += [target_act_desc]

        prompt_input += [init_act_desc]
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if gpt_response.split("Answer: Option")[-1].strip().lower() in ["3", "2", "1"]:
                return True
            return False
        except:
            return False

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.split("Answer: Option")[-1].strip().lower()

    def get_fail_safe():
        fs = "3"
        return fs

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 20,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/decide_to_react_v1.txt"
    prompt_input = create_prompt_input(persona, target_persona, retrieved, test_input)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_create_conversation(
    persona, target_persona, curr_loc, test_input=None, verbose=False
):
    def create_prompt_input(init_persona, target_persona, curr_loc, test_input=None):

        prev_convo_insert = "\n"
        if init_persona.a_mem.seq_chat:
            for i in init_persona.a_mem.seq_chat:
                if i.object == target_persona.scratch.name:
                    v1 = int((init_persona.scratch.curr_time - i.created).total_seconds() / 60)
                    prev_convo_insert += (
                        f"{str(v1)} minutes ago, they had the following conversation.\n"
                    )
                    for row in i.filling:
                        prev_convo_insert += f'{row[0]}: "{row[1]}"\n'
                    break
        if prev_convo_insert == "\n":
            prev_convo_insert = ""
        if init_persona.a_mem.seq_chat:
            if (
                int(
                    (
                        init_persona.scratch.curr_time - init_persona.a_mem.seq_chat[-1].created
                    ).total_seconds()
                    / 60
                )
                > 480
            ):
                prev_convo_insert = ""

        init_persona_thought_nodes = init_persona.a_mem.retrieve_relevant_thoughts(
            target_persona.scratch.act_event[0],
            target_persona.scratch.act_event[1],
            target_persona.scratch.act_event[2],
        )
        init_persona_thought = ""
        for i in init_persona_thought_nodes:
            init_persona_thought += f"-- {i.description}\n"

        target_persona_thought_nodes = target_persona.a_mem.retrieve_relevant_thoughts(
            init_persona.scratch.act_event[0],
            init_persona.scratch.act_event[1],
            init_persona.scratch.act_event[2],
        )
        target_persona_thought = ""
        for i in target_persona_thought_nodes:
            target_persona_thought += f"-- {i.description}\n"

        init_persona_curr_desc = ""
        if init_persona.scratch.planned_path:
            init_persona_curr_desc = (
                f"{init_persona.name} is on the way to {init_persona.scratch.act_description}"
            )
        else:
            init_persona_curr_desc = (
                f"{init_persona.name} is {init_persona.scratch.act_description}"
            )

        target_persona_curr_desc = ""
        if target_persona.scratch.planned_path:
            target_persona_curr_desc = (
                f"{target_persona.name} is on the way to {target_persona.scratch.act_description}"
            )
        else:
            target_persona_curr_desc = (
                f"{target_persona.name} is {target_persona.scratch.act_description}"
            )

        curr_loc = curr_loc["arena"]

        prompt_input = []
        prompt_input += [init_persona.scratch.get_str_iss()]
        prompt_input += [target_persona.scratch.get_str_iss()]

        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        prompt_input += [init_persona_thought]

        prompt_input += [target_persona.name]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona_thought]

        prompt_input += [init_persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S")]

        prompt_input += [init_persona_curr_desc]
        prompt_input += [target_persona_curr_desc]

        prompt_input += [prev_convo_insert]

        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]

        prompt_input += [curr_loc]
        prompt_input += [init_persona.name]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        # print ("???")
        # print (gpt_response)

        gpt_response = (prompt + gpt_response).split("What would they talk about now?")[-1].strip()
        content = re.findall('"([^"]*)"', gpt_response)

        speaker_order = []
        for i in gpt_response.split("\n"):
            name = i.split(":")[0].strip()
            if name:
                speaker_order += [name]

        ret = []
        for count, speaker in enumerate(speaker_order):
            ret += [[speaker, content[count]]]

        return ret

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe(init_persona, target_persona):
        convo = [[init_persona.name, "Hi!"], [target_persona.name, "Hi!"]]
        return convo

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 1000,
        "temperature": 0.7,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/create_conversation_v2.txt"
    prompt_input = create_prompt_input(persona, target_persona, curr_loc, test_input)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe(persona, target_persona)
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_summarize_conversation(persona, conversation, test_input=None, verbose=False):
    def create_prompt_input(conversation, test_input=None):
        convo_str = ""
        for row in conversation:
            convo_str += f'{row[0]}: "{row[1]}"\n'

        prompt_input = [convo_str]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        ret = "conversing about " + gpt_response.strip()
        return ret

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return "conversing with a housemate about morning greetings"

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        ret = "conversing about " + gpt_response.strip()
        return ret

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 11")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/summarize_conversation_v1.txt"  ########
    prompt_input = create_prompt_input(conversation, test_input)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "conversing about what to eat for lunch"  ########
    special_instruction = "The output must continue the sentence above by filling in the <fill in> tag. Don't start with 'this is a conversation about...' Just finish the sentence but do not miss any important details (including who are chatting)."  ########
    fail_safe = get_fail_safe()  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    # gpt_param = {"engine": "text-davinci-003", "max_tokens": 50,
    #              "temperature": 0, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    # prompt_template = "persona/prompt_template/v2/summarize_conversation_v1.txt"
    # prompt_input = create_prompt_input(conversation, test_input)
    # prompt = generate_prompt(prompt_input, prompt_template)

    # fail_safe = get_fail_safe()
    # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
    #                                  __func_validate, __func_clean_up)

    # if debug or verbose:
    #   print_run_prompts(prompt_template, persona, gpt_param,
    #                     prompt_input, prompt, output)

    # return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_extract_keywords(persona, description, test_input=None, verbose=False):
    def create_prompt_input(description, test_input=None):
        if "\n" in description:
            description = description.replace("\n", " <LINE_BREAK> ")
        prompt_input = [description]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print("???")
        print(gpt_response)
        gpt_response = gpt_response.strip().split("Emotive keywords:")
        factual = [i.strip() for i in gpt_response[0].split(",")]
        emotive = [i.strip() for i in gpt_response[1].split(",")]
        all_keywords = factual + emotive
        ret = []
        for i in all_keywords:
            if i:
                i = i.lower()
                if i[-1] == ".":
                    i = i[:-1]
                ret += [i]
        print(ret)
        return set(ret)

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return []

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 50,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/get_keywords_v1.txt"
    prompt_input = create_prompt_input(description, test_input)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_keyword_to_thoughts(
    persona, keyword, concept_summary, test_input=None, verbose=False
):
    def create_prompt_input(persona, keyword, concept_summary, test_input=None):
        prompt_input = [keyword, concept_summary, persona.name]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.strip()
        return gpt_response

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return ""

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 40,
        "temperature": 0.7,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/keyword_to_thoughts_v1.txt"
    prompt_input = create_prompt_input(persona, keyword, concept_summary)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_convo_to_thoughts(
    persona,
    init_persona_name,
    target_persona_name,
    convo_str,
    fin_target,
    test_input=None,
    verbose=False,
):
    def create_prompt_input(
        init_persona_name, target_persona_name, convo_str, fin_target, test_input=None
    ):
        prompt_input = [
            init_persona_name,
            target_persona_name,
            convo_str,
            init_persona_name,
            fin_target,
        ]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.strip()
        return gpt_response

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return ""

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 40,
        "temperature": 0.7,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/convo_to_thoughts_v1.txt"
    prompt_input = create_prompt_input(
        init_persona_name, target_persona_name, convo_str, fin_target
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_event_poignancy(persona, event_description, test_input=None, verbose=False):
    def create_prompt_input(persona, event_description, test_input=None):
        prompt_input = [
            persona.scratch.name,
            persona.scratch.get_str_iss(),
            persona.scratch.name,
            event_description,
        ]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = int(gpt_response.strip())
        return gpt_response

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return 4

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        gpt_response = int(gpt_response)
        return gpt_response

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 7")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/poignancy_event_v1.txt"  ########
    prompt_input = create_prompt_input(persona, event_description)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "5"  ########
    special_instruction = (
        "The output should ONLY contain ONE integer value on the scale of 1 to 10."  ########
    )
    fail_safe = get_fail_safe()  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_thought_poignancy(persona, event_description, test_input=None, verbose=False):
    def create_prompt_input(persona, event_description, test_input=None):
        prompt_input = [
            persona.scratch.name,
            persona.scratch.get_str_iss(),
            persona.scratch.name,
            event_description,
        ]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = int(gpt_response.strip())
        return gpt_response

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return 4

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        gpt_response = int(gpt_response)
        return gpt_response

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 8")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/poignancy_thought_v1.txt"  ########
    prompt_input = create_prompt_input(persona, event_description)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "5"  ########
    special_instruction = (
        "The output should ONLY contain ONE integer value on the scale of 1 to 10."  ########
    )
    fail_safe = get_fail_safe()  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    # gpt_param = {"engine": "text-davinci-003", "max_tokens": 3,
    #              "temperature": 0, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    # prompt_template = "persona/prompt_template/v2/poignancy_thought_v1.txt"
    # prompt_input = create_prompt_input(persona, event_description)
    # prompt = generate_prompt(prompt_input, prompt_template)

    # fail_safe = get_fail_safe()
    # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
    #                                  __func_validate, __func_clean_up)

    # if debug or verbose:
    #   print_run_prompts(prompt_template, persona, gpt_param,
    #                     prompt_input, prompt, output)

    # return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_chat_poignancy(persona, event_description, test_input=None, verbose=False):
    def create_prompt_input(persona, event_description, test_input=None):
        prompt_input = [
            persona.scratch.name,
            persona.scratch.get_str_iss(),
            persona.scratch.name,
            event_description,
        ]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = int(gpt_response.strip())
        return gpt_response

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return 4

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        gpt_response = int(gpt_response)
        return gpt_response

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 9")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/poignancy_chat_v1.txt"  ########
    prompt_input = create_prompt_input(persona, event_description)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "5"  ########
    special_instruction = (
        "The output should ONLY contain ONE integer value on the scale of 1 to 10."  ########
    )
    fail_safe = get_fail_safe()  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    # gpt_param = {"engine": "text-davinci-003", "max_tokens": 3,
    #              "temperature": 0, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    # prompt_template = "persona/prompt_template/v2/poignancy_chat_v1.txt"
    # prompt_input = create_prompt_input(persona, event_description)
    # prompt = generate_prompt(prompt_input, prompt_template)

    # fail_safe = get_fail_safe()
    # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
    #                                  __func_validate, __func_clean_up)

    # if debug or verbose:
    #   print_run_prompts(prompt_template, persona, gpt_param,
    #                     prompt_input, prompt, output)

    # return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_focal_pt(persona, statements, n, test_input=None, verbose=False):
    def create_prompt_input(persona, statements, n, test_input=None):
        prompt_input = [statements, str(n)]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = "1) " + gpt_response.strip()
        ret = []
        for i in gpt_response.split("\n"):
            ret += [i.split(") ")[-1]]
        return ret

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe(n):
        return ["Who am I"] * n

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        ret = ast.literal_eval(gpt_response)
        return ret

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 12")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/generate_focal_pt_v1.txt"  ########
    prompt_input = create_prompt_input(persona, statements, n)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = (
        '["What should Jane do for lunch", "Does Jane like strawberry", "Who is Jane"]'  ########
    )
    special_instruction = "Output must be a list of str."  ########
    fail_safe = get_fail_safe(n)  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================


def run_gpt_prompt_focal_pt_new(persona, statements, n, test_input=None, verbose=False):
    def create_prompt_input(persona, statements, n, test_input=None):
        prompt_input = [statements, str(n)]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = "1) " + gpt_response.strip()
        ret = []
        for i in gpt_response.split("\n"):
            ret += [i.split(") ")[-1]]
        return ret

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe(n):
        return ["Who am I"] * n

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        ret = ast.literal_eval(gpt_response)
        return ret

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 12")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/generate_focal_pt_v1.txt"  ########
    prompt_input = create_prompt_input(persona, statements, n)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = '["xxx", "xxx", "xxx"]'  ########
    special_instruction = "Output must be a list of str."  ########
    fail_safe = get_fail_safe(n)  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 150,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/generate_focal_pt_v1.txt"
    prompt_input = create_prompt_input(persona, statements, n)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe(n)
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 150,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/generate_focal_pt_v1.txt"
    prompt_input = create_prompt_input(persona, statements, n)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe(n)
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_insight_and_guidance(persona, statements, n, test_input=None, verbose=False):
    # The old function and prompt does not work at all
    @llm_function(is_chat=True, prompt_file="insight_and_evidence.md")
    def llm_insight_and_evidence(statements, target):

        return [
            {"insight": "<the first insight>", "evidence": [1, 5, 3]},
            {"insight": "<the second insight>", "evidence": [2, 3]},
        ]

    output = llm_insight_and_evidence(statements, str(n))
    ret = {item["insight"]: item["evidence"] for item in output}
    return [ret]


def run_gpt_prompt_insight_and_guidance_old(persona, statements, n, test_input=None, verbose=False):
    def create_prompt_input(persona, statements, n, test_input=None):
        prompt_input = [statements, str(n)]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = "1. " + gpt_response.strip()
        ret = dict()
        for i in gpt_response.split("\n"):
            row = i.split(". ")[-1]
            thought = row.split("(because of ")[0].strip()
            evi_raw = row.split("(because of ")[1].split(")")[0].strip()
            evi_raw = re.findall(r"\d+", evi_raw)
            evi_raw = [int(i.strip()) for i in evi_raw]
            ret[thought] = evi_raw
        return ret

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe(n):
        return ["I am hungry"] * n

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 150,
        "temperature": 0.5,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/insight_and_evidence_v1.txt"
    prompt_input = create_prompt_input(persona, statements, n)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe(n)
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_agent_chat_summarize_ideas(
    persona, target_persona, statements, curr_context, test_input=None, verbose=False
):
    def create_prompt_input(persona, target_persona, statements, curr_context, test_input=None):
        prompt_input = [
            persona.scratch.get_str_curr_date_str(),
            curr_context,
            persona.scratch.currently,
            statements,
            persona.scratch.name,
            target_persona.scratch.name,
        ]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.split('"')[0].strip()

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return "..."

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        return gpt_response.split('"')[0].strip()

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 17")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/summarize_chat_ideas_v1.txt"  ########
    prompt_input = create_prompt_input(persona, target_persona, statements, curr_context)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "Jane Doe is working on a project"  ########
    special_instruction = "The output should be a string that responds to the question."  ########
    fail_safe = get_fail_safe()  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    # gpt_param = {"engine": "text-davinci-003", "max_tokens": 150,
    #              "temperature": 0.5, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    # prompt_template = "persona/prompt_template/v2/summarize_chat_ideas_v1.txt"
    # prompt_input = create_prompt_input(persona, target_persona, statements, curr_context)
    # prompt = generate_prompt(prompt_input, prompt_template)

    # fail_safe = get_fail_safe()
    # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
    #                                  __func_validate, __func_clean_up)

    # if debug or verbose:
    #   print_run_prompts(prompt_template, persona, gpt_param,
    #                     prompt_input, prompt, output)

    # return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_agent_chat_summarize_relationship(
    persona, target_persona, statements, test_input=None, verbose=False
):
    def create_prompt_input(persona, target_persona, statements, test_input=None):
        prompt_input = [statements, persona.scratch.name, target_persona.scratch.name]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.split('"')[0].strip()

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return "..."

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        return gpt_response.split('"')[0].strip()

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 18")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = (
        "persona/prompt_template/v3_ChatGPT/summarize_chat_relationship_v2.txt"  ########
    )
    prompt_input = create_prompt_input(persona, target_persona, statements)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "Jane Doe is working on a project"  ########
    special_instruction = "The output should be a string that responds to the question."  ########
    fail_safe = get_fail_safe()  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    # gpt_param = {"engine": "text-davinci-003", "max_tokens": 150,
    #              "temperature": 0.5, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    # prompt_template = "persona/prompt_template/v2/summarize_chat_relationship_v1.txt"
    # prompt_input = create_prompt_input(persona, target_persona, statements)
    # prompt = generate_prompt(prompt_input, prompt_template)

    # fail_safe = get_fail_safe()
    # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
    #                                  __func_validate, __func_clean_up)

    # if debug or verbose:
    #   print_run_prompts(prompt_template, persona, gpt_param,
    #                     prompt_input, prompt, output)

    # return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_agent_chat(
    maze,
    persona,
    target_persona,
    curr_context,
    init_summ_idea,
    target_summ_idea,
    test_input=None,
    verbose=False,
):
    def create_prompt_input(
        persona, target_persona, curr_context, init_summ_idea, target_summ_idea, test_input=None
    ):
        prev_convo_insert = "\n"
        if persona.a_mem.seq_chat:
            for i in persona.a_mem.seq_chat:
                if i.object == target_persona.scratch.name:
                    v1 = int((persona.scratch.curr_time - i.created).total_seconds() / 60)
                    prev_convo_insert += f"{str(v1)} minutes ago, {persona.scratch.name} and {target_persona.scratch.name} were already {i.description} This context takes place after that conversation."
                    break
        if prev_convo_insert == "\n":
            prev_convo_insert = ""
        if persona.a_mem.seq_chat:
            if (
                int(
                    (persona.scratch.curr_time - persona.a_mem.seq_chat[-1].created).total_seconds()
                    / 60
                )
                > 480
            ):
                prev_convo_insert = ""
        print(prev_convo_insert)

        curr_sector = f"{maze.access_tile(persona.scratch.curr_tile)['sector']}"
        curr_arena = f"{maze.access_tile(persona.scratch.curr_tile)['arena']}"
        curr_location = f"{curr_arena} in {curr_sector}"

        prompt_input = [
            persona.scratch.currently,
            target_persona.scratch.currently,
            prev_convo_insert,
            curr_context,
            curr_location,
            persona.scratch.name,
            init_summ_idea,
            persona.scratch.name,
            target_persona.scratch.name,
            target_persona.scratch.name,
            target_summ_idea,
            target_persona.scratch.name,
            persona.scratch.name,
            persona.scratch.name,
        ]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)

        gpt_response = (prompt + gpt_response).split("Here is their conversation.")[-1].strip()
        content = re.findall('"([^"]*)"', gpt_response)

        speaker_order = []
        for i in gpt_response.split("\n"):
            name = i.split(":")[0].strip()
            if name:
                speaker_order += [name]

        ret = []
        for count, speaker in enumerate(speaker_order):
            ret += [[speaker, content[count]]]

        return ret

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return "..."

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        # ret = ast.literal_eval(gpt_response)

        print("a;dnfdap98fh4p9enf HEREE!!!")
        for row in gpt_response:
            print(row)

        return gpt_response

    def __chat_func_validate(gpt_response, prompt=""):  ############
        return True

    # print ("HERE JULY 23 -- ----- ") ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/agent_chat_v1.txt"  ########
    prompt_input = create_prompt_input(
        persona, target_persona, curr_context, init_summ_idea, target_summ_idea
    )  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = '[["Jane Doe", "Hi!"], ["John Doe", "Hello there!"] ... ]'  ########
    special_instruction = 'The output should be a list of list where the inner lists are in the form of ["<Name>", "<Utterance>"].'  ########
    fail_safe = get_fail_safe()  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    # print ("HERE END JULY 23 -- ----- ") ########
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    # gpt_param = {"engine": "text-davinci-003", "max_tokens": 2000,
    #              "temperature": 0.7, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    # prompt_template = "persona/prompt_template/v2/agent_chat_v1.txt"
    # prompt_input = create_prompt_input(persona, target_persona, curr_context, init_summ_idea, target_summ_idea)
    # prompt = generate_prompt(prompt_input, prompt_template)

    # fail_safe = get_fail_safe()
    # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
    #                                  __func_validate, __func_clean_up)

    # if debug or verbose:
    #   print_run_prompts(prompt_template, persona, gpt_param,
    #                     prompt_input, prompt, output)

    # return output, [output, prompt, gpt_param, prompt_input, fail_safe]


# =======================
# =======================
# =======================
# =======================


def run_gpt_prompt_summarize_ideas(persona, statements, question, test_input=None, verbose=False):
    def create_prompt_input(persona, statements, question, test_input=None):
        prompt_input = [statements, persona.scratch.name, question]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.split('"')[0].strip()

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return "..."

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        return gpt_response.split('"')[0].strip()

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 16")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/summarize_ideas_v1.txt"  ########
    prompt_input = create_prompt_input(persona, statements, question)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "Jane Doe is working on a project"  ########
    special_instruction = "The output should be a string that responds to the question."  ########
    fail_safe = get_fail_safe()  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    # gpt_param = {"engine": "text-davinci-003", "max_tokens": 150,
    #              "temperature": 0.5, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    # prompt_template = "persona/prompt_template/v2/summarize_ideas_v1.txt"
    # prompt_input = create_prompt_input(persona, statements, question)
    # prompt = generate_prompt(prompt_input, prompt_template)

    # fail_safe = get_fail_safe()
    # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
    #                                  __func_validate, __func_clean_up)

    # if debug or verbose:
    #   print_run_prompts(prompt_template, persona, gpt_param,
    #                     prompt_input, prompt, output)

    # return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_generate_next_convo_line(
    persona, interlocutor_desc, prev_convo, retrieved_summary, test_input=None, verbose=False
):
    def create_prompt_input(
        persona, interlocutor_desc, prev_convo, retrieved_summary, test_input=None
    ):
        prompt_input = [
            persona.scratch.name,
            persona.scratch.get_str_iss(),
            persona.scratch.name,
            interlocutor_desc,
            prev_convo,
            persona.scratch.name,
            retrieved_summary,
            persona.scratch.name,
        ]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.split('"')[0].strip()

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return "..."

    # # ChatGPT Plugin ===========================================================
    # def __chat_func_clean_up(gpt_response, prompt=""): ############
    #   return gpt_response.split('"')[0].strip()

    # def __chat_func_validate(gpt_response, prompt=""): ############
    #   try:
    #     __func_clean_up(gpt_response, prompt)
    #     return True
    #   except:
    #     return False

    # print ("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 15") ########
    # gpt_param = {"engine": "text-davinci-002", "max_tokens": 15,
    #              "temperature": 0, "top_p": 1, "stream": False,
    #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    # prompt_template = "persona/prompt_template/v3_ChatGPT/generate_next_convo_line_v1.txt" ########
    # prompt_input = create_prompt_input(persona, interlocutor_desc, prev_convo, retrieved_summary)  ########
    # prompt = generate_prompt(prompt_input, prompt_template)
    # example_output = 'Hello' ########
    # special_instruction = 'The output should be a string that responds to the question. Again, only use the context included in the "Note" to generate the response' ########
    # fail_safe = get_fail_safe() ########
    # output = chat_safe_generate_response(prompt, example_output, special_instruction, 3, fail_safe,
    #                                         __chat_func_validate, __chat_func_clean_up, True)
    # if output != False:
    #   return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # # ChatGPT Plugin ===========================================================

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 250,
        "temperature": 1,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/generate_next_convo_line_v1.txt"
    prompt_input = create_prompt_input(persona, interlocutor_desc, prev_convo, retrieved_summary)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_generate_whisper_inner_thought(persona, whisper, test_input=None, verbose=False):
    def create_prompt_input(persona, whisper, test_input=None):
        prompt_input = [persona.scratch.name, whisper]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.split('"')[0].strip()

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return "..."

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 50,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/whisper_inner_thought_v1.txt"
    prompt_input = create_prompt_input(persona, whisper)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_planning_thought_on_convo(persona, all_utt, test_input=None, verbose=False):
    def create_prompt_input(persona, all_utt, test_input=None):
        prompt_input = [all_utt, persona.scratch.name, persona.scratch.name, persona.scratch.name]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.split('"')[0].strip()

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return "..."

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 50,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/planning_thought_on_convo_v1.txt"
    prompt_input = create_prompt_input(persona, all_utt)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_memo_on_convo(persona, all_utt, test_input=None, verbose=False):
    def create_prompt_input(persona, all_utt, test_input=None):
        prompt_input = [all_utt, persona.scratch.name, persona.scratch.name, persona.scratch.name]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.split('"')[0].strip()

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return "..."

    # ChatGPT Plugin ===========================================================
    def __chat_func_clean_up(gpt_response, prompt=""):  ############
        return gpt_response.strip()

    def __chat_func_validate(gpt_response, prompt=""):  ############
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 15")  ########
    gpt_param = {
        "engine": "text-davinci-002",
        "max_tokens": 15,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v3_ChatGPT/memo_on_convo_v1.txt"  ########
    prompt_input = create_prompt_input(persona, all_utt)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "Jane Doe was interesting to talk to."  ########
    special_instruction = "The output should ONLY contain a string that summarizes anything interesting that the agent may have noticed"  ########
    fail_safe = get_fail_safe()  ########
    output = chat_safe_generate_response(
        prompt,
        example_output,
        special_instruction,
        gpt_param,
        3,
        fail_safe,
        __chat_func_validate,
        __chat_func_clean_up,
        True,
    )
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]
    # ChatGPT Plugin ===========================================================

    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 50,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "persona/prompt_template/v2/memo_on_convo_v1.txt"
    prompt_input = create_prompt_input(persona, all_utt)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_generate_safety_score(persona, comment, test_input=None, verbose=False):
    def create_prompt_input(comment, test_input=None):
        prompt_input = [comment]
        return prompt_input

    def __chat_func_clean_up(gpt_response, prompt=""):
        gpt_response = json.loads(gpt_response)
        return gpt_response["output"]

    def __chat_func_validate(gpt_response, prompt=""):
        try:
            fields = ["output"]
            response = json.loads(gpt_response)
            for field in fields:
                if field not in response:
                    return False
            return True
        except:
            return False

    def get_fail_safe():
        return None

    print("11")
    prompt_template = "persona/prompt_template/safety/anthromorphosization_v1.txt"
    prompt_input = create_prompt_input(comment)
    print("22")
    prompt = generate_prompt(prompt_input, prompt_template)
    print(prompt)
    fail_safe = get_fail_safe()
    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 50,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    output = completion_safe_generate_response(
        prompt, gpt_param, 3, fail_safe, __chat_func_validate, __chat_func_clean_up, verbose
    )
    print(output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def has_json_content(unstructured_string):
    # Check whether a string contains json content
    json_pattern = re.compile(r"(\{.*?\}|\[.*?\])", flags=re.DOTALL)
    json_strings = json_pattern.findall(unstructured_string)

    for json_str in json_strings:
        try:
            # Try to load the JSON to ensure it's valid
            json_obj = json.loads(json_str)
            return True

        except json.JSONDecodeError:
            continue

    return False


def run_gpt_generate_iterative_chat_utt(
    maze,
    init_persona,
    target_persona,
    retrieved,
    curr_context,
    curr_chat,
    test_input=None,
    verbose=False,
):
    def create_prompt_input(
        maze, init_persona, target_persona, retrieved, curr_context, curr_chat, test_input=None
    ):
        persona = init_persona
        prev_convo_insert = "\n"
        if persona.a_mem.seq_chat:
            for i in persona.a_mem.seq_chat:
                if i.object == target_persona.scratch.name:
                    v1 = int((persona.scratch.curr_time - i.created).total_seconds() / 60)
                    prev_convo_insert += f"{str(v1)} minutes ago, {persona.scratch.name} and {target_persona.scratch.name} were already {i.description} This context takes place after that conversation."
                    break
        if prev_convo_insert == "\n":
            prev_convo_insert = ""
        if persona.a_mem.seq_chat:
            if (
                int(
                    (persona.scratch.curr_time - persona.a_mem.seq_chat[-1].created).total_seconds()
                    / 60
                )
                > 480
            ):
                prev_convo_insert = ""
        print(prev_convo_insert)

        curr_sector = f"{maze.access_tile(persona.scratch.curr_tile)['sector']}"
        curr_arena = f"{maze.access_tile(persona.scratch.curr_tile)['arena']}"
        curr_location = f"{curr_arena} in {curr_sector}"

        retrieved_str = ""
        for key, vals in retrieved.items():
            for v in vals:
                retrieved_str += f"- {v.description}\n"

        convo_str = ""
        for i in curr_chat:
            convo_str += ": ".join(i) + "\n"
        if convo_str == "":
            convo_str = "[The conversation has not started yet -- start it!]"

        init_iss = f"Here is Here is a brief description of {init_persona.scratch.name}.\n{init_persona.scratch.get_str_iss()}"
        prompt_input = [
            init_iss,
            init_persona.scratch.name,
            retrieved_str,
            prev_convo_insert,
            curr_location,
            curr_context,
            init_persona.scratch.name,
            target_persona.scratch.name,
            convo_str,
            init_persona.scratch.name,
            target_persona.scratch.name,
            init_persona.scratch.name,
            init_persona.scratch.name,
            init_persona.scratch.name,
        ]
        return prompt_input

    def __chat_func_clean_up(gpt_response, prompt=""):
        gpt_response = extract_first_json_dict(gpt_response)

        cleaned_dict = dict()
        cleaned = []
        for key, val in gpt_response.items():
            cleaned += [val]
        cleaned_dict["utterance"] = cleaned[0]
        cleaned_dict["end"] = True
        if "f" in str(cleaned[1]) or "F" in str(cleaned[1]):
            cleaned_dict["end"] = False

        return cleaned_dict

    def __chat_func_validate(gpt_response, prompt=""):
        return has_json_content(gpt_response)

    def get_fail_safe():
        cleaned_dict = dict()
        cleaned_dict["utterance"] = "..."
        cleaned_dict["end"] = False
        return cleaned_dict

    print("11")
    prompt_template = "persona/prompt_template/v3_ChatGPT/iterative_convo_v1.txt"
    prompt_input = create_prompt_input(
        maze, init_persona, target_persona, retrieved, curr_context, curr_chat
    )
    print("22")
    prompt = generate_prompt(prompt_input, prompt_template)
    print(prompt)
    fail_safe = get_fail_safe()
    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 50,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    output = completion_safe_generate_response(
        prompt, gpt_param, 3, fail_safe, __chat_func_validate, __chat_func_clean_up, verbose
    )
    print(output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


### new version--all new
def run_gpt_generate_iterative_comment_utt_with_policy(
    persona, retrieved, all_news, policy, test_input=None, verbose=False
):
    def create_prompt_input(persona, retrieved, test_input=None):
        pm = ""
        n, m = 1, 1
        ###pm->[memorynode[name,s,p,o,description]]
        retrieved_context = ""
        description1 = []
        description2 = []
        for key, vals in retrieved.items():

            pm_node = str(n) + "."
            pm_node += vals["curr_event"].name
            pm_node += " said, "
            pm_node += vals["curr_event"].description + "\n"
            pm += pm_node

            for c_node in vals["events"]:
                description1 += [c_node.description]

            for c_node in vals["thoughts"]:
                description2 += [c_node.description]

            n += 1

        for des in set(description1):
            retrieved_context += str(m) + f". {des}\n"
            m += 1

        for des in set(description2):
            retrieved_context += str(m) + f". {des}\n"
            m += 1

        ###个人信息概述 (init_iss)：
        init_iss = f"{persona.scratch.get_str_iss()}"  # Here is the content and comments about the case, here is a brief description of {persona.scratch.name}.\n
        prompt_input = [
            init_iss,
            pm,
            persona.scratch.name,
            retrieved_context,
            persona.scratch.name,
            persona.scratch.name,
            persona.scratch.name,
            all_news,
            policy,
        ]
        return prompt_input

    def __chat_func_clean_up(gpt_response, prompt=""):
        gpt_response = extract_first_json_dict(gpt_response)
        cleaned_dict = dict()
        cleaned = []
        for key, val in gpt_response.items():
            cleaned += [val]
        cleaned_dict["comment"] = cleaned[0]
        return cleaned_dict

    def __chat_func_validate(gpt_response, prompt=""):
        try:
            print(extract_first_json_dict(gpt_response))
            return True
        except:
            return False

    def get_fail_safe():
        cleaned_dict = dict()
        cleaned_dict["utterance"] = "..."
        return cleaned_dict

    prompt_template = "persona/prompt_template/v3_ChatGPT/iterative_comment_v1.txt"
    prompt_input = create_prompt_input(persona, retrieved)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()
    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 500,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    output = completion_safe_generate_response(
        prompt, gpt_param, 3, fail_safe, __chat_func_validate, __chat_func_clean_up, verbose
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_generate_iterative_comment_utt_new(
    persona, retrieved, all_news, test_input=None, verbose=False
):
    @llm_function(prompt_file="iterative_comment.md", is_chat=True, stop="---")
    def iterative_comments(
        persona_iss: str,
        public_memory: str,
        retrieved_memory: str,
        persona_name: str,
        all_news: str,
    ):

        # You must write an example of output here
        return {"comment": f"<comments on news>"}

    # Step 1. Create prompt inputs
    pm = ""
    n, m = 1, 1
    retrieved_context = ""
    description1, description2 = [], []

    for key, vals in retrieved.items():
        pm += f"{n}. {vals['curr_event'].name} said, {vals['curr_event'].description}\n"

        # Collect descriptions from events and thoughts
        description1 += [c_node.description for c_node in vals["events"]]
        description2 += [c_node.description for c_node in vals["thoughts"]]
        n += 1

    for des in dict.fromkeys(description1):
        retrieved_context += f"{m}. {des}\n"
        m += 1

    for des in dict.fromkeys(description2):
        retrieved_context += f"{m}. {des}\n"
        m += 1

    ###个人信息概述 (init_iss)：
    init_iss = f"{persona.scratch.get_str_iss()}"  # Here is the content and comments about the case, here is a brief description of {persona.scratch.name}.

    # Step 2. Call llm function
    result = iterative_comments(init_iss, pm, retrieved_context, persona.scratch.name, all_news)
    return result


def run_gpt_generate_iterative_comment_utt(
    persona, retrieved, all_news, test_input=None, verbose=False
):

    return output, None


def run_gpt_generate_iterative_comment_utt_with_websearch(
    persona, retrieved, all_news, websearch, test_input=None, verbose=False
):
    def create_prompt_input(persona, retrieved, test_input=None):
        pm = ""
        n, m = 1, 1
        ###pm->[memorynode[name,s,p,o,description]]
        retrieved_context = ""
        description1 = []
        description2 = []
        for key, vals in retrieved.items():

            pm_node = str(n) + "."
            pm_node += vals["curr_event"].name
            pm_node += " said, "
            pm_node += vals["curr_event"].description + "\n"
            pm += pm_node

            for c_node in vals["events"]:
                description1 += [c_node.description]

            for c_node in vals["thoughts"]:
                description2 += [c_node.description]
                n += 1

        for des in set(description1):
            retrieved_context += str(m) + f". {des}\n"
            m += 1

        for des in set(description2):
            retrieved_context += str(m) + f". {des}\n"
            m += 1

        ###个人信息概述 (init_iss)：
        init_iss = f"{persona.scratch.get_str_iss()}"  # Here is the content and comments about the case, here is a brief description of {persona.scratch.name}.\n
        prompt_input = [
            init_iss,
            pm,
            persona.scratch.name,
            retrieved_context,
            persona.scratch.name,
            persona.scratch.name,
            persona.scratch.name,
            all_news,
            websearch,
        ]
        return prompt_input

    def __chat_func_clean_up(gpt_response, prompt=""):
        gpt_response = extract_first_json_dict(gpt_response)
        cleaned_dict = dict()
        cleaned = []
        for key, val in gpt_response.items():
            cleaned += [val]
        cleaned_dict["comment"] = cleaned[0]
        return cleaned_dict

    def __chat_func_validate(gpt_response, prompt=""):
        return has_json_content(gpt_response)

    def get_fail_safe():
        cleaned_dict = dict()
        cleaned_dict["utterance"] = "..."
        return cleaned_dict

    prompt_template = "persona/prompt_template/v3_ChatGPT/iterative_comment_v3.txt"
    prompt_input = create_prompt_input(persona, retrieved)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()
    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 500,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    output = completion_safe_generate_response(
        prompt, gpt_param, 3, fail_safe, __chat_func_validate, __chat_func_clean_up, verbose
    )
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_generate_iterative_comment_utt_with_policy_and_websearch(
    persona, retrieved, all_news, policy, websearch, test_input=None, verbose=False
):
    def create_prompt_input(persona, retrieved, test_input=None):
        pm = ""
        n, m = 1, 1
        ###pm->[memorynode[name,s,p,o,description]]
        retrieved_context = ""
        description1 = []
        description2 = []
        for key, vals in retrieved.items():

            pm_node = str(n) + "."
            pm_node += vals["curr_event"].name
            pm_node += " said, "
            pm_node += vals["curr_event"].description + "\n"
            pm += pm_node

            for c_node in vals["events"]:
                description1 += [c_node.description]

            for c_node in vals["thoughts"]:
                description2 += [c_node.description]

            n += 1

        for des in set(description1):
            retrieved_context += str(m) + f". {des}\n"
            m += 1

        for des in set(description2):
            retrieved_context += str(m) + f". {des}\n"
            m += 1

        ###个人信息概述 (init_iss)：
        init_iss = f"{persona.scratch.get_str_iss()}"  # Here is the content and comments about the case, here is a brief description of {persona.scratch.name}.\n
        prompt_input = [
            init_iss,
            pm,
            persona.scratch.name,
            retrieved_context,
            persona.scratch.name,
            persona.scratch.name,
            persona.scratch.name,
            all_news,
            policy,
            websearch,
        ]
        return prompt_input

    def __chat_func_clean_up(gpt_response, prompt=""):
        gpt_response = extract_first_json_dict(gpt_response)
        cleaned_dict = dict()
        cleaned = []
        for key, val in gpt_response.items():
            cleaned += [val]
        cleaned_dict["comment"] = cleaned[0]
        return cleaned_dict

    def __chat_func_validate(gpt_response, prompt=""):
        return has_json_content(gpt_response)

    def get_fail_safe():
        cleaned_dict = dict()
        cleaned_dict["utterance"] = "..."
        return cleaned_dict

    prompt_template = "persona/prompt_template/v3_ChatGPT/iterative_comment_v4.txt"
    prompt_input = create_prompt_input(persona, retrieved)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()
    gpt_param = {
        "engine": "text-davinci-003",
        "max_tokens": 500,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    output = completion_safe_generate_response(
        prompt, gpt_param, 3, fail_safe, __chat_func_validate, __chat_func_clean_up, verbose
    )
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


###wzt plan里面调用的判断
def run_gpt_prompt_decide_to_comment(persona, retrieved, test_input=None, verbose=False):
    pm = ""
    retrieved_context = ""
    description1, description2 = set(), set()

    for n, (key, vals) in enumerate(retrieved.items(), start=1):
        pm += f"{n}. {vals['curr_event'].name} said, {vals['curr_event'].description}\n"

        description1.update(c_node.description for c_node in vals["events"])
        description2.update(c_node.description for c_node in vals["thoughts"])

    for m, des in enumerate(description1 | description2, start=1):
        retrieved_context += f"{m}. {des}\n"

    curr_time = persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S %p")
    init_iss = f"{persona.scratch.get_str_iss()}"

    @llm_function(prompt_file="decide_to_comment.md", is_chat=True, stop="---")
    def decide_to_comment(public_memory, time, context, persona_name, persona_iss):

        return {
            "reasoning": "Let's think step by step.<the reasoning of the answer...>",
            "answer": "Yes or No",
        }

    output = decide_to_comment(pm, curr_time, retrieved_context, persona.name, init_iss)
    return [output["answer"].lower()]
