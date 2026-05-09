<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getKnowledgeBases,
  createKnowledgeBase,
  updateKnowledgeBase,
  deleteKnowledgeBase,
  type KnowledgeBase,
  type KnowledgeBaseCreate,
  type KnowledgeBaseUpdate,
} from '../api/knowledgeBase'

const knowledgeBases = ref<KnowledgeBase[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = ref<KnowledgeBaseCreate>({ name: '', description: '' })

async function fetchList() {
  try {
    knowledgeBases.value = await getKnowledgeBases()
  } catch {
    ElMessage.error('加载知识库列表失败')
  }
}

function openCreate() {
  editingId.value = null
  form.value = { name: '', description: '' }
  dialogVisible.value = true
}

function openEdit(kb: KnowledgeBase) {
  editingId.value = kb.id
  form.value = { name: kb.name, description: kb.description || '' }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name.trim()) {
    ElMessage.warning('知识库名称不能为空')
    return
  }
  try {
    if (editingId.value) {
      await updateKnowledgeBase(editingId.value, form.value as KnowledgeBaseUpdate)
      ElMessage.success('知识库已更新')
    } else {
      await createKnowledgeBase(form.value)
      ElMessage.success('知识库已创建')
    }
    dialogVisible.value = false
    await fetchList()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

async function handleDelete(kb: KnowledgeBase) {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识库「${kb.name}」吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
    await deleteKnowledgeBase(kb.id)
    ElMessage.success('知识库已删除')
    await fetchList()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(fetchList)
</script>

<template>
  <div class="page">
    <div class="header">
      <div class="title">
        <h2>知识库管理</h2>
        <p>按科目或备考方向管理资料和知识点。</p>
      </div>
      <el-button type="primary" @click="openCreate">＋ 新建知识库</el-button>
    </div>

    <div v-if="knowledgeBases.length === 0" class="empty">
      暂无知识库，点击「新建知识库」开始。
    </div>

    <div v-else class="card-grid">
      <div v-for="kb in knowledgeBases" :key="kb.id" class="kb-card">
        <div class="kb-info">
          <h3>{{ kb.name }}</h3>
          <p v-if="kb.description">{{ kb.description }}</p>
          <div class="kb-meta">
            <span>资料 {{ kb.material_count }} 篇</span>
            <span>知识点 {{ kb.knowledge_point_count }} 个</span>
          </div>
        </div>
        <div class="kb-actions">
          <el-button size="small" @click="openEdit(kb)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(kb)">删除</el-button>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑知识库' : '新建知识库'" width="480px">
      <el-form label-position="top">
        <el-form-item label="知识库名称">
          <el-input v-model="form.name" placeholder="例如：三支一扶" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="描述（选填）">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="简要描述这个知识库的内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 30px 42px;
}

.header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 24px;
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

.empty {
  text-align: center;
  padding: 60px 0;
  color: var(--muted);
  font-size: 15px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 18px;
}

.kb-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.kb-info h3 {
  font-size: 17px;
  margin: 0 0 6px;
}

.kb-info p {
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.5;
}

.kb-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--muted);
}

.kb-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
