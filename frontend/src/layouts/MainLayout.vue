<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { checkHealth } from '../api/health'
import { searchLocal, type SearchResult } from '../api/search'
import { THEME_OPTIONS, applyTheme, getStoredTheme, type ThemeName } from '../utils/theme'

const router = useRouter()
const route = useRoute()
const backendStatus = ref<'loading' | 'ok' | 'error'>('loading')
const currentTheme = ref<ThemeName>(getStoredTheme())
const searchKeyword = ref('')
const searchResults = ref<SearchResult[]>([])
const searchLoading = ref(false)
const searchTouched = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | null = null

async function fetchHealth() {
  try {
    await checkHealth()
    backendStatus.value = 'ok'
  } catch {
    backendStatus.value = 'error'
  }
}

onMounted(() => {
  applyTheme(currentTheme.value)
  fetchHealth()
})

function handleThemeChange(theme: ThemeName) {
  currentTheme.value = theme
  applyTheme(theme)
}

function handleSearchInput() {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = setTimeout(runSearch, 300)
}

async function runSearch() {
  const keyword = searchKeyword.value.trim()
  searchTouched.value = Boolean(keyword)
  if (!keyword) {
    searchResults.value = []
    return
  }
  searchLoading.value = true
  try {
    const data = await searchLocal(keyword)
    searchResults.value = data.results
  } catch {
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}

function goSearchResult(item: SearchResult) {
  router.push(item.target_url)
  searchKeyword.value = ''
  searchResults.value = []
  searchTouched.value = false
}

function resultTypeLabel(type: SearchResult['type']) {
  return type === 'knowledge_point' ? '知识点' : '资料'
}

const menuItems = [
  { key: '/dashboard', label: '首页', icon: '🏠' },
  { key: '/knowledge-bases', label: '知识库', icon: '📚' },
  { key: '/materials/import', label: '资料导入', icon: '📝' },
  { key: '/knowledge-points', label: '知识点', icon: '🧠' },
  { key: '/practice', label: '刷题练习', icon: '✅' },
  { key: '/wrong-questions', label: '错题本', icon: '📌' },
  { key: '/review', label: '复习计划', icon: '🔄' },
  { key: '/audio', label: '音频播报', icon: '🎧' },
  { key: '/ai-call-logs', label: 'AI 日志', icon: '📊' },
  { key: '/settings', label: '设置', icon: '⚙️' },
]
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="brand">
        <div class="logo">AI</div>
        <div class="brand-text">
          <h1>AI Study Cast</h1>
          <p>知识点学习与音频播报系统</p>
        </div>
      </div>
      <div class="brand-note">
        <span class="note-chip">Study Engine</span>
        <p>把资料整理成知识点、题目、复习任务和音频卡片。</p>
      </div>
      <nav class="nav">
        <button
          v-for="item in menuItems"
          :key="item.key"
          :class="{ active: route.path === item.key || (item.key !== '/dashboard' && route.path.startsWith(item.key)) }"
          @click="router.push(item.key)"
        >
          <span class="icon">{{ item.icon }}</span>
          {{ item.label }}
        </button>
      </nav>
    </aside>

    <main class="main">
      <div class="top-bar">
        <div class="global-search">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索知识点或资料..."
            clearable
            @input="handleSearchInput"
            @clear="handleSearchInput"
            @keyup.enter="runSearch"
          />
          <div v-if="searchTouched" class="search-panel">
            <div v-if="searchLoading" class="search-empty">正在搜索...</div>
            <template v-else-if="searchResults.length > 0">
              <button
                v-for="item in searchResults"
                :key="`${item.type}-${item.id}`"
                class="search-item"
                @click="goSearchResult(item)"
              >
                <span class="search-type">{{ resultTypeLabel(item.type) }}</span>
                <span class="search-title">{{ item.title }}</span>
                <span class="search-summary">{{ item.summary || '暂无摘要' }}</span>
              </button>
            </template>
            <div v-else class="search-empty">没有找到相关结果</div>
          </div>
        </div>
        <div class="theme-switch">
          <span class="theme-label">配色</span>
          <div class="theme-buttons">
            <button
              v-for="theme in THEME_OPTIONS"
              :key="theme.key"
              class="theme-btn"
              :class="{ active: currentTheme === theme.key }"
              @click="handleThemeChange(theme.key)"
            >
              {{ theme.label }}
            </button>
          </div>
        </div>
        <div class="status-pill" :class="backendStatus">
          <span class="dot"></span>
          <span v-if="backendStatus === 'loading'">正在连接后端...</span>
          <span v-else-if="backendStatus === 'ok'">后端连接正常 · 本地模式</span>
          <span v-else>后端连接失败，请确认后端服务是否启动</span>
        </div>
      </div>

      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: grid;
  grid-template-columns: 290px 1fr;
  min-height: 100vh;
}

.sidebar {
  background:
    linear-gradient(180deg, var(--sidebar-bg-start), var(--sidebar-bg-end));
  border-right: 1px solid var(--line);
  box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.55);
  padding: 26px 18px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 100vh;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px 10px 18px;
  border-bottom: 1px solid var(--line);
}

