import request from './request'
import { mockChat, mockGenerateDescription, mockSuggestPrice } from './mock/ai'

const useMock = import.meta.env.VITE_USE_MOCK === 'true'

/**
 * AI 价格建议（预留）
 * 请求: { title, categoryId, condition }
 * 响应: { low, high, suggest, reason }
 */
export function suggestPrice(data) {
  return useMock ? mockSuggestPrice(data) : request.post('/ai/price', data)
}

/**
 * AI 生成商品描述（预留）
 * 请求: { title, categoryId, condition, campus }
 * 响应: { text } 或纯文本，接入时统一成 { text }
 */
export function generateDescription(data) {
  return useMock
    ? mockGenerateDescription(data).then((text) => ({ text }))
    : request.post('/ai/description', data)
}

/**
 * AI 对话（预留：智能客服 / 导购）
 * 请求: { message, context? }
 * 响应: { reply }
 */
export function chat(data) {
  return useMock ? mockChat(data) : request.post('/ai/chat', data)
}
