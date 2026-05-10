import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          vue: ['vue', 'vue-router'],
          axios: ['axios'],
          element: ['element-plus'],
        },
      },
    },
  },
  server: {
    port: 5173,
    host: true,
  },
})
