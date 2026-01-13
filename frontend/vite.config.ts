import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,      // Permite acesso fora do container
    port: 5173,
    watch: {
      usePolling: true // Necessário para Windows + Docker (Hot Reload)
    }
  }
})