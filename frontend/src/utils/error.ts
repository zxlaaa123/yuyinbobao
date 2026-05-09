import axios from 'axios'

function getMessageFromData(data: unknown): string | null {
  if (!data) {
    return null
  }

  if (typeof data === 'string') {
    return data.trim() || null
  }

  if (Array.isArray(data)) {
    const messages = data.map(getMessageFromData).filter(Boolean)
    return messages.length ? messages.join('；') : null
  }

  if (typeof data === 'object') {
    const source = data as Record<string, unknown>
    return (
      getMessageFromData(source.detail) ||
      getMessageFromData(source.message) ||
      getMessageFromData(source.error) ||
      getMessageFromData(source.msg)
    )
  }

  return String(data)
}

export function isUserCanceled(error: unknown): boolean {
  return error === 'cancel' || error === 'close' || axios.isCancel(error)
}

export function getErrorMessage(error: unknown, fallback = '操作失败'): string {
  if (axios.isAxiosError(error)) {
    const serverMessage = getMessageFromData(error.response?.data)
    if (serverMessage) {
      return serverMessage
    }

    if (!error.response || error.message === 'Network Error') {
      return '后端连接失败，请确认后端服务是否启动'
    }

    return error.message || fallback
  }

  const message = getMessageFromData(error)
  return message || fallback
}
