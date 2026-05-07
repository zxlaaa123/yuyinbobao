import request from './request'

export interface KnowledgeBase {
  id: number
  name: string
  description: string | null
  sort_order: number
  material_count: number
  knowledge_point_count: number
  created_at: string
  updated_at: string
}

export interface KnowledgeBaseCreate {
  name: string
  description?: string
}

export interface KnowledgeBaseUpdate {
  name?: string
  description?: string
}

export function getKnowledgeBases() {
  return request.get('/api/knowledge-bases') as Promise<KnowledgeBase[]>
}

export function getKnowledgeBase(id: number) {
  return request.get(`/api/knowledge-bases/${id}`) as Promise<KnowledgeBase>
}

export function createKnowledgeBase(data: KnowledgeBaseCreate) {
  return request.post('/api/knowledge-bases', data) as Promise<KnowledgeBase>
}

export function updateKnowledgeBase(id: number, data: KnowledgeBaseUpdate) {
  return request.put(`/api/knowledge-bases/${id}`, data) as Promise<KnowledgeBase>
}

export function deleteKnowledgeBase(id: number) {
  return request.delete(`/api/knowledge-bases/${id}`) as Promise<{ success: boolean; message: string }>
}
