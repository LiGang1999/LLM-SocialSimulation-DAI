import { defineConfig } from 'vite'
import path from "path"
import { resolve } from 'path';
import fs from 'fs';
import react from '@vitejs/plugin-react'
import yaml from 'js-yaml';

// Load YAML configuration
const configPath = resolve(__dirname, '../config.yaml');
const fileContents = fs.readFileSync(configPath, 'utf8');
const config = yaml.load(fileContents) as Record<string, any>;


// https://vitejs.dev/config/
export default defineConfig({
  define: {
    'process.env': {
      VITE_API_BASE_URL: JSON.stringify(config.server_ip),
      VITE_API_PORT: JSON.stringify(config.front_port),
    },
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
