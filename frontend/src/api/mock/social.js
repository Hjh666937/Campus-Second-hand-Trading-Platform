/**
 * 收藏 / 举报 / 评价 / 卖家资料 Mock
 * 对齐后端约定：
 *   POST   /api/favorites          收藏 / 取消收藏
 *   GET    /api/favorites
 *   POST   /api/reports            举报商品
 *   GET    /api/reports            管理员看待处理举报
 *   GET    /api/users/{nickname}   卖家主页
 */

import { SELLER_CREDIT, findItemById, findItemsBySeller } from './items'

const FAV_KEY = 'mock-favorites'
const REPORT_KEY = 'mock-reports'
const REVIEW_KEY = 'mock-reviews'

const delay = (ms = 220) => new Promise((resolve) => setTimeout(resolve, ms))
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

/* ---------------- 收藏 ---------------- */

export async function mockToggleFavorite({ account, itemId }) {
  await delay(180)

  const favorites = read(FAV_KEY)
  const index = favorites.findIndex(
    (row) => row.account === account && row.itemId === Number(itemId)
  )

  if (index !== -1) {
    favorites.splice(index, 1)
    write(FAV_KEY, favorites)
    return { favorite: false }
  }

  favorites.unshift({ account, itemId: Number(itemId), createdAt: now() })
  write(FAV_KEY, favorites)
  return { favorite: true }
}

export async function mockGetFavorites(account) {
  await delay(200)

  return read(FAV_KEY)
    .filter((row) => row.account === account)
    .map((row) => findItemById(row.itemId))
    .filter(Boolean)
}

export async function mockIsFavorite({ account, itemId }) {
  return read(FAV_KEY).some(
    (row) => row.account === account && row.itemId === Number(itemId)
  )
}

/* ---------------- 举报 ---------------- */

export async function mockCreateReport({ itemId, itemTitle, account, reason, detail }) {
  await delay(260)

  const reports = read(REPORT_KEY)
  reports.unshift({
    id: Date.now(),
    itemId: Number(itemId),
    itemTitle,
    account,
    reason,
    detail: detail || '',
    status: 'pending',
    createdAt: now()
  })
  write(REPORT_KEY, reports)

  return true
}

export async function mockGetReports() {
  await delay(200)
  return read(REPORT_KEY)
}

export async function mockHandleReport(id, status) {
  await delay(180)

  const reports = read(REPORT_KEY)
  const report = reports.find((row) => row.id === Number(id))
  if (report) {
    report.status = status
    write(REPORT_KEY, reports)
  }
  return true
}

/* ---------------- 评价与卖家资料 ---------------- */

export async function mockGetReviews(sellerNickname) {
  await delay(200)
  return read(REVIEW_KEY).filter((row) => row.sellerNickname === sellerNickname)
}

export async function mockGetSellerProfile(nickname) {
  await delay(280)

  const items = findItemsBySeller(nickname)
  const reviews = read(REVIEW_KEY).filter((row) => row.sellerNickname === nickname)
  const totalRating = reviews.reduce((sum, row) => sum + row.rating, 0)

  return {
    nickname,
    campus: items[0]?.campus || '',
    credit: SELLER_CREDIT[nickname] ?? 90,
    rating: reviews.length ? Number((totalRating / reviews.length).toFixed(1)) : 5,
    reviewCount: reviews.length,
    onSaleCount: items.filter((item) => item.status === 'on_sale').length,
    soldCount: items.filter((item) => item.status === 'sold').length,
    items: items.filter((item) => item.status === 'on_sale'),
    reviews
  }
}
