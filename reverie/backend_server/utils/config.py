# Copy and paste your OpenAI API Key
openai_api_base = "https://api.v3.cm/v1"
openai_api_key = "sk-o0M0axm0I0N7xjlbC97c6aA8F8274e6bBa77282629EeA251"

override_model = "gpt-4o"
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

BASE_TEMPLATES = [
    # "base_the_villie_isabella_maria_klaus",
    "base_the_villie_isabella_maria_klaus_online",
    # "base_the_villie_n25",
    "base_the_villie_n25_info"
]
