<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardSummary } from '../api/dashboard'
import type { DashboardSummary } from '../api/dashboard'

const router = useRouter()
const summary = ref<DashboardSummary | null>(null)
const loading = ref(true)

const stats = [
  { key: 'knowledge_base_count', label: '知识库', icon: '📚', color: 0 },
  { key: 'material_count', label: '学习资料', icon: '📄', color: 1 },
  { key: 'knowledge_point_count', label: '知识点', icon: '🧠', color: 2 },
  { key: 'question_count', label: '练习题', icon: '✅', color: 3 },
  { key: 'wrong_question_count', label: '错题', icon: '📌', color: 4 },
  { key: 'audio_count', label: '音频', icon: '🎧', color: 5 },
]

async function fetchSummary() {
  try {
    summary.value = await getDashboardSummary()
  } catch {
    summary.value = {
      knowledge_base_count: 0,
      material_count: 0,
      knowledge_point_count: 0,
      question_count: 0,
      wrong_question_count: 0,
      audio_count: 0,
    }
  } finally {
    loading.value = false
  }
}

function goTo(path: string) {
  router.push(path)
}

onMounted(fetchSummary)
</script>

<template>
  <div class="dashboard">
    <!-- Hero 区域 -->
    <div class="hero-card">
      <h3>把学习资料变成知识点、题目和音频</h3>
      <p>适合三支一扶、公基、时政、管理学、法律、经济和古文复习。粘贴资料后，系统可以自动提取知识点、练习题，并生成可播放的复习音频。</p>
      <div class="hero-actions">
        <el-button type="primary" @click="goTo('/materials/import')">开始导入资料</el-button>
        <el-button @click="goTo('/practice')">进入刷题练习</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div
        v-for="stat in stats"
        :key="stat.key"
        class="stat-card"
        :class="'color-' + stat.color"
        @click="goTo(stat.key === 'knowledge_base_count' ? '/knowledge-bases' : stat.key === 'material_count' ? '/materials/import' : stat.key === 'knowledge_point_count' ? '/knowledge-points' : stat.key === 'question_count' ? '/practice' : stat.key === 'wrong_question_count' ? '/wrong-questions' : '/audio')"
      >
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-value">{{ loading ? '-' : summary ? summary[stat.key as keyof DashboardSummary] : 0 }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Hero */
.hero-card {
  background: linear-gradient(135deg, rgba(79, 124, 255, 0.95), rgba(124, 58, 237, 0.92));
  color: #fff;
  border-radius: 24px;
  padding: 40px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 18px 45px rgba(79, 124, 255, 0.25);
}

.hero-card::after {
  content: "";
  position: absolute;
  width: 300px;
  height: 300px;
  right: -92px;
  top: -94px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}

.hero-card::before {
  content: "";
  position: absolute;
  width: 180px;
  height: 180px;
  right: 90px;
  bottom: -80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.13);
}

.hero-card > * {
  position: relative;
  z-index: 1;
}

.hero-card h3 {
  font-size: 26px;
  letter-spacing: -0.03em;
  margin: 0 0 12px;
  color: #fff;
}

.hero-card p {
  opacity: 0.92;
  line-height: 1.7;
  margin: 0 0 20px;
  font-size: 15px;
  max-width: 500px;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.hero-actions .el-button {
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 600;
}

.hero-actions .el-button--primary {
  background: #fff;
  color: #4f7cff;
  border-color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.hero-actions .el-button:not(.el-button--primary) {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(120px, 1fr));
  gap: 16px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
  box-shadow: 0 4px 12px rgba(25, 36, 70, 0.06);
}

.stat-card:hover {
  box-shadow: 0 8px 24px rgba(25, 36, 70, 0.12);
  transform: translateY(-2px);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: #edf3ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  font-size: 20px;
}

.stat-card.color-0 .stat-icon { background: #edf3ff; }
.stat-card.color-1 .stat-icon { background: #f3ecff; }
.stat-card.color-2 .stat-icon { background: #e9fbf5; }
.stat-card.color-3 .stat-icon { background: #fff8e7; }
.stat-card.color-4 .stat-icon { background: #fff0f0; }
.stat-card.color-5 .stat-icon { background: #edf3ff; }

.stat-value {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: #182033;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #667085;
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
