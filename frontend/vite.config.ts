import { defineConfig } from 'vite'
import path from "path"
import { resolve } from 'path'
import fs from 'fs'
import react from '@vitejs/plugin-react'
import yaml from 'js-yaml'
import dotenv from 'dotenv'

// Load YAML configuration
const configPath = resolve(__dirname, '../config.yaml')
const fileContents = fs.readFileSync(configPath, 'utf8')
const config = yaml.load(fileContents) as Record<string, any>

// Create .env file content
const envContent = Object.entries(config).map(([key, value]) => `VITE_${key.toUpperCase()}=${value}`).join('\n')

// Write to .env file
fs.writeFileSync('.env', envContent)

// Load .env file
dotenv.config()

// https://vitejs.dev/config/
export default defineConfig({
  define: {
    'process.env': process.env
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})