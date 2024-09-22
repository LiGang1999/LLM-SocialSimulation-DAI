import os
import json
from typing import List, Dict
import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

templates_storage_dir = "../../backend_server/prompt_templates"

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
    params: List[str]
    system_prompt: str
    user_prompt: str


class GeneratePromptRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    params: Dict[str, str]


class GeneratePromptResponse(BaseModel):
    generated_system_prompt: str
    generated_user_prompt: str


class GenerateResponseRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    params: Dict[str, str]
    llm_params: Dict[str, str]


class GenerateResponse(BaseModel):
    tokens_used: int
    content: str


# Helper functions
def get_templates():
    return [f for f in os.listdir(templates_storage_dir) if f.endswith(".md")]


def load_template(template_name):
    template_path = os.path.join(templates_storage_dir, f"{template_name}.json")
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Template not found")
    with open(template_path, "r") as file:
        template = json.load(file)
    return template


def render_prompt(prompt, params):
    for key, value in params.items():
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
    generated_system_prompt = render_prompt(data.system_prompt, data.params)
    generated_user_prompt = render_prompt(data.user_prompt, data.params)
    return {
        "generated_system_prompt": generated_system_prompt,
        "generated_user_prompt": generated_user_prompt,
    }


@app.post("/generate_response", response_model=GenerateResponse)
async def generate_response(data: GenerateResponseRequest):
    generated_system_prompt = render_prompt(data.system_prompt, data.params)
    generated_user_prompt = render_prompt(data.user_prompt, data.params)
    prompt = generated_system_prompt + "\n" + generated_user_prompt

    # Prepare OpenAI API call
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {data.llm_params.get('api_key')}",
    }
    payload = {
        "model": data.llm_params.get("model", "gpt-3.5-turbo"),
        "prompt": prompt,
        "max_tokens": int(data.llm_params.get("max_tokens", 150)),
        "top_p": float(data.llm_params.get("top_p", 1)),
        "temperature": float(data.llm_params.get("temperature", 1)),
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            data.llm_params.get("base_url", "https://api.openai.com/v1/completions"),
            headers=headers,
            json=payload,
        ) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            result = await resp.json()

    tokens_used = result["usage"]["total_tokens"]
    content = result["choices"][0]["text"].strip()
    return {"tokens_used": tokens_used, "content": content}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
