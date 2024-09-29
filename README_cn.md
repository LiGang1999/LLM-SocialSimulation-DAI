# 通用 LLM（大型语言模型）社会模拟工具

<a href="README.md">English</a>

## 介绍

本仓库扩展了 [生成式智能体（GA）](https://github.com/joonspk-research/generative_agents) 的工作，旨在创建一个更全面、可扩展的模拟工具。我们的项目包括一个离线模拟模块（基于 GA）和一个在线模拟模块。我们还在开发一个用户友好的界面，用于启动、展示和交互模拟过程。


## 目录

- [环境配置](#环境配置)
  - [先决条件](#先决条件)
  - [前端环境配置](#前端环境配置)
  - [后端环境配置](#后端环境配置)
- [运行配置](#运行配置)
  - [更改端口](#更改端口)
  - [LLM 配置](#llm-配置)
- [运行系统](#运行系统)
- [调试](#调试)
- [关闭](#关闭)
- [致谢](#致谢)


## 环境配置

### 先决条件

- 建议使用 Linux 操作系统
- Git
- 互联网连接

### 前端环境配置

#### 使用 NVM（Node 版本管理器）安装 Node.js

1. 安装 NVM：
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
   ```

2. 重新启动终端或运行：
   ```bash
   source ~/.bashrc
   ```

3. 安装并使用最新的 LTS 版本的 Node.js：
   ```bash
   nvm install --lts
   nvm use --lts
   ```

4. 验证安装：
   ```bash
   node --version
   npm --version
   ```

#### 安装前端依赖

安装 pnpm 包管理器：<https://pnpm.io/installation>

导航到前端目录并安装依赖：

```bash
cd frontend
pnpm install
```

### 后端环境配置

我们建议使用 Miniconda 来管理 Python 环境，避免包冲突。

#### 安装 Miniconda

1. 下载 Miniconda 安装程序：
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   ```

2. 运行安装程序：
   ```bash
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

3. 按提示完成安装。

4. 重新启动终端或运行：
   ```bash
   source ~/.bashrc
   ```

#### 创建 Conda 环境并安装依赖

1. 创建新的 conda 环境：
   ```bash
   conda create -n llm-sim python=3.12
   ```

2. 激活环境：
   ```bash
   conda activate llm-sim
   ```

3. 安装 PyTorch（如果使用 GPU，请根据您的 CUDA 版本调整命令）：
   <https://pytorch.org/get-started/locally/>
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```

4. 安装其他依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 运行配置

### 更改端口

1. 将 `config.template.yaml` 复制为 `config.yaml`。

2. 修改 `front_port` 和 `back_port` 为可用的端口：

```yaml
server_ip: <你的服务器 IP 地址>
front_port: <前端端口>
back_port: <后端端口>
```

### LLM 配置

将 `config_template.py` 复制到 `config.py`，路径为 `reverie/backend_server/utils`。使用以下模板，并用您的实际 API 密钥和偏好替换占位符：

```python
openai_api_base = "https://api.openai.com/v1"
openai_api_key = "<你的 OpenAI API 密钥>"
override_model = "<你的模型名称>"  # 设置为非空字符串以覆盖所有 API 调用
google_api_key = "<你的 Google API 密钥>"
google_api_cx = "c2ab1202fad094a87"
key_owner = "<你的名字>"
maze_assets_loc = "../api/static/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"
storage_path = "../storage"
temp_storage_path = "../temp_storage"
collision_block_id = "32125"
debug = True
```

## 运行系统

1. 确保您位于项目的根目录。

2. 启动系统：
```bash
python start.py
```

使用 `python start.py --help` 查看其他选项。

3. 如果你想直接在终端中运行：
```bash
cd reverie/backend_server
python reverie.py
```


## 调试

设置 `LOG_LEVEL` 环境变量以控制日志记录的详细程度：

```bash
export LOG_LEVEL=debug  # 选项：debug, info, warning, error, critical
python start.py
```

要保存服务器日志，使用 `--save` 参数：

```bash
python start.py --save
```

这将日志保存到 `webpage.log`、`frontend.log` 和 `backend.log`。

## 关闭

按 `Ctrl+C` 关闭所有服务。

## 致谢

本项目基于 [生成代理（GA）](https://github.com/joonspk-research/generative_agents) 的工作。我们对原作者在该领域的贡献表示衷心的感谢。