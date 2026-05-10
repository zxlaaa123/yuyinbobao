<script setup lang="ts">
import { useRouter } from 'vue-router'
import DashboardSections from '../components/dashboard/DashboardSections.vue'
import { useDashboard } from '../composables/useDashboard'

const router = useRouter()
const dashboard = useDashboard()

function goTo(path: string) {
  router.push(path)
}
</script>

<template>
  <DashboardSections
    :summary="dashboard.summary.value"
    :loading="dashboard.loading.value"
    :stats="dashboard.stats"
    :v2-stats="dashboard.v2Stats.value"
    :v2-loading="dashboard.v2Loading.value"
    :kb-stats="dashboard.kbStats.value"
    :kb-loading="dashboard.kbLoading.value"
    :trends="dashboard.trends.value"
    :trends-loading="dashboard.trendsLoading.value"
    :recent-sessions="dashboard.recentSessions.value"
    :sessions-loading="dashboard.sessionsLoading.value"
    :review-overview="dashboard.reviewOverview.value"
    :review-loading="dashboard.reviewLoading.value"
    @navigate="goTo"
    @retry-stats="dashboard.fetchV2Stats"
  />
</template>
