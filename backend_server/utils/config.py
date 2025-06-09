import os
from string import Template

import yaml

# Load default provider configurations from YAML file
with open("default_providers.yaml", "r") as f:
    default_providers = yaml.safe_load(f)

# Substitute environment variables
for provider_name, config in default_providers.items():
    for key, value in config.items():
        if isinstance(value, str):
            template = Template(value)
            config[key] = template.safe_substitute(os.environ)


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
per_instance_llm_config = os.environ.get("ENABLE_PUBLIC_LLM", "False").lower() == "true"

BASE_TEMPLATES = [
    # "base_the_villie_isabella_maria_klaus",
    "base_the_villie_isabella_maria_klaus_online",
    # "base_the_villie_n25",
    "base_the_villie_n25_info",
]
