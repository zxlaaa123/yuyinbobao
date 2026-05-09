<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettings, saveSettings, testAiConnection, testTtsConnection } from '../api/setting'
import { THEME_OPTIONS, applyTheme, getStoredTheme, type ThemeName } from '../utils/theme'

const form = reactive({
  AI_PROVIDER: '',
  AI_API_KEY: '',
  AI_BASE_URL: '',
  AI_MODEL: '',
  AI_TEMPERATURE: 0.3,
  AI_TIMEOUT: 60,
  AI_SEGMENT_SIZE: 3000,
  AI_MAX_SEGMENTS: 5,
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
const selectedTheme = ref<ThemeName>(getStoredTheme())

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
    // 敏感字段如果包含脱敏标记（****），不传该字段，避免覆盖真实 key
    const payload: Record<string, any> = { ...form }
    for (const key of ['AI_API_KEY', 'XIAOMI_TTS_API_KEY']) {
      const val = payload[key]
      if (typeof val === 'string' && val.includes('****')) {
        delete payload[key]
      }
    }
    await saveSettings(payload)
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

function handleThemeChange(value: ThemeName) {
  selectedTheme.value = value
  applyTheme(value)
  ElMessage.success(`已切换到${THEME_OPTIONS.find((item) => item.key === value)?.label || '新主题'}`)
}
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
      <div class="settings-card theme-card">
        <div class="card-title">
          <h3>界面主题</h3>
          <p>切换整站配色风格，选择会自动保存在当前浏览器。</p>
        </div>
        <div class="theme-list">
          <button
            v-for="theme in THEME_OPTIONS"
            :key="theme.key"
            class="theme-option"
            :class="{ active: selectedTheme === theme.key }"
            @click="handleThemeChange(theme.key)"
          >
            <div class="theme-swatch" :class="theme.key"></div>
            <div class="theme-meta">
              <strong>{{ theme.label }}</strong>
              <span>{{ theme.description }}</span>
            </div>
          </button>
        </div>
      </div>

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
          <el-form-item label="分段大小（字符）">
            <el-input-number v-model="form.AI_SEGMENT_SIZE" :min="1000" :max="20000" :step="500" style="width: 100%" />
            <div class="field-tip">长文本分段提取时每段的字符数，根据模型上下文窗口调整</div>
          </el-form-item>
          <el-form-item label="最大分段数">
            <el-input-number v-model="form.AI_MAX_SEGMENTS" :min="1" :max="20" style="width: 100%" />
            <div class="field-tip">长文本最多分几段，超出部分合并到最后一段</div>
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
  color: var(--muted);
  font-size: 14px;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.settings-card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
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
  color: var(--muted);
  font-size: 13px;
}

.theme-card {
  grid-column: 1 / -1;
}

.theme-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.theme-option {
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.45);
  border-radius: 18px;
  padding: 14px;
  cursor: pointer;
  display: flex;
  gap: 14px;
  align-items: center;
  text-align: left;
  transition: 0.18s ease;
}

.theme-option:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-soft);
}

.theme-option.active {
  border-color: var(--green);
  box-shadow: 0 0 0 3px rgba(32, 79, 61, 0.10);
}

.theme-swatch {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.theme-swatch.warm-paper {
  background: linear-gradient(145deg, #204f3d, #f3efe6 55%, #b07a2a);
}

.theme-swatch.night-focus {
  background: linear-gradient(145deg, #131713, #2a342c 55%, #c9a15f);
}

.theme-swatch.clear-sky {
  background: linear-gradient(145deg, #2f5f88, #edf5fb 55%, #4b90d9);
}

.theme-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.theme-meta strong {
  color: var(--text);
  font-size: 15px;
}

.theme-meta span {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.5;
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

.field-tip {
  margin-top: 4px;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.4;
}

.test-result {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.5;
}

.test-result.ok {
  background: rgba(228, 243, 235, 0.95);
  color: #215844;
}

.test-result.fail {
  background: #fff3ee;
  color: #a13e20;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }

  .theme-list {
    grid-template-columns: 1fr;
  }
}
</style>
