<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardSummary } from '../api/dashboard'
import type { DashboardSummary } from '../api/dashboard'
import { getStatsOverview, getKnowledgeBaseStats, getStatsTrends } from '../api/stats'
import type { StatsOverview, KnowledgeBaseStats, TrendItem } from '../api/stats'

const router = useRouter()
const summary = ref<DashboardSummary | null>(null)
const loading = ref(true)
const v2Stats = ref<StatsOverview | null>(null)
const v2Loading = ref(true)
const kbStats = ref<KnowledgeBaseStats[]>([])
const kbLoading = ref(true)
const trends = ref<TrendItem[]>([])
const trendsLoading = ref(true)

const stats = [
  { key: 'knowledge_base_count', label: '知识库', icon: '📚', color: 0 },
  { key: 'material_count', label: '学习资料', icon: '📄', color: 1 },
  { key: 'knowledge_point_count', label: '知识点', icon: '🧠', color: 2 },
  { key: 'question_count', label: '练习题', icon: '✅', color: 3 },
  { key: 'wrong_question_count', label: '错题', icon: '📌', color: 4 },
  { key: 'audio_count', label: '音频', icon: '🎧', color: 5 },
]

async function fetchSummary() {
  try {
    summary.value = await getDashboardSummary()
  } catch {
    summary.value = {
      knowledge_base_count: 0,
      material_count: 0,
      knowledge_point_count: 0,
      question_count: 0,
      wrong_question_count: 0,
      audio_count: 0,
    }
  } finally {
    loading.value = false
  }
}

async function fetchV2Stats() {
  try {
    v2Stats.value = await getStatsOverview()
  } catch {
    v2Stats.value = null
  } finally {
    v2Loading.value = false
  }
}

async function fetchKbStats() {
  try {
    kbStats.value = await getKnowledgeBaseStats()
  } catch {
    kbStats.value = []
  } finally {
    kbLoading.value = false
  }
}

async function fetchTrends() {
  try {
    trends.value = await getStatsTrends(7)
  } catch {
    trends.value = []
  } finally {
    trendsLoading.value = false
  }
}

function goTo(path: string) {
  router.push(path)
}

function formatTrendDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

onMounted(() => {
  fetchSummary()
  fetchV2Stats()
  fetchKbStats()
  fetchTrends()
})
</script>

