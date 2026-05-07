<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { createMaterial, getKnowledgeBasesForSelect } from '../api/material'
import type { KnowledgeBase } from '../api/material'

const form = reactive({
  knowledge_base_id: undefined as number | undefined,
  title: '',
  content: '',
  source: '',
  note: '',
})

const knowledgeBases = ref<KnowledgeBase[]>([])
const saving = ref(false)

async function fetchKnowledgeBases() {
  try {
    knowledgeBases.value = await getKnowledgeBasesForSelect()
  } catch {
    ElMessage.error('加载知识库列表失败')
  }
}

async function handleSave() {
  if (!form.knowledge_base_id) {
    ElMessage.warning('请选择知识库')
    return
  }
  if (!form.title.trim()) {
    ElMessage.warning('资料标题不能为空')
    return
  }
  if (!form.content.trim()) {
    ElMessage.warning('资料正文不能为空')
    return
  }
  saving.value = true
  try {
    await createMaterial({
      knowledge_base_id: form.knowledge_base_id,
      title: form.title.trim(),
      content: form.content,
      source: form.source.trim() || undefined,
      note: form.note.trim() || undefined,
    })
    ElMessage.success('资料保存成功')
    resetForm()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败，请重试')
  } finally {
    saving.value = false
  }
}

function resetForm() {
  form.knowledge_base_id = undefined
  form.title = ''
  form.content = ''
  form.source = ''
  form.note = ''
}

onMounted(fetchKnowledgeBases)
</script>

<template>
  <div class="page">
    <div class="header">
      <div class="title">
        <h2>资料导入</h2>
        <p>粘贴学习资料，保存后可用于 AI 提取知识点。</p>
      </div>
    </div>

    <div class="form-card">
      <div class="form-row">
        <div class="form-item">
          <label>所属知识库 <span class="required">*</span></label>
          <el-select v-model="form.knowledge_base_id" placeholder="请选择知识库" style="width: 100%">
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id"
            />
          </el-select>
        </div>
        <div class="form-item">
          <label>资料来源</label>
          <el-input v-model="form.source" placeholder="例如：手动粘贴、教材名称" />
        </div>
      </div>

      <div class="form-item">
        <label>资料标题 <span class="required">*</span></label>
        <el-input v-model="form.title" placeholder="例如：政府社会职能" maxlength="200" show-word-limit />
      </div>

      <div class="form-item">
        <label>资料正文 <span class="required">*</span></label>
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="12"
          placeholder="在此粘贴学习资料内容..."
          resize="vertical"
        />
        <div class="tip">建议单次导入 5000～10000 字以内。内容太长可以分段导入。</div>
      </div>

      <div class="form-item">
        <label>备注</label>
        <el-input v-model="form.note" type="textarea" :rows="2" placeholder="选填，记录资料来源或其他说明" />
      </div>

      <div class="actions">
        <el-button @click="resetForm">清空</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存资料</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 30px 42px;
  max-width: 900px;
}

.header {
  margin-bottom: 24px;
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

.form-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 22px rgba(25, 36, 70, 0.06);
  padding: 28px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-item {
  margin-bottom: 18px;
}

.form-item label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #344054;
  margin-bottom: 6px;
}

.required {
  color: #ef4444;
}

.tip {
  margin-top: 6px;
  font-size: 12px;
  color: #667085;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
