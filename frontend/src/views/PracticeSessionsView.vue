<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPracticeSession, getPracticeSessions } from '../api/practiceSession'
import type { PracticeSession } from '../api/practiceSession'
import { getErrorMessage } from '../utils/error'
import { formatDateTime } from '../utils/date'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const list = ref<PracticeSession[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const detailLoading = ref(false)
const detail = ref<PracticeSession | null>(null)

function formatTime(value?: string | null) {
  return formatDateTime(value)
}

function formatDuration(seconds?: number | null) {
  const totalSec = Math.max(0, seconds || 0)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  return min > 0 ? `${min} 分 ${sec} 秒` : `${sec} 秒`
}

function questionTypeLabel(type?: string | null) {
  const map: Record<string, string> = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    true_false: '判断题',
    fill_blank: '填空题',
    short_answer: '简答题',
  }
  return map[type || ''] || type || '-'
}

async function loadList() {
  loading.value = true
  try {
    const data = await getPracticeSessions({ page: page.value, page_size: pageSize.value })
    list.value = data.items
    total.value = data.total
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '加载练习历史失败'))
  } finally {
    loading.value = false
  }
}

async function loadDetail(sessionId: number) {
  detailLoading.value = true
  try {
    detail.value = await getPracticeSession(sessionId)
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '加载会话详情失败'))
  } finally {
    detailLoading.value = false
  }
}

function openDetail(item: PracticeSession) {
  router.push(`/practice-sessions/${item.id}`)
}

async function handlePageChange(newPage: number) {
  page.value = newPage
  await loadList()
}

onMounted(async () => {
  const maybeId = Number(route.params.id)
  if (Number.isInteger(maybeId) && maybeId > 0) {
    await loadDetail(maybeId)
  } else {
    await loadList()
  }
})
</script>

<template>
  <div class="page">
    <div class="header">
      <div class="title">
        <h2>练习历史</h2>
        <p>查看每次练习的统计结果、错题和薄弱知识点。</p>
      </div>
      <div class="actions">
        <el-button @click="router.push('/practice')">返回练习</el-button>
      </div>
    </div>

    <div v-if="detailLoading || loading" class="card loading">加载中...</div>

    <div v-else-if="detail" class="card">
      <div class="detail-head">
        <h3>{{ detail.title || `练习会话 #${detail.id}` }}</h3>
        <span class="time">{{ formatTime(detail.created_at) }}</span>
      </div>
      <div class="summary-grid">
        <div class="summary-item">
          <b>{{ detail.total_count }}</b>
          <span>总题数</span>
        </div>
        <div class="summary-item ok">
          <b>{{ detail.correct_count }}</b>
          <span>正确</span>
        </div>
        <div class="summary-item bad">
          <b>{{ detail.wrong_count }}</b>
          <span>错误</span>
        </div>
        <div class="summary-item rate">
          <b>{{ detail.accuracy_rate }}%</b>
          <span>正确率</span>
        </div>
        <div class="summary-item">
          <b>{{ formatDuration(detail.duration_seconds) }}</b>
          <span>耗时</span>
        </div>
      </div>
      <div class="meta">
        <div>薄弱知识点：{{ detail.weak_knowledge_point_ids.length }}</div>
        <div>错题：{{ detail.wrong_question_ids.length }}</div>
      </div>
      <p v-if="detail.suggestion" class="suggestion">{{ detail.suggestion }}</p>

      <el-divider />

      <el-table :data="detail.items || []" stripe>
        <el-table-column prop="question_type" label="题型" width="110">
          <template #default="{ row }">{{ questionTypeLabel(row.question_type) }}</template>
        </el-table-column>
        <el-table-column prop="stem" label="题目" min-width="320" />
        <el-table-column label="你的答案" min-width="120">
          <template #default="{ row }">{{ row.user_answer || '-' }}</template>
        </el-table-column>
        <el-table-column label="正确答案" min-width="120">
          <template #default="{ row }">{{ row.correct_answer || '-' }}</template>
        </el-table-column>
        <el-table-column label="结果" width="90">
          <template #default="{ row }">
            <span :class="row.is_correct ? 'ok-text' : 'bad-text'">{{ row.is_correct ? '正确' : '错误' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="actions">
        <el-button @click="router.push('/practice-sessions')">返回列表</el-button>
      </div>
    </div>

    <div v-else class="card">
      <el-table :data="list" stripe>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="会话" min-width="220">
          <template #default="{ row }">{{ row.title || `练习会话 #${row.id}` }}</template>
        </el-table-column>
        <el-table-column label="总题数" width="90" prop="total_count" />
        <el-table-column label="正确率" width="90">
          <template #default="{ row }">{{ row.accuracy_rate }}%</template>
        </el-table-column>
        <el-table-column label="薄弱点" width="90">
          <template #default="{ row }">{{ row.weak_knowledge_point_ids.length }}</template>
        </el-table-column>
        <el-table-column label="错题" width="90">
          <template #default="{ row }">{{ row.wrong_question_ids.length }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          layout="prev, pager, next, total"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          @current-change="handlePageChange"
        />
      </div>
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
  gap: 12px;
}

.title h2 {
  margin: 0;
  font-size: 24px;
}

.title p {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 14px;
}

.card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 20px;
}

.card.loading {
  text-align: center;
  color: var(--muted);
}

.detail-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 10px;
}

.detail-head h3 {
  margin: 0;
}

.time {
  color: var(--muted);
  font-size: 13px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 10px;
  margin: 16px 0;
}

.summary-item {
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px;
  text-align: center;
  background: var(--card);
}

.summary-item b {
  display: block;
  font-size: 22px;
}

.summary-item span {
  color: var(--muted);
  font-size: 12px;
}

.summary-item.ok b {
  color: var(--green);
}

.summary-item.bad b {
  color: var(--danger);
}

.summary-item.rate b {
  color: var(--gold);
}

.meta {
  display: flex;
  gap: 18px;
  color: var(--muted);
  font-size: 14px;
}

.suggestion {
  margin: 10px 0 0;
  font-size: 14px;
  color: var(--text);
}

.ok-text {
  color: var(--green);
}

.bad-text {
  color: var(--danger);
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
