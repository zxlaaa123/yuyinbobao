import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import KnowledgeBaseView from '../views/KnowledgeBaseView.vue'
import MaterialImportView from '../views/MaterialImportView.vue'
import KnowledgePointListView from '../views/KnowledgePointListView.vue'
import KnowledgePointDetailView from '../views/KnowledgePointDetailView.vue'
import PracticeView from '../views/PracticeView.vue'
import PracticeSessionsView from '../views/PracticeSessionsView.vue'
import WrongQuestionView from '../views/WrongQuestionView.vue'
import AudioView from '../views/AudioView.vue'
import SettingsView from '../views/SettingsView.vue'
import ReviewView from '../views/ReviewView.vue'
import AICallLogView from '../views/AICallLogView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', component: () => import('../views/DashboardView.vue') },
        { path: 'knowledge-bases', component: KnowledgeBaseView },
        { path: 'materials/import', component: MaterialImportView },
        { path: 'knowledge-points', component: KnowledgePointListView },
        { path: 'knowledge-points/:id', component: KnowledgePointDetailView },
        { path: 'practice', component: PracticeView },
        { path: 'practice-sessions', component: PracticeSessionsView },
        { path: 'practice-sessions/:id', component: PracticeSessionsView },
        { path: 'wrong-questions', component: WrongQuestionView },
        { path: 'review', component: ReviewView },
        { path: 'audio', component: AudioView },
        { path: 'ai-call-logs', component: AICallLogView },
        { path: 'settings', component: SettingsView },
      ],
    },
  ],
})

export default router
