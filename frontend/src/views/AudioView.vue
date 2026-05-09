<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAudioFiles, deleteAudioFile, retryAudioFile } from '../api/audio'
import { getKnowledgeBasesForSelect } from '../api/material'
import type { AudioFile } from '../api/audio'
import type { KnowledgeBase } from '../api/material'
import { getErrorMessage, isUserCanceled } from '../utils/error'

const audioFiles = ref<AudioFile[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const filterKB = ref<number | undefined>()
const filterStatus = ref<string | undefined>()
const filterType = ref<string | undefined>()
const filterFormat = ref<string | undefined>()
const retryingId = ref<number | null>(null)

function getAudioUrl(fileUrl: string | null): string {
  if (!fileUrl) return ''
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}${fileUrl}`
}

const filteredAudio = computed(() => {
  return audioFiles.value
})

async function fetchData() {
  loading.value = true
  try {
    audioFiles.value = await getAudioFiles({
      knowledge_base_id: filterKB.value,
      status: filterStatus.value,
      audio_type: filterType.value,
      audio_format: filterFormat.value,
    })
  } catch {
    ElMessage.error('加载音频列表失败')
  } finally {
    loading.value = false
  }
}

async function handleDelete(audio: AudioFile) {
  try {
    await ElMessageBox.confirm(
      `确定要删除音频「${audio.title}」吗？将删除数据库记录，并尝试同步删除本地音频文件。此操作不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    const result = await deleteAudioFile(audio.id)
    audioFiles.value = audioFiles.value.filter((a) => a.id !== audio.id)
    ElMessage.success(result.message || '音频已删除')
  } catch (e) {
    if (!isUserCanceled(e)) {
      ElMessage.error(getErrorMessage(e, '删除失败'))
    }
  }
}

async function handleRetry(audio: AudioFile) {
  retryingId.value = audio.id
  try {
    await retryAudioFile(audio.id)
    ElMessage.success('音频已重新生成')
    await fetchData()
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '重新生成失败'))
    await fetchData()
  } finally {
    retryingId.value = null
  }
}

function statusLabel(status: string) {
  return { success: '成功', failed: '失败', pending: '生成中' }[status] || status
}

function statusClass(status: string) {
  return { success: 'ok', failed: 'error', pending: 'loading' }[status] || ''
}

function typeLabel(type: string) {
  return {
    single: '单个知识点',
    collection: '合集音频',
    daily_review: '每日复习',
    wrong_question: '错题复习',
  }[type] || type
}

function formatFileSize(size: number | null): string {
  if (!size) return '-'
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

onMounted(async () => {
  knowledgeBases.value = await getKnowledgeBasesForSelect()
  await fetchData()
})
</script>

<template>
  <div class="page">
    <div class="header">
      <div class="title">
        <h2>音频播报</h2>
        <p>集中管理已生成的知识点音频，适合碎片时间复习。</p>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="filters">
      <el-select v-model="filterKB" placeholder="全部知识库" clearable style="width: 200px" @change="fetchData">
        <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.name" :value="kb.id" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="全部状态" clearable style="width: 160px" @change="fetchData">
        <el-option label="成功" value="success" />
        <el-option label="失败" value="failed" />
        <el-option label="生成中" value="pending" />
      </el-select>
      <el-select v-model="filterType" placeholder="全部类型" clearable style="width: 160px" @change="fetchData">
        <el-option label="单个知识点" value="single" />
        <el-option label="合集音频" value="collection" />
        <el-option label="每日复习" value="daily_review" />
        <el-option label="错题复习" value="wrong_question" />
      </el-select>
      <el-select v-model="filterFormat" placeholder="全部格式" clearable style="width: 140px" @change="fetchData">
        <el-option label="WAV" value="wav" />
        <el-option label="PCM16" value="pcm16" />
      </el-select>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && filteredAudio.length === 0" class="empty">
      暂无音频，请在知识点详情页生成音频。
    </div>

    <!-- 音频列表 -->
    <div v-else class="audio-list">
      <div v-for="audio in filteredAudio" :key="audio.id" class="audio-card">
        <div class="audio-info">
          <div class="audio-title">{{ audio.title }}</div>
          <div class="audio-meta">
            <span class="status-badge" :class="statusClass(audio.status)">
              {{ statusLabel(audio.status) }}
            </span>
            <span class="type-badge">{{ typeLabel(audio.audio_type) }}</span>
            <span class="type-badge">{{ (audio.audio_format || '-').toUpperCase() }}</span>
            <span class="time">{{ audio.created_at }}</span>
          </div>
          <div class="audio-detail">
            <span>Provider：{{ audio.provider || '-' }}</span>
            <span>音色：{{ audio.voice || '-' }}</span>
            <span>大小：{{ formatFileSize(audio.file_size) }}</span>
          </div>
          <div v-if="audio.error_message" class="error-msg">
            错误：{{ audio.error_message }}
          </div>
        </div>

        <div class="audio-player">
          <audio
            v-if="audio.status === 'success' && audio.file_url"
            controls
            :src="getAudioUrl(audio.file_url)"
            style="width: 100%"
          ></audio>
        </div>

        <div class="audio-actions">
          <el-button
            v-if="audio.status === 'failed'"
            size="small"
            type="primary"
            :loading="retryingId === audio.id"
            @click="handleRetry(audio)"
          >
            重新生成
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(audio)">删除</el-button>
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
  color: var(--muted);
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
  color: var(--muted);
  font-size: 15px;
}

.audio-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.audio-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.audio-info {
  flex: 0 0 200px;
}

.audio-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 8px;
}

.audio-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.ok {
  background: var(--success-bg);
  color: var(--success-text);
}

.status-badge.error {
  background: var(--danger-bg);
  color: var(--danger-text);
}

.status-badge.loading {
  background: var(--warning-bg);
  color: var(--warning-text);
}

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 12px;
  background: var(--panel-strong);
  color: var(--muted);
}

.audio-detail {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 8px;
  font-size: 12px;
  color: var(--muted);
}

.time {
  font-size: 12px;
  color: var(--muted);
}

.error-msg {
  margin-top: 6px;
  font-size: 12px;
  color: var(--danger-text);
}

.audio-player {
  flex: 1;
}

.audio-player audio {
  width: 100%;
  border-radius: 8px;
}

.audio-actions {
  flex-shrink: 0;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 700px) {
  .audio-card {
    flex-direction: column;
    align-items: stretch;
  }
  .audio-info {
    flex: none;
  }
}
</style>
