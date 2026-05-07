import request from './request'

export interface StatsOverview {
  today_answers: number
  today_correct: number
  total_answers: number
  total_correct: number
  accuracy: number
  pending_review: number
  wrong_total: number
  audio_success: number
  audio_failed: number
}

export interface KnowledgeBaseStats {
  id: number
  name: string
  knowledge_point_count: number
  question_count: number
}

export function getStatsOverview() {
  return request.get('/api/stats/overview') as Promise<StatsOverview>
}

export function getKnowledgeBaseStats() {
  return request.get('/api/stats/knowledge-bases') as Promise<KnowledgeBaseStats[]>
}
