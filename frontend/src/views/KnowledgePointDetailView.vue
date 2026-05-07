<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKnowledgePoint, updateKnowledgePoint, deleteKnowledgePoint } from '../api/knowledgePoint'
import type { KnowledgePoint, KnowledgePointUpdate } from '../api/knowledgePoint'

const route = useRoute()
const router = useRouter()
const kp = ref<KnowledgePoint | null>(null)
const loading = ref(false)
const editing = ref(false)
const editForm = reactive<KnowledgePointUpdate>({})

async function fetchData() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    kp.value = await getKnowledgePoint(id)
  } catch {
    ElMessage.error('加载知识点失败')
    router.push('/knowledge-points')
  } finally {
    loading.value = false
  }
}

function startEdit() {
  if (!kp.value) return
  editForm.title = kp.value.title
  editForm.summary = kp.value.summary || ''
  editForm.detail = kp.value.detail || ''
  editForm.exam_points = [...(kp.value.exam_points || [])]
  editForm.confusing_points = [...(kp.value.confusing_points || [])]
  editForm.memory_tips = [...(kp.value.memory_tips || [])]
  editForm.examples = [...(kp.value.examples || [])]
  editForm.importance = kp.value.importance
  editForm.tags = [...(kp.value.tags || [])]
  editing.value = true
}

function cancelEdit() {
  editing.value = false
}

async function handleSave() {
  if (!kp.value) return
  if (!editForm.title?.trim()) {
    ElMessage.warning('知识点标题不能为空')
    return
  }
  try {
    const updated = await updateKnowledgePoint(kp.value.id, editForm)
    kp.value = updated
    editing.value = false
    ElMessage.success('知识点已更新')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  }
}

