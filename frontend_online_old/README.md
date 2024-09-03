# 社会仿真Agent前端
## 环境安装
### 安装nodejs
测试时用的nodejs版本是21.6.0，但应该用其他版本的也行。
- Linux
```bash
# 添加源
curl -sL https://deb.nodesource.com/setup_21.x | sudo -E bash -
# 安装nodejs
sudo apt-get install -y nodejs
sudo apt-get install -y npm
```
### 安装依赖
进入到前端目录后，执行以下命令：
```bash
npm install
```
## 运行
```bash
npm run dev
```