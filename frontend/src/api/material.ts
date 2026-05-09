import request from './request'
import type { KnowledgeBase } from './knowledgeBase'

export type { KnowledgeBase }

export interface Material {
  id: number
  knowledge_base_id: number
  knowledge_base_name: string
  title: string
  content: string
  source: string | null
  note: string | null
  material_type: string
  content_length: number
  extracted_count: number
  created_at: string
  updated_at: string
}

export interface MaterialCreate {
  knowledge_base_id: number
  title: string
  content: string
  source?: string
  note?: string
}

export interface UploadedTextMaterial {
  title: string
  content: string
  source: string
  file_name: string
  saved_path: string
  content_length: number
}

export function getMaterials(knowledgeBaseId?: number) {
  const params = knowledgeBaseId ? `?knowledge_base_id=${knowledgeBaseId}` : ''
  return request.get(`/api/materials${params}`) as Promise<Material[]>
}

export function getMaterial(id: number) {
  return request.get(`/api/materials/${id}`) as Promise<Material>
}

export function createMaterial(data: MaterialCreate) {
  return request.post('/api/materials', data) as Promise<Material>
}

export function uploadTextMaterial(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/api/materials/upload-text', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }) as Promise<UploadedTextMaterial>
}

export function getKnowledgeBasesForSelect() {
  return request.get('/api/knowledge-bases') as Promise<KnowledgeBase[]>
}

export interface ExtractResult {
  material_id: number
  split_used: boolean
  segment_count: number
  created_count: number
  skipped_count: number
  knowledge_points: { id: number; title: string; importance: string; tags: string[] }[]
}

export function importAndExtract(data: MaterialCreate & { enable_split?: boolean }) {
  return request.post('/api/materials/import-and-extract', data) as Promise<ExtractResult>
}
