import request from './request'

export interface StudySession {
  id: number
  knowledge_base_id: number | null
  knowledge_base_name?: string | null
  knowledge_point_id: number | null
  knowledge_point_title?: string | null
  started_at: string
  ended_at: string | null
  total_count: number
  correct_count: number
  accuracy_rate: number
}

export function createStudySession(data: {
  knowledge_base_id?: number
  knowledge_point_id?: number
  total_count?: number
}) {
  return request.post('/api/study-sessions', data) as Promise<StudySession>
}

export function finishStudySession(id: number, data: { total_count: number; correct_count: number }) {
  return request.post(`/api/study-sessions/${id}/finish`, data) as Promise<StudySession>
}
