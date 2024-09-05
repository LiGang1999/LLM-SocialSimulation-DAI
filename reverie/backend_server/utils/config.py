# Copy and paste your OpenAI API Key
openai_api_base = "https://api.bianxie.ai/v1"
openai_api_key = "sk-Mc0h6rJZ1dvmnZiRD3B8F117B65d437c8a1a38D6E26c8585"

override_model = "gpt-3.5-turbo"
override_gpt_param = {
    "engine": override_model,
    "temperature": 1.0,
    "max_tokens": 512,
    "top_p": 0.7,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stream": False,
}

google_api_key = "AIzaSyDuYLLNJHv_51Gafiw7Vc2NIucFLf4MaNg"  # search engine key
google_api_cx = "c2ab1202fad094a87"  # search engine id

# Put your name
key_owner = "<Name>"

maze_assets_loc = "api/static/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

storage_path = "../storage"
temp_storage_path = "../temp_storage"
compressed_storage_path = "../compressed_storage"
port_config_file = "../../config.yaml"

collision_block_id = "32125"

# Verbose
debug = True
