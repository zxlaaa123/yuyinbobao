<script setup lang="ts">
import type { DashboardSummary } from '../../api/dashboard'
import type { KnowledgeBaseStats, StatsOverview, TrendItem } from '../../api/stats'
import type { TodayReviewOverview } from '../../api/review'
import type { StudySession } from '../../api/studySession'
import type { DashboardStat } from '../../composables/useDashboard'
import { formatMonthDay, formatShortDateTime } from '../../utils/date'
import './dashboard.css'

defineProps<{
  summary: DashboardSummary | null
  loading: boolean
  stats: readonly DashboardStat[]
  v2Stats: StatsOverview | null
  v2Loading: boolean
  kbStats: KnowledgeBaseStats[]
  kbLoading: boolean
  trends: TrendItem[]
  trendsLoading: boolean
  recentSessions: StudySession[]
  sessionsLoading: boolean
  reviewOverview: TodayReviewOverview | null
  reviewLoading: boolean
}>()

const emit = defineEmits<{
  navigate: [path: string]
  retryStats: []
}>()

function getSessionTitle(item: StudySession): string {
  return item.knowledge_base_name || item.knowledge_point_title || '自由练习'
}
</script>

<template>
  <div class="dashboard">
    <section class="hero-card">
      <h3>把学习资料变成知识点、题目和音频</h3>
      <p>适合三支一扶、公基、时政、管理学、法律、经济和古文复习。粘贴资料后，系统可以自动提取知识点、练习题，并生成可播放的复习音频。</p>
      <div class="hero-actions">
        <el-button type="primary" @click="emit('navigate', '/materials/import')">开始导入资料</el-button>
        <el-button @click="emit('navigate', '/practice')">进入刷题练习</el-button>
        <el-button @click="emit('navigate', '/review')">开始今日复习</el-button>
      </div>
    </section>

    <section class="stats-grid">
      <button
        v-for="stat in stats"
        :key="stat.key"
        class="stat-card"
        :class="'color-' + stat.color"
        type="button"
        @click="emit('navigate', stat.path)"
      >
        <span class="stat-icon">{{ stat.icon }}</span>
        <span class="stat-value">{{ loading ? '-' : summary ? summary[stat.key] : 0 }}</span>
        <span class="stat-label">{{ stat.label }}</span>
      </button>
    </section>

    <section class="dashboard-panel">
      <div class="section-header">
        <h3>📊 学习统计</h3>
        <span v-if="v2Loading" class="loading-text">加载中...</span>
        <button v-else-if="!v2Stats" class="link-button error-text" type="button" @click="emit('retryStats')">加载失败，点击重试</button>
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
        <button class="v2-card" type="button" @click="emit('navigate', '/wrong-questions')">
          <div class="v2-label">待复习错题</div>
          <div class="v2-value accent-red">{{ v2Stats.pending_review }}</div>
          <div class="v2-sub">已掌握 {{ v2Stats.mastered_count }} / 共 {{ v2Stats.wrong_total }}</div>
        </button>
        <button class="v2-card" type="button" @click="emit('navigate', '/review')">
          <div class="v2-label">复习任务</div>
          <div class="v2-value">{{ v2Stats.review_pending }}</div>
          <div class="v2-sub">已完成 {{ v2Stats.review_completed }}</div>
        </button>
        <div class="v2-card">
          <div class="v2-label">知识点覆盖</div>
          <div class="v2-value">{{ v2Stats.kp_coverage }}%</div>
          <div class="v2-sub">{{ v2Stats.kp_with_questions }}/{{ v2Stats.total_knowledge_points }} 有题目</div>
        </div>
        <button class="v2-card" type="button" @click="emit('navigate', '/audio')">
          <div class="v2-label">音频</div>
          <div class="v2-value accent-green">{{ v2Stats.audio_success }}</div>
          <div v-if="v2Stats.audio_failed > 0" class="v2-sub error">失败 {{ v2Stats.audio_failed }}</div>
          <div v-else class="v2-sub">成功生成</div>
        </button>
      </div>
      <div v-else-if="!v2Stats && !v2Loading" class="v2-empty">暂无统计数据，开始刷题后这里会显示学习进度</div>
    </section>

    <section class="dashboard-panel">
      <div class="section-header">
        <h3>🗓️ 今日复习概览</h3>
        <span v-if="reviewLoading" class="loading-text">加载中...</span>
      </div>
      <div v-if="reviewOverview && !reviewLoading" class="v2-grid review-grid">
        <div class="v2-card"><div class="v2-label">今日待复习</div><div class="v2-value">{{ reviewOverview.due_count }}</div></div>
        <div class="v2-card"><div class="v2-label">逾期复习</div><div class="v2-value accent-red">{{ reviewOverview.overdue_count }}</div></div>
        <div class="v2-card"><div class="v2-label">薄弱知识点</div><div class="v2-value">{{ reviewOverview.weak_count }}</div></div>
        <button class="v2-card review-action-card" type="button" @click="emit('navigate', '/review')">
          <div class="v2-label">复习入口</div>
          <div class="v2-value accent-green">开始</div>
          <div class="v2-sub">进入复习计划页</div>
        </button>
      </div>
      <div v-if="reviewOverview && !reviewLoading && reviewOverview.items.length > 0" class="review-list">
        <div v-for="item in reviewOverview.items" :key="item.knowledge_point_id" class="review-item">
          <div class="review-item-main">
            <div class="review-item-title">{{ item.title }}</div>
            <div class="review-item-summary">{{ item.summary || '暂无摘要' }}</div>
          </div>
          <div class="review-item-meta">
            <el-tag size="small" :type="item.is_overdue ? 'danger' : 'success'">{{ item.is_overdue ? '逾期' : '今日' }}</el-tag>
            <span>掌握度 {{ item.mastery_level }}%</span>
          </div>
        </div>
      </div>
      <div v-else-if="!reviewLoading" class="v2-empty">今日暂无待复习知识点</div>
    </section>

    <section v-if="!kbLoading && kbStats.length > 0" class="dashboard-panel">
      <div class="section-header"><h3>📚 知识库掌握度</h3></div>
      <div class="kb-mastery-list">
        <div v-for="kb in kbStats" :key="kb.id" class="kb-mastery-card">
          <div class="kb-mastery-header">
            <span class="kb-name">{{ kb.name }}</span>
            <span class="kb-mastery-value" :class="kb.mastery >= 60 ? 'good' : kb.mastery >= 30 ? 'medium' : 'low'">{{ kb.mastery }}%</span>
          </div>
          <div class="kb-mastery-bar"><div class="kb-mastery-fill" :style="{ width: kb.mastery + '%' }"></div></div>
          <div class="kb-mastery-detail">
            <span>正确率 {{ kb.accuracy }}%</span>
            <span>题目 {{ kb.question_count }}</span>
            <span>错题 {{ kb.pending_wrong }}</span>
            <span>复习 {{ kb.review_pending }}</span>
          </div>
        </div>
      </div>
    </section>

    <section v-if="!trendsLoading && trends.length > 0" class="dashboard-panel">
      <div class="section-header"><h3>📈 7 天答题趋势</h3></div>
      <div class="trends-grid">
        <div v-for="t in trends" :key="t.date" class="trend-card">
          <div class="trend-bar-wrap"><div class="trend-bar" :style="{ height: Math.max(t.answers * 3, 4) + 'px' }"></div></div>
          <div class="trend-answers">{{ t.answers }}</div>
          <div class="trend-label">{{ formatMonthDay(t.date) }}</div>
        </div>
      </div>
    </section>

    <section class="dashboard-panel">
      <div class="section-header">
        <h3>最近学习记录</h3>
        <span v-if="sessionsLoading" class="loading-text">加载中...</span>
      </div>
      <div v-if="!sessionsLoading && recentSessions.length > 0" class="session-list">
        <div v-for="item in recentSessions" :key="item.id" class="session-card">
          <div class="session-main">
            <div class="session-title">{{ getSessionTitle(item) }}</div>
            <div class="session-time">{{ formatShortDateTime(item.started_at) }}</div>
          </div>
          <div class="session-metrics">
            <span>{{ item.correct_count }}/{{ item.total_count }} 题</span>
            <strong>{{ item.accuracy_rate }}%</strong>
          </div>
        </div>
      </div>
      <div v-else-if="!sessionsLoading" class="v2-empty">暂无学习记录，完成一次刷题后这里会显示最近会话</div>
    </section>
  </div>
</template>
