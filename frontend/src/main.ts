import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import './style.css'

import KnowledgeBaseView from './views/KnowledgeBaseView.vue'
import MaterialImportView from './views/MaterialImportView.vue'
import KnowledgePointListView from './views/KnowledgePointListView.vue'
import KnowledgePointDetailView from './views/KnowledgePointDetailView.vue'
import PracticeView from './views/PracticeView.vue'
import WrongQuestionView from './views/WrongQuestionView.vue'
import AudioView from './views/AudioView.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: () => import('./views/DashboardView.vue') },
  { path: '/knowledge-bases', component: KnowledgeBaseView },
  { path: '/materials/import', component: MaterialImportView },
  { path: '/knowledge-points', component: KnowledgePointListView },
  { path: '/knowledge-points/:id', component: KnowledgePointDetailView },
  { path: '/practice', component: PracticeView },
  { path: '/wrong-questions', component: WrongQuestionView },
  { path: '/audio', component: AudioView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
