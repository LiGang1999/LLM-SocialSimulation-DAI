import { defineConfig } from 'vite'
import path from "path"
import react from '@vitejs/plugin-react'
import dotenv from 'dotenv'

// Load .env file from project root
dotenv.config({ path: '../.env' })

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
  server: {
    host: process.env.LISTEN_ADDRESS || '0.0.0.0',
    port: parseInt(process.env.LISTEN_PORT || '9080'),
    proxy: {
      '/api': {
        target: `http://localhost:${process.env.BACKEND_PORT || '9081'}`,
        changeOrigin: true,
      },
      '/api/ws': {
        target: `http://localhost:${process.env.BACKEND_PORT || '9081'}`,
        changeOrigin: true,
        ws: true
      }
    }
  },
  preview: {
    port: parseInt(process.env.LISTEN_PORT || '9080')
  }
})
