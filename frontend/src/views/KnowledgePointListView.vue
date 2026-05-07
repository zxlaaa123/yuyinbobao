<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKnowledgePoints, deleteKnowledgePoint } from '../api/knowledgePoint'
import { getKnowledgeBasesForSelect } from '../api/material'
import { generateBatchAudio } from '../api/audio'
import type { KnowledgePoint } from '../api/knowledgePoint'
import type { KnowledgeBase } from '../api/material'

const router = useRouter()
const knowledgePoints = ref<KnowledgePoint[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const filterKB = ref<number | undefined>()
const filterImportance = ref('')
const searchKeyword = ref('')
const selectedIds = ref<number[]>([])
const batchLoading = ref(false)

const filteredList = computed(() => {
  let list = knowledgePoints.value
  if (filterKB.value) {
    list = list.filter((kp) => kp.knowledge_base_id === filterKB.value)
  }
  if (filterImportance.value) {
    list = list.filter((kp) => kp.importance === filterImportance.value)
  }
  if (searchKeyword.value.trim()) {
    const kw = searchKeyword.value.trim().toLowerCase()
    list = list.filter(
      (kp) =>
        kp.title.toLowerCase().includes(kw) ||
        (kp.summary && kp.summary.toLowerCase().includes(kw))
    )
  }
  return list
})

async function fetchData() {
  loading.value = true
  try {
    knowledgePoints.value = await getKnowledgePoints()
    knowledgeBases.value = await getKnowledgeBasesForSelect()
  } catch {
    ElMessage.error('加载知识点列表失败')
  } finally {
    loading.value = false
  }
}

function goDetail(kp: KnowledgePoint) {
  router.push(`/knowledge-points/${kp.id}`)
}

async function handleDelete(kp: KnowledgePoint) {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识点「${kp.title}」吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await deleteKnowledgePoint(kp.id)
    ElMessage.success('知识点已删除')
    selectedIds.value = selectedIds.value.filter((id) => id !== kp.id)
    await fetchData()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

function handleSelectionChange(selection: KnowledgePoint[]) {
  selectedIds.value = selection.map((kp) => kp.id)
}

async function handleBatchGenerate() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择至少一个知识点')
    return
  }
  if (selectedIds.value.length > 20) {
    ElMessage.warning('一次最多选择 20 个知识点')
    return
  }
  batchLoading.value = true
  try {
    const result = await generateBatchAudio(selectedIds.value)
    ElMessage.success(`合集音频生成成功（${result.knowledge_point_count} 个知识点）`)
    selectedIds.value = []
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '批量生成音频失败')
  } finally {
    batchLoading.value = false
  }
}

function importanceTag(importance: string) {
  const map: Record<string, { label: string; class: string }> = {
    high: { label: '重点', class: 'high' },
    medium: { label: '普通', class: 'medium' },
    low: { label: '低频', class: 'low' },
  }
  return map[importance] || { label: importance, class: '' }
}

onMounted(fetchData)
</script>

<template>
  <div class="page">
    <div class="header">
      <div class="title">
        <h2>知识点</h2>
        <p>查看、筛选、管理 AI 提取的知识点。</p>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filters">
      <el-select v-model="filterKB" placeholder="全部知识库" clearable style="width: 200px">
        <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.name" :value="kb.id" />
      </el-select>
      <el-select v-model="filterImportance" placeholder="全部重要程度" clearable style="width: 160px">
        <el-option label="重点" value="high" />
        <el-option label="普通" value="medium" />
        <el-option label="低频" value="low" />
      </el-select>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索知识点..."
        clearable
        style="width: 240px"
      />
    </div>

    <!-- 批量操作栏 -->
    <div class="batch-bar" v-if="selectedIds.length > 0">
      <span class="batch-info">已选择 {{ selectedIds.length }} 个知识点</span>
      <el-button
        type="primary"
        size="small"
        :loading="batchLoading"
        :disabled="batchLoading"
        @click="handleBatchGenerate"
      >
        批量生成音频
      </el-button>
      <el-button size="small" @click="selectedIds = []">取消选择</el-button>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && filteredList.length === 0" class="empty">
      暂无知识点，请先在「资料导入」中提取知识点。
    </div>

    <!-- 表格列表 -->
    <div v-else>
      <el-table
        :data="filteredList"
        @selection-change="handleSelectionChange"
        stripe
        style="width: 100%"
        row-key="id"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="标题" min-width="200">
          <template #default="{ row }">
            <span class="kp-title-link" @click="goDetail(row)">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="摘要" min-width="200">
          <template #default="{ row }">
            <span class="kp-summary-cell">{{ row.summary || '暂无摘要' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="重要度" width="100">
          <template #default="{ row }">
            <span class="importance-badge" :class="importanceTag(row.importance).class">
              {{ importanceTag(row.importance).label }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="150">
          <template #default="{ row }">
            <span v-for="tag in (row.tags || [])" :key="tag" class="tag">{{ tag }}</span>
          </template>
        </el-table-column>
        <el-table-column label="统计" width="120">
          <template #default="{ row }">
            <span class="kp-stat">题目 {{ row.question_count }}</span>
            <span class="kp-stat">音频 {{ row.audio_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="goDetail(row)">详情</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
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
  color: #667085;
  font-size: 14px;
}

.filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 10px 16px;
  background: #edf3ff;
  border-radius: 12px;
}

.batch-info {
  font-size: 14px;
  color: #315de6;
  font-weight: 600;
  flex: 1;
}

.empty {
  text-align: center;
  padding: 60px 0;
  color: #667085;
  font-size: 15px;
}

.kp-title-link {
  cursor: pointer;
  color: #315de6;
  font-weight: 600;
}

.kp-title-link:hover {
  text-decoration: underline;
}

.kp-summary-cell {
  color: #667085;
  font-size: 13px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.importance-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
}

.importance-badge.high {
  background: #fff0f0;
  color: #a61b1b;
}

.importance-badge.medium {
  background: #fff8e7;
  color: #a06000;
}

.importance-badge.low {
  background: #e9fbf5;
  color: #087a59;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 12px;
  background: #edf3ff;
  color: #315de6;
  margin-right: 4px;
  margin-bottom: 2px;
}

.kp-stat {
  display: block;
  font-size: 12px;
  color: #667085;
  line-height: 1.6;
}
</style>
