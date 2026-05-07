<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPracticeQuestions, submitAnswer } from '../api/practice'
import { getKnowledgeBasesForSelect } from '../api/material'
import type { PracticeQuestion } from '../api/practice'
import type { KnowledgeBase } from '../api/material'

type Phase = 'setup' | 'practicing' | 'finished'

const knowledgeBases = ref<KnowledgeBase[]>([])
const questions = ref<PracticeQuestion[]>([])
const currentIndex = ref(0)
const selectedAnswer = ref('')
const answered = ref(false)
const answerResult = ref<any>(null)
const phase = ref<Phase>('setup')
const correctCount = ref(0)
const wrongCount = ref(0)

// 设置
const selKB = ref<number | undefined>()
const selType = ref<string | undefined>()
const selCount = ref(10)

const currentQuestion = computed(() => questions.value[currentIndex.value] || null)
const totalQuestions = computed(() => questions.value.length)
const progress = computed(() => {
  if (totalQuestions.value === 0) return 0
  return Math.round(((currentIndex.value + (answered.value ? 1 : 0)) / totalQuestions.value) * 100)
})

async function fetchKBs() {
  try {
    knowledgeBases.value = await getKnowledgeBasesForSelect()
  } catch {
    ElMessage.error('加载知识库失败')
  }
}

async function startPractice() {
  if (!selKB.value) {
    ElMessage.warning('请选择知识库')
    return
  }
  try {
    questions.value = await getPracticeQuestions({
      knowledge_base_id: selKB.value,
      question_type: selType.value,
      count: selCount.value,
    })
    if (questions.value.length === 0) {
      ElMessage.warning('该知识库下暂无题目，请先生成题目')
      return
    }
    currentIndex.value = 0
    selectedAnswer.value = ''
    answered.value = false
    answerResult.value = null
    correctCount.value = 0
    wrongCount.value = 0
    phase.value = 'practicing'
  } catch {
    ElMessage.error('获取题目失败')
  }
}

async function handleSubmit() {
  if (!selectedAnswer.value) {
    ElMessage.warning('请选择答案')
    return
  }
  if (!currentQuestion.value) return
  try {
    const result = await submitAnswer(currentQuestion.value.id, selectedAnswer.value)
    answerResult.value = result
    answered.value = true
    if (result.is_correct) {
      correctCount.value++
    } else {
      wrongCount.value++
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  }
}

function nextQuestion() {
  if (currentIndex.value + 1 >= totalQuestions.value) {
    phase.value = 'finished'
    return
  }
  currentIndex.value++
  selectedAnswer.value = ''
  answered.value = false
  answerResult.value = null
}

function resetPractice() {
  phase.value = 'setup'
  questions.value = []
  currentIndex.value = 0
  selectedAnswer.value = ''
  answered.value = false
  answerResult.value = null
  correctCount.value = 0
  wrongCount.value = 0
}

onMounted(fetchKBs)
</script>

<template>
  <div class="page">
    <div class="header">
      <div class="title">
        <h2>刷题练习</h2>
        <p>选择题目进行练习，答错自动进入错题本。</p>
      </div>
    </div>

    <!-- 设置阶段 -->
    <div v-if="phase === 'setup'" class="setup-card">
      <el-form label-position="top">
        <el-form-item label="选择知识库">
          <el-select v-model="selKB" placeholder="请选择知识库" style="width: 100%">
            <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.name" :value="kb.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="selType" placeholder="全部题型" clearable style="width: 100%">
            <el-option label="单选题" value="single_choice" />
            <el-option label="判断题" value="true_false" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目数量">
          <el-input-number v-model="selCount" :min="1" :max="50" />
        </el-form-item>
      </el-form>
      <div class="actions">
        <el-button type="primary" @click="startPractice">开始练习</el-button>
      </div>
    </div>

    <!-- 练习阶段 -->
    <div v-else-if="phase === 'practicing' && currentQuestion" class="practice-card">
      <!-- 进度 -->
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        <span class="progress-text">{{ currentIndex + 1 }} / {{ totalQuestions }}</span>
      </div>

      <!-- 题目 -->
      <div class="question-area">
        <div class="q-type">{{ currentQuestion.question_type === 'single_choice' ? '单选题' : '判断题' }}</div>
        <div class="q-stem">{{ currentQuestion.stem }}</div>

        <!-- 选项 -->
        <div class="options">
          <div
            v-for="opt in currentQuestion.options"
            :key="opt.key"
            class="option"
            :class="{
              selected: selectedAnswer === opt.key,
              correct: answered && opt.key === answerResult?.correct_answer,
              wrong: answered && selectedAnswer === opt.key && !answerResult?.is_correct,
            }"
            :disabled="answered"
            @click="!answered && (selectedAnswer = opt.key)"
          >
            <span class="opt-key">{{ opt.key }}</span>
            <span class="opt-text">{{ opt.text }}</span>
          </div>
        </div>
      </div>

      <!-- 结果 -->
      <div v-if="answered && answerResult" class="result-area">
        <div class="result-badge" :class="answerResult.is_correct ? 'ok' : 'bad'">
          {{ answerResult.is_correct ? '✓ 回答正确' : '✗ 回答错误' }}
        </div>
        <div class="result-info">
          <p>正确答案：<strong>{{ answerResult.correct_answer }}</strong></p>
          <p v-if="answerResult.analysis" class="analysis">解析：{{ answerResult.analysis }}</p>
        </div>
      </div>

      <!-- 操作 -->
      <div class="actions">
        <el-button v-if="!answered" type="primary" :disabled="!selectedAnswer" @click="handleSubmit">
          提交答案
        </el-button>
        <el-button v-else-if="currentIndex + 1 < totalQuestions" type="primary" @click="nextQuestion">
          下一题
        </el-button>
        <el-button v-else type="primary" @click="nextQuestion">查看结果</el-button>
      </div>
    </div>

    <!-- 结束阶段 -->
    <div v-else-if="phase === 'finished'" class="result-card">
      <h3>练习完成</h3>
      <div class="stats">
        <div class="stat-item correct">
          <b>{{ correctCount }}</b>
          <span>正确</span>
        </div>
        <div class="stat-item wrong">
          <b>{{ wrongCount }}</b>
          <span>错误</span>
        </div>
        <div class="stat-item rate">
          <b>{{ totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0 }}%</b>
          <span>正确率</span>
        </div>
      </div>
      <div class="actions">
        <el-button @click="resetPractice">再来一次</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 30px 42px;
  max-width: 800px;
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

