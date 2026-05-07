<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { checkHealth } from './api/health'

const backendStatus = ref<'loading' | 'ok' | 'error'>('loading')

async function fetchHealth() {
  try {
    await checkHealth()
    backendStatus.value = 'ok'
  } catch {
    backendStatus.value = 'error'
  }
}

onMounted(() => {
  fetchHealth()
})
</script>

<template>
  <div class="page">
    <!-- 顶部状态条 -->
    <div class="top-bar">
      <div class="status-pill" :class="backendStatus">
        <span class="dot"></span>
        <span v-if="backendStatus === 'loading'">正在连接后端...</span>
        <span v-else-if="backendStatus === 'ok'">后端连接正常 · 本地模式</span>
        <span v-else>后端连接失败，请确认后端服务是否启动</span>
      </div>
    </div>

    <!-- 主内容 -->
    <div class="main-content">
      <div class="hero-card">
        <h1>AI 知识点学习与音频播报系统</h1>
        <p>本地学习辅助工具</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24px 30px 42px;
}

/* 顶部状态条 */
.top-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 24px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 99px;
  padding: 8px 14px;
  font-size: 13px;
  white-space: nowrap;
}

.status-pill.ok {
  background: #e9fbf5;
  border: 1px solid #c8f4e4;
  color: #087a59;
}

.status-pill.error {
  background: #fff0f0;
  border: 1px solid #ffd1d1;
  color: #a61b1b;
}

.status-pill.loading {
  background: #fff8e7;
  border: 1px solid #ffe7b8;
  color: #a06000;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-pill.ok .dot {
  background: #13b981;
  box-shadow: 0 0 0 6px rgba(19, 185, 129, 0.12);
}

.status-pill.error .dot {
  background: #ef4444;
  box-shadow: 0 0 0 6px rgba(239, 68, 68, 0.12);
}

.status-pill.loading .dot {
  background: #f59e0b;
  box-shadow: 0 0 0 6px rgba(245, 158, 11, 0.12);
  animation: pulse 1.2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* 主内容居中 */
.main-content {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 100px);
}

.hero-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 24px;
  box-shadow: 0 18px 45px rgba(25, 36, 70, 0.09);
  padding: 60px 48px;
  text-align: center;
  max-width: 560px;
  width: 100%;
}

.hero-card h1 {
  font-size: 28px;
  letter-spacing: -0.04em;
  margin: 0 0 12px;
  background: linear-gradient(135deg, #4f7cff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-card p {
  margin: 0;
  color: #667085;
  font-size: 16px;
}
</style>
