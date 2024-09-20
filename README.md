# Generalized LLM Based Social Simulation Instrument

<p align="center" width="100%">
<img src="uml.jpg" alt="System Architecture" style="width: 80%; min-width: 300px; display: block; margin: auto;">
</p>

## Introduction

This repository extends the work of [Generative Agents (GA)](https://github.com/joonspk-research/generative_agents) to create a more comprehensive and scalable simulation tool. Our project includes both an offline simulation module (based on GA) and an online simulation module. We are also developing a user-friendly interface for launching, displaying, and interacting with the simulation.

## Environment Setup

### Prerequisites

- Linux operating system (recommended)
- Git
- Internet connection

### Frontend Environment Setup

#### Installing Node.js using NVM (Node Version Manager)

1. Install NVM:
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
   ```

2. Restart your terminal or run:
   ```bash
   source ~/.bashrc
   ```

3. Install and use the latest LTS version of Node.js:
   ```bash
   nvm install --lts
   nvm use --lts
   ```

4. Verify the installation:
   ```bash
   node --version
   npm --version
   ```

#### Installing Frontend Dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd frontend_online_old
npm install
```

### Backend Environment Setup

We recommend using Miniconda to manage Python environments and avoid package conflicts.

#### Installing Miniconda

1. Download the Miniconda installer:
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   ```

2. Run the installer:
   ```bash
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

3. Follow the prompts to complete the installation.

4. Restart your terminal or run:
   ```bash
   source ~/.bashrc
   ```

#### Creating a Conda Environment and Installing Dependencies

1. Create a new conda environment:
   ```bash
   conda create -n llm-sim python=3.12
   ```

2. Activate the environment:
   ```bash
   conda activate llm-sim
   ```

3. Install PyTorch (adjust the command based on your CUDA version if using GPU):
   https://pytorch.org/get-started/locally/
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```

4. Install other dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Changing Ports

Modify `port1`, `port2`, and `port3` in `config.yaml` to use available ports:

```yaml
server_ip: 10.72.74.13
front_port: port1
front_port2: port2
back_port: port3
```

### LLM Configuration

Create `utils/config.py` under `reverie/backend_server`. Use the following template and replace the placeholders with your actual API keys and preferences:

```python
openai_api_base = "https://api.openai.com/v1"
openai_api_key = "<Your OpenAI API Key>"
override_model = "<Your Model Name>"  # Set to non-empty string to override all API calls
google_api_key = "<Your Google API Key>"
google_api_cx = "c2ab1202fad094a87"
key_owner = "<Your Name>"
maze_assets_loc = "../api/static/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"
storage_path = "../storage"
temp_storage_path = "../temp_storage"
collision_block_id = "32125"
debug = True
```

## Running the System

1. Ensure you're in the project root directory.

2. Start the system:
   ```bash
   python start.py
   ```

   Use `python start.py --help` for additional options.

3. If Django prompts for migrations, run:
   ```bash
   cd reverie/backend_server && python manage.py migrate
   cd environment/frontend_server && python manage.py migrate
   ```

## Debugging

Set the `LOG_LEVEL` environment variable to control logging verbosity:

```bash
export LOG_LEVEL=debug  # Options: debug, info, warning, error, critical
python start.py
```

To save server logs, use the `--save` argument:

```bash
python start.py --save
```

This will save logs to `webpage.log`, `frontend.log`, and `backend.log`.

## Shutting Down

Press `Ctrl+C` to shut down all services.

## Acknowledgements

This project builds upon the work of [Generative Agents (GA)](https://github.com/joonspk-research/generative_agents). We extend our gratitude to the original authors for their contributions to the field.