import request from './request'

export interface PracticeSessionItemPayload {
  question_id: number
  knowledge_point_id?: number
  user_answer?: string
  is_correct: boolean
  duration_seconds?: number
}

export interface PracticeSessionPayload {
  mode?: string
  title?: string
  knowledge_base_id?: number
  items: PracticeSessionItemPayload[]
  duration_seconds?: number
  started_at?: string
  ended_at?: string
}

export interface PracticeSessionItem {
  id: number
  question_id: number
  knowledge_point_id: number | null
  user_answer: string | null
  is_correct: boolean
  duration_seconds: number
  question_type: string | null
  stem: string | null
  correct_answer: string | null
  reference_answer: string | null
  analysis: string | null
  knowledge_point_title: string | null
  created_at: string
}

export interface PracticeSession {
  id: number
  title: string | null
  mode: string
  knowledge_base_id: number | null
  knowledge_base_name: string | null
  total_count: number
  correct_count: number
  wrong_count: number
  accuracy_rate: number
  duration_seconds: number
  knowledge_point_ids: number[]
  weak_knowledge_point_ids: number[]
  wrong_question_ids: number[]
  suggestion: string | null
  started_at: string | null
  ended_at: string | null
  created_at: string
  items?: PracticeSessionItem[]
}

export interface PracticeSessionListResponse {
  items: PracticeSession[]
  total: number
  page: number
  page_size: number
}

export function createPracticeSession(data: PracticeSessionPayload) {
  return request.post('/api/practice/sessions', data) as Promise<PracticeSession>
}

export function getPracticeSessions(params?: {
  page?: number
  page_size?: number
  mode?: string
}) {
  const qs = new URLSearchParams()
  if (params?.page) qs.set('page', String(params.page))
  if (params?.page_size) qs.set('page_size', String(params.page_size))
  if (params?.mode) qs.set('mode', params.mode)
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return request.get(`/api/practice/sessions${suffix}`) as Promise<PracticeSessionListResponse>
}

export function getPracticeSession(id: number) {
  return request.get(`/api/practice/sessions/${id}`) as Promise<PracticeSession>
}
