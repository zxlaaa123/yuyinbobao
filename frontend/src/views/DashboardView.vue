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
  gap: 24px;
}

/* Hero */
.hero-card {
  background: linear-gradient(135deg, rgba(79, 124, 255, 0.95), rgba(124, 58, 237, 0.92));
  color: #fff;
  border-radius: 24px;
  padding: 40px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 18px 45px rgba(79, 124, 255, 0.25);
}

.hero-card::after {
  content: "";
  position: absolute;
  width: 300px;
  height: 300px;
  right: -92px;
  top: -94px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}

.hero-card::before {
  content: "";
  position: absolute;
  width: 180px;
  height: 180px;
  right: 90px;
  bottom: -80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.13);
}

.hero-card > * {
  position: relative;
  z-index: 1;
}

.hero-card h3 {
  font-size: 26px;
  letter-spacing: -0.03em;
  margin: 0 0 12px;
  color: #fff;
}

.hero-card p {
  opacity: 0.92;
  line-height: 1.7;
  margin: 0 0 20px;
  font-size: 15px;
  max-width: 500px;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.hero-actions .el-button {
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 600;
}

.hero-actions .el-button--primary {
  background: #fff;
  color: #4f7cff;
  border-color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.hero-actions .el-button:not(.el-button--primary) {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(120px, 1fr));
  gap: 16px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
  box-shadow: 0 4px 12px rgba(25, 36, 70, 0.06);
}

.stat-card:hover {
  box-shadow: 0 8px 24px rgba(25, 36, 70, 0.12);
  transform: translateY(-2px);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: #edf3ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  font-size: 20px;
}

.stat-card.color-0 .stat-icon { background: #edf3ff; }
.stat-card.color-1 .stat-icon { background: #f3ecff; }
.stat-card.color-2 .stat-icon { background: #e9fbf5; }
.stat-card.color-3 .stat-icon { background: #fff8e7; }
.stat-card.color-4 .stat-icon { background: #fff0f0; }
.stat-card.color-5 .stat-icon { background: #edf3ff; }

.stat-value {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: #182033;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #667085;
}

/* V2 学习统计 */
.v2-stats {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(25, 36, 70, 0.06);
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
  color: #182033;
}

.loading-text {
  font-size: 13px;
  color: #667085;
}

.error-text {
  font-size: 13px;
  color: #a61b1b;
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
  background: #f8fbff;
  border: 1px solid #e6eaf2;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
}

.v2-label {
  font-size: 13px;
  color: #667085;
  margin-bottom: 8px;
}

.v2-value {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: #182033;
  margin-bottom: 4px;
}

.v2-value.accent-red {
  color: #dc2626;
}

.v2-value.accent-green {
  color: #087a59;
}

.v2-sub {
  font-size: 12px;
  color: #667085;
}

.v2-sub.error {
  color: #dc2626;
}

.v2-empty {
  text-align: center;
  padding: 32px 0;
  color: #667085;
  font-size: 14px;
}

/* 知识库掌握度 */
.kb-mastery-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.kb-mastery-card {
  background: #f8fbff;
  border: 1px solid #e6eaf2;
  border-radius: 12px;
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
  color: #182033;
}

.kb-mastery-value {
  font-size: 18px;
  font-weight: 800;
}

.kb-mastery-value.good { color: #087a59; }
.kb-mastery-value.medium { color: #a06000; }
.kb-mastery-value.low { color: #dc2626; }

.kb-mastery-bar {
  height: 8px;
  background: #e6eaf2;
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
  color: #667085;
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
  background: linear-gradient(180deg, #4f7cff, #c7d2fe);
  border-radius: 4px 4px 0 0;
  min-height: 4px;
}

.trend-answers {
  font-size: 12px;
  font-weight: 600;
  color: #182033;
}

.trend-label {
  font-size: 11px;
  color: #667085;
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
