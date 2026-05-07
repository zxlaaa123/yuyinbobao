import request from './request'

export interface DashboardSummary {
  knowledge_base_count: number
  material_count: number
  knowledge_point_count: number
  question_count: number
  wrong_question_count: number
  audio_count: number
}

export function getDashboardSummary() {
  return request.get('/api/dashboard/summary') as Promise<DashboardSummary>
}
