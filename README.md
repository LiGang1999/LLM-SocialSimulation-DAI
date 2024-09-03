# Generalized LLM Based Social Simulation Instrument

this is xmt branch!

<!-- <p align="center" width="100%">
<img src="cover.png" alt="Smallville" style="width: 80%; min-width: 300px; display: block; margin: auto;">
</p> -->

<p align="center" width="100%">
<img src="uml.jpg" alt="Smallville" style="width: 80%; min-width: 300px; display: block; margin: auto;">
</p>

This repository has its origins in [GA](https://github.com/joonspk-research/generative_agents) but extends beyond it. Our simulation tool is readily scalable and encompasses an offline simulation module (GA) as well as an online simulation module. Additionally, we are in the process of developing a user interface (for launch, display, and interaction) to enhance user-friendliness.

## Environment
### Frontend Environment Setup
#### Installing NodeJS
- For Linux
```bash
# Add the repository
curl -sL https://deb.nodesource.com/setup_21.x | sudo -E bash -
# Install NodeJS
sudo apt-get install -y nodejs
sudo apt-get install -y npm
```
#### Installing Dependencies
Install frontend dependencies:
```bash
cd frontend_online_old
npm install
```


Install backend dependencies:
```bash
cd . # projct root directory
pip install -r requirements.txt
```

We recommend using `Miniconda` or `Anaconda` to avoid package conflicts.

## Changing Ports
Modify `port1`, `port2`, and `port3` in `config.yaml` to unused ports.
```yaml
server_ip: 10.72.74.13
front_port: port1
front_port2: port2
back_port: port3
```

## Modify llm configurations
Create `utils/config.py` under `reverie/backend_server`. Here is a template:
```python
# Copy and paste your OpenAI API Key
openai_api_base = "https://api.openai.com/v1"
openai_api_key = "<Your OpenAI API>"
override_model = "<Your Model Name>" # if override_model is set to non-empty string, all api calls will be overrided to this model

# model_name="gpt-3.5-turbo",
# model_name="Llama-2-7b-chat-hf",
# model_name="Llama-2-13b-chat-hf",
# model_name="vicuna-13b-v1.5-16k",
# model_name="vicuna-33b-v1.3",
# model_name="Baichuan-13B-Chat",

google_api_key = "<>"  # Google Custom Search, api key
google_api_cx = "c2ab1202fad094a87"  # Google Custom Search, engine id

# Put your name
key_owner = "<Name>"

maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

fs_storage = "../../environment/frontend_server/storage"
fs_temp_storage = "../../environment/frontend_server/temp_storage"

collision_block_id = "32125"

# Verbose
debug = True

```

## Starting the System
```bash
python start.py
# python start.py --help to show helps
```

如果`Django` 提示你需要 `migrate`，输入下面命令：
```bash
cd reverie/backend_server && python manage.py migrate
```

```bash
cd environment/frontend_server && python manage.py migrate
```

## Debugging

set the environment variable LOG_LEVEL to `debug`, `info`, `warning`, `error` or `critical` to enable different levels of logging.

```bash
export LOG_LEVEL=debug
python start.py
```

You can save the stdout of web server, frontend server and backend server by adding `--save` argument, the logs will be saved to `webpage.log`, `frontend.log` and `backend.log` respectively.
```bash
python start.py --save
```

## Shutting Down
Press `Ctrl+C` to shut down the services.

## Acknowledgements

The source code has been adapted from [GA](https://github.com/joonspk-research/generative_agents).