<template>
  <div class="dashboard">
    <!-- Hero 区域 -->
    <div class="hero-card">
      <h3>把学习资料变成知识点、题目和音频</h3>
      <p>适合三支一扶、公基、时政、管理学、法律、经济和古文复习。粘贴资料后，系统可以自动提取知识点、练习题，并生成可播放的复习音频。</p>
      <div class="hero-actions">
        <el-button type="primary" @click="goTo('/materials/import')">开始导入资料</el-button>
        <el-button @click="goTo('/practice')">进入刷题练习</el-button>
      </div>
    </div>

    <!-- V1 统计卡片 -->
    <div class="stats-grid">
      <div
        v-for="stat in stats"
        :key="stat.key"
        class="stat-card"
        :class="'color-' + stat.color"
        @click="goTo(stat.key === 'knowledge_base_count' ? '/knowledge-bases' : stat.key === 'material_count' ? '/materials/import' : stat.key === 'knowledge_point_count' ? '/knowledge-points' : stat.key === 'question_count' ? '/practice' : stat.key === 'wrong_question_count' ? '/wrong-questions' : '/audio')"
      >
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-value">{{ loading ? '-' : summary ? summary[stat.key as keyof DashboardSummary] : 0 }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>

    <!-- V2 学习统计 -->
    <div class="v2-stats">
      <div class="section-header">
        <h3>📊 学习统计</h3>
        <span v-if="v2Loading" class="loading-text">加载中...</span>
        <span v-else-if="!v2Stats" class="error-text" @click="fetchV2Stats">加载失败，点击重试</span>
      </div>
      <div v-if="v2Stats && !v2Loading" class="v2-grid">
        <div class="v2-card">
          <div class="v2-label">今日练题</div>
          <div class="v2-value">{{ v2Stats.today_answers }}</div>
          <div class="v2-sub">正确 {{ v2Stats.today_correct }}</div>
        </div>
        <div class="v2-card">
          <div class="v2-label">总正确率</div>
          <div class="v2-value">{{ v2Stats.accuracy }}%</div>
          <div class="v2-sub">{{ v2Stats.total_correct }}/{{ v2Stats.total_answers }} 题</div>
        </div>
        <div class="v2-card" @click="goTo('/wrong-questions')" style="cursor: pointer">
          <div class="v2-label">待复习错题</div>
          <div class="v2-value accent-red">{{ v2Stats.pending_review }}</div>
          <div class="v2-sub">已掌握 {{ v2Stats.mastered_count }} / 共 {{ v2Stats.wrong_total }}</div>
        </div>
        <div class="v2-card" @click="goTo('/review')" style="cursor: pointer">
          <div class="v2-label">复习任务</div>
          <div class="v2-value">{{ v2Stats.review_pending }}</div>
          <div class="v2-sub">已完成 {{ v2Stats.review_completed }}</div>
        </div>
        <div class="v2-card">
          <div class="v2-label">知识点覆盖</div>
          <div class="v2-value">{{ v2Stats.kp_coverage }}%</div>
          <div class="v2-sub">{{ v2Stats.kp_with_questions }}/{{ v2Stats.total_knowledge_points }} 有题目</div>
        </div>
        <div class="v2-card" @click="goTo('/audio')" style="cursor: pointer">
          <div class="v2-label">音频</div>
          <div class="v2-value accent-green">{{ v2Stats.audio_success }}</div>
          <div v-if="v2Stats.audio_failed > 0" class="v2-sub error">失败 {{ v2Stats.audio_failed }}</div>
          <div v-else class="v2-sub">成功生成</div>
        </div>
      </div>
      <div v-else-if="!v2Stats && !v2Loading" class="v2-empty">
        暂无统计数据，开始刷题后这里会显示学习进度
      </div>
    </div>

    <!-- 知识库掌握度 -->
    <div class="v2-stats" v-if="!kbLoading && kbStats.length > 0">
      <div class="section-header">
        <h3>📚 知识库掌握度</h3>
      </div>
      <div class="kb-mastery-list">
        <div v-for="kb in kbStats" :key="kb.id" class="kb-mastery-card">
          <div class="kb-mastery-header">
            <span class="kb-name">{{ kb.name }}</span>
            <span class="kb-mastery-value" :class="kb.mastery >= 60 ? 'good' : kb.mastery >= 30 ? 'medium' : 'low'">
              {{ kb.mastery }}%
            </span>
          </div>
          <div class="kb-mastery-bar">
            <div class="kb-mastery-fill" :style="{ width: kb.mastery + '%' }"></div>
          </div>
          <div class="kb-mastery-detail">
            <span>正确率 {{ kb.accuracy }}%</span>
            <span>题目 {{ kb.question_count }}</span>
            <span>错题 {{ kb.pending_wrong }}</span>
            <span>复习 {{ kb.review_pending }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 7 天趋势 -->
    <div class="v2-stats" v-if="!trendsLoading && trends.length > 0">
      <div class="section-header">
        <h3>📈 7 天答题趋势</h3>
      </div>
      <div class="trends-grid">
        <div v-for="t in trends" :key="t.date" class="trend-card">
          <div class="trend-bar-wrap">
            <div class="trend-bar" :style="{ height: Math.max(t.answers * 3, 4) + 'px' }"></div>
          </div>
          <div class="trend-answers">{{ t.answers }}</div>
          <div class="trend-label">{{ formatTrendDate(t.date) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 26px;
}

/* Hero */
.hero-card {
  background:
    radial-gradient(circle at top right, rgba(230, 201, 152, 0.18), transparent 22%),
    linear-gradient(145deg, var(--dashboard-hero-start), var(--dashboard-hero-end));
  color: var(--dashboard-hero-text);
  border-radius: 30px;
  padding: 42px 42px 38px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 28px 56px rgba(30, 40, 30, 0.22);
  border: 1px solid rgba(255, 239, 205, 0.12);
}

.hero-card::after {
  content: "";
  position: absolute;
  width: 340px;
  height: 340px;
  right: -82px;
  top: -112px;
  border-radius: 50%;
  background: rgba(230, 201, 152, 0.12);
}

.hero-card::before {
  content: "";
  position: absolute;
  inset: auto 24px 24px auto;
  width: 180px;
  height: 46px;
  border-radius: 999px;
  background: rgba(255, 248, 236, 0.08);
  border: 1px solid rgba(255, 239, 205, 0.12);
}

.hero-card > * {
  position: relative;
  z-index: 1;
}

.hero-card h3 {
  font-size: 34px;
  letter-spacing: -0.03em;
  line-height: 1.18;
  margin: 0 0 14px;
  color: var(--dashboard-hero-text);
}

.hero-card p {
  opacity: 0.9;
  line-height: 1.8;
  margin: 0 0 24px;
  font-size: 15px;
  max-width: 620px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-actions .el-button {
  border-radius: 14px;
  padding: 11px 22px;
  font-weight: 700;
}

.hero-actions .el-button--primary {
  background: #f7e8cd;
  color: #193a2d;
  border-color: #f7e8cd;
  box-shadow: 0 10px 20px rgba(14, 22, 17, 0.16);
}

.hero-actions .el-button:not(.el-button--primary) {
  background: rgba(255, 248, 236, 0.08);
  color: var(--dashboard-hero-text);
  border-color: rgba(255, 239, 205, 0.24);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(120px, 1fr));
  gap: 18px;
}

.stat-card {
  background: var(--dashboard-stat-card);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 22px 18px;
  text-align: center;
  cursor: pointer;
  transition: box-shadow 0.18s, transform 0.18s, border-color 0.18s;
  box-shadow: 0 10px 22px rgba(74, 57, 28, 0.08);
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  box-shadow: 0 18px 34px rgba(74, 57, 28, 0.14);
  transform: translateY(-3px);
  border-color: var(--panel-accent);
}

.stat-card::after {
  content: "";
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, rgba(32, 79, 61, 0.85), rgba(176, 122, 42, 0.75));
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 15px;
  background: rgba(32, 79, 61, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  font-size: 20px;
  border: 1px solid rgba(32, 79, 61, 0.08);
}

.stat-card.color-0 .stat-icon { background: rgba(32, 79, 61, 0.08); }
.stat-card.color-1 .stat-icon { background: rgba(176, 122, 42, 0.10); }
.stat-card.color-2 .stat-icon { background: rgba(56, 118, 96, 0.10); }
.stat-card.color-3 .stat-icon { background: rgba(247, 232, 205, 0.92); }
.stat-card.color-4 .stat-icon { background: rgba(244, 221, 214, 0.96); }
.stat-card.color-5 .stat-icon { background: rgba(214, 231, 224, 0.92); }

.stat-value {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--text);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--muted);
}

