<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPracticeQuestions, submitAnswer } from '../api/practice'
import { createStudySession, finishStudySession } from '../api/studySession'
import { createPracticeSession } from '../api/practiceSession'
import { getKnowledgeBasesForSelect } from '../api/material'
import type { PracticeQuestion } from '../api/practice'
import type { StudySession } from '../api/studySession'
import type { KnowledgeBase } from '../api/material'
import { getErrorMessage } from '../utils/error'

type Phase = 'setup' | 'practicing' | 'finished'

const knowledgeBases = ref<KnowledgeBase[]>([])
const questions = ref<PracticeQuestion[]>([])
const currentIndex = ref(0)
const selectedAnswer = ref('')
const selectedAnswers = ref<string[]>([])
const textAnswer = ref('')
const answered = ref(false)
const answerResult = ref<any>(null)
const phase = ref<Phase>('setup')
const correctCount = ref(0)
const wrongCount = ref(0)
const sessionId = ref<number | null>(null)
const finishedSession = ref<StudySession | null>(null)
const sessionStartedAt = ref<Date | null>(null)
const savedPracticeSessionId = ref<number | null>(null)
const practiceItems = ref<Array<{
  question_id: number
  knowledge_point_id?: number
  user_answer?: string
  is_correct: boolean
  duration_seconds: number
}>>([])

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
    const session = await createStudySession({
      knowledge_base_id: selKB.value,
      knowledge_point_id: getSessionKnowledgePointId(),
      total_count: questions.value.length,
    })
    sessionId.value = session.id
    finishedSession.value = null
    currentIndex.value = 0
    selectedAnswer.value = ''
    selectedAnswers.value = []
    textAnswer.value = ''
    sessionStartedAt.value = new Date()
    savedPracticeSessionId.value = null
    practiceItems.value = []
    answered.value = false
    answerResult.value = null
    correctCount.value = 0
    wrongCount.value = 0
    phase.value = 'practicing'
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '获取题目失败'))
  }
}

function getSessionKnowledgePointId(): number | undefined {
  const ids = Array.from(new Set(questions.value.map((q) => q.knowledge_point_id).filter(Boolean)))
  return ids.length === 1 ? ids[0] : undefined
}

function questionTypeLabel(type: string) {
  const map: Record<string, string> = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    true_false: '判断题',
    fill_blank: '填空题',
    short_answer: '简答题',
  }
  return map[type] || type || '单选题'
}

function isChoiceQuestion(question?: PracticeQuestion | null) {
  return ['single_choice', 'true_false'].includes(question?.question_type || 'single_choice')
}

function isMultipleChoiceQuestion(question?: PracticeQuestion | null) {
  return question?.question_type === 'multiple_choice'
}

function isTextQuestion(question?: PracticeQuestion | null) {
  return ['fill_blank', 'short_answer'].includes(question?.question_type || '')
}

function currentUserAnswer() {
  if (isMultipleChoiceQuestion(currentQuestion.value)) {
    return [...selectedAnswers.value].sort().join(',')
  }
  if (isTextQuestion(currentQuestion.value)) {
    return textAnswer.value.trim()
  }
  return selectedAnswer.value
}

function hasAnswer() {
  return Boolean(currentUserAnswer())
}

function toggleMultiAnswer(key: string) {
  if (answered.value) return
  if (selectedAnswers.value.includes(key)) {
    selectedAnswers.value = selectedAnswers.value.filter((item) => item !== key)
  } else {
    selectedAnswers.value = [...selectedAnswers.value, key]
  }
}

function answerParts(answer: string | undefined | null) {
  return (answer || '').split(',').map((item) => item.trim()).filter(Boolean)
}

function isCorrectOption(key: string) {
  return answerParts(answerResult.value?.correct_answer).includes(key)
}

