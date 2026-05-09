import { ElMessageBox } from 'element-plus'

export function confirmDelete(type: string, name?: string, detail?: string) {
  const target = name ? `${type}「${name}」` : `这个${type}`
  const extra = detail ? `${detail}。` : ''
  return ElMessageBox.confirm(
    `确定要删除${target}吗？${extra}删除后不可恢复。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    },
  )
}
