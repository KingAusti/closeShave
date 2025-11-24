import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'icons/*.png'],
      manifest: {
        name: 'CloseShave - Web Scraper',
        short_name: 'CloseShave',
        description: 'Find the cheapest products across major merchants',
        theme_color: '#00ff41',
        background_color: '#000000',
        display: 'standalone',
        icons: [
          {
            src: 'icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}']
      }
    })
  ],
  server: {
    port: 5173,
    host: '0.0.0.0', // Allow external connections
    proxy: {
      '/api': {
        // In Docker, use service name; locally, use localhost
        target: process.env.VITE_API_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})

