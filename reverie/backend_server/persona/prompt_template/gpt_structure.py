"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: gpt_structure.py
Description: Wrapper functions for calling OpenAI APIs.
"""

import json
import random
import re
import time

from openai import OpenAI
from utils.config import openai_api_base, openai_api_key, override_gpt_param, override_model
from utils.logs import L, get_outer_caller

client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)


def extract_largest_jsno_dict(data_str):
    # Find the largest json from a unstructured string
    # Regular expression to find JSON objects or arrays in the string
    json_pattern = re.compile(r"(\{.*?\}|\[.*?\])", flags=re.DOTALL)
    json_strings = json_pattern.findall(data_str)

    largest_json_str = None
    largest_json_length = 0

    for json_str in json_strings:
        try:
            # Try to load the JSON to ensure it's valid
            json_obj = json.loads(json_str)
            json_length = len(json_str)

            if json_length > largest_json_length:
                largest_json_length = json_length
                largest_json_str = json_str

        except json.JSONDecodeError:
            continue

    return json.loads(largest_json_str) if largest_json_str else None


def extract_first_json_dict(data_str):
    # Find the largest json from a unstructured string
    # Regular expression to find JSON objects or arrays in the string
    json_pattern = re.compile(r"(\{.*?\}|\[.*?\])", flags=re.DOTALL)
    json_strings = json_pattern.findall(data_str)

    for json_str in json_strings:
        try:
            # Try to load the JSON to ensure it's valid
            json_obj = json.loads(json_str)
            return json_obj

        except json.JSONDecodeError:
            continue

    return None


def unescape_markdown(text):
    """
    Sometimes the model gives markdown escaped results. So we need to unescape them.
    """
    # 使用正则表达式去除反斜杠前缀
    temp_text = text.replace("\\\\", "TEMP_DOUBLE_BACKSLASH")
    unescaped_text = re.sub(r"\\([\\\*\_\#\[\]\(\)\!\>\|\{\}\+\\\-\.])", r"\1", temp_text)

    # 恢复原有的双反斜杠
    unescaped_text = unescaped_text.replace("TEMP_DOUBLE_BACKSLASH", "\\\\")
    return unescaped_text


def generate_gpt_response(
    prompt: str,
    gpt_parameters: dict,
    max_retries=3,
    fail_safe_response="error",
    func_validate=None,
    func_clean_up=None,
    is_chat=True,
    example_output=None,
    special_instruction=None,
):
    """
    Safely generate a GPT response (chat or completion) with retries, validation, and cleanup.

    ARGS:
      prompt: A string prompt for the GPT model.
      gpt_parameters: A dictionary with keys for parameter names and values for parameter values.
      max_retries: Maximum number of retry attempts.
      fail_safe_response: A response to return in case of failure.
      func_validate: A function to validate the GPT response.
      func_clean_up: A function to clean up the GPT response.
      is_chat: If true, uses the chat model, otherwise uses the completion model.
      example_output: (Optional) A Python dict, list, or string for example output in chat mode.
      special_instruction: (Optional) A string containing special instructions for chat mode.

    RETURNS:
      A string containing the GPT response, or the fail_safe_response if unsuccessful.
    """
    tries = 0

    if override_gpt_param:
        gpt_parameters.update(override_gpt_param)
    while tries < max_retries:
        try:
            model = gpt_parameters["engine"] + ("" if is_chat else "-instruct")
            start_time = time.time()

            if is_chat:
                # Prepare system prompt if in chat mode
                example_output_str = (
                    example_output
                    if isinstance(example_output, str)
                    else json.dumps(example_output)
                )
                system_prompt = f"""
You are a helpful assistant. You should only output your response to the user in JSON format, and you should meet the requirements.

Example for your response:

{{
"output" : {example_output_str}
}}

