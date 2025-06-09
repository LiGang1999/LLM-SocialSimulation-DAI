import { defineConfig, UserConfig } from 'vite'
import path from "path"
import react from '@vitejs/plugin-react'
import mdx from '@mdx-js/rollup'
import customDocPlugin from "./vite-plugin-docs"

const LISTEN_PREFIX = process.env.LISTEN_PREFIX;
const API_PREFIX = `${LISTEN_PREFIX}/api`

const config: UserConfig = {
  base: LISTEN_PREFIX,
  define: {
    'process.env': process.env
  },
  plugins: [
    customDocPlugin(),
    mdx(),
    react()
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: process.env.LISTEN_ADDRESS || '0.0.0.0',
    allowedHosts: true,
    port: parseInt(process.env.LISTEN_PORT || '9080'),
    proxy: {}
  },
  preview: {
    port: parseInt(process.env.LISTEN_PORT || '9080')
  }
}

if (config.server?.proxy) {
  config.server.proxy[API_PREFIX] = {
    target: `http://localhost:${process.env.BACKEND_PORT || '9081'}`,
    rewrite: (path) => path.replace(new RegExp(`^${LISTEN_PREFIX}`), ''),
    changeOrigin: true,
    ws: true
  }
}

// https://vitejs.dev/config/
export default defineConfig(config);
