<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAudioFiles, deleteAudioFile } from '../api/audio'
import { getKnowledgeBasesForSelect } from '../api/material'
import type { AudioFile } from '../api/audio'
import type { KnowledgeBase } from '../api/material'

const audioFiles = ref<AudioFile[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const filterKB = ref<number | undefined>()
const filterStatus = ref<string | undefined>()

function getAudioUrl(fileUrl: string | null): string {
  if (!fileUrl) return ''
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}${fileUrl}`
}

async function fetchData() {
  loading.value = true
  try {
    audioFiles.value = await getAudioFiles({
      knowledge_base_id: filterKB.value,
      status: filterStatus.value,
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
      `确定要删除音频「${audio.title}」吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await deleteAudioFile(audio.id)
    audioFiles.value = audioFiles.value.filter((a) => a.id !== audio.id)
    ElMessage.success('音频已删除')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

function statusLabel(status: string) {
  return { success: '成功', failed: '失败', pending: '生成中' }[status] || status
}

function statusClass(status: string) {
  return { success: 'ok', failed: 'error', pending: 'loading' }[status] || ''
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
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && audioFiles.length === 0" class="empty">
      暂无音频，请在知识点详情页生成音频。
    </div>

    <!-- 音频列表 -->
    <div v-else class="audio-list">
      <div v-for="audio in audioFiles" :key="audio.id" class="audio-card">
        <div class="audio-info">
          <div class="audio-title">{{ audio.title }}</div>
          <div class="audio-meta">
            <span class="status-badge" :class="statusClass(audio.status)">
              {{ statusLabel(audio.status) }}
            </span>
            <span class="time">{{ audio.created_at }}</span>
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

.audio-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.audio-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 22px rgba(25, 36, 70, 0.06);
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
  color: #182033;
  margin-bottom: 8px;
}

.audio-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.ok {
  background: #e9fbf5;
  color: #087a59;
}

.status-badge.error {
  background: #fff0f0;
  color: #a61b1b;
}

.status-badge.loading {
  background: #fff8e7;
  color: #a06000;
}

.time {
  font-size: 12px;
  color: #667085;
}

.error-msg {
  margin-top: 6px;
  font-size: 12px;
  color: #a61b1b;
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
