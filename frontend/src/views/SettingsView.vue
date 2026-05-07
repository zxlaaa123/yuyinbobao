<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettings, saveSettings, testAiConnection, testTtsConnection } from '../api/setting'

const form = reactive({
  AI_PROVIDER: '',
  AI_API_KEY: '',
  AI_BASE_URL: '',
  AI_MODEL: '',
  AI_TEMPERATURE: 0.3,
  AI_TIMEOUT: 60,
  TTS_PROVIDER: '',
  XIAOMI_TTS_API_KEY: '',
  XIAOMI_TTS_BASE_URL: '',
  XIAOMI_TTS_VOICE: '',
  XIAOMI_TTS_FORMAT: '',
  XIAOMI_TTS_SPEED: 1.0,
})

const saving = ref(false)
const testingAi = ref(false)
const testingTts = ref(false)
const aiTestResult = ref<{ success: boolean; message: string } | null>(null)
const ttsTestResult = ref<{ success: boolean; message: string } | null>(null)

async function fetchSettings() {
  try {
    const data = await getSettings()
    Object.assign(form, data)
  } catch {
    ElMessage.error('加载设置失败')
  }
}

async function handleSave() {
  saving.value = true
  aiTestResult.value = null
  ttsTestResult.value = null
  try {
    await saveSettings(form)
    ElMessage.success('设置已保存')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleTestAi() {
  testingAi.value = true
  aiTestResult.value = null
  try {
    const result = await testAiConnection()
    aiTestResult.value = result
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.warning(result.message)
    }
  } catch (e: any) {
    aiTestResult.value = { success: false, message: e.response?.data?.detail || '测试失败' }
    ElMessage.error(aiTestResult.value.message)
  } finally {
    testingAi.value = false
  }
}

async function handleTestTts() {
  testingTts.value = true
  ttsTestResult.value = null
  try {
    const result = await testTtsConnection()
    ttsTestResult.value = result
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.warning(result.message)
    }
  } catch (e: any) {
    ttsTestResult.value = { success: false, message: e.response?.data?.detail || '测试失败' }
    ElMessage.error(ttsTestResult.value.message)
  } finally {
    testingTts.value = false
  }
}

onMounted(fetchSettings)
</script>

<template>
  <div class="page">
    <div class="header">
      <div class="title">
        <h2>设置</h2>
        <p>配置 AI 模型接口和 TTS 音频服务。</p>
      </div>
    </div>

    <div class="settings-grid">
      <!-- AI 模型设置 -->
      <div class="settings-card">
        <div class="card-title">
          <h3>AI 模型设置</h3>
          <p>配置 OpenAI-compatible 模型接口。</p>
        </div>
        <el-form label-position="top">
          <el-form-item label="AI Provider">
            <el-select v-model="form.AI_PROVIDER" placeholder="选择 Provider" style="width: 100%">
              <el-option label="DeepSeek" value="deepseek" />
              <el-option label="OpenAI" value="openai" />
              <el-option label="Xiaomi MiMo" value="xiaomi" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>
          <el-form-item label="AI API Key">
            <el-input v-model="form.AI_API_KEY" placeholder="sk-****" show-password />
          </el-form-item>
          <el-form-item label="AI Base URL">
            <el-input v-model="form.AI_BASE_URL" placeholder="https://api.deepseek.com" />
          </el-form-item>
          <el-form-item label="AI Model">
            <el-input v-model="form.AI_MODEL" placeholder="deepseek-chat" />
          </el-form-item>
          <el-form-item label="Temperature">
            <el-input-number v-model="form.AI_TEMPERATURE" :min="0" :max="2" :step="0.1" style="width: 100%" />
          </el-form-item>
          <el-form-item label="Timeout (秒)">
            <el-input-number v-model="form.AI_TIMEOUT" :min="10" :max="300" style="width: 100%" />
          </el-form-item>
        </el-form>
        <div class="card-actions">
          <el-button type="primary" :loading="saving" @click="handleSave">保存 AI 设置</el-button>
          <el-button :loading="testingAi" @click="handleTestAi">测试 AI 连接</el-button>
        </div>
        <div v-if="aiTestResult" class="test-result" :class="aiTestResult.success ? 'ok' : 'fail'">
          {{ aiTestResult.success ? '✓' : '✗' }} {{ aiTestResult.message }}
        </div>
      </div>

      <!-- TTS 音频设置 -->
      <div class="settings-card">
        <div class="card-title">
          <h3>TTS 音频设置</h3>
          <p>V1 支持 mock 模式，并预留小米 TTS。</p>
        </div>
        <el-form label-position="top">
          <el-form-item label="TTS Provider">
            <el-select v-model="form.TTS_PROVIDER" placeholder="选择 Provider" style="width: 100%">
              <el-option label="Mock（占位）" value="mock" />
              <el-option label="小米 TTS" value="xiaomi" />
            </el-select>
          </el-form-item>
          <el-form-item label="小米 TTS API Key">
            <el-input v-model="form.XIAOMI_TTS_API_KEY" placeholder="tp-****" show-password />
          </el-form-item>
          <el-form-item label="小米 TTS Base URL">
            <el-input v-model="form.XIAOMI_TTS_BASE_URL" placeholder="https://token-plan-cn.xiaomimimo.com/v1" />
          </el-form-item>
          <el-form-item label="音色">
            <el-select v-model="form.XIAOMI_TTS_VOICE" placeholder="选择音色" style="width: 100%">
              <el-option label="MiMo-默认" value="mimo_default" />
              <el-option label="冰糖" value="冰糖" />
              <el-option label="茉莉" value="茉莉" />
              <el-option label="苏打" value="苏打" />
              <el-option label="白桦" value="白桦" />
              <el-option label="Mia" value="Mia" />
              <el-option label="Chloe" value="Chloe" />
              <el-option label="Milo" value="Milo" />
              <el-option label="Dean" value="Dean" />
            </el-select>
          </el-form-item>
          <el-form-item label="音频格式">
            <el-select v-model="form.XIAOMI_TTS_FORMAT" style="width: 100%">
              <el-option label="WAV" value="wav" />
              <el-option label="PCM16" value="pcm16" />
            </el-select>
          </el-form-item>
          <el-form-item label="语速">
            <el-input-number v-model="form.XIAOMI_TTS_SPEED" :min="0.5" :max="2" :step="0.1" style="width: 100%" />
          </el-form-item>
        </el-form>
        <div class="card-actions">
          <el-button type="primary" :loading="saving" @click="handleSave">保存 TTS 设置</el-button>
          <el-button :loading="testingTts" @click="handleTestTts">测试 TTS 连接</el-button>
        </div>
        <div v-if="ttsTestResult" class="test-result" :class="ttsTestResult.success ? 'ok' : 'fail'">
          {{ ttsTestResult.success ? '✓' : '✗' }} {{ ttsTestResult.message }}
        </div>
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

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.settings-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(230, 234, 242, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 22px rgba(25, 36, 70, 0.06);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-title h3 {
  font-size: 18px;
  margin: 0 0 4px;
}

.card-title p {
  margin: 0;
  color: #667085;
  font-size: 13px;
}

.el-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}

.test-result {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.5;
}

.test-result.ok {
  background: #e9fbf5;
  color: #087a59;
}

.test-result.fail {
  background: #fff0f0;
  color: #a61b1b;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
