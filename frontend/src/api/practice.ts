import request from './request'

export interface PracticeQuestion {
  id: number
  question_type: string
  stem: string
  options: { key: string; text: string }[]
  difficulty: string
  knowledge_point_id: number
}

export interface AnswerResult {
  question_id: number
  is_correct: boolean
  user_answer: string
  correct_answer: string
  analysis: string
  wrong_question_id: number | null
}

export function getPracticeQuestions(params?: {
  knowledge_base_id?: number
  knowledge_point_id?: number
  question_type?: string
  count?: number
}) {
  const qs = new URLSearchParams()
  if (params?.knowledge_base_id) qs.set('knowledge_base_id', String(params.knowledge_base_id))
  if (params?.knowledge_point_id) qs.set('knowledge_point_id', String(params.knowledge_point_id))
  if (params?.question_type) qs.set('question_type', params.question_type)
  if (params?.count) qs.set('count', String(params.count))
  return request.get(`/api/practice/questions?${qs.toString()}`) as Promise<PracticeQuestion[]>
}

export function submitAnswer(questionId: number, userAnswer: string) {
  return request.post('/api/practice/answer', {
    question_id: questionId,
    user_answer: userAnswer,
  }) as Promise<AnswerResult>
}
