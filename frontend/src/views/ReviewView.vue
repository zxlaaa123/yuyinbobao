<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getReviewTasks,
  generateReviewTasks,
  completeReviewTask,
  snoozeReviewTask,
  deleteReviewTask,
} from '../api/review'
import { generateDailyReviewAudio } from '../api/audio'
import type { ReviewTask } from '../api/review'
import { useRouter } from 'vue-router'
import { getErrorMessage, isUserCanceled } from '../utils/error'

const router = useRouter()
const tasks = ref<ReviewTask[]>([])
const loading = ref(false)
const generateLoading = ref(false)
const audioLoading = ref(false)
const filterStatus = ref<string>('pending')

const filteredTasks = computed(() => {
  if (!filterStatus.value) return tasks.value
  return tasks.value.filter((t) => t.status === filterStatus.value)
})

const pendingCount = computed(() => tasks.value.filter((t) => t.status === 'pending').length)
const completedCount = computed(() => tasks.value.filter((t) => t.status === 'completed').length)
const totalCount = computed(() => tasks.value.length)

async function fetchTasks() {
  loading.value = true
  try {
    tasks.value = await getReviewTasks()
  } catch {
    ElMessage.error('加载复习任务失败')
  } finally {
    loading.value = false
  }
}

async function handleGenerate() {
  generateLoading.value = true
  try {
    const result = await generateReviewTasks(30)
    if (result.created > 0) {
      ElMessage.success(`已生成 ${result.created} 个复习任务`)
    } else {
      ElMessage.info(result.message || '没有新任务生成')
    }
    await fetchTasks()
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '生成失败'))
  } finally {
    generateLoading.value = false
  }
}

async function handleGenerateAudio() {
  audioLoading.value = true
  try {
    const result = await generateDailyReviewAudio()
    ElMessage.success(`每日复习音频生成成功（${result.knowledge_point_count} 个知识点）`)
  } catch (e) {
    const msg = getErrorMessage(e, '生成失败')
    ElMessage.error(msg)
  } finally {
    audioLoading.value = false
  }
}

async function handleComplete(task: ReviewTask, quality: string) {
  try {
    await completeReviewTask(task.id, quality)
    ElMessage.success('已完成')
    await fetchTasks()
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '操作失败'))
  }
}

async function handleSnooze(task: ReviewTask) {
  try {
    await snoozeReviewTask(task.id, 24)
    ElMessage.success('已推迟 24 小时')
    await fetchTasks()
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '操作失败'))
  }
}

async function handleDelete(task: ReviewTask) {
  try {
    await ElMessageBox.confirm('确定要删除这个复习任务吗？', '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteReviewTask(task.id)
    ElMessage.success('任务已删除')
    await fetchTasks()
  } catch (e) {
    if (!isUserCanceled(e)) {
      ElMessage.error(getErrorMessage(e, '删除失败'))
    }
  }
}

function sourceLabel(source: string): string {
  const map: Record<string, string> = {
    wrong_question: '错题复习',
    importance_high: '重点知识点',
    new_knowledge: '新知识点',
  }
  return map[source] || source
}

function difficultyLabel(difficulty: string): string {
  const map: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难',
  }
  return map[difficulty] || difficulty
}

