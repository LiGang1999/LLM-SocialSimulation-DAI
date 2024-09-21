# 基于LLM的通用社会模拟工具

<p align="center" width="100%">
<img src="uml.jpg" alt="系统架构" style="width: 80%; min-width: 300px; display: block; margin: auto;">
</p>

## 简介

本项目在[生成式智能体（GA）](https://github.com/joonspk-research/generative_agents)的基础上进行了扩展，创建了一个更全面且可扩展的模拟工具。我们的项目包括离线模拟模块（基于GA）和在线模拟模块。我们还在开发一个用户友好的界面，用于启动、显示和与模拟进行交互。

## 环境设置

### 前提条件

- Linux操作系统（推荐）
- Git
- 互联网连接

### 前端环境设置

#### 使用NVM（Node版本管理器）安装Node.js

1. 安装NVM：
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
   ```

2. 重启终端或运行：
   ```bash
   source ~/.bashrc
   ```

3. 安装并使用最新的LTS版本Node.js：
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

安装pnpm:
```bash
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

进入前端目录并安装依赖：

```bash
cd frontend_online_old
pnpm install
```

### 后端环境设置

我们建议使用Miniconda来管理Python环境，以避免包冲突。

#### 安装Miniconda

1. 下载Miniconda安装程序：
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   ```

2. 运行安装程序：
   ```bash
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

3. 按照提示完成安装。

4. 重启终端或运行：
   ```bash
   source ~/.bashrc
   ```

#### 创建Conda环境并安装依赖

1. 创建新的conda环境：
   ```bash
   conda create -n llm-sim python=3.12
   ```

2. 激活环境：
   ```bash
   conda activate llm-sim
   ```

3. 安装PyTorch（如果使用GPU，请根据您的CUDA版本调整命令）：
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```

4. 安装其他依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 配置

### 更改端口

修改`config.yaml`中的`port1`、`port2`和`port3`以使用可用端口：

```yaml
server_ip: 10.72.74.13
front_port: port1
front_port2: port2
back_port: port3
```

### LLM配置

在`reverie/backend_server`下创建`utils/config.py`。使用以下模板，并用您的实际API密钥和首选项替换占位符：

```python
openai_api_base = "https://api.openai.com/v1"
openai_api_key = "<您的OpenAI API密钥>"
override_model = "<您的模型名称>"  # 设置为非空字符串以覆盖所有API调用
google_api_key = "<您的Google API密钥>"
google_api_cx = "c2ab1202fad094a87"
key_owner = "<您的名字>"
maze_assets_loc = "../api/static/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"
storage_path = "../storage"
temp_storage_path = "../temp_storage"
collision_block_id = "32125"
debug = True
```

## 运行系统

1. 确保您在项目根目录中。

2. 启动系统：
   ```bash
   python start.py
   ```

   使用`python start.py --help`查看其他选项。

3. 如果Django提示需要迁移，请运行：
   ```bash
   cd reverie/backend_server && python manage.py migrate
   cd environment/frontend_server && python manage.py migrate
   ```

## 调试

设置`LOG_LEVEL`环境变量以控制日志详细程度：

```bash
export LOG_LEVEL=debug  # 选项：debug, info, warning, error, critical
python start.py
```

要保存服务器日志，请使用`--save`参数：

```bash
python start.py --save
```

这将把日志保存到`webpage.log`、`frontend.log`和`backend.log`。

## 关闭系统

按`Ctrl+C`关闭所有服务。

## 致谢

本项目基于[生成式智能体（GA）](https://github.com/joonspk-research/generative_agents)的工作。我们向原作者为该领域做出的贡献表示感谢。