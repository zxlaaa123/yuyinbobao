<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKnowledgePoints, deleteKnowledgePoint } from '../api/knowledgePoint'
import { getKnowledgeBasesForSelect } from '../api/material'
import type { KnowledgePoint } from '../api/knowledgePoint'
import type { KnowledgeBase } from '../api/material'

const router = useRouter()
const knowledgePoints = ref<KnowledgePoint[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const filterKB = ref<number | undefined>()
const filterImportance = ref('')
const searchKeyword = ref('')

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
    await fetchData()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
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

    <!-- 空状态 -->
    <div v-if="!loading && filteredList.length === 0" class="empty">
      暂无知识点，请先在「资料导入」中提取知识点。
    </div>

    <!-- 卡片列表 -->
    <div v-else class="card-grid">
      <div v-for="kp in filteredList" :key="kp.id" class="kp-card" @click="goDetail(kp)">
        <div class="kp-header">
          <h3>{{ kp.title }}</h3>
          <span class="importance-badge" :class="importanceTag(kp.importance).class">
            {{ importanceTag(kp.importance).label }}
          </span>
        </div>
        <p class="kp-summary">{{ kp.summary || '暂无摘要' }}</p>
        <div class="kp-tags">
          <span v-for="tag in (kp.tags || [])" :key="tag" class="tag">{{ tag }}</span>
        </div>
        <div class="kp-meta">
          <span>题目 {{ kp.question_count }}</span>
          <span>音频 {{ kp.audio_count }}</span>
        </div>
        <div class="kp-actions" @click.stop>
          <el-button size="small" @click="goDetail(kp)">详情</el-button>
          <el-button size="small" type="danger" @click="handleDelete(kp)">删除</el-button>
        </div>
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
  color: #667085;
  font-size: 14px;
}

.filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.empty {
  text-align: center;
  padding: 60px 0;
  color: #667085;
  font-size: 15px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 18px;
}

.kp-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 22px rgba(25, 36, 70, 0.06);
  padding: 20px;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.kp-card:hover {
  box-shadow: 0 12px 28px rgba(25, 36, 70, 0.1);
  transform: translateY(-2px);
}

.kp-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.kp-header h3 {
  font-size: 16px;
  margin: 0;
  flex: 1;
}

.importance-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
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

.kp-summary {
  margin: 0;
  color: #667085;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.kp-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 12px;
  background: #edf3ff;
  color: #315de6;
}

.kp-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #667085;
}

.kp-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
