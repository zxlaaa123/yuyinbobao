import request from './request'

export function getSettings() {
  return request.get('/api/settings') as Promise<Record<string, string>>
}

export function saveSettings(data: Record<string, any>) {
  return request.put('/api/settings', data) as Promise<{ success: boolean; message: string; settings: Record<string, string> }>
}

export function testAiConnection() {
  return request.post('/api/settings/test-ai') as Promise<{ success: boolean; message: string; model?: string }>
}

export function testTtsConnection() {
  return request.post('/api/settings/test-tts') as Promise<{ success: boolean; message: string }>
}
