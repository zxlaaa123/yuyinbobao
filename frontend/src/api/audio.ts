import request from './request'

export interface AudioFile {
  id: number
  knowledge_point_id: number
  title: string
  text_content: string
  file_path: string | null
  file_url: string | null
  duration: number | null
  status: string
  error_message: string | null
  created_at: string
  updated_at: string
}

export function generateAudio(knowledgePointId: number) {
  return request.post('/api/tts/generate', {
    knowledge_point_id: knowledgePointId,
  }) as Promise<{
    audio_id: number
    knowledge_point_id: number
    title: string
    status: string
    file_url: string
  }>
}

export function getAudioFiles(params?: {
  knowledge_base_id?: number
  knowledge_point_id?: number
  status?: string
}) {
  const qs = new URLSearchParams()
  if (params?.knowledge_base_id) qs.set('knowledge_base_id', String(params.knowledge_base_id))
  if (params?.knowledge_point_id) qs.set('knowledge_point_id', String(params.knowledge_point_id))
  if (params?.status) qs.set('status', params.status)
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return request.get(`/api/audio-files${suffix}`) as Promise<AudioFile[]>
}

export function getAudioFile(id: number) {
  return request.get(`/api/audio-files/${id}`) as Promise<AudioFile>
}

export function deleteAudioFile(id: number) {
  return request.delete(`/api/audio-files/${id}`) as Promise<{ success: boolean; message: string }>
}
