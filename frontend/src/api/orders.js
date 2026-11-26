import request from './request'

/**
 * 下单
 * 请求: { itemId }
 */
export function createOrder(data) {
  return request.post('/orders', { itemId: data.itemId })
}

/**
 * 我的订单
 * @param {{ account: string, nickname: string, role: 'buyer'|'seller' }} params
 */
export function getOrders(params) {
  return request.get('/orders', { params: { role: params.role } })
}

/**
 * 流转订单状态
 * @param {number} orderId
 * @param {'confirmed'|'completed'|'cancelled'} status
 */
export function updateOrderStatus(orderId, status) {
  return request.patch(`/orders/${orderId}/status`, { status })
}

/**
 * 评价订单
 * @param {{ rating: number, content: string }} data
 */
export function reviewOrder(orderId, data) {
  return request.post(`/orders/${orderId}/review`, data)
}
