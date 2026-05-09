import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './style.css'
import { applyTheme, getStoredTheme } from './utils/theme'

applyTheme(getStoredTheme())

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
