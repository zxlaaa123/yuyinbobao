import request from './request'

export interface WrongQuestion {
  id: number
  question_id: number
  wrong_count: number
  last_wrong_answer: string | null
  last_wrong_at: string
  is_mastered: boolean
  question: {
    id: number
    question_type: string
    stem: string
    options: { key: string; text: string }[]
    answer: string
    analysis: string | null
    knowledge_point_title: string
  }
}

export function getWrongQuestions(params?: {
  is_mastered?: boolean
  knowledge_base_id?: number
}) {
  const qs = new URLSearchParams()
  if (params?.is_mastered !== undefined) qs.set('is_mastered', String(params.is_mastered))
  if (params?.knowledge_base_id) qs.set('knowledge_base_id', String(params.knowledge_base_id))
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return request.get(`/api/wrong-questions${suffix}`) as Promise<WrongQuestion[]>
}

export function markMastered(id: number) {
  return request.post(`/api/wrong-questions/${id}/mark-mastered`) as Promise<{ id: number; is_mastered: boolean; message: string }>
}

export function unmarkMastered(id: number) {
  return request.post(`/api/wrong-questions/${id}/unmark-mastered`) as Promise<{ id: number; is_mastered: boolean; message: string }>
}

export function deleteWrongQuestion(id: number) {
  return request.delete(`/api/wrong-questions/${id}`) as Promise<{ success: boolean; message: string }>
}
