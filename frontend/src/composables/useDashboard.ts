import { onMounted, ref } from 'vue'
import { getDashboardSummary, getRecentStudySessions } from '../api/dashboard'
import type { DashboardSummary } from '../api/dashboard'
import { getKnowledgeBaseStats, getStatsOverview, getStatsTrends } from '../api/stats'
import type { KnowledgeBaseStats, StatsOverview, TrendItem } from '../api/stats'
import { getTodayReviewOverview } from '../api/review'
import type { TodayReviewOverview } from '../api/review'
import type { StudySession } from '../api/studySession'

const EMPTY_SUMMARY: DashboardSummary = {
  knowledge_base_count: 0,
  material_count: 0,
  knowledge_point_count: 0,
  question_count: 0,
  wrong_question_count: 0,
  audio_count: 0,
}

export const dashboardStats = [
  { key: 'knowledge_base_count', label: '知识库', icon: '📚', color: 0, path: '/knowledge-bases' },
  { key: 'material_count', label: '学习资料', icon: '📄', color: 1, path: '/materials/import' },
  { key: 'knowledge_point_count', label: '知识点', icon: '🧠', color: 2, path: '/knowledge-points' },
  { key: 'question_count', label: '练习题', icon: '✅', color: 3, path: '/practice' },
  { key: 'wrong_question_count', label: '错题', icon: '📌', color: 4, path: '/wrong-questions' },
  { key: 'audio_count', label: '音频', icon: '🎧', color: 5, path: '/audio' },
] as const

export type DashboardStat = (typeof dashboardStats)[number]

export function useDashboard() {
  const summary = ref<DashboardSummary | null>(null)
  const loading = ref(true)
  const v2Stats = ref<StatsOverview | null>(null)
  const v2Loading = ref(true)
  const kbStats = ref<KnowledgeBaseStats[]>([])
  const kbLoading = ref(true)
  const trends = ref<TrendItem[]>([])
  const trendsLoading = ref(true)
  const recentSessions = ref<StudySession[]>([])
  const sessionsLoading = ref(true)
  const reviewOverview = ref<TodayReviewOverview | null>(null)
  const reviewLoading = ref(true)

  async function fetchSummary() {
    try {
      summary.value = await getDashboardSummary()
    } catch {
      summary.value = EMPTY_SUMMARY
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

  async function fetchRecentSessions() {
    try {
      recentSessions.value = await getRecentStudySessions(5)
    } catch {
      recentSessions.value = []
    } finally {
      sessionsLoading.value = false
    }
  }

  async function fetchReviewOverview() {
    try {
      reviewOverview.value = await getTodayReviewOverview({ limit: 5 })
    } catch {
      reviewOverview.value = null
    } finally {
      reviewLoading.value = false
    }
  }

  function refresh() {
    fetchSummary()
    fetchV2Stats()
    fetchKbStats()
    fetchTrends()
    fetchRecentSessions()
    fetchReviewOverview()
  }

  onMounted(refresh)

  return {
    summary,
    loading,
    v2Stats,
    v2Loading,
    kbStats,
    kbLoading,
    trends,
    trendsLoading,
    recentSessions,
    sessionsLoading,
    reviewOverview,
    reviewLoading,
    stats: dashboardStats,
    fetchV2Stats,
  }
}
