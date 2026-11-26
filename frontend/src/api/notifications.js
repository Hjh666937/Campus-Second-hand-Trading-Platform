import request from './request'

/**
 * 站内通知，对应 dbo.notifications。
 * 返回 { list, unread }
 */
export function getNotifications() {
  return request.get('/notifications')
}

/** 全部标记为已读，返回 { unread: 0 } */
export function readNotifications() {
  return request.post('/notifications/read')
}