function isWrongSelectedOption(key: string) {
  if (!answered.value || answerResult.value?.is_correct) return false
  if (isMultipleChoiceQuestion(currentQuestion.value)) {
    return selectedAnswers.value.includes(key) && !isCorrectOption(key)
  }
  return selectedAnswer.value === key && !isCorrectOption(key)
}

function upsertPracticeItem(question: PracticeQuestion, userAnswer: string, isCorrect: boolean) {
  const payload = {
    question_id: question.id,
    knowledge_point_id: question.knowledge_point_id,
    user_answer: userAnswer,
    is_correct: isCorrect,
    duration_seconds: 0,
  }
  const idx = practiceItems.value.findIndex((item) => item.question_id === question.id)
  if (idx >= 0) {
    practiceItems.value[idx] = payload
  } else {
    practiceItems.value.push(payload)
  }
}

async function handleSubmit() {
  const answer = currentUserAnswer()
  if (!answer) {
    ElMessage.warning(isTextQuestion(currentQuestion.value) ? '请填写答案' : '请选择答案')
    return
  }
  if (!currentQuestion.value) return
  try {
    const result = await submitAnswer(currentQuestion.value.id, answer)
    upsertPracticeItem(currentQuestion.value, answer, result.is_correct)
    answerResult.value = result
    answered.value = true
    if (result.is_correct) {
      correctCount.value++
    } else {
      wrongCount.value++
    }
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '提交失败'))
  }
}

async function finishCurrentSession() {
  const startedAt = sessionStartedAt.value || new Date()
  const endedAt = new Date()
  const durationSeconds = Math.max(0, Math.floor((endedAt.getTime() - startedAt.getTime()) / 1000))

  if (sessionId.value && !finishedSession.value) {
    try {
      finishedSession.value = await finishStudySession(sessionId.value, {
        total_count: totalQuestions.value,
        correct_count: correctCount.value,
      })
    } catch (e) {
      ElMessage.error(getErrorMessage(e, '保存练习记录失败'))
    }
  }

  if (savedPracticeSessionId.value || practiceItems.value.length === 0) {
    return
  }

  try {
    const title = `练习会话 ${new Date().toLocaleString()}`
    const session = await createPracticeSession({
      mode: 'normal',
      title,
      knowledge_base_id: selKB.value,
      items: practiceItems.value,
      duration_seconds: durationSeconds,
      started_at: startedAt.toISOString(),
      ended_at: endedAt.toISOString(),
    })
    savedPracticeSessionId.value = session.id
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '保存会话明细失败'))
  }
}

async function nextQuestion() {
  if (currentIndex.value + 1 >= totalQuestions.value) {
    await finishCurrentSession()
    phase.value = 'finished'
    return
  }
  currentIndex.value++
  selectedAnswer.value = ''
  selectedAnswers.value = []
  textAnswer.value = ''
  answered.value = false
  answerResult.value = null
}

