<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteAiCallLog, getAiCallLogDetail, getAiCallLogs, getAiCallLogSummary } from '../api/aiCallLog'
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
const detailLoading = ref(false)
const deletingId = ref<number | null>(null)
const detailVisible = ref(false)
const currentLog = ref<AICallLog | null>(null)
const filters = reactive({
  page: 1,
  page_size: 20,
  status: '',
  operation: '',
  error_type: '',
  json_parse_status: '',
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
        error_type: filters.error_type || undefined,
        json_parse_status: filters.json_parse_status || undefined,
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

function operationLabel(value: string): string {
  const labels: Record<string, string> = {
    extract_knowledge_points: '知识点提取',
    generate_questions: '题目生成',
    generate_flashcards: '闪卡生成',
    fix_json: 'JSON 修复',
    test_ai_connection: 'AI 连接测试',
    chat: '通用对话',
  }
  return labels[value] || value || '-'
}

function errorTypeLabel(value: string | null): string {
  const labels: Record<string, string> = {
    timeout: '超时',
    http_error: 'HTTP 失败',
    json_parse_error: 'JSON 解析失败',
    validation_error: '业务校验失败',
    unknown: '未知错误',
  }
  return value ? labels[value] || value : '-'
}

function jsonStatusLabel(value: string): string {
  const labels: Record<string, string> = {
    not_required: '无需解析',
    success: '解析成功',
    failed: '解析失败',
    fixed: '修复成功',
  }
  return labels[value] || value || '-'
}

function jsonStatusType(value: string): 'success' | 'warning' | 'danger' | 'info' {
  if (value === 'success') return 'success'
  if (value === 'fixed') return 'warning'
  if (value === 'failed') return 'danger'
  return 'info'
}

async function openDetail(row: AICallLog) {
  detailVisible.value = true
  detailLoading.value = true
  currentLog.value = row
  try {
    currentLog.value = await getAiCallLogDetail(row.id)
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '加载 AI 日志详情失败'))
  } finally {
    detailLoading.value = false
  }
}

async function copyError(row: AICallLog | null = currentLog.value) {
  if (!row) return
  const text = row.error_message || row.response_summary || row.request_summary || ''
  if (!text) {
    ElMessage.warning('没有可复制的日志内容')
    return
  }
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败，请手动选择内容复制')
  }
}

async function handleDelete(row: AICallLog) {
  try {
    await ElMessageBox.confirm('删除后无法恢复，确认删除这条 AI 日志吗？', '删除 AI 日志', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }

  deletingId.value = row.id
  try {
    await deleteAiCallLog(row.id)
    ElMessage.success('AI 日志已删除')
    if (currentLog.value?.id === row.id) {
      detailVisible.value = false
      currentLog.value = null
    }
    fetchData()
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '删除 AI 日志失败'))
  } finally {
    deletingId.value = null
  }
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
        <el-option label="AI 连接测试" value="test_ai_connection" />
      </el-select>
      <el-select
        v-model="filters.error_type"
        placeholder="错误类型"
        clearable
        style="width: 180px"
        @change="handleFilterChange"
      >
        <el-option label="超时" value="timeout" />
        <el-option label="HTTP 失败" value="http_error" />
        <el-option label="JSON 解析失败" value="json_parse_error" />
        <el-option label="业务校验失败" value="validation_error" />
        <el-option label="未知错误" value="unknown" />
      </el-select>
      <el-select
        v-model="filters.json_parse_status"
        placeholder="JSON 状态"
        clearable
        style="width: 180px"
        @change="handleFilterChange"
      >
        <el-option label="无需解析" value="not_required" />
        <el-option label="解析成功" value="success" />
        <el-option label="解析失败" value="failed" />
        <el-option label="修复成功" value="fixed" />
      </el-select>
      <el-button :loading="loading" @click="fetchData">刷新</el-button>
    </div>

    <div class="table-card">
      <el-table v-loading="loading" :data="logs" stripe>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">{{ operationLabel(row.operation) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="错误类型" width="130">
          <template #default="{ row }">{{ errorTypeLabel(row.error_type) }}</template>
        </el-table-column>
        <el-table-column label="JSON 状态" width="120">
          <template #default="{ row }">
            <el-tag :type="jsonStatusType(row.json_parse_status)">
              {{ jsonStatusLabel(row.json_parse_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="HTTP" width="80">
          <template #default="{ row }">{{ row.http_status_code || '-' }}</template>
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
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">详情</el-button>
            <el-button link type="primary" @click="copyError(row)">复制</el-button>
            <el-button
              link
              type="danger"
              :loading="deletingId === row.id"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
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

    <el-dialog v-model="detailVisible" title="AI 日志详情" width="760px">
      <div v-loading="detailLoading" class="detail-panel">
        <template v-if="currentLog">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="调用类型">{{ operationLabel(currentLog.operation) }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              {{ currentLog.status === 'success' ? '成功' : '失败' }}
            </el-descriptions-item>
            <el-descriptions-item label="模型">{{ currentLog.model || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Base URL">{{ currentLog.base_url_host || '-' }}</el-descriptions-item>
            <el-descriptions-item label="错误类型">{{ errorTypeLabel(currentLog.error_type) }}</el-descriptions-item>
            <el-descriptions-item label="JSON 状态">{{ jsonStatusLabel(currentLog.json_parse_status) }}</el-descriptions-item>
            <el-descriptions-item label="HTTP 状态">{{ currentLog.http_status_code || '-' }}</el-descriptions-item>
            <el-descriptions-item label="耗时">{{ currentLog.duration_ms }} ms</el-descriptions-item>
            <el-descriptions-item label="Prompt 字符">{{ currentLog.prompt_chars }}</el-descriptions-item>
            <el-descriptions-item label="Response 字符">{{ currentLog.response_chars }}</el-descriptions-item>
            <el-descriptions-item label="Prompt token">{{ currentLog.prompt_tokens }}</el-descriptions-item>
            <el-descriptions-item label="Completion token">{{ currentLog.completion_tokens }}</el-descriptions-item>
            <el-descriptions-item label="总 token">{{ currentLog.total_tokens }}</el-descriptions-item>
            <el-descriptions-item label="估算成本">{{ formatCost(currentLog.estimated_cost) }}</el-descriptions-item>
            <el-descriptions-item label="关联对象">{{ currentLog.related_type || '-' }} / {{ currentLog.related_id || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(currentLog.created_at) }}</el-descriptions-item>
          </el-descriptions>

          <div class="detail-section">
            <h3>请求摘要</h3>
            <pre>{{ currentLog.request_summary || '无' }}</pre>
          </div>
          <div class="detail-section">
            <h3>响应摘要</h3>
            <pre>{{ currentLog.response_summary || '无' }}</pre>
          </div>
          <div class="detail-section">
            <h3>错误信息</h3>
            <pre>{{ currentLog.error_message || '无' }}</pre>
          </div>
        </template>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="copyError()">复制错误</el-button>
        <el-button v-if="currentLog" type="danger" :loading="deletingId === currentLog.id" @click="handleDelete(currentLog)">
          删除日志
        </el-button>
      </template>
    </el-dialog>
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

.detail-panel {
  min-height: 240px;
}

.detail-section {
  margin-top: 16px;
}

.detail-section h3 {
  margin: 0 0 8px;
  font-size: 14px;
}

.detail-section pre {
  margin: 0;
  padding: 12px;
  max-height: 180px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--text);
  background: #f8fafc;
  border: 1px solid var(--line);
  border-radius: 8px;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
