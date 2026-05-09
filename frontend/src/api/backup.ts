import request from './request'

export interface BackupRecord {
  id: number
  filename: string
  file_path: string
  file_size: number
  status: string
  trigger_type: string
  note: string | null
  error_message: string | null
  created_at: string
}

export function getBackups() {
  return request.get('/api/backups') as Promise<BackupRecord[]>
}

export function createBackup(note?: string) {
  return request.post('/api/backups', { note }) as Promise<BackupRecord>
}

export function restoreBackup(id: number) {
  return request.post(`/api/backups/${id}/restore`, { confirm: true }) as Promise<{
    success: boolean
    message: string
    restored_backup_id: number
    safety_backup_id: number
  }>
}

export function deleteBackup(id: number) {
  return request.delete(`/api/backups/${id}`) as Promise<{ success: boolean; message: string }>
}
