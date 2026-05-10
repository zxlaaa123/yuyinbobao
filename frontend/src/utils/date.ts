const DISPLAY_LOCALE = 'zh-CN'

function parseApiDate(value?: string | null): Date | null {
  if (!value) return null
  const normalized = /[zZ]|[+-]\d{2}:\d{2}$/.test(value) ? value : `${value}Z`
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? null : date
}

export function formatDateTime(value?: string | null): string {
  const date = parseApiDate(value)
  if (!date) return value || '-'
  return date.toLocaleString(DISPLAY_LOCALE)
}

export function formatShortDateTime(value?: string | null): string {
  const date = parseApiDate(value)
  if (!date) return value || '-'
  return date.toLocaleString(DISPLAY_LOCALE, {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatMonthDay(value?: string | null): string {
  const date = parseApiDate(value)
  if (!date) return value || '-'
  return `${date.getMonth() + 1}/${date.getDate()}`
}
