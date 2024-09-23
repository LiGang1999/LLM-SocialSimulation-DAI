import functools
import inspect
import json
import os
import re
import time

import openai
from utils.config import openai_api_base, openai_api_key, override_gpt_param, override_model
from utils.logs import L
from jinja2 import Template

default_client = openai.Client(api_key=openai_api_key, base_url=openai_api_base)

default_llm_config = override_gpt_param

print_raw_log = False
print_short_log = True


def llm_logging_repr(object):
    if print_raw_log:
        s = str(object)
    else:
        s = repr(object)
    if print_short_log:
        s = s[:50] + "..."
    return s


def unescape_markdown(text):
    temp_text = text.replace("\\\\", "TEMP_DOUBLE_BACKSLASH")
    unescaped_text = re.sub(r"\\([\\\*\_\#\[\]\(\)\!\>\|\{\}\+\\\-\.])", r"\1", temp_text)
    unescaped_text = unescaped_text.replace("TEMP_DOUBLE_BACKSLASH", "\\\\")
    return unescaped_text


def extract_sections_with_content(md_content):
    header_pattern = re.compile(r"^(#+)\s+(.*)")
    sections = {}
    current_header = None
    current_content = []
    for line in md_content.splitlines():
        header_match = header_pattern.match(line)
        if header_match:
            if current_header:
                sections[current_header.lower().strip()] = "\n".join(current_content).strip()
            current_header = header_match.group(2)
            current_content = []
        else:
            if current_header:
                current_content.append(line)
    if current_header:
        sections[current_header.lower().strip()] = "\n".join(current_content).strip()
    return sections


def extract_parameters(parameters_content):
    parameters = []
    for line in parameters_content.split("\n"):
        if line.strip().startswith("-"):
            param = line.strip()[1:].split(":")[0].strip()
            parameters.append(param)
    return parameters


def load_prompt_file(prompt_file, prompt_storage="prompt_templates"):
    cwd = os.getcwd()
    fullpath = os.path.join(cwd, prompt_storage, prompt_file)
    L.debug(f"{prompt_file, prompt_storage, fullpath}")

    with open(fullpath, "r") as f:
        file_content = f.read()
        sections = extract_sections_with_content(file_content)
        system_prompt = unescape_markdown(sections.get("system prompt", "").strip())
        user_prompt = unescape_markdown(sections.get("user prompt", "").strip())
        parameters = extract_parameters(unescape_markdown(sections.get("parameters", "")))
        description = sections.get("description", "").strip()
        example = sections.get("example output", "")
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "parameters": parameters,
        "description": description,
        "example": example,
    }


