import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', component: () => import('../views/DashboardView.vue') },
        { path: 'knowledge-bases', component: () => import('../views/KnowledgeBaseView.vue') },
        { path: 'materials/import', component: () => import('../views/MaterialImportView.vue') },
        { path: 'knowledge-points', component: () => import('../views/KnowledgePointListView.vue') },
        { path: 'knowledge-points/:id', component: () => import('../views/KnowledgePointDetailView.vue') },
        { path: 'practice', component: () => import('../views/PracticeView.vue') },
        { path: 'practice-sessions', component: () => import('../views/PracticeSessionsView.vue') },
        { path: 'practice-sessions/:id', component: () => import('../views/PracticeSessionsView.vue') },
        { path: 'wrong-questions', component: () => import('../views/WrongQuestionView.vue') },
        { path: 'review', component: () => import('../views/ReviewView.vue') },
        { path: 'audio', component: () => import('../views/AudioView.vue') },
        { path: 'ai-call-logs', component: () => import('../views/AICallLogView.vue') },
        { path: 'settings', component: () => import('../views/SettingsView.vue') },
      ],
    },
  ],
})

export default router