.logo {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  background: linear-gradient(145deg, #204f3d, #133428);
  display: grid;
  place-items: center;
  color: #f7e8cd;
  font-weight: 900;
  font-size: 17px;
  box-shadow: 0 16px 28px rgba(30, 74, 58, 0.26);
  border: 1px solid rgba(255, 239, 205, 0.34);
}

.brand-text h1 {
  font-size: 18px;
  letter-spacing: -0.02em;
  margin: 0;
}

.brand-text p {
  font-size: 12px;
  color: var(--muted);
  margin: 4px 0 0;
}

.brand-note {
  margin: 0 8px;
  padding: 16px 16px 18px;
  border-radius: 20px;
  background: var(--sidebar-card);
  border: 1px solid var(--panel-accent);
  box-shadow: var(--shadow-soft);
}

.note-chip {
  display: inline-flex;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(32, 79, 61, 0.08);
  color: var(--green);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.brand-note p {
  margin: 12px 0 0;
  font-size: 13px;
  line-height: 1.7;
  color: var(--muted);
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav button {
  border: 0;
  background: transparent;
  color: #566052;
  font-size: 15px;
  text-align: left;
  padding: 14px 16px;
  border-radius: 18px;
  cursor: pointer;
  transition: 0.18s ease;
  display: flex;
  gap: 12px;
  align-items: center;
  position: relative;
}

.nav button:hover {
  background: var(--sidebar-hover);
  color: var(--green);
  transform: translateX(3px);
  box-shadow: var(--shadow-soft);
}

.nav button.active {
  background: linear-gradient(135deg, #204f3d, #2c654f);
  color: var(--sidebar-active-text);
  box-shadow: 0 16px 28px rgba(32, 79, 61, 0.26);
}

.nav button.active::after {
  content: "";
  position: absolute;
  right: 14px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--gold-soft);
  box-shadow: 0 0 0 5px rgba(230, 201, 152, 0.18);
}

.icon {
  font-size: 17px;
}

.main {
  padding: 30px 34px 48px;
  min-width: 0;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 26px;
  gap: 16px;
  flex-wrap: wrap;
}

.top-bar::before {
  content: "学习控制台";
  font-size: 13px;
  color: var(--muted);
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.global-search {
  position: relative;
  width: min(360px, 100%);
}

.search-panel {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 20;
  padding: 8px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fffaf0;
  box-shadow: 0 18px 40px rgba(31, 50, 40, 0.18);
  max-height: 360px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.search-panel::-webkit-scrollbar {
  width: 8px;
}

.search-panel::-webkit-scrollbar-track {
  background: rgba(32, 79, 61, 0.06);
  border-radius: 999px;
}

.search-panel::-webkit-scrollbar-thumb {
  background: rgba(32, 79, 61, 0.28);
  border-radius: 999px;
}

.search-item {
  width: 100%;
  border: 0;
  background: transparent;
  text-align: left;
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
  display: grid;
  gap: 4px;
}

.search-item:hover {
  background: var(--sidebar-hover);
}

.search-type {
  width: fit-content;
  padding: 2px 7px;
  border-radius: 999px;
  background: rgba(32, 79, 61, 0.08);
  color: var(--green);
  font-size: 12px;
  font-weight: 700;
}

.search-title {
  color: var(--text);
  font-size: 14px;
  font-weight: 700;
}

.search-summary {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.5;
}

.search-empty {
  padding: 14px 10px;
  color: var(--muted);
  font-size: 13px;
}

.theme-switch {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.theme-label {
  font-size: 12px;
  color: var(--muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.theme-buttons {
  display: inline-flex;
  gap: 8px;
  padding: 6px;
  border-radius: 999px;
  background: var(--sidebar-card);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-soft);
}

.theme-btn {
  border: 0;
  background: transparent;
  color: var(--muted);
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: 0.18s ease;
}

.theme-btn:hover {
  color: var(--text);
  background: rgba(255, 255, 255, 0.5);
}

.theme-btn.active {
  background: var(--green);
  color: #fef6e7;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 99px;
  padding: 10px 16px;
  font-size: 13px;
  white-space: nowrap;
  box-shadow: var(--shadow-soft);
}

.status-pill.ok {
  background: rgba(228, 243, 235, 0.95);
  border: 1px solid rgba(47, 111, 87, 0.18);
  color: #215844;
}

.status-pill.error {
  background: #fff3ee;
  border: 1px solid rgba(181, 80, 44, 0.18);
  color: #a13e20;
}

.status-pill.loading {
  background: #fbf2df;
  border: 1px solid rgba(176, 122, 42, 0.18);
  color: #8d6020;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-pill.ok .dot {
  background: #2f6f57;
  box-shadow: 0 0 0 6px rgba(47, 111, 87, 0.12);
}

.status-pill.error .dot {
  background: #c25539;
  box-shadow: 0 0 0 6px rgba(194, 85, 57, 0.12);
}

.status-pill.loading .dot {
  background: var(--gold);
  box-shadow: 0 0 0 6px rgba(176, 122, 42, 0.12);
  animation: pulse 1.2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@media (max-width: 980px) {
  .app-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: relative;
    height: auto;
    min-height: auto;
  }

  .top-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