Requirements:
{special_instruction}
"""
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ]
                L.debug(f"SYSTEM_PROMPT:{repr(system_prompt)};USER_PROMPT:{repr(prompt)}")
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=gpt_parameters["temperature"],
                    max_tokens=gpt_parameters["max_tokens"],
                    top_p=gpt_parameters["top_p"],
                    frequency_penalty=gpt_parameters["frequency_penalty"],
                    presence_penalty=gpt_parameters["presence_penalty"],
                    stream=gpt_parameters["stream"],
                    stop=gpt_parameters["stop"],
                )
                L.debug(response)
                curr_gpt_response = str(
                    extract_first_json_dict(response.choices[0].message.content.strip())["output"]
                )
            else:
                # Directly use completion API
                L.debug(f"USER_PROMPT:{repr(prompt)}")
                response = client.completions.create(
                    model=model,
                    prompt=prompt,
                    temperature=gpt_parameters["temperature"],
                    max_tokens=gpt_parameters["max_tokens"],
                    top_p=gpt_parameters["top_p"],
                    frequency_penalty=gpt_parameters["frequency_penalty"],
                    presence_penalty=gpt_parameters["presence_penalty"],
                    stream=gpt_parameters["stream"],
                    stop=gpt_parameters["stop"],
                )
                curr_gpt_response = response.choices[0].text.strip()

            L.debug(f"GPT_RESPONSE:{repr(curr_gpt_response)}")

            valid = func_validate(curr_gpt_response, prompt=prompt)
            L.stats(
                get_outer_caller(__name__),
                model=model,
                is_chat=is_chat,
                valid=valid,
                duration=time.time() - start_time,
                request_tokens=response.usage.prompt_tokens,
                response_tokens=response.usage.completion_tokens,
            )
            if valid:
                return (
                    func_clean_up(unescape_markdown(curr_gpt_response), prompt=prompt)
                    if func_clean_up
                    else unescape_markdown(curr_gpt_response)
                )
            else:
                return unescape_markdown(curr_gpt_response)

        except Exception as e:
            L.warning(f"Error during GPT request: {e}", exc_info=True)

        tries += 1
        time.sleep(0.1)  # Optional: Wait before retrying
        L.debug(f"Attempt {tries}/{max_retries} failed.")

    L.error("GPT Request failed after all attempts", exc_info=True)
    return fail_safe_response


def safe_generate_response(
    prompt,
    gpt_param,
    repeat=5,
    fail_safe="error",
    func_validate=None,
    func_cleanup=None,
    verbose=False,
):

    # 暂时使用 completion_request
    return generate_gpt_response(
        prompt, gpt_param, repeat, fail_safe, func_validate, func_cleanup, is_chat=False
    )


def completion_safe_generate_response(
    prompt,
    gpt_param,
    repeat=5,
    fail_safe="error",
    func_validate=None,
    func_cleanup=None,
    verbose=False,
):

    # 暂时使用 completion_request
    return generate_gpt_response(
        prompt, gpt_param, repeat, fail_safe, func_validate, func_cleanup, is_chat=False
    )


def chat_safe_generate_response(
    prompt,
    example_output,
    special_instruction,
    gpt_param,
    repeat=5,
    fail_safe="error",
    func_validate=None,
    func_cleanup=None,
    verbose=False,
):
    return generate_gpt_response(
        prompt,
        gpt_param,
        repeat,
        fail_safe,
        func_validate,
        func_cleanup,
        is_chat=True,
        special_instruction=special_instruction,
        example_output=example_output,
    )


def convert_to_json(obj):
    """
    Converts a Python object into a JSON string.

    Parameters:
        obj: The Python object to convert. This can be a dict, list, or any object that is JSON serializable.

    Returns:
        A JSON string representation of the object.
    """
    try:
        return json.dumps(obj, ensure_ascii=False, indent=4)
    except TypeError as e:
        return f"Object of type {type(obj).__name__} is not JSON serializable: {e}"


def generate_prompt(curr_input, prompt_lib_file):
    """
    Takes in the current input (e.g. comment that you want to classifiy) and
    the path to a prompt file. The prompt file contains the raw str prompt that
    will be used, which contains the following substr: !<INPUT>! -- this
    function replaces this substr with the actual curr_input to produce the
    final promopt that will be sent to the GPT3 server.
    ARGS:
      curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                  INPUT, THIS CAN BE A LIST.)
      prompt_lib_file: the path to the promopt file.
    RETURNS:
      a str prompt that will be sent to OpenAI's GPT server.
    """
    if type(curr_input) == type("string"):
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]

    f = open(prompt_lib_file, "r")
    prompt = f.read()
    f.close()
    for count, i in enumerate(curr_input):
        prompt = prompt.replace(f"!<INPUT {count}>!", i)
    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
    return prompt.strip()


def get_embedding(text, model="text-embedding-ada-002"):

    model = model if not override_model else override_model
    model = "text-embedding-ada-002"

    text = text.replace("\n", " ")
    if not text:
        text = "this is blank"
    return client.embeddings.create(input=[text], model=model).data[0].embedding


if __name__ == "__main__":
    gpt_parameter = {
        "engine": "text-davinci-003",
        "max_tokens": 50,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": ['"'],
    }
    curr_input = ["driving to a friend's house"]
    prompt_lib_file = "prompt_template/test_prompt_July5.txt"
    prompt = generate_prompt(curr_input, prompt_lib_file)

    def __func_validate(gpt_response):
        if len(gpt_response.strip()) <= 1:
            return False
        if len(gpt_response.strip().split(" ")) > 1:
            return False
        return True

    def __func_clean_up(gpt_response):
        cleaned_response = gpt_response.strip()
        return cleaned_response

    output = completion_safe_generate_response(
        prompt, gpt_parameter, 5, "rest", __func_validate, __func_clean_up, True
    )

    print(output)
