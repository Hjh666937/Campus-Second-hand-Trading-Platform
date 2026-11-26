import request from './request'

/**
 * 聊天接口，已接入真实后端。
 * 依赖 dbo.conversations / dbo.messages 两张表。
 */

/**
 * 打开（或创建）与卖家的会话
 * 请求: { itemId }
 */
export function openConversation({ itemId }) {
  return request.post('/conversations', { itemId })
}

/**
 * 我的会话列表
 */
export function getConversations() {
  return request.get('/conversations')
}

/**
 * 会话内历史消息
 */
export function getMessages(conversationId) {
  return request.get(`/conversations/${conversationId}/messages`)
}

/**
 * 发送消息
 * 请求: { conversationId, type, content }
 */
export function sendMessage({ conversationId, type = 'text', content }) {
  return request.post(`/conversations/${conversationId}/messages`, { type, content })
}

/**
 * 标记会话已读
 */
export function markRead(conversationId) {
  return request.post(`/conversations/${conversationId}/read`)
}

/**
 * 未读消息总数
 */
export function getUnreadCount() {
  return request.get('/conversations/unread-count')
}
