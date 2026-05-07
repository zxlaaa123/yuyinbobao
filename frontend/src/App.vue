<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { checkHealth } from './api/health'
import KnowledgeBaseView from './views/KnowledgeBaseView.vue'
import MaterialImportView from './views/MaterialImportView.vue'

const backendStatus = ref<'loading' | 'ok' | 'error'>('loading')
const currentView = ref('dashboard')

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

const menuItems = [
  { key: 'dashboard', label: '首页', icon: '🏠' },
  { key: 'knowledge-bases', label: '知识库', icon: '📚' },
  { key: 'materials/import', label: '资料导入', icon: '📝' },
]
</script>

<template>
  <div class="app-layout">
    <!-- 左侧菜单 -->
    <aside class="sidebar">
      <div class="brand">
        <div class="logo">AI</div>
        <div class="brand-text">
          <h1>AI Study Cast</h1>
          <p>知识点学习与音频播报系统</p>
        </div>
      </div>
      <nav class="nav">
        <button
          v-for="item in menuItems"
          :key="item.key"
          :class="{ active: currentView === item.key }"
          @click="currentView = item.key"
        >
          <span class="icon">{{ item.icon }}</span>
          {{ item.label }}
        </button>
      </nav>
    </aside>

    <!-- 右侧内容 -->
    <main class="main">
      <!-- 顶部状态条 -->
      <div class="top-bar">
        <div class="status-pill" :class="backendStatus">
          <span class="dot"></span>
          <span v-if="backendStatus === 'loading'">正在连接后端...</span>
          <span v-else-if="backendStatus === 'ok'">后端连接正常 · 本地模式</span>
          <span v-else>后端连接失败，请确认后端服务是否启动</span>
        </div>
      </div>

      <!-- 首页 -->
      <div v-if="currentView === 'dashboard'" class="dashboard">
        <div class="hero-card">
          <h1>AI 知识点学习与音频播报系统</h1>
          <p>本地学习辅助工具</p>
        </div>
      </div>

      <!-- 知识库页面 -->
      <KnowledgeBaseView v-else-if="currentView === 'knowledge-bases'" />

      <!-- 资料导入页面 -->
      <MaterialImportView v-else-if="currentView === 'materials/import'" />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
}

/* 左侧菜单 */
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(18px);
  border-right: 1px solid #e6eaf2;
  padding: 22px 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px 8px 18px;
  border-bottom: 1px solid #e6eaf2;
}

.logo {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  background: linear-gradient(135deg, #4f7cff, #7c3aed);
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 900;
  font-size: 16px;
  box-shadow: 0 12px 26px rgba(79, 124, 255, 0.26);
}

.brand-text h1 {
  font-size: 16px;
  margin: 0;
}

.brand-text p {
  font-size: 12px;
  color: #667085;
  margin: 4px 0 0;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav button {
  border: 0;
  background: transparent;
  color: #667085;
  font-size: 15px;
  text-align: left;
  padding: 12px 14px;
  border-radius: 15px;
  cursor: pointer;
  transition: 0.16s;
  display: flex;
  gap: 10px;
  align-items: center;
}

.nav button:hover {
  background: #edf3ff;
  color: #315de6;
  transform: translateX(2px);
}

.nav button.active {
  background: linear-gradient(135deg, #4f7cff, #6b8dff);
  color: #fff;
  box-shadow: 0 12px 24px rgba(79, 124, 255, 0.24);
}

.icon {
  font-size: 16px;
}

/* 右侧内容 */
.main {
  padding: 24px 30px 42px;
  min-width: 0;
}

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

/* 首页 */
.dashboard {
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
