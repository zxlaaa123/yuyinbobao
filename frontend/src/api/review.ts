import request from './request'

export interface ReviewTask {
  id: number
  knowledge_point_id: number
  kp_title: string
  kp_summary: string
  source: string
  status: string
  review_bucket: 'today' | 'overdue' | 'later' | 'completed'
  difficulty: string
  scheduled_at: string | null
  completed_at: string | null
  last_reviewed_at: string | null
  last_quality: string | null
  review_count: number
  next_interval_days: number
  snooze_count: number
  created_at: string
  updated_at: string
}

export interface GenerateResult {
  created: number
  message?: string
  total_pending?: number
}

export function getReviewTasks(params?: {
  status?: string
  knowledge_base_id?: number
  limit?: number
  offset?: number
}) {
  const qs = new URLSearchParams()
  if (params?.status) qs.set('status', params.status)
  if (params?.knowledge_base_id) qs.set('knowledge_base_id', String(params.knowledge_base_id))
  if (params?.limit) qs.set('limit', String(params.limit))
  if (params?.offset) qs.set('offset', String(params.offset))
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return request.get(`/api/review/tasks${suffix}`) as Promise<ReviewTask[]>
}

export function generateReviewTasks(max_tasks: number = 30) {
  return request.post(`/api/review/tasks/generate?max_tasks=${max_tasks}`) as Promise<GenerateResult>
}

export function completeReviewTask(task_id: number, quality: string) {
  return request.post(`/api/review/tasks/${task_id}/complete?quality=${quality}`) as Promise<ReviewTask>
}

export function snoozeReviewTask(task_id: number, hours: number = 24) {
  return request.post(`/api/review/tasks/${task_id}/snooze?hours=${hours}`) as Promise<ReviewTask>
}

export function deleteReviewTask(task_id: number) {
  return request.delete(`/api/review/tasks/${task_id}`) as Promise<{ success: boolean; message: string }>
}
