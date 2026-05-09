export type ThemeName = 'warm-paper' | 'night-focus' | 'clear-sky'

export interface ThemeOption {
  key: ThemeName
  label: string
  description: string
}

export const THEME_STORAGE_KEY = 'ai-study-cast-theme'

export const THEME_OPTIONS: ThemeOption[] = [
  { key: 'warm-paper', label: '暖纸风', description: '温暖纸张感，适合长时间阅读和整理资料。' },
  { key: 'night-focus', label: '深夜专注', description: '低亮度深色风格，适合晚间专注刷题。' },
  { key: 'clear-sky', label: '清爽浅蓝', description: '更干净明亮，工具感更强。' },
]

export function isThemeName(value: string | null | undefined): value is ThemeName {
  return THEME_OPTIONS.some((item) => item.key === value)
}

export function getStoredTheme(): ThemeName {
  if (typeof window === 'undefined') return 'warm-paper'
  const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
  return isThemeName(stored) ? stored : 'warm-paper'
}

export function applyTheme(theme: ThemeName) {
  if (typeof document === 'undefined') return
  document.documentElement.setAttribute('data-theme', theme)
  window.localStorage.setItem(THEME_STORAGE_KEY, theme)
}