/* V2 学习统计 */
.v2-stats {
  background: var(--dashboard-panel);
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 12px 24px rgba(74, 57, 28, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 18px;
  margin: 0;
  color: var(--text);
}

.loading-text {
  font-size: 13px;
  color: var(--muted);
}

.error-text {
  font-size: 13px;
  color: #a13e20;
  cursor: pointer;
}

.error-text:hover {
  text-decoration: underline;
}

.v2-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.v2-card {
  background: var(--dashboard-panel-alt);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 18px 16px;
  text-align: center;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75);
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.v2-card:hover {
  transform: translateY(-2px);
  border-color: var(--panel-accent);
  box-shadow: var(--shadow-soft);
}

.v2-label {
  font-size: 13px;
  color: var(--muted);
  margin-bottom: 8px;
}

.v2-value {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--text);
  margin-bottom: 4px;
}

.v2-value.accent-red {
  color: #b54b2f;
}

.v2-value.accent-green {
  color: #215844;
}

.v2-sub {
  font-size: 12px;
  color: var(--muted);
}

.v2-sub.error {
  color: #b54b2f;
}

.v2-empty {
  text-align: center;
  padding: 32px 0;
  color: var(--muted);
  font-size: 14px;
}

/* 知识库掌握度 */
.kb-mastery-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.kb-mastery-card {
  background: var(--dashboard-panel-alt);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.kb-mastery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kb-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.kb-mastery-value {
  font-size: 18px;
  font-weight: 800;
}

.kb-mastery-value.good { color: #215844; }
.kb-mastery-value.medium { color: #9b6821; }
.kb-mastery-value.low { color: #b54b2f; }

.kb-mastery-bar {
  height: 8px;
  background: var(--card-2);
  border-radius: 99px;
  overflow: hidden;
}

.kb-mastery-fill {
  height: 100%;
  background: linear-gradient(90deg, #4f7cff, #7c3aed);
  border-radius: 99px;
  transition: width 0.3s;
}

.kb-mastery-detail {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--muted);
}

/* 7 天趋势 */
.trends-grid {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  padding: 16px 0 4px;
}

.trend-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.trend-bar-wrap {
  height: 60px;
  display: flex;
  align-items: flex-end;
}

.trend-bar {
  width: 24px;
  background: linear-gradient(180deg, var(--green), var(--gold-soft));
  border-radius: 4px 4px 0 0;
  min-height: 4px;
}

.trend-answers {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
}

.trend-label {
  font-size: 11px;
  color: var(--muted);
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .v2-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .v2-grid {
    grid-template-columns: 1fr;
  }
}
</style>
