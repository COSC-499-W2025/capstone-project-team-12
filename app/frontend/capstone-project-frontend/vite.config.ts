import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const API_TARGET = process.env.API_TARGET || 'http://localhost:8080'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), ],
  server: {
    host: true,
    port: 5173,
    watch: {
      usePolling: true,
    },
    proxy: {
      '/projects': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '/skills': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '/resumes': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '/resume': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '/portfolios': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '/portfolio': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '/privacy-consent': {
        target: API_TARGET,
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./tests_frontend/setupTests.ts"],
}
})

