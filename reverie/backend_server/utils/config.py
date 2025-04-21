import os

# Copy and paste your OpenAI API Key
openai_api_base = os.environ.get("LLM_BASE_URL")
openai_api_key = os.environ.get("LLM_API_KEY")

override_model = os.environ.get("LLM_MODEL_NAME")
override_gpt_param = {
    "model": override_model,
    "temperature": 1.0,
    "max_tokens": 512,
    "top_p": 0.7,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stream": False,
}

google_api_key = "<Google API Key>"  # search model key
google_api_cx = "<Google API CX>"  # search model id

# Put your name
key_owner = "<Name>"

storage_path = os.getenv("STORAGE_PATH", "../storage")
temp_storage_path = f"{storage_path}/temp_storage"

maze_assets_loc = f"{storage_path}/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

collision_block_id = "32125"

# Verbose
debug = True
per_instance_llm_config = True

BASE_TEMPLATES = [
    # "base_the_villie_isabella_maria_klaus",
    "base_the_villie_isabella_maria_klaus_online",
    # "base_the_villie_n25",
    "base_the_villie_n25_info",
]