function formatDate(d: string | null): string {
  if (!d) return '-'
  return new Date(d).toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function goDetail(kpId: number) {
  router.push(`/knowledge-points/${kpId}`)
}

onMounted(fetchTasks)
</script>

<template>
  <div class="page">
    <!-- 顶部 -->
    <div class="header">
      <div class="title">
        <h2>复习计划</h2>
        <p>基于错题和知识点重要性生成复习任务。</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" :loading="generateLoading" @click="handleGenerate">
          生成今日复习
        </el-button>
        <el-button :loading="audioLoading" @click="handleGenerateAudio">
          生成每日复习音频
        </el-button>
      </div>
    </div>

    <!-- 统计摘要 -->
    <div class="summary-row">
      <div class="summary-card">
        <span class="s-label">待复习</span>
        <span class="s-value accent-red">{{ pendingCount }}</span>
      </div>
      <div class="summary-card">
        <span class="s-label">已完成</span>
        <span class="s-value accent-green">{{ completedCount }}</span>
      </div>
      <div class="summary-card">
        <span class="s-label">全部任务</span>
        <span class="s-value">{{ totalCount }}</span>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="filters">
      <el-radio-group v-model="filterStatus">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="pending">待复习</el-radio-button>
        <el-radio-button value="completed">已完成</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && filteredTasks.length === 0" class="empty">
      <div class="empty-icon">📋</div>
      <p v-if="filterStatus === 'pending'">暂无待复习任务，点击"生成今日复习"开始</p>
      <p v-else-if="filterStatus === 'completed'">暂无已完成任务</p>
      <p v-else>暂无复习任务</p>
    </div>

    <!-- 任务列表 -->
    <div v-else-if="!loading" class="task-list">
      <div
        v-for="task in filteredTasks"
        :key="task.id"
        class="task-card"
        :class="{ completed: task.status === 'completed' }"
      >
        <div class="task-main">
          <div class="task-info">
            <div class="task-title" @click="goDetail(task.knowledge_point_id)">
              {{ task.kp_title || '知识点 #' + task.knowledge_point_id }}
            </div>
            <div class="task-badges">
              <span class="badge source">{{ sourceLabel(task.source) }}</span>
              <span class="badge difficulty" :class="task.difficulty">{{ difficultyLabel(task.difficulty) }}</span>
              <span class="badge status" :class="task.status">{{ task.status === 'completed' ? '已完成' : '待复习' }}</span>
            </div>
          </div>
          <div class="task-summary" v-if="task.kp_summary">{{ task.kp_summary }}</div>
          <div class="task-meta">
            <span>创建于 {{ formatDate(task.created_at) }}</span>
            <span v-if="task.scheduled_at"> · 计划 {{ formatDate(task.scheduled_at) }}</span>
            <span v-if="task.snooze_count > 0"> · 推迟 {{ task.snooze_count }} 次</span>
          </div>
        </div>

        <div class="task-actions" v-if="task.status === 'pending'">
          <el-button-group class="quality-buttons">
            <el-button size="small" :loading="false" @click="handleComplete(task, 'again')">Again</el-button>
            <el-button size="small" @click="handleComplete(task, 'hard')">Hard</el-button>
            <el-button size="small" type="success" @click="handleComplete(task, 'good')">Good</el-button>
            <el-button size="small" type="primary" @click="handleComplete(task, 'easy')">Easy</el-button>
          </el-button-group>
          <el-button size="small" @click="handleSnooze(task)">稍后</el-button>
          <el-button size="small" type="danger" @click="handleDelete(task)">删除</el-button>
        </div>

        <div class="task-actions" v-else>
          <span class="completed-text">完成于 {{ formatDate(task.completed_at) }}</span>
          <el-button size="small" type="danger" @click="handleDelete(task)">删除</el-button>
        </div>
      </div>
    </div>

    <!-- loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 30px 42px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.title h2 {
  font-size: 24px;
  margin: 0;
}

.title p {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 14px;
}

/* 统计摘要 */
.summary-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card {
  flex: 1;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow-soft);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.s-label {
  font-size: 13px;
  color: var(--muted);
}

.s-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--text);
}

.s-value.accent-red {
  color: var(--danger);
}

.s-value.accent-green {
  color: var(--green);
}

/* 筛选 */
.filters {
  margin-bottom: 20px;
}

/* 空状态 */
.empty {
  text-align: center;
  padding: 60px 0;
  color: var(--muted);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty p {
  font-size: 15px;
  margin: 0;
}

/* 任务列表 */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow-soft);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card.completed {
  opacity: 0.7;
}

.task-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.task-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--green);
  cursor: pointer;
  margin-bottom: 4px;
}

.task-title:hover {
  text-decoration: underline;
}

.task-summary {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-badges {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 600;
}

.badge.source {
  background: var(--panel-strong);
  color: var(--green);
}

.badge.difficulty.easy {
  background: var(--success-bg);
  color: var(--success-text);
}

.badge.difficulty.medium {
  background: var(--warning-bg);
  color: var(--warning-text);
}

.badge.difficulty.hard {
  background: var(--danger-bg);
  color: var(--danger-text);
}

.badge.status.pending {
  background: var(--warning-bg);
  color: var(--warning-text);
}

.badge.status.completed {
  background: var(--success-bg);
  color: var(--success-text);
}

.task-meta {
  font-size: 12px;
  color: var(--muted);
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.quality-buttons {
  display: flex;
}

.completed-text {
  font-size: 12px;
  color: var(--muted);
  flex: 1;
}

/* loading */
.loading-state {
  text-align: center;
  padding: 40px 0;
  color: var(--muted);
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--line);
  border-top-color: var(--green);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