.setup-card,
.practice-card,
.result-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 22px rgba(25, 36, 70, 0.06);
  padding: 28px;
}

.setup-card .el-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 16px;
}

/* 进度条 */
.progress-bar {
  position: relative;
  height: 28px;
  background: #f0f2f5;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 24px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4f7cff, #7c3aed);
  border-radius: 14px;
  transition: width 0.3s;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 13px;
  font-weight: 600;
  color: #344054;
}

/* 题目 */
.q-type {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
  background: #edf3ff;
  color: #315de6;
  margin-bottom: 12px;
}

.q-stem {
  font-size: 17px;
  font-weight: 600;
  color: #182033;
  line-height: 1.6;
  margin-bottom: 20px;
}

/* 选项 */
.options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border: 1px solid #dbe2ee;
  border-radius: 14px;
  background: #fff;
  cursor: pointer;
  transition: all 0.15s;
}

.option:hover:not([disabled]) {
  border-color: #4f7cff;
  background: #edf3ff;
}

.option.selected {
  border-color: #4f7cff;
  background: #edf3ff;
  font-weight: 600;
}

.option.correct {
  border-color: #13b981;
  background: #e9fbf5;
  color: #087a59;
}

.option.wrong {
  border-color: #ef4444;
  background: #fff0f0;
  color: #a61b1b;
}

.option[disabled] {
  cursor: default;
}

.opt-key {
  font-weight: 700;
  min-width: 24px;
}

.opt-text {
  font-size: 14px;
}

/* 结果 */
.result-area {
  margin-bottom: 20px;
}

.result-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 99px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.result-badge.ok {
  background: #e9fbf5;
  color: #087a59;
}

.result-badge.bad {
  background: #fff0f0;
  color: #a61b1b;
}

.result-info p {
  margin: 4px 0;
  font-size: 14px;
  color: #344054;
}

.result-info .analysis {
  color: #667085;
  line-height: 1.6;
}

/* 结束统计 */
.result-card {
  text-align: center;
}

.result-card h3 {
  font-size: 22px;
  margin: 0 0 24px;
}

.stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-item b {
  font-size: 32px;
}

.stat-item span {
  font-size: 13px;
  color: #667085;
}

.stat-item.correct b {
  color: #13b981;
}

.stat-item.wrong b {
  color: #ef4444;
}

.stat-item.rate b {
  color: #4f7cff;
}
</style>
