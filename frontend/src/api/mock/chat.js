/**
 * 聊天 Mock 数据层
 * 结构对齐后端约定：
 *   POST /api/conversations
 *   GET  /api/conversations
 *   GET  /api/conversations/{id}/messages
 *   POST /api/conversations/{id}/messages
 *   POST /api/conversations/{id}/read
 */

const CONV_KEY = 'mock-conversations'
const MSG_KEY = 'mock-messages'

const delay = (ms = 240) => new Promise((resolve) => setTimeout(resolve, ms))
const now = () => new Date().toISOString()

function read(key) {
  try {
    const value = JSON.parse(localStorage.getItem(key) || '[]')
    return Array.isArray(value) ? value : []
  } catch (error) {
    return []
  }
}

function write(key, value) {
  localStorage.setItem(key, JSON.stringify(value))
}

/**
 * 打开（或创建）与卖家的会话：同一商品 + 同一买家只保留一条
 */
export async function mockOpenConversation({
  itemId,
  itemTitle,
  itemCover,
  sellerNickname,
  buyerAccount,
  buyerNickname
}) {
  await delay()

  const conversations = read(CONV_KEY)
  const existed = conversations.find(
    (row) => row.itemId === Number(itemId) && row.buyerAccount === buyerAccount
  )

  if (existed) {
    return existed
  }

  const conversation = {
    id: Date.now(),
    itemId: Number(itemId),
    itemTitle,
    itemCover,
    sellerNickname,
    buyerAccount,
    buyerNickname,
    lastMessage: '',
    lastAt: now(),
    buyerUnread: 0,
    sellerUnread: 0
  }

  conversations.unshift(conversation)
  write(CONV_KEY, conversations)

  return conversation
}

/**
 * 我的会话列表，按最近消息时间倒序
 */
export async function mockGetConversations(account) {
  await delay(180)

  return read(CONV_KEY)
    .filter((row) => row.buyerAccount === account || row.sellerAccount === account)
    .sort((a, b) => String(b.lastAt).localeCompare(String(a.lastAt)))
    .map((row) => ({
      ...row,
      unread: row.buyerAccount === account ? row.buyerUnread : row.sellerUnread
    }))
}

/**
 * 会话内消息，按时间正序
 */
export async function mockGetMessages(conversationId) {
  await delay(180)

  return read(MSG_KEY)
    .filter((row) => row.conversationId === Number(conversationId))
    .sort((a, b) => String(a.createdAt).localeCompare(String(b.createdAt)))
}

/**
 * 发送消息
 */
export async function mockSendMessage({ conversationId, account, nickname, content }) {
  await delay(160)

  const messages = read(MSG_KEY)
  const message = {
    id: Date.now(),
    conversationId: Number(conversationId),
    senderAccount: account,
    senderNickname: nickname,
    type: 'text',
    content,
    createdAt: now()
  }
  messages.push(message)
  write(MSG_KEY, messages)

  const conversations = read(CONV_KEY)
  const conversation = conversations.find((row) => row.id === Number(conversationId))
  if (conversation) {
    conversation.lastMessage = content
    conversation.lastAt = message.createdAt
    if (conversation.buyerAccount === account) {
      conversation.sellerUnread += 1
    } else {
      conversation.buyerUnread += 1
    }
    write(CONV_KEY, conversations)
  }

  return message
}

/**
 * 标记会话已读
 */
export async function mockMarkRead(conversationId, account) {
  const conversations = read(CONV_KEY)
  const conversation = conversations.find((row) => row.id === Number(conversationId))
  if (!conversation) return true

  if (conversation.buyerAccount === account) {
    conversation.buyerUnread = 0
  } else {
    conversation.sellerUnread = 0
  }
  write(CONV_KEY, conversations)

  return true
}

/**
 * 未读总数（顶部导航红点用）
 */
export async function mockGetUnreadCount(account) {
  return read(CONV_KEY).reduce(
    (sum, row) => sum + (row.buyerAccount === account ? row.buyerUnread : row.sellerUnread),
    0
  )
}
