const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function downloadCsv(url: string) {
  // 直接用 window.open 触发下载，不走 axios（避免响应拦截器把二进制当 JSON 解析）
  window.open(url, '_blank')
}

export function exportKnowledgePointsCsv(knowledgeBaseId?: number) {
  const qs = knowledgeBaseId ? `?knowledge_base_id=${knowledgeBaseId}` : ''
  downloadCsv(`${BASE}/api/export/knowledge-points.csv${qs}`)
}

export function exportQuestionsCsv(knowledgeBaseId?: number, knowledgePointId?: number) {
  const params = new URLSearchParams()
  if (knowledgeBaseId) params.set('knowledge_base_id', String(knowledgeBaseId))
  if (knowledgePointId) params.set('knowledge_point_id', String(knowledgePointId))
  const qs = params.toString() ? `?${params.toString()}` : ''
  downloadCsv(`${BASE}/api/export/questions.csv${qs}`)
}

export function exportWrongQuestionsCsv(knowledgeBaseId?: number, isMastered?: boolean) {
  const params = new URLSearchParams()
  if (knowledgeBaseId) params.set('knowledge_base_id', String(knowledgeBaseId))
  if (isMastered !== undefined) params.set('is_mastered', String(isMastered))
  const qs = params.toString() ? `?${params.toString()}` : ''
  downloadCsv(`${BASE}/api/export/wrong-questions.csv${qs}`)
}
