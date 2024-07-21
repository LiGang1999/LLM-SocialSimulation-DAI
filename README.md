Here's the translation of your provided text into English:

# Generalized LLM Based Social Simulation Instrument

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
Navigate to the frontend directory:
```bash
cd dai_agent_fronted
```
Run the following command:
```bash
npm install
```

## Changing Ports
Modify `port1`, `port2`, and `port3` in `config.yaml` to unused ports.
```yaml
server_ip: 10.72.74.13
front_port: port1
front_port2: port2
back_port: port3
```

## Starting the System
```bash
bash start.sh
```
If you encounter issues, check `dai_agent_fronted/stdout.log`, `environment/frontend_server/stdout.log`, and `reverie/backend_server/stdout.log` for potential port conflicts.

## Shutting Down
```bash
bash shutdown.sh
```

## Acknowledgements

The source code has been adapted from [GA](https://github.com/joonspk-research/generative_agents).
