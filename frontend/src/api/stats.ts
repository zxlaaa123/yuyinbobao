import request from './request'

export interface StatsOverview {
  today_answers: number
  today_correct: number
  total_answers: number
  total_correct: number
  accuracy: number
  pending_review: number
  wrong_total: number
  mastered_count: number
  review_pending: number
  review_completed: number
  review_total: number
  total_knowledge_points: number
  kp_with_questions: number
  kp_coverage: number
  audio_success: number
  audio_failed: number
}

export interface KnowledgeBaseStats {
  id: number
  name: string
  knowledge_point_count: number
  question_count: number
  answer_count: number
  correct_count: number
  accuracy: number
  wrong_count: number
  pending_wrong: number
  review_pending: number
  mastery: number
}

export interface TrendItem {
  date: string
  answers: number
  correct: number
  accuracy: number
}

export function getStatsOverview() {
  return request.get('/api/stats/overview') as Promise<StatsOverview>
}

export function getKnowledgeBaseStats() {
  return request.get('/api/stats/knowledge-bases') as Promise<KnowledgeBaseStats[]>
}

export function getStatsTrends(days: number = 7) {
  return request.get(`/api/stats/trends?days=${days}`) as Promise<TrendItem[]>
}
