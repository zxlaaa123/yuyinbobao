<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getWrongQuestions, markMastered, unmarkMastered, deleteWrongQuestion } from '../api/wrongQuestion'
import { getKnowledgeBasesForSelect } from '../api/material'
import type { WrongQuestion } from '../api/wrongQuestion'
import type { KnowledgeBase } from '../api/material'

const wrongQuestions = ref<WrongQuestion[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const filterMastered = ref<boolean | undefined>(undefined)
const filterKB = ref<number | undefined>()

const filteredList = computed(() => {
  let list = wrongQuestions.value
  if (filterMastered.value !== undefined) {
    list = list.filter((wq) => wq.is_mastered === filterMastered.value)
  }
  if (filterKB.value) {
    list = list.filter((wq) => wq.question.knowledge_point_title)
  }
  return list
})

async function fetchData() {
  loading.value = true
  try {
    wrongQuestions.value = await getWrongQuestions()
    knowledgeBases.value = await getKnowledgeBasesForSelect()
  } catch {
    ElMessage.error('加载错题列表失败')
  } finally {
    loading.value = false
  }
}

async function handleMarkMastered(wq: WrongQuestion) {
  try {
    await markMastered(wq.id)
    wq.is_mastered = true
    ElMessage.success('已标记为掌握')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

async function handleUnmarkMastered(wq: WrongQuestion) {
  try {
    await unmarkMastered(wq.id)
    wq.is_mastered = false
    ElMessage.success('已取消掌握标记')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

async function handleDelete(wq: WrongQuestion) {
  try {
    await ElMessageBox.confirm(
      `确定要删除这道错题记录吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await deleteWrongQuestion(wq.id)
    wrongQuestions.value = wrongQuestions.value.filter((w) => w.id !== wq.id)
    ElMessage.success('错题记录已删除')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
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

    <!-- 空状态 -->
    <div v-if="!loading && filteredList.length === 0" class="empty">
      暂无错题，继续保持。
    </div>

    <!-- 错题列表 -->
    <div v-else class="wq-list">
      <div v-for="wq in filteredList" :key="wq.id" class="wq-card">
        <div class="wq-header">
          <div class="wq-title">{{ wq.question.stem }}</div>
          <div class="wq-badges">
            <span class="badge mastered" :class="{ active: wq.is_mastered }">
              {{ wq.is_mastered ? '已掌握' : '未掌握' }}
            </span>
            <span class="badge count">错误 {{ wq.wrong_count }} 次</span>
          </div>
        </div>

        <div class="wq-options">
          <div
            v-for="opt in wq.question.options"
            :key="opt.key"
            class="wq-opt"
            :class="{
              'user-wrong': opt.key === wq.last_wrong_answer,
              'correct': opt.key === wq.question.answer,
            }"
          >
            <span class="opt-key">{{ opt.key }}</span>
            <span class="opt-text">{{ opt.text }}</span>
            <span v-if="opt.key === wq.last_wrong_answer" class="opt-tag wrong">你的答案</span>
            <span v-if="opt.key === wq.question.answer" class="opt-tag right">正确答案</span>
          </div>
        </div>

        <div v-if="wq.question.analysis" class="wq-analysis">
          <strong>解析：</strong>{{ wq.question.analysis }}
        </div>

        <div class="wq-meta" v-if="wq.question.knowledge_point_title">
          关联知识点：{{ wq.question.knowledge_point_title }}
        </div>

        <div class="wq-actions">
          <el-button v-if="!wq.is_mastered" size="small" type="success" @click="handleMarkMastered(wq)">
            标记掌握
          </el-button>
          <el-button v-else size="small" @click="handleUnmarkMastered(wq)">
            取消掌握
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(wq)">删除</el-button>
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

.wq-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.wq-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 22px rgba(25, 36, 70, 0.06);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.wq-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.wq-title {
  font-size: 15px;
  font-weight: 600;
  color: #182033;
  line-height: 1.5;
  flex: 1;
}

.wq-badges {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
}

.badge.mastered {
  background: #fff0f0;
  color: #a61b1b;
}

.badge.mastered.active {
  background: #e9fbf5;
  color: #087a59;
}

.badge.count {
  background: #fff8e7;
  color: #a06000;
}

.wq-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.wq-opt {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 10px;
  background: #f8fbff;
  font-size: 14px;
}

.wq-opt.user-wrong {
  background: #fff0f0;
  border: 1px solid #ffd1d1;
}

.wq-opt.correct {
  background: #e9fbf5;
  border: 1px solid #bcefdc;
}

.opt-key {
  font-weight: 700;
  min-width: 20px;
  color: #344054;
}

.opt-text {
  flex: 1;
  color: #344054;
}

.opt-tag {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 99px;
  font-weight: 600;
}

.opt-tag.wrong {
  background: #ffd1d1;
  color: #a61b1b;
}

.opt-tag.right {
  background: #bcefdc;
  color: #087a59;
}

.wq-analysis {
  font-size: 14px;
  color: #667085;
  line-height: 1.6;
  padding: 10px 14px;
  background: #f8fbff;
  border-radius: 10px;
}

.wq-meta {
  font-size: 13px;
  color: #667085;
}

.wq-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
