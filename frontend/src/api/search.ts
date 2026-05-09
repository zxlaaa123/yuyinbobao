import request from './request'

export interface SearchResult {
  type: 'knowledge_point' | 'material'
  id: number
  title: string
  summary: string
  target_url: string
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
}

export function searchLocal(q: string) {
  const params = new URLSearchParams()
  params.set('q', q)
  return request.get(`/api/search?${params.toString()}`) as Promise<SearchResponse>
}
