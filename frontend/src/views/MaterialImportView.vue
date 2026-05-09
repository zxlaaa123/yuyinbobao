<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { createMaterial, getKnowledgeBasesForSelect, importAndExtract } from '../api/material'
import type { KnowledgeBase, ExtractResult } from '../api/material'

const form = reactive({
  knowledge_base_id: undefined as number | undefined,
  title: '',
  content: '',
  source: '',
  note: '',
  enable_split: false,
})

const knowledgeBases = ref<KnowledgeBase[]>([])
const saving = ref(false)
const extracting = ref(false)
const extractResult = ref<ExtractResult | null>(null)

async function fetchKnowledgeBases() {
  try {
    knowledgeBases.value = await getKnowledgeBasesForSelect()
  } catch {
    ElMessage.error('加载知识库列表失败')
  }
}

function validate(): boolean {
  if (!form.knowledge_base_id) {
    ElMessage.warning('请选择知识库')
    return false
  }
  if (!form.title.trim()) {
    ElMessage.warning('资料标题不能为空')
    return false
  }
  if (!form.content.trim()) {
    ElMessage.warning('资料正文不能为空')
    return false
  }
  return true
}

async function handleSave() {
  if (!validate()) return
  saving.value = true
  try {
    await createMaterial({
      knowledge_base_id: form.knowledge_base_id!,
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

async function handleSaveAndExtract() {
  if (!validate()) return
  extracting.value = true
  extractResult.value = null
  try {
    const result = await importAndExtract({
      knowledge_base_id: form.knowledge_base_id!,
      title: form.title.trim(),
      content: form.content,
      source: form.source.trim() || undefined,
      note: form.note.trim() || undefined,
      enable_split: form.enable_split,
    })
    extractResult.value = result
    const splitInfo = result.split_used ? `（分 ${result.segment_count} 段处理）` : ''
    ElMessage.success(`成功提取 ${result.created_count} 个知识点${splitInfo}`)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || 'AI 提取失败，请重试')
  } finally {
    extracting.value = false
  }
}

function resetForm() {
  form.knowledge_base_id = undefined
  form.title = ''
  form.content = ''
  form.source = ''
  form.note = ''
  form.enable_split = false
  extractResult.value = null
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

    <div class="two-col">
      <!-- 左侧表单 -->
      <div class="form-card">
        <div class="form-row">
          <div class="form-item">
            <label>所属知识库 <span class="required">*</span></label>
            <el-select v-model="form.knowledge_base_id" placeholder="请选择知识库" style="width: 100%">
              <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.name" :value="kb.id" />
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
          <div class="tip">
          建议单次导入 5000～10000 字以内。内容太长可开启分段提取。
          <el-checkbox v-model="form.enable_split" style="margin-left: 8px">长文本分段提取</el-checkbox>
        </div>
        </div>

        <div class="form-item">
          <label>备注</label>
          <el-input v-model="form.note" type="textarea" :rows="2" placeholder="选填，记录资料来源或其他说明" />
        </div>

        <div class="actions">
          <el-button @click="resetForm">清空</el-button>
          <el-button type="primary" :loading="saving || extracting" @click="handleSave">保存资料</el-button>
          <el-button type="success" :loading="extracting" @click="handleSaveAndExtract">保存并提取知识点</el-button>
        </div>
      </div>

      <!-- 右侧 AI 提取结果 -->
      <div class="result-card">
        <div class="result-title">
          <h3>AI 提取结果</h3>
          <p>点击左侧"保存并提取知识点"后，这里会显示结构化知识点。</p>
        </div>

        <div v-if="extracting" class="loading-box">
          <div class="spinner"></div>
          <p v-if="form.enable_split">正在分段提取知识点，可能需要几分钟，请耐心等待...</p>
          <p v-else>正在调用 AI 提取知识点，请稍候...</p>
        </div>

        <div v-else-if="extractResult" class="result-content">
          <div class="result-summary">
            本次提取 <strong>{{ extractResult.created_count }}</strong> 个知识点
            <span v-if="extractResult.skipped_count > 0" class="skipped-hint">
              跳过 {{ extractResult.skipped_count }} 个重复/无效
            </span>
          </div>
          <div v-if="extractResult.split_used" class="split-info">
            📄 长文本已分段处理：分 <strong>{{ extractResult.segment_count }}</strong> 段提取
          </div>
          <div class="kp-list">
            <div v-for="kp in extractResult.knowledge_points" :key="kp.id" class="kp-item">
              <div class="kp-name">{{ kp.title }}</div>
              <div class="kp-tags">
                <span v-for="tag in (kp.tags || [])" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-hint">
          暂无提取结果。粘贴一段资料后点击"保存并提取知识点"试试。
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

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-card,
.result-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
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
  color: var(--text);
  margin-bottom: 6px;
}

.required {
  color: var(--danger);
}

.tip {
  margin-top: 6px;
  font-size: 12px;
  color: var(--muted);
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 8px;
}

/* 右侧结果 */
.result-title h3 {
  font-size: 18px;
  margin: 0 0 6px;
}

.result-title p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}

.loading-box {
  text-align: center;
  padding: 40px 0;
  color: var(--muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--line);
  border-top-color: var(--green);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.result-summary {
  padding: 12px 16px;
  background: var(--panel-strong);
  border-radius: 12px;
  font-size: 14px;
  color: var(--green);
  margin-bottom: 12px;
}

.skipped-hint {
  margin-left: 8px;
  color: var(--warning-text);
  font-size: 13px;
}

.split-info {
  padding: 8px 16px;
  background: var(--warning-bg);
  border-radius: 12px;
  font-size: 13px;
  color: var(--warning-text);
  margin-bottom: 16px;
}

.kp-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.kp-item {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 12px 14px;
  background: var(--card);
}

.kp-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
}

.kp-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 99px;
  font-size: 12px;
  background: var(--panel-strong);
  color: var(--green);
}

.empty-hint {
  text-align: center;
  padding: 40px 0;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.6;
}

@media (max-width: 900px) {
  .two-col {
    grid-template-columns: 1fr;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