function resetPractice() {
  phase.value = 'setup'
  questions.value = []
  currentIndex.value = 0
  selectedAnswer.value = ''
  selectedAnswers.value = []
  textAnswer.value = ''
  answered.value = false
  answerResult.value = null
  correctCount.value = 0
  wrongCount.value = 0
  sessionId.value = null
  finishedSession.value = null
  sessionStartedAt.value = null
  savedPracticeSessionId.value = null
  practiceItems.value = []
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
            <el-option label="多选题" value="multiple_choice" />
            <el-option label="判断题" value="true_false" />
            <el-option label="填空题" value="fill_blank" />
            <el-option label="简答题" value="short_answer" />
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
        <div class="q-type">{{ questionTypeLabel(currentQuestion.question_type) }}</div>
        <div class="q-stem">{{ currentQuestion.stem }}</div>

        <!-- 单选 / 判断 -->
        <div v-if="isChoiceQuestion(currentQuestion)" class="options">
          <div
            v-for="opt in currentQuestion.options"
            :key="opt.key"
            class="option"
            :class="{
              selected: selectedAnswer === opt.key,
              correct: answered && isCorrectOption(opt.key),
              wrong: isWrongSelectedOption(opt.key),
            }"
            :disabled="answered"
            @click="!answered && (selectedAnswer = opt.key)"
          >
            <span class="opt-key">{{ opt.key }}</span>
            <span class="opt-text">{{ opt.text }}</span>
          </div>
        </div>

        <!-- 多选 -->
        <div v-else-if="isMultipleChoiceQuestion(currentQuestion)" class="options">
          <div
            v-for="opt in currentQuestion.options"
            :key="opt.key"
            class="option"
            :class="{
              selected: selectedAnswers.includes(opt.key),
              correct: answered && isCorrectOption(opt.key),
              wrong: isWrongSelectedOption(opt.key),
            }"
            :disabled="answered"
            @click="toggleMultiAnswer(opt.key)"
          >
            <span class="opt-key">{{ opt.key }}</span>
            <span class="opt-text">{{ opt.text }}</span>
          </div>
        </div>

        <!-- 填空 / 简答 -->
        <div v-else class="text-answer">
          <el-input
            v-model="textAnswer"
            :type="currentQuestion.question_type === 'short_answer' ? 'textarea' : 'text'"
            :autosize="{ minRows: 4, maxRows: 8 }"
            :disabled="answered"
            :placeholder="currentQuestion.question_type === 'short_answer' ? '请输入简答内容' : '请输入填空答案'"
          />
        </div>
      </div>

      <!-- 结果 -->
      <div v-if="answered && answerResult" class="result-area">
        <div class="result-badge" :class="answerResult.is_correct ? 'ok' : 'bad'">
          {{ answerResult.is_correct ? '✓ 回答正确' : '✗ 回答错误' }}
        </div>
        <div class="result-info">
          <p>正确答案：<strong>{{ answerResult.correct_answer }}</strong></p>
          <p v-if="currentQuestion.question_type === 'short_answer' && answerResult.reference_answer" class="reference">
            参考答案：{{ answerResult.reference_answer }}
          </p>
          <p v-if="answerResult.analysis" class="analysis">解析：{{ answerResult.analysis }}</p>
        </div>
      </div>

      <!-- 操作 -->
      <div class="actions">
        <el-button v-if="!answered" type="primary" :disabled="!hasAnswer()" @click="handleSubmit">
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
  color: var(--muted);
  font-size: 14px;
}

.setup-card,
.practice-card,
.result-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
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
  background: var(--card-2);
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 24px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--green), var(--gold));
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
  color: var(--text);
}

/* 题目 */
.q-type {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
  background: var(--panel-strong);
  color: var(--green);
  margin-bottom: 12px;
}

.q-stem {
  font-size: 17px;
  font-weight: 600;
  color: var(--text);
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

.text-answer {
  margin-bottom: 20px;
}

.option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--card);
  cursor: pointer;
  transition: all 0.15s;
}

.option:hover:not([disabled]) {
  border-color: var(--green);
  background: var(--panel-strong);
}

.option.selected {
  border-color: var(--green);
  background: var(--panel-strong);
  font-weight: 600;
}

.option.correct {
  border-color: var(--green);
  background: var(--success-bg);
  color: var(--success-text);
}

.option.wrong {
  border-color: var(--danger);
  background: var(--danger-bg);
  color: var(--danger-text);
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
  background: var(--success-bg);
  color: var(--success-text);
}

.result-badge.bad {
  background: var(--danger-bg);
  color: var(--danger-text);
}

.result-info p {
  margin: 4px 0;
  font-size: 14px;
  color: var(--text);
}

.result-info .analysis {
  color: var(--muted);
  line-height: 1.6;
}

.result-info .reference {
  color: var(--text);
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
  color: var(--muted);
}

.stat-item.correct b {
  color: var(--green);
}

.stat-item.wrong b {
  color: var(--danger);
}

.stat-item.rate b {
  color: var(--gold);
}
</style>
