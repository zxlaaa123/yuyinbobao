<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAiCallLogs, getAiCallLogSummary } from '../api/aiCallLog'
import type { AICallLog, AICallLogSummary } from '../api/aiCallLog'
import { getErrorMessage } from '../utils/error'

const logs = ref<AICallLog[]>([])
const summary = ref<AICallLogSummary>({
  total: 0,
  success: 0,
  failed: 0,
  total_tokens: 0,
  estimated_cost: 0,
})
const loading = ref(false)
const filters = reactive({
  page: 1,
  page_size: 20,
  status: '',
  operation: '',
})
const total = ref(0)

async function fetchData() {
  loading.value = true
  try {
    const [listResult, summaryResult] = await Promise.all([
      getAiCallLogs({
        page: filters.page,
        page_size: filters.page_size,
        status: filters.status || undefined,
        operation: filters.operation || undefined,
      }),
      getAiCallLogSummary(),
    ])
    logs.value = listResult.items
    total.value = listResult.total
    summary.value = summaryResult
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '加载 AI 调用日志失败'))
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  filters.page = 1
  fetchData()
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString()
}

function formatCost(value: number): string {
  return value ? value.toFixed(6) : '0'
}

onMounted(fetchData)
</script>

<template>
  <div class="page">
    <div class="header">
      <div class="title">
        <h2>AI 调用日志</h2>
        <p>记录成功和失败调用，只保存摘要、字符数、token 和估算成本。</p>
      </div>
    </div>

    <div class="summary-grid">
      <div class="summary-card">
        <span>总调用</span>
        <strong>{{ summary.total }}</strong>
      </div>
      <div class="summary-card">
        <span>成功 / 失败</span>
        <strong>{{ summary.success }} / {{ summary.failed }}</strong>
      </div>
      <div class="summary-card">
        <span>总 token</span>
        <strong>{{ summary.total_tokens }}</strong>
      </div>
      <div class="summary-card">
        <span>估算成本</span>
        <strong>{{ formatCost(summary.estimated_cost) }}</strong>
      </div>
    </div>

    <div class="toolbar">
      <el-select v-model="filters.status" placeholder="状态" clearable style="width: 160px" @change="handleFilterChange">
        <el-option label="成功" value="success" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-select
        v-model="filters.operation"
        placeholder="操作"
        clearable
        style="width: 220px"
        @change="handleFilterChange"
      >
        <el-option label="知识点提取" value="extract_knowledge_points" />
        <el-option label="题目生成" value="generate_questions" />
        <el-option label="闪卡生成" value="generate_flashcards" />
        <el-option label="JSON 修复" value="fix_json" />
      </el-select>
      <el-button :loading="loading" @click="fetchData">刷新</el-button>
    </div>

    <div class="table-card">
      <el-table v-loading="loading" :data="logs" stripe>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="operation" label="操作" width="170" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="模型" width="160" />
        <el-table-column label="token" width="150">
          <template #default="{ row }">
            {{ row.total_tokens }}
            <span v-if="row.tokens_estimated" class="muted">估</span>
          </template>
        </el-table-column>
        <el-table-column label="成本" width="120">
          <template #default="{ row }">{{ formatCost(row.estimated_cost) }}</template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="{ row }">{{ row.duration_ms }} ms</template>
        </el-table-column>
        <el-table-column prop="request_summary" label="请求摘要" min-width="260" show-overflow-tooltip />
        <el-table-column prop="response_summary" label="响应摘要" min-width="260" show-overflow-tooltip />
        <el-table-column prop="error_message" label="错误信息" min-width="220" show-overflow-tooltip />
      </el-table>
      <div class="pager">
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchData"
          @size-change="handleFilterChange"
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
  margin-bottom: 20px;
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

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}

.summary-card,
.table-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow-soft);
}

.summary-card {
  padding: 16px;
}

.summary-card span,
.muted {
  color: var(--muted);
  font-size: 12px;
}

.summary-card strong {
  display: block;
  margin-top: 8px;
  font-size: 22px;
  color: var(--text);
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.table-card {
  padding: 16px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
