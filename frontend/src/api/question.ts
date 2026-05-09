import request from './request'

export interface Question {
  id: number
  knowledge_base_id: number
  knowledge_point_id: number
  question_type: string
  stem: string
  options: { key: string; text: string }[]
  answer: string
  reference_answer: string | null
  analysis: string | null
  difficulty: string
  created_at: string
  updated_at: string
}

export function getQuestions(params?: {
  knowledge_base_id?: number
  knowledge_point_id?: number
  question_type?: string
  difficulty?: string
}) {
  const qs = new URLSearchParams()
  if (params?.knowledge_base_id) qs.set('knowledge_base_id', String(params.knowledge_base_id))
  if (params?.knowledge_point_id) qs.set('knowledge_point_id', String(params.knowledge_point_id))
  if (params?.question_type) qs.set('question_type', params.question_type)
  if (params?.difficulty) qs.set('difficulty', params.difficulty)
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return request.get(`/api/questions${suffix}`) as Promise<Question[]>
}

export function getQuestion(id: number) {
  return request.get(`/api/questions/${id}`) as Promise<Question>
}

export function deleteQuestion(id: number) {
  return request.delete(`/api/questions/${id}`) as Promise<{ success: boolean; message: string }>
}

export interface GeneratedQuestion {
  id: number
  question_type: string
  stem: string
  options: { key: string; text: string }[]
  answer: string
  reference_answer: string | null
  analysis: string | null
  difficulty: string
}

export function generateQuestions(knowledgePointId: number, questionTypes: string[], count: number) {
  return request.post('/api/ai/generate-questions', {
    knowledge_point_id: knowledgePointId,
    question_types: questionTypes,
    count,
  }) as Promise<{ created_count: number; skipped_count: number; questions: GeneratedQuestion[] }>
}
