import request from './request'

/**
 * 管理后台接口，已接入真实后端。
 * 权限由后端 require_admin 校验。
 */

export function getStats() {
  return request.get('/admin/stats')
}

export function getUsers() {
  return request.get('/admin/users')
}

export function setUserStatus(account, status) {
  return request.patch(`/admin/users/${encodeURIComponent(account)}/status`, { status })
}

export function resetUserPassword(account) {
  return request.patch(`/admin/users/${encodeURIComponent(account)}/password/reset`)
}

export function getReports() {
  return request.get('/admin/reports')
}

export function handleReport(reportId, status) {
  return request.patch(`/admin/reports/${reportId}`, { status })
}
