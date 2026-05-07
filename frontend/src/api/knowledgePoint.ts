import request from './request'

export interface KnowledgePoint {
  id: number
  knowledge_base_id: number
  knowledge_base_name: string
  material_id: number | null
  material_title?: string
  title: string
  summary: string | null
  detail: string | null
  exam_points: string[]
  confusing_points: string[]
  memory_tips: string[]
  examples: string[]
  importance: string
  tags: string[]
  question_count: number
  audio_count: number
  audio_files?: { id: number; title: string; file_url: string | null; status: string }[]
  created_at: string
  updated_at: string
}

export interface KnowledgePointUpdate {
  title?: string
  summary?: string
  detail?: string
  exam_points?: string[]
  confusing_points?: string[]
  memory_tips?: string[]
  examples?: string[]
  importance?: string
  tags?: string[]
}

export function getKnowledgePoints(params?: {
  knowledge_base_id?: number
  material_id?: number
  keyword?: string
  importance?: string
  tag?: string
}) {
  const qs = new URLSearchParams()
  if (params?.knowledge_base_id) qs.set('knowledge_base_id', String(params.knowledge_base_id))
  if (params?.material_id) qs.set('material_id', String(params.material_id))
  if (params?.keyword) qs.set('keyword', params.keyword)
  if (params?.importance) qs.set('importance', params.importance)
  if (params?.tag) qs.set('tag', params.tag)
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return request.get(`/api/knowledge-points${suffix}`) as Promise<KnowledgePoint[]>
}

export function getKnowledgePoint(id: number) {
  return request.get(`/api/knowledge-points/${id}`) as Promise<KnowledgePoint>
}

export function updateKnowledgePoint(id: number, data: KnowledgePointUpdate) {
  return request.put(`/api/knowledge-points/${id}`, data) as Promise<KnowledgePoint>
}

export function deleteKnowledgePoint(id: number) {
  return request.delete(`/api/knowledge-points/${id}`) as Promise<{ success: boolean; message: string }>
}