async function handleDelete() {
  if (!kp.value) return
  try {
    await ElMessageBox.confirm(
      `确定要删除知识点「${kp.value.title}」吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await deleteKnowledgePoint(kp.value.id)
    ElMessage.success('知识点已删除')
    router.push('/knowledge-points')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

function addItem(field: 'exam_points' | 'confusing_points' | 'memory_tips' | 'examples' | 'tags') {
  if (!editForm[field]) editForm[field] = []
  editForm[field]!.push('')
}

function removeItem(field: 'exam_points' | 'confusing_points' | 'memory_tips' | 'examples' | 'tags', index: number) {
  editForm[field]!.splice(index, 1)
}

function importanceLabel(v: string) {
  return { high: '重点', medium: '普通', low: '低频' }[v] || v
}

onMounted(fetchData)
</script>

<template>
  <div class="page">
    <div v-if="loading" class="loading">加载中...</div>

    <template v-else-if="kp">
      <!-- 顶部操作栏 -->
      <div class="top-bar">
        <el-button @click="router.push('/knowledge-points')">← 返回列表</el-button>
        <div class="actions">
          <el-button v-if="!editing" @click="startEdit">编辑</el-button>
          <el-button v-if="editing" @click="cancelEdit">取消</el-button>
          <el-button v-if="editing" type="primary" @click="handleSave">保存</el-button>
          <el-button type="danger" @click="handleDelete">删除</el-button>
        </div>
      </div>

      <!-- 查看模式 -->
      <div v-if="!editing" class="detail-card">
        <div class="detail-header">
          <div class="title-row">
            <h2>{{ kp.title }}</h2>
            <span class="importance-badge" :class="kp.importance">
              {{ importanceLabel(kp.importance) }}
            </span>
          </div>
          <div class="meta-row">
            <span v-if="kp.knowledge_base_name">知识库：{{ kp.knowledge_base_name }}</span>
            <span v-if="kp.material_title">来源：{{ kp.material_title }}</span>
          </div>
          <div class="tags">
            <span v-for="tag in (kp.tags || [])" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>

        <div class="section" v-if="kp.summary">
          <h3>摘要</h3>
          <p>{{ kp.summary }}</p>
        </div>

        <div class="section" v-if="kp.detail">
          <h3>详细解释</h3>
          <p>{{ kp.detail }}</p>
        </div>

        <div class="section" v-if="kp.exam_points?.length">
          <h3>高频考点</h3>
          <ul>
            <li v-for="(p, i) in kp.exam_points" :key="i">{{ p }}</li>
          </ul>
        </div>

        <div class="section" v-if="kp.confusing_points?.length">
          <h3>易混点</h3>
          <ul>
            <li v-for="(p, i) in kp.confusing_points" :key="i">{{ p }}</li>
          </ul>
        </div>

        <div class="section" v-if="kp.memory_tips?.length">
          <h3>记忆方法</h3>
          <ul>
            <li v-for="(p, i) in kp.memory_tips" :key="i">{{ p }}</li>
          </ul>
        </div>

        <div class="section" v-if="kp.examples?.length">
          <h3>示例</h3>
          <ul>
            <li v-for="(p, i) in kp.examples" :key="i">{{ p }}</li>
          </ul>
        </div>
      </div>

      <!-- 编辑模式 -->
      <div v-else class="detail-card edit-mode">
        <el-form label-position="top">
          <el-form-item label="标题">
            <el-input v-model="editForm.title" />
          </el-form-item>
          <el-form-item label="摘要">
            <el-input v-model="editForm.summary" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item label="详细解释">
            <el-input v-model="editForm.detail" type="textarea" :rows="4" />
          </el-form-item>
          <el-form-item label="重要程度">
            <el-select v-model="editForm.importance" style="width: 160px">
              <el-option label="重点" value="high" />
              <el-option label="普通" value="medium" />
              <el-option label="低频" value="low" />
            </el-select>
          </el-form-item>

          <el-form-item label="高频考点">
            <div v-for="(_, i) in (editForm.exam_points || [])" :key="i" class="list-input">
              <el-input v-model="editForm.exam_points![i]" />
              <el-button size="small" type="danger" @click="removeItem('exam_points', i)">删除</el-button>
            </div>
            <el-button size="small" @click="addItem('exam_points')">+ 添加</el-button>
          </el-form-item>

          <el-form-item label="易混点">
            <div v-for="(_, i) in (editForm.confusing_points || [])" :key="i" class="list-input">
              <el-input v-model="editForm.confusing_points![i]" />
              <el-button size="small" type="danger" @click="removeItem('confusing_points', i)">删除</el-button>
            </div>
            <el-button size="small" @click="addItem('confusing_points')">+ 添加</el-button>
          </el-form-item>

          <el-form-item label="记忆方法">
            <div v-for="(_, i) in (editForm.memory_tips || [])" :key="i" class="list-input">
              <el-input v-model="editForm.memory_tips![i]" />
              <el-button size="small" type="danger" @click="removeItem('memory_tips', i)">删除</el-button>
            </div>
            <el-button size="small" @click="addItem('memory_tips')">+ 添加</el-button>
          </el-form-item>

          <el-form-item label="示例">
            <div v-for="(_, i) in (editForm.examples || [])" :key="i" class="list-input">
              <el-input v-model="editForm.examples![i]" />
              <el-button size="small" type="danger" @click="removeItem('examples', i)">删除</el-button>
            </div>
            <el-button size="small" @click="addItem('examples')">+ 添加</el-button>
          </el-form-item>

          <el-form-item label="标签">
            <div v-for="(_, i) in (editForm.tags || [])" :key="i" class="list-input">
              <el-input v-model="editForm.tags![i]" />
              <el-button size="small" type="danger" @click="removeItem('tags', i)">删除</el-button>
            </div>
            <el-button size="small" @click="addItem('tags')">+ 添加</el-button>
          </el-form-item>
        </el-form>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 30px 42px;
  max-width: 800px;
}

.loading {
  text-align: center;
  padding: 60px;
  color: #667085;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  gap: 10px;
}

.detail-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 22px rgba(25, 36, 70, 0.06);
  padding: 28px;
}

.detail-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e6eaf2;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.title-row h2 {
  font-size: 22px;
  margin: 0;
}

.importance-badge {
  display: inline-block;
  padding: 3px 10px;
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

.meta-row {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #667085;
  margin-bottom: 10px;
}

.tags {
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

.section {
  margin-bottom: 20px;
}

.section h3 {
  font-size: 15px;
  color: #344054;
  margin: 0 0 8px;
}

.section p {
  margin: 0;
  color: #344054;
  line-height: 1.7;
  font-size: 14px;
}

.section ul {
  margin: 0;
  padding-left: 20px;
}

.section li {
  color: #344054;
  font-size: 14px;
  line-height: 1.8;
}

.list-input {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.edit-mode .el-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
