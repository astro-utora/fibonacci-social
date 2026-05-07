import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

// Get __dirname equivalent in ESM
const __dirname = dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL,
        changeOrigin: true,
        secure: true
      }
    }
  },
  preview: {
    port: 3000,
    host: true,
    allowedHosts: [
      'localhost',
      '*.railway.app',
      '*.up.railway.app',
      'fibonaccisocial-production.up.railway.app'
    ]
  }
}) 