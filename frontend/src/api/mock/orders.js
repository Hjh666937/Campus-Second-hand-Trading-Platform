/**
 * 订单 Mock
 * 对齐后端约定：
 *   POST  /api/orders
 *   GET   /api/orders?role=buyer|seller
 *   PATCH /api/orders/{id}/status
 *   POST  /api/orders/{id}/review
 */

import { mockUpdateItemStatus } from './items'

const ORDER_KEY = 'mock-orders'
const delay = (ms = 260) => new Promise((resolve) => setTimeout(resolve, ms))
const now = () => new Date().toISOString()

function readOrders() {
  try {
    const list = JSON.parse(localStorage.getItem(ORDER_KEY) || '[]')
    return Array.isArray(list) ? list : []
  } catch (error) {
    return []
  }
}

function writeOrders(list) {
  localStorage.setItem(ORDER_KEY, JSON.stringify(list))
}

/** 合法状态流转：待确认 → 待交易 → 已完成，中途可取消 */
const TRANSITIONS = {
  pending: ['confirmed', 'cancelled'],
  confirmed: ['completed', 'cancelled'],
  completed: [],
  cancelled: []
}

export async function mockCreateOrder(payload) {
  await delay(320)

  const orders = readOrders()
  const duplicated = orders.find(
    (row) =>
      row.itemId === Number(payload.itemId) &&
      row.buyerAccount === payload.buyerAccount &&
      ['pending', 'confirmed'].includes(row.status)
  )
  if (duplicated) {
    const error = new Error('你已经下过单了，去「我的」里查看')
    error.code = 409
    throw error
  }

  const order = {
    id: Date.now(),
    orderNo: `C${Date.now()}`,
    itemId: Number(payload.itemId),
    itemTitle: payload.itemTitle,
    itemCover: payload.itemCover,
    price: Number(payload.price),
    buyerAccount: payload.buyerAccount,
    buyerNickname: payload.buyerNickname,
    sellerNickname: payload.sellerNickname,
    status: 'pending',
    reviewed: false,
    createdAt: now(),
    finishedAt: null
  }

  orders.unshift(order)
  writeOrders(orders)

  return order
}

export async function mockGetOrders({ account, nickname, role = 'buyer' }) {
  await delay(220)

  const orders = readOrders()
  return orders.filter((row) =>
    role === 'buyer'
      ? row.buyerAccount === account && row.status !== 'cancelled'
      : row.sellerNickname === nickname
  )
}

export async function mockUpdateOrderStatus({ orderId, status, account, nickname }) {
  await delay(220)

  const orders = readOrders()
  const order = orders.find((row) => row.id === Number(orderId))
  if (!order) {
    const error = new Error('订单不存在')
    error.code = 404
    throw error
  }

  const allowed = TRANSITIONS[order.status] || []
  if (!allowed.includes(status)) {
    const error = new Error('当前订单状态不支持该操作')
    error.code = 400
    throw error
  }

  const isBuyer = order.buyerAccount === account
  const isSeller = order.sellerNickname === nickname
  if (!isBuyer && !isSeller) {
    const error = new Error('无权操作该订单')
    error.code = 403
    throw error
  }

  // 卖家只能确认订单，不能替买家确认收货或取消
  if (isSeller && !isBuyer && status !== 'confirmed') {
    const error = new Error('卖家只能确认订单')
    error.code = 403
    throw error
  }

  order.status = status
  if (status === 'completed') {
    order.finishedAt = now()
    order.reviewed = false

    // 交易完成，商品标记为已售，避免继续挂在首页
    try {
      await mockUpdateItemStatus(order.itemId, 'sold')
    } catch (error) {
      // 商品已被删除时忽略
    }
  }
  writeOrders(orders)

  return order
}

export async function mockReviewOrder({ orderId, rating, content, account }) {
  await delay(240)

  const orders = readOrders()
  const order = orders.find((row) => row.id === Number(orderId))
  if (!order || order.buyerAccount !== account) {
    const error = new Error('订单不存在')
    error.code = 404
    throw error
  }
  if (order.status !== 'completed') {
    const error = new Error('订单完成后才能评价')
    error.code = 400
    throw error
  }

  order.reviewed = true
  writeOrders(orders)

  // 评价内容单独存档，供卖家主页展示
  const key = 'mock-reviews'
  let reviews = []
  try {
    reviews = JSON.parse(localStorage.getItem(key) || '[]')
  } catch (error) {
    reviews = []
  }

  const review = {
    id: Date.now(),
    orderId: order.id,
    itemId: order.itemId,
    itemTitle: order.itemTitle,
    sellerNickname: order.sellerNickname,
    buyerAccount: account,
    buyerNickname: order.buyerNickname,
    rating: Number(rating),
    content,
    createdAt: now()
  }

  reviews.unshift(review)
  localStorage.setItem(key, JSON.stringify(reviews))

  return review
}
