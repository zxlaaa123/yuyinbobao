<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import AppEmpty from '../components/AppEmpty.vue'
import { getWrongQuestions, markMastered, unmarkMastered, deleteWrongQuestion } from '../api/wrongQuestion'
import { getKnowledgeBasesForSelect } from '../api/material'
import { generateWrongQuestionAudio } from '../api/audio'
import { exportWrongQuestionsCsv } from '../api/export'
import type { WrongQuestion } from '../api/wrongQuestion'
import type { KnowledgeBase } from '../api/material'
import { getErrorMessage, isUserCanceled } from '../utils/error'
import { confirmDelete } from '../utils/confirm'

const wrongQuestions = ref<WrongQuestion[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const filterMastered = ref<boolean | undefined>(undefined)
const filterKB = ref<number | undefined>()
const selectedIds = ref<number[]>([])
const batchLoading = ref(false)

const filteredList = computed(() => {
  let list = wrongQuestions.value
  if (filterMastered.value !== undefined) {
    list = list.filter((wq) => wq.is_mastered === filterMastered.value)
  }
  return list
})

async function fetchData() {
  loading.value = true
  try {
    wrongQuestions.value = await getWrongQuestions()
    knowledgeBases.value = await getKnowledgeBasesForSelect()
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '加载错题列表失败'))
  } finally {
    loading.value = false
  }
}

function handleSelectionChange(selection: WrongQuestion[]) {
  selectedIds.value = selection.map((wq) => wq.id)
}

async function handleBatchAudio() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择至少一道错题')
    return
  }
  if (selectedIds.value.length > 20) {
    ElMessage.warning('一次最多选择 20 道错题')
    return
  }
  batchLoading.value = true
  try {
    const result = await generateWrongQuestionAudio(selectedIds.value)
    ElMessage.success(`错题音频生成成功（${result.knowledge_point_count} 个知识点）`)
    selectedIds.value = []
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '生成失败'))
  } finally {
    batchLoading.value = false
  }
}

async function handleMarkMastered(wq: WrongQuestion) {
  try {
    await markMastered(wq.id)
    wq.is_mastered = true
    ElMessage.success('已标记为掌握')
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '操作失败'))
  }
}

async function handleUnmarkMastered(wq: WrongQuestion) {
  try {
    await unmarkMastered(wq.id)
    wq.is_mastered = false
    ElMessage.success('已取消掌握标记')
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '操作失败'))
  }
}

async function handleDelete(wq: WrongQuestion) {
  try {
    await confirmDelete('错题记录')
    await deleteWrongQuestion(wq.id)
    wrongQuestions.value = wrongQuestions.value.filter((w) => w.id !== wq.id)
    selectedIds.value = selectedIds.value.filter((id) => id !== wq.id)
    ElMessage.success('错题记录已删除')
  } catch (e) {
    if (!isUserCanceled(e)) {
      ElMessage.error(getErrorMessage(e, '删除失败'))
    }
  }
}

function handleExport() {
  exportWrongQuestionsCsv(filterKB.value, filterMastered.value)
  ElMessage.success('已开始导出错题 CSV')
}

onMounted(fetchData)
</script>

<template>
  <div class="page">
    <div class="header">
      <div class="title">
        <h2>错题本</h2>
        <p>复习答错的题目，标记已掌握。</p>
      </div>
      <el-button @click="handleExport">导出 CSV</el-button>
    </div>

    <!-- 筛选 -->
    <div class="filters">
      <el-select v-model="filterMastered" placeholder="全部状态" clearable style="width: 160px">
        <el-option label="未掌握" :value="false" />
        <el-option label="已掌握" :value="true" />
      </el-select>
      <el-select v-model="filterKB" placeholder="全部知识库" clearable style="width: 200px">
        <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.name" :value="kb.id" />
      </el-select>
    </div>

    <!-- 批量操作栏 -->
    <div class="batch-bar" v-if="selectedIds.length > 0">
      <span class="batch-info">已选择 {{ selectedIds.length }} 道错题</span>
      <el-button
        type="primary"
        size="small"
        :loading="batchLoading"
        :disabled="batchLoading"
        @click="handleBatchAudio"
      >
        生成错题音频
      </el-button>
      <el-button size="small" @click="selectedIds = []">取消选择</el-button>
    </div>

    <!-- 空状态 -->
    <AppEmpty
      v-if="!loading && filteredList.length === 0"
      title="暂无错题"
      description="答错的题目会自动进入这里，方便后续复习。"
    />

    <!-- 错题表格 -->
    <div v-else>
      <el-table
        :data="filteredList"
        @selection-change="handleSelectionChange"
        stripe
        style="width: 100%"
        row-key="id"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="题干" min-width="250">
          <template #default="{ row }">
            <span>{{ row.question.stem }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span class="badge mastered" :class="{ active: row.is_mastered }">
              {{ row.is_mastered ? '已掌握' : '未掌握' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="错误次数" width="100">
          <template #default="{ row }">
            <span class="badge count">错误 {{ row.wrong_count }} 次</span>
          </template>
        </el-table-column>
        <el-table-column label="上次错误答案" width="120">
          <template #default="{ row }">
            <span>{{ row.last_wrong_answer || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="关联知识点" min-width="150">
          <template #default="{ row }">
            <span v-if="row.question.knowledge_point_title">{{ row.question.knowledge_point_title }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!row.is_mastered" size="small" type="success" @click="handleMarkMastered(row)">
              标记掌握
            </el-button>
            <el-button v-else size="small" @click="handleUnmarkMastered(row)">
              取消掌握
            </el-button>
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
  color: var(--muted);
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
  background: var(--panel-strong);
  border-radius: 12px;
  border: 1px solid var(--line);
}

.batch-info {
  font-size: 14px;
  color: var(--green);
  font-weight: 600;
  flex: 1;
}

:deep(.el-table) {
  border-radius: 18px;
  overflow: hidden;
}

.badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
}

.badge.mastered {
  background: var(--danger-bg);
  color: var(--danger-text);
}

.badge.mastered.active {
  background: var(--success-bg);
  color: var(--success-text);
}

.badge.count {
  background: var(--warning-bg);
  color: var(--warning-text);
}
</style>
