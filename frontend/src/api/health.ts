import request from './request'

export interface HealthResponse {
  status: string
  app_name: string
  version: string
}

export async function checkHealth(): Promise<HealthResponse> {
  return request.get('/api/health')
}
