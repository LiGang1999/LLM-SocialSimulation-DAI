import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig, loadEnv } from "vite"
import { fileURLToPath } from 'url';
import fs from 'fs'
import yaml from 'js-yaml'

// because __dirname was showing undefined
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// read config
const file_contents = fs.readFileSync("../config.yaml", 'utf-8')
const config_data = yaml.load(file_contents)

// convert to .env
let envContent = '';
for (const key in config_data) {
  if (config_data.hasOwnProperty(key)) {
    envContent += `VITE_${key}=${config_data[key]}\n`;
  }
}
const envFilePath = '.env'; // 替换为您的 .env 文件路径
fs.writeFileSync(envFilePath, envContent, 'utf8');

export default defineConfig(({command, mode}) => {
  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./"),
      },
    },
    server: {
      host: '0.0.0.0',
      port: config_data.front_port 
    },
  }
})