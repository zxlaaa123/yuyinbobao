import { createApp } from 'vue'
import 'element-plus/dist/index.css'
import {
  ElButton,
  ElButtonGroup,
  ElCheckbox,
  ElCheckboxGroup,
  ElDescriptions,
  ElDescriptionsItem,
  ElDialog,
  ElDivider,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElOption,
  ElPagination,
  ElRadioButton,
  ElRadioGroup,
  ElSelect,
  ElTable,
  ElTableColumn,
  ElTag,
  ElUpload,
  vLoading,
} from 'element-plus'
import App from './App.vue'
import router from './router'
import './style.css'
import { applyTheme, getStoredTheme } from './utils/theme'

applyTheme(getStoredTheme())

const app = createApp(App)
const elementComponents = [
  ElButton,
  ElButtonGroup,
  ElCheckbox,
  ElCheckboxGroup,
  ElDescriptions,
  ElDescriptionsItem,
  ElDialog,
  ElDivider,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElOption,
  ElPagination,
  ElRadioButton,
  ElRadioGroup,
  ElSelect,
  ElTable,
  ElTableColumn,
  ElTag,
  ElUpload,
]

for (const component of elementComponents) {
  app.component(component.name!, component)
}
app.directive('loading', vLoading)
app.use(router)
app.mount('#app')
