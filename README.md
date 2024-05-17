

# Generalized LLM based Social Simulation Instrument 

<!-- <p align="center" width="100%">
<img src="cover.png" alt="Smallville" style="width: 80%; min-width: 300px; display: block; margin: auto;">
</p> -->

<p align="center" width="100%">
<img src="uml.jpg" alt="Smallville" style="width: 80%; min-width: 300px; display: block; margin: auto;">
</p>

This repository is originated from [GA](https://github.com/joonspk-research/generative_agents) but covers it. Our simulation instrument is easily scalable and contains offline simulation module (GA) and online simulation module. Besides, we are developing UI (launch, display and interact) for user-friendliness.

## 启动前端
### 环境安装
#### 安装nodejs
- Linux
```bash
# 添加源
curl -sL https://deb.nodesource.com/setup_21.x | sudo -E bash -
# 安装nodejs
sudo apt-get install -y nodejs
sudo apt-get install -y npm
```
#### 安装依赖
进入到前端目录:
```bash
cd dai_agent_fronted
```
执行以下命令：
```bash
npm install
```
### 运行前端
```bash
npm run dev
```
如果前端使用的端口被占用了，可以在dai_agent_fronted/vite.config.js文件中修改：
```javascript
export default defineConfig({
  ...
  server: {
    host: '0.0.0.0',
    port: front_port
  }
})
```
## 启动后端
```bash
# 进入到后端目录
cd reverie/backend_server
python manage.py runserver 0.0.0.0:back_port 
```
此处back_port代表启动后端服务所使用的端口，如果该端口被占用可以更换为其他端口，且前端对应的端口也需要修改，分别是：
- dai_agent_fronted/src/App.jsx
- dai_agent_fronted/src/StartApp.jsx

## 备注
注意将以下几个文件中的server_ip替换掉：
- dai_agent_fronted/src/App.jsx
- dai_agent_fronted/src/StartApp.jsx
- reverie/backend_server/api/settings.py

## Acknowledgements

The source code is adapted from [GA](https://github.com/joonspk-research/generative_agents).
