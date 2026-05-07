<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKnowledgePoint, updateKnowledgePoint, deleteKnowledgePoint } from '../api/knowledgePoint'
import type { KnowledgePoint, KnowledgePointUpdate } from '../api/knowledgePoint'
import { generateQuestions } from '../api/question'
import type { GeneratedQuestion } from '../api/question'
import { generateAudio, getAudioFiles } from '../api/audio'

function getAudioUrl(fileUrl: string | null): string {
  if (!fileUrl) return ''
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}${fileUrl}`
}

const route = useRoute()
const router = useRouter()
const kp = ref<KnowledgePoint | null>(null)
const loading = ref(false)
const editing = ref(false)
const editForm = reactive<KnowledgePointUpdate>({})

// 音频
const audioLoading = ref(false)
const audioFileUrl = ref<string | null>(null)
const audioError = ref<string | null>(null)

async function loadExistingAudio() {
  if (!kp.value) return
  try {
    const files = await getAudioFiles({ knowledge_point_id: kp.value.id })
    // 找最近一个成功的音频
    const successFile = files.find((f: any) => f.status === 'success')
    if (successFile && successFile.file_url) {
      audioFileUrl.value = successFile.file_url
    }
  } catch {
    // 忽略加载错误
  }
}

async function handleGenerateAudio() {
  if (!kp.value) return
  audioLoading.value = true
  audioError.value = null
  try {
    const result = await generateAudio(kp.value.id)
    audioFileUrl.value = result.file_url
    ElMessage.success('音频生成成功')
  } catch (e: any) {
    audioError.value = e.response?.data?.detail || '音频生成失败'
    ElMessage.error(audioError.value || '音频生成失败')
  } finally {
    audioLoading.value = false
  }
}

// 生成题目
const genDialogVisible = ref(false)
const genCount = ref(5)
const genTypes = ref<string[]>(['single_choice'])
const genLoading = ref(false)
const genResult = ref<{ created_count: number; skipped_count: number; questions?: GeneratedQuestion[] } | null>(null)

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

async function handleGenerateQuestions() {
  if (!kp.value) return
  if (genCount.value < 1 || genCount.value > 20) {
    ElMessage.warning('题目数量必须在 1 到 20 之间')
    return
  }
  if (genTypes.value.length === 0) {
    ElMessage.warning('请至少选择一种题型')
    return
  }
  genLoading.value = true
  genResult.value = null
  try {
    const result = await generateQuestions(kp.value.id, genTypes.value, genCount.value)
    genResult.value = result
    ElMessage.success(`已生成 ${result.created_count} 道题`)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '生成失败，请重试')
  } finally {
    genLoading.value = false
  }
}

onMounted(async () => {
  await fetchData()
  await loadExistingAudio()
})
</script>

<template>
  <div class="page">
    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="kp">
      <!-- 顶部操作栏 -->
      <div class="top-bar">
        <el-button @click="router.push('/knowledge-points')">← 返回列表</el-button>
        <div class="actions">
          <el-button @click="handleGenerateAudio" :loading="audioLoading">生成音频</el-button>
          <el-button @click="genDialogVisible = true">生成题目</el-button>
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

      <!-- 音频区域 -->
      <div v-if="audioFileUrl || audioError || audioLoading" class="audio-section">
        <h3>🎧 知识点音频</h3>
        <div v-if="audioLoading" class="audio-loading">
          <div class="spinner"></div>
          <p>正在生成音频，请稍候...</p>
        </div>
        <div v-else-if="audioFileUrl" class="audio-player">
          <audio controls :src="getAudioUrl(audioFileUrl)" style="width: 100%"></audio>
        </div>
        <div v-else-if="audioError" class="audio-error">
          {{ audioError }}
        </div>
      </div>

      <!-- 生成题目弹窗 -->
      <el-dialog v-model="genDialogVisible" title="生成题目" width="480px">
        <el-form label-position="top">
          <el-form-item label="题型">
            <el-checkbox-group v-model="genTypes">
              <el-checkbox value="single_choice">单选题</el-checkbox>
              <el-checkbox value="true_false">判断题</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="题目数量">
            <el-input-number v-model="genCount" :min="1" :max="20" />
          </el-form-item>
        </el-form>

        <div v-if="genLoading" class="gen-loading">
          <div class="spinner"></div>
          <p>正在调用 AI 生成题目，请稍候...</p>
        </div>

        <div v-else-if="genResult" class="gen-result">
          <p>已生成 <strong>{{ genResult.created_count }}</strong> 道题</p>
          <p v-if="genResult.skipped_count" class="skipped">跳过 {{ genResult.skipped_count }} 道不合格题目</p>
          <div class="question-preview">
            <div v-for="q in genResult.questions" :key="q.id" class="q-item">
              <div class="q-stem">{{ q.stem }}</div>
              <div class="q-options">
                <span v-for="opt in (q.options || [])" :key="opt.key" class="q-opt" :class="{ answer: opt.key === q.answer }">
                  {{ opt.key }}. {{ opt.text }}
                </span>
              </div>
              <div class="q-answer">答案：{{ q.answer }} | 难度：{{ q.difficulty }}</div>
            </div>
          </div>
        </div>

        <template #footer>
          <el-button @click="genDialogVisible = false">关闭</el-button>
          <el-button type="primary" :loading="genLoading" @click="handleGenerateQuestions">生成</el-button>
        </template>
      </el-dialog>
    </div>

    <div v-else class="empty">知识点不存在</div>
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

.gen-loading {
  text-align: center;
  padding: 30px 0;
  color: #667085;
}

.gen-loading .spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e6eaf2;
  border-top-color: #4f7cff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.gen-result {
  text-align: center;
  padding: 20px 0;
  font-size: 15px;
}

.gen-result strong {
  color: #4f7cff;
  font-size: 18px;
}

.gen-result .skipped {
  color: #667085;
  font-size: 13px;
  margin-top: 6px;
}

/* 音频区域 */
.audio-section {
  margin-top: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 22px rgba(25, 36, 70, 0.06);
}

.audio-section h3 {
  font-size: 16px;
  margin: 0 0 12px;
}

.audio-loading {
  text-align: center;
  padding: 20px;
  color: #667085;
}

.audio-loading .spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e6eaf2;
  border-top-color: #4f7cff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 8px;
}

.audio-player audio {
  width: 100%;
  border-radius: 8px;
}

.audio-error {
  color: #a61b1b;
  font-size: 14px;
  padding: 10px;
  background: #fff0f0;
  border-radius: 8px;
}

.question-preview {
  margin-top: 16px;
  text-align: left;
  max-height: 300px;
  overflow-y: auto;
}

.q-item {
  border: 1px solid #e6eaf2;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 10px;
  background: #f8fbff;
}

.q-stem {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #182033;
}

.q-options {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.q-opt {
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 8px;
  color: #344054;
}

.q-opt.answer {
  background: #e9fbf5;
  color: #087a59;
  font-weight: 600;
}

.q-answer {
  font-size: 12px;
  color: #667085;
}

.empty {
  text-align: center;
  padding: 60px;
  color: #667085;
  font-size: 15px;
}
</style>
