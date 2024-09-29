import os
import json
from typing import List, Dict, Any
import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.llm_function import *

app = FastAPI()

templates_storage_dir = "../../reverie/backend_server/prompt_templates"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class TemplateListResponse(BaseModel):
    templates: List[str]


class TemplateDetailResponse(BaseModel):
    parameters: List[str]
    system_prompt: str
    user_prompt: str
    example: str


class GeneratePromptRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    parameters: Dict[str, str]
    example: str


class GeneratePromptResponse(BaseModel):
    system: str
    user: str


class GenerateResponseRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    parameters: Dict[str, str]
    example: str
    llm_params: Dict[str, Any]


class GenerateResponse(BaseModel):
    tokens_used: int
    content: str


# Helper functions
def get_templates():
    return [f for f in os.listdir(templates_storage_dir) if f.endswith(".md")]


def load_template(template_name):
    template = load_prompt_file(template_name, prompt_storage=templates_storage_dir)
    return template


def render_prompt(prompt, parameters):
    for key, value in parameters.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", value)
    return prompt


# Routes
@app.get("/prompt_templates", response_model=TemplateListResponse)
async def get_prompt_templates():
    templates = get_templates()
    return {"templates": templates}


@app.get("/prompt_template/{template_name}", response_model=TemplateDetailResponse)
async def get_prompt_template(template_name: str):
    template = load_template(template_name)
    return template


@app.post("/generate_prompt", response_model=GeneratePromptResponse)
async def generate_prompt(data: GeneratePromptRequest):
    generated_system_prompt = insert_prompt_args(
        data.system_prompt, data.parameters
    ) + example_output_format({}, {}, data.example)
    generated_user_prompt = insert_prompt_args(data.user_prompt, data.parameters)
    return {"system": generated_system_prompt, "user": generated_user_prompt}


@app.post("/generate_response", response_model=GenerateResponse)
async def generate_response(data: GenerateResponseRequest):

    params = data.parameters

    user_prompt = insert_prompt_args(data.user_prompt, params)
    system_prompt = insert_prompt_args(data.system_prompt, params) + example_output_format(
        {}, {}, data.example
    )

    def dummy_validate_fn(result, kwargs):
        return True

    def dummy_failsafe_fn(result, kwargs):
        return result

    def dummy_cleanup_fn(result, kwargs):
        return result

    config = override_gpt_param
    config["chat"] = True
    config["engine"] = data.llm_params["model"]
    config["base_url"] = data.llm_params["base_url"]
    config["api_key"] = data.llm_params["api_key"]

    result = llm_request(
        usr_prompt=user_prompt,
        sys_prompt=system_prompt,
        llm_config=config,
        validate_fn=dummy_validate_fn,
        cleanup_fn=dummy_cleanup_fn,
        failsafe_fn=dummy_failsafe_fn,
        kwargs=params,
        raw_response=True,
    )

    tokens_used = result.usage.total_tokens
    print(result)
    content = result.choices[0].message.content.strip()
    return {"tokens_used": tokens_used, "content": content}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
