/**
 * 管理员 Mock
 * 对齐后端约定：
 *   GET   /api/admin/stats
 *   GET   /api/admin/users
 *   PATCH /api/admin/users/{account}/status
 *   GET   /api/admin/reports
 */

const BAN_KEY = 'mock-banned-users'
const USER_KEY = 'mock-registered-users'
const ITEM_KEY = 'mock-created-items'

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

const BUILTIN_USERS = [
  { account: 'admin', nickname: '平台管理员', campus: '-', role: 'admin' },
  { account: '20261116', nickname: '林小满', campus: '东校区', role: 'student' }
]

export async function mockGetUsers() {
  await delay(220)

  const banned = read(BAN_KEY)
  const registered = read(USER_KEY)
  const merged = [...BUILTIN_USERS]

  registered.forEach((user) => {
    if (!merged.some((row) => row.account === user.account)) {
      merged.push({
        account: user.account,
        nickname: user.nickname,
        campus: user.campus,
        role: 'student'
      })
    }
  })

  return merged.map((user) => {
    const record = banned.find((row) => row.account === user.account)
    return {
      ...user,
      status: record ? 'banned' : 'active',
      bannedAt: record?.bannedAt || null
    }
  })
}

export async function mockSetUserStatus(account, status) {
  await delay(180)

  const banned = read(BAN_KEY)
  const index = banned.findIndex((row) => row.account === account)

  if (status === 'banned') {
    if (index === -1) banned.push({ account, bannedAt: now() })
  } else if (index !== -1) {
    banned.splice(index, 1)
  }

  write(BAN_KEY, banned)
  return true
}

export async function mockGetStats() {
  await delay(260)

  const localItems = read(ITEM_KEY)
  const orders = read('mock-orders')
  const reports = read('mock-reports')
  const users = await mockGetUsers()

  const soldOrders = orders.filter((row) => row.status === 'completed')
  const categoryCount = {}

  localItems.forEach((item) => {
    const key = String(item.categoryId)
    categoryCount[key] = (categoryCount[key] || 0) + 1
  })

  return {
    userCount: users.length,
    bannedCount: users.filter((row) => row.status === 'banned').length,
    publishedCount: localItems.length,
    orderCount: orders.length,
    completedCount: soldOrders.length,
    turnover: soldOrders.reduce((sum, row) => sum + Number(row.price || 0), 0),
    pendingReports: reports.filter((row) => row.status === 'pending').length,
    categoryCount
  }
}
