import request from './request'

export interface AICallLog {
  id: number
  operation: string
  model: string | null
  base_url_host: string | null
  status: 'success' | 'failed'
  prompt_chars: number
  response_chars: number
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  tokens_estimated: boolean
  estimated_cost: number
  input_price_per_1m: number
  output_price_per_1m: number
  duration_ms: number
  request_summary: string | null
  response_summary: string | null
  error_message: string | null
  related_type: string | null
  related_id: number | null
  created_at: string
}

export interface AICallLogSummary {
  total: number
  success: number
  failed: number
  total_tokens: number
  estimated_cost: number
}

export function getAiCallLogs(params: {
  page?: number
  page_size?: number
  status?: string
  operation?: string
}) {
  return request.get('/api/ai-call-logs', { params }) as Promise<{ total: number; items: AICallLog[] }>
}

export function getAiCallLogSummary() {
  return request.get('/api/ai-call-logs/summary') as Promise<AICallLogSummary>
}