def llm_request(
    usr_prompt,
    sys_prompt,
    llm_config,
    validate_fn,
    cleanup_fn,
    failsafe_fn,
    kwargs,
    func_name="",
    max_retries=3,
    retry_delay=0.5,
    raw_response=False,
):
    """
    Send a LLM request with error handling and logging. The llm_config dictionary consists of the following fields:
    - engine: str                the model name, e.g. "gpt-4",
    - chat: bool                whether to use chat mode or not,
    - temperature: float
    - max_tokens: int
    - top_p: float
    - frequency_penalty: float
    - presence_penalty: float
    - stop: list of str         stop sequence
    - base_url: str             the base URL of the API endpoint, e.g. "https://api.openai.com/v1"
    - api_key: str              the API key for the OpenAI API
    - max_retries: int          maximum number of retry attempts (default: 3)
    - retry_delay: int          delay in seconds between retries (default: 2)
    """

    # Validate the necessary fields
    if "engine" not in llm_config or "chat" not in llm_config:
        raise ValueError("The 'engine' and 'chat' fields are required in llm_config.")

    # Provide default values for optional fields
    temperature = llm_config.get("temperature", 1.0)  # Default temperature
    max_tokens = llm_config.get("max_tokens", 150)  # Default max tokens
    top_p = llm_config.get("top_p", 1.0)  # Default top_p
    frequency_penalty = llm_config.get("frequency_penalty", 0.0)  # Default frequency penalty
    presence_penalty = llm_config.get("presence_penalty", 0.0)  # Default presence penalty
    stop = llm_config.get("stop", None)  # Default stop sequence
    model = override_model if override_model else llm_config["engine"]

    attempt = 0
    L.debug(
        f"[{func_name}] LLM REQUEST; KIND: {'chat' if llm_config['chat'] else 'completion'}; USER_PROMPT:{llm_logging_repr(usr_prompt)}; SYSTEM_PROMPT:{llm_logging_repr(sys_prompt)}"
    )
    while attempt < max_retries:
        try:
            result = ""
            L.debug(
                f"[{func_name}] Attempt {attempt + 1}: Sending LLM request. Model: {llm_config['engine']}, Chat: {llm_config['chat']}"
            )
            start_time = time.time()
            if llm_config["chat"]:
                # Chat mode implementation
                messages = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": usr_prompt},
                ]
                # L.debug(f"Prompt:{str(messages)}")
                response = default_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    stream=False,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stop=stop,
                )
                if raw_response:
                    return response
                result = response.choices[0].message.content

                # result = response["choices"][0]["message"]["content"]
            else:
                # Standard completion mode
                # L.debug(f"Prompt:{str(sys_prompt + "\n" + usr_prompt)}")
                response = default_client.completions.create(
                    model=model,
                    prompt=sys_prompt + "\n" + usr_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    stream=False,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stop=stop,
                )
                if raw_response:
                    return response

                result = response.choices[0].text

                # result = response["choices"][0]["text"]
            valid = validate_fn(result, kwargs)
            L.stats(
                function_name=func_name,
                model=model,
                is_chat=llm_config["chat"],
                duration=time.time() - start_time,
                request_tokens=response.usage.prompt_tokens,
                response_tokens=response.usage.completion_tokens,
                valid=valid,
            )
            result = unescape_markdown(result)
            L.debug(f"[{func_name}] LLM RESPONSE: {llm_logging_repr(result)}")
            if valid:
                L.debug(f"[{func_name}] LLM Request succeeded.")
                return cleanup_fn(result, kwargs)
            else:
                L.warning(f"[{func_name}] LLM Response validation failed, retry scheduled")
                # continue

        except Exception as e:
            # Log the error
            L.error(f"[{func_name}] Error on attempt {attempt + 1}: {str(e)}")

            if attempt <= max_retries:
                L.warning(f"[{func_name}] Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                L.error(f"[{func_name}] Max retries exceeded. Request failed.")
                result = ""
                # raise e
        attempt += 1

    return failsafe_fn(result, kwargs)


def insert_prompt_args(prompt: str, kwargs):
    template = Template(prompt)
    return template.render(**kwargs)


def example_output_format(example_kwargs: dict, example_retval={}, example_ret_json=""):
    prompt = f"""
\n
Here is the example user input and the answer:

{'\n'.join([ f"{key}: {value}" for key, value in example_kwargs.items()])}"""
    # TODO shoud we include the example inputs and outputs here?
    prompt = f"""\n
 
You MUST reply the answer in the following json format (the values for each key are for reference only):
{example_ret_json if example_ret_json else json.dumps(example_retval, indent=4)}

You should not give any explanation unless it is required in your answer.
You MUST not add additional formats (headers, footers, points ) in your answer.
You MUST not reply anything else. Just reply the json answer.
"""

    return prompt


def types_match(actual, example, path=""):
    """Helper function to check if the types of two objects match (including nested types)."""

    def print_warning(expected, got):
        L.warning(f"Warning: Type mismatch at {path}. Expected {expected}, got {got}")

    if isinstance(example, dict):
        if not isinstance(actual, dict):
            print_warning("dict", type(actual).__name__)
            return False
        return all(
            k in actual and types_match(actual[k], v, f"{path}.{k}" if path else k)
            for k, v in example.items()
        )
    elif isinstance(example, list):
        if not isinstance(actual, list):
            print_warning("list", type(actual).__name__)
            return False
        return all(types_match(a, example[0], f"{path}[{i}]") for i, a in enumerate(actual))
    else:
        if not isinstance(actual, type(example)):
            print_warning(type(example).__name__, type(actual).__name__)
            return False
        return True


def has_json_content(unstructured_string):
    # Regular expression to find JSON objects or arrays in the string
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


def extract_largest_json(unstructured_string):
    import json

    decoder = json.JSONDecoder()

    max_len = 0
    result = ""
    n = len(unstructured_string)

    i = 0
    while i < n:
        # Skip any whitespace or characters that cannot start a JSON value
        if unstructured_string[i] not in "{[":
            i += 1
            continue

        try:
            # Attempt to decode a JSON object starting at index i
            obj, end = decoder.raw_decode(unstructured_string, idx=i)
            length = end - i
            if length > max_len:
                max_len = length
                result = unstructured_string[i:end]
            # Move i to the end of the current JSON object to avoid overlapping parsing
            i = end
        except json.JSONDecodeError:
            # If parsing fails, move to the next character
            i += 1
    return result


def llm_function(
    user_prompt: str = None,  # If prompt_file is not provided, this is used as the user prompt directly
    system_prompt: str = None,  # If prompt_file is not provided, this is used as the system prompt directly
    prompt_file: str = None,  # If provided, the user prompt and system prompt are loaded from this file
    is_chat: bool = False,  # If True, the function is a chat function
    stop: str = "",  # Stop sequence for the LLM
    llm_config={},  # Use this parameter to override the default configurations of the llm
    cleanup_fn=None,  # optional cleanup function. A default cleanup function is provided.
    failsafe_fn=None,  # optional failsafe function. A default failsafe function is provided.
    failsafe=None,  # optional failsafe value. If this is not None, the failsafe function will return this value.
    validate_fn=None,  # optional validate function.
):
    # load prompt files if necessary
    if prompt_file:
        loaded_prompt = load_prompt_file(prompt_file)
        user_prompt = loaded_prompt["user_prompt"]
        system_prompt = loaded_prompt["system_prompt"]

    def decorator(desc_func):
        # Use inspect to get the function signature and default values
        signature = inspect.signature(desc_func)

        # Generate example arguments based on type hints
        example_args = []
        for param in signature.parameters.values():
            if param.default is not inspect.Parameter.empty:
                example_args.append(param.default)
            else:
                # Determine default value based on type hints
                param_type = param.annotation
                if param_type == int:
                    example_args.append(0)
                elif param_type == float:
                    example_args.append(0.0)
                elif param_type == str:
                    example_args.append("")
                elif param_type == bool:
                    example_args.append(False)
                elif param_type == list:
                    example_args.append([])
                elif param_type == dict:
                    example_args.append({})
                else:
                    example_args.append(None)  # Default for unknown types

        @functools.wraps(desc_func)
        def wrapper(*args, _llm_config=default_llm_config, **kwargs):
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            bound_example_args = signature.bind(*example_args)
            bound_example_args.apply_defaults()
            example_kwargs = dict(bound_example_args.arguments)
            _llm_config.update(llm_config)
            if is_chat:
                _llm_config["chat"] = True
            if stop:
                _llm_config["stop"] = stop
            kwargs = dict(bound_args.arguments)

            usr_prompt = user_prompt.strip()
            sys_prompt = system_prompt.strip()

            usr_prompt = insert_prompt_args(usr_prompt, kwargs)
            example_result = desc_func(**example_kwargs)

            sys_prompt = insert_prompt_args(sys_prompt, kwargs) + example_output_format(
                example_kwargs, example_result
            )

            def default_validate_fn(result, kwargs):
                """
                Default validation function for llm returned results.
                It will try to parse the result as json and compare it with the example result. If they have the same nested types, the function returns True.
                """
                try:
                    largest_json = extract_largest_json(result)
                    json_result = json.loads(largest_json)
                    return types_match(json_result, example_result)
                except:
                    return False

            def default_failsafe_fn(result, kwargs):
                if failsafe:
                    return failsafe
                else:
                    return desc_func(**kwargs)

            def default_cleanup_fn(result, kwargs):
                return json.loads(extract_largest_json(result))

            _validate_fn = validate_fn if validate_fn is not None else default_validate_fn
            _failsafe_fn = failsafe_fn if failsafe_fn is not None else default_failsafe_fn
            _cleanup_fn = cleanup_fn if cleanup_fn is not None else default_cleanup_fn

            result = llm_request(
                usr_prompt,
                sys_prompt,
                _llm_config,
                _validate_fn,
                _cleanup_fn,
                _failsafe_fn,
                kwargs,
                desc_func.__name__,
            )
            return result

        return wrapper

    return decorator
