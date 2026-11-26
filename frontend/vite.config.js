import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 2064,
    strictPort: true,
    // 启动后自动打开登录页，省去手动输入地址
    open: '/login',
    proxy: {
      // 后端就绪后，/api 请求转发到 Flask 服务
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
