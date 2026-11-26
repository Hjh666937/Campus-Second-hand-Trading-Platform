const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const cover = (prompt) =>
  `https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(prompt)}&image_size=landscape_4_3`

const ITEMS = [
  {
    id: 1,
    title: '高等数学同济第七版 上下册',
    price: 25,
    cover: cover('stack of used college calculus textbooks on a wooden desk, natural light, realistic photo'),
    condition: '九成新',
    campus: '东校区',
    categoryId: 1,
    sellerNickname: '林小满',
    viewCount: 86,
    createdAt: '2026-11-10'
  },
  {
    id: 2,
    title: '大学英语四级真题 + 词汇书',
    price: 15,
    cover: cover('used english exam prep books and vocabulary book on a desk, realistic photo'),
    condition: '八成新',
    campus: '东校区',
    categoryId: 1,
    sellerNickname: '陈一鸣',
    viewCount: 45,
    createdAt: '2026-11-09'
  },
  {
    id: 3,
    title: '87 键机械键盘 红轴',
    price: 120,
    cover: cover('compact mechanical keyboard with red switches on a clean desk, realistic product photo'),
    condition: '九成新',
    campus: '南湖校区',
    categoryId: 2,
    sellerNickname: '周舟',
    viewCount: 132,
    createdAt: '2026-11-11'
  },
  {
    id: 4,
    title: 'iPad 2021 64G 无线局域网版',
    price: 1350,
    cover: cover('used tablet computer with white screen on a desk next to a notebook, realistic photo'),
    condition: '八成新',
    campus: '西校区',
    categoryId: 2,
    sellerNickname: '许知远',
    viewCount: 301,
    createdAt: '2026-11-08'
  },
  {
    id: 5,
    title: '蓝牙耳机 入耳式 续航 24 小时',
    price: 80,
    cover: cover('wireless earbuds in charging case on a light background, realistic product photo'),
    condition: '九成新',
    campus: '东校区',
    categoryId: 2,
    sellerNickname: '林小满',
    viewCount: 97,
    createdAt: '2026-11-11'
  },
  {
    id: 6,
    title: '护眼台灯 三档调光',
    price: 30,
    cover: cover('white led desk lamp on a study desk, warm light, realistic photo'),
    condition: '九成新',
    campus: '南湖校区',
    categoryId: 3,
    sellerNickname: '赵一诺',
    viewCount: 28,
    createdAt: '2026-11-07'
  },
  {
    id: 7,
    title: '宿舍收纳箱 大号两只',
    price: 20,
    cover: cover('two stacked plastic storage boxes in a dorm room, realistic photo'),
    condition: '全新',
    campus: '西校区',
    categoryId: 3,
    sellerNickname: '孙可',
    viewCount: 19,
    createdAt: '2026-11-12'
  },
  {
    id: 8,
    title: '小电煮锅 1.5L 宿舍可用',
    price: 45,
    cover: cover('small electric cooking pot on a kitchen counter, realistic product photo'),
    condition: '八成新',
    campus: '东校区',
    categoryId: 3,
    sellerNickname: '周舟',
    viewCount: 64,
    createdAt: '2026-11-06'
  },
  {
    id: 9,
    title: '斯伯丁篮球 七号',
    price: 40,
    cover: cover('used basketball on an outdoor court at sunset, realistic photo'),
    condition: '七成新',
    campus: '南湖校区',
    categoryId: 4,
    sellerNickname: '陈一鸣',
    viewCount: 52,
    createdAt: '2026-11-05'
  },
  {
    id: 10,
    title: '加厚瑜伽垫 183×61cm',
    price: 25,
    cover: cover('rolled purple yoga mat on a wooden floor, realistic photo'),
    condition: '九成新',
    campus: '西校区',
    categoryId: 4,
    sellerNickname: '赵一诺',
    viewCount: 33,
    createdAt: '2026-11-10'
  },
  {
    id: 11,
    title: '二手自行车 26 寸 带车锁',
    price: 260,
    cover: cover('bicycle parked outside a university dormitory, daylight, photo'),
    condition: '八成新',
    campus: '东校区',
    categoryId: 4,
    sellerNickname: '许知远',
    viewCount: 178,
    createdAt: '2026-11-04'
  },
  {
    id: 12,
    title: '轻薄羽绒服 男款 L',
    price: 150,
    cover: cover('black winter jacket on a hanger, product photo'),
    condition: '九成新',
    campus: '南湖校区',
    categoryId: 5,
    sellerNickname: '孙可',
    viewCount: 41,
    createdAt: '2026-11-09'
  },
  {
    id: 13,
    title: '跑步鞋 42 码',
    price: 90,
    cover: cover('pair of used running shoes on a light gray background, realistic photo'),
    condition: '七成新',
    campus: '西校区',
    categoryId: 5,
    sellerNickname: '周舟',
    viewCount: 57,
    createdAt: '2026-11-03'
  },
  {
    id: 14,
    title: '帆布托特包 米白色',
    price: 25,
    cover: cover('beige canvas tote bag on a chair, natural light, realistic photo'),
    condition: '全新',
    campus: '东校区',
    categoryId: 5,
    sellerNickname: '林小满',
    viewCount: 22,
    createdAt: '2026-11-12'
  },
  {
    id: 15,
    title: '考研英语词汇 乱序版',
    price: 18,
    cover: cover('thick english vocabulary book with pen on a library table, realistic photo'),
    condition: '九成新',
    campus: '东校区',
    categoryId: 1,
    sellerNickname: '陈一鸣',
    viewCount: 73,
    createdAt: '2026-11-08'
  },
  {
    id: 16,
    title: '24 寸显示器 1080P',
    price: 380,
    cover: cover('24 inch computer monitor on a desk in a dorm room, realistic photo'),
    condition: '八成新',
    campus: '南湖校区',
    categoryId: 2,
    sellerNickname: '许知远',
    viewCount: 156,
    createdAt: '2026-11-07'
  }
]

// 用户自己发布的商品，存本地，刷新后仍在
const CREATED_KEY = 'mock-created-items'

function readCreated() {
  try {
    const list = JSON.parse(localStorage.getItem(CREATED_KEY) || '[]')
    return Array.isArray(list) ? list : []
  } catch (error) {
    return []
  }
}

const createdItems = readCreated()

function allItems() {
  return [...createdItems, ...ITEMS]
}

function saveCreated() {
  localStorage.setItem(CREATED_KEY, JSON.stringify(createdItems))
}

// 商品状态（在售/已售/已下架）单独存本地，刷新后仍保留
const STATUS_KEY = 'mock-item-status'

function readStatusMap() {
  try {
    const map = JSON.parse(localStorage.getItem(STATUS_KEY) || '{}')
    return map && typeof map === 'object' ? map : {}
  } catch (error) {
    return {}
  }
}

function statusOf(item) {
  return readStatusMap()[item.id] || item.status || 'on_sale'
}

function saveStatus(id, status) {
  const map = readStatusMap()
  map[id] = status
  localStorage.setItem(STATUS_KEY, JSON.stringify(map))
}

/**
 * 商品列表 Mock
 * 与后端 GET /api/items 的分页结构保持一致。
 */
export async function mockGetItems({
  keyword = '',
  categoryId = 0,
  page = 1,
  size = 12,
  sort = 'latest',
  minPrice = null,
  maxPrice = null,
  campus = '',
  sellerNickname = '',
  status = 'on_sale'
} = {}) {
  await delay(350)

  const kw = keyword.trim().toLowerCase()
  let filtered = allItems().filter((item) => {
    const matchCategory = !categoryId || item.categoryId === categoryId
    const matchKeyword =
      !kw ||
      item.title.toLowerCase().includes(kw) ||
      item.campus.toLowerCase().includes(kw) ||
      item.condition.toLowerCase().includes(kw)
    const matchPrice =
      (minPrice === null || minPrice === '' || item.price >= Number(minPrice)) &&
      (maxPrice === null || maxPrice === '' || item.price <= Number(maxPrice))
    const matchCampus = !campus || item.campus === campus
    const matchSeller = !sellerNickname || item.sellerNickname === sellerNickname
    const matchStatus = status === 'all' || statusOf(item) === status
    return matchCategory && matchKeyword && matchPrice && matchCampus && matchSeller && matchStatus
  })

  filtered = filtered.map((item) => ({
    ...item,
    status: statusOf(item),
    images: item.images?.length ? item.images : [item.cover]
  }))

  if (sort === 'priceAsc') {
    filtered.sort((a, b) => a.price - b.price)
  } else if (sort === 'priceDesc') {
    filtered.sort((a, b) => b.price - a.price)
  } else if (sort === 'hot') {
    filtered.sort((a, b) => b.viewCount - a.viewCount)
  } else {
    filtered.sort((a, b) => String(b.createdAt).localeCompare(String(a.createdAt)))
  }

  const start = (page - 1) * size

  return {
    list: filtered.slice(start, start + size),
    total: filtered.length,
    page,
    size
  }
}

/**
 * 记录一次商品浏览（点击量 +1）
 * 同一账号看同一件商品只计一次，真实后端应按 user_id + item_id 去重。
 */
export async function mockRecordItemView(id, account = '') {
  const item = allItems().find((row) => row.id === Number(id))
  if (!item) return 0

  const key = 'mock-viewed-ids'
  let viewed = []
  try {
    viewed = JSON.parse(localStorage.getItem(key) || '[]')
  } catch (error) {
    viewed = []
  }

  const mark = `${account}:${id}`
  if (!viewed.includes(mark)) {
    viewed.push(mark)
    localStorage.setItem(key, JSON.stringify(viewed))
    item.viewCount += 1
  }

  return item.viewCount
}

/**
 * 按卖家昵称查商品（卖家主页用）
 */
export function findItemsBySeller(nickname) {
  return allItems()
    .filter((item) => item.sellerNickname === nickname)
    .map((item) => ({
      ...item,
      status: statusOf(item),
      images: item.images?.length ? item.images : [item.cover]
    }))
}

/**
 * 按 id 查商品（收藏夹、订单展示用）
 */
export function findItemById(id) {
  const item = allItems().find((row) => row.id === Number(id))
  if (!item) return null
  return {
    ...item,
    status: statusOf(item),
    images: item.images?.length ? item.images : [item.cover]
  }
}

/**
 * 更新商品状态：on_sale / off_shelf / sold
 */
export async function mockUpdateItemStatus(id, status) {
  await delay(180)

  const target = allItems().find((row) => row.id === Number(id))
  if (!target) {
    const error = new Error('商品不存在')
    error.code = 404
    throw error
  }

  const created = createdItems.find((row) => row.id === Number(id))
  if (created) {
    created.status = status
    saveCreated()
  }
  saveStatus(Number(id), status)

  return { ...target, status }
}

/**
 * 删除自己发布的商品（仅限本地发布的）
 */
export async function mockDeleteItem(id) {
  await delay(200)

  const index = createdItems.findIndex((row) => row.id === Number(id))
  if (index === -1) {
    const error = new Error('演示商品不支持删除，可改为下架')
    error.code = 400
    throw error
  }

  createdItems.splice(index, 1)
  saveCreated()
  return true
}

/**
 * 编辑商品
 */
export async function mockUpdateItem(id, payload) {
  await delay(320)

  const target = createdItems.find((row) => row.id === Number(id))
  if (!target) {
    const error = new Error('演示商品不支持编辑，可发布自己的商品再试')
    error.code = 400
    throw error
  }

  Object.assign(target, {
    title: payload.title,
    categoryId: Number(payload.categoryId),
    price: Number(payload.price),
    condition: payload.condition,
    campus: payload.campus,
    description: payload.description,
    cover: payload.images?.[0] || target.cover,
    images: payload.images?.length ? payload.images : [target.cover]
  })
  saveCreated()

  return target
}

// 商品描述（卖家填写）
const DESCRIPTIONS = {
  1: '大一上学期用过，书页干净，只有少量标注，可送到宿舍楼下。',
  2: '四级一次过，真题只做了前两套，词汇书没有笔记。',
  3: '换了静音键盘闲置，红轴手感完好，键帽无磨损。',
  4: '自用一年，屏幕无划痕，电池健康 89%，带原装充电器。',
  5: '买了新耳机，这副闲置，续航正常，附四副耳塞。',
  6: '宿舍换了大灯，台灯闲置，三档调光都正常。',
  7: '买多了没用上，两只一起出，可折叠收纳。',
  8: '毕业带不走，煮面煮粥都行，宿舍限电 800W 内可用。',
  9: '换新球了，这个还能打，气很足。',
  10: '买来练了两次就吃灰，无破损，送收纳带。',
  11: '毕业出，链条刚上过油，带一把 U 型锁。',
  12: '去年买的，穿过几次，无污渍无破损，L 码。',
  13: '脚长大了穿不下，鞋底磨损轻微。',
  14: '买重了，全新未拆吊牌。',
  15: '背了两遍，书角轻微卷起，内页干净。',
  16: '换了更大的屏，这台闲置，无坏点，附 DP 线。'
}

export const SELLER_CREDIT = {
  林小满: 98,
  陈一鸣: 92,
  周舟: 96,
  许知远: 88,
  赵一诺: 95,
  孙可: 90
}

/**
 * 商品详情 Mock
 * 与后端 GET /api/items/{id} 的结构保持一致。
 */
export async function mockGetItem(id) {
  await delay(280)

  const item = allItems().find((row) => row.id === Number(id))
  if (!item) {
    const error = new Error('商品不存在或已下架')
    error.code = 404
    throw error
  }

  return {
    ...item,
    description: item.description || DESCRIPTIONS[item.id] || '卖家暂未填写描述。',
    status: statusOf(item),
    images: item.images?.length ? item.images : [item.cover],
    seller: {
      nickname: item.sellerNickname,
      avatar: '',
      campus: item.campus,
      credit: SELLER_CREDIT[item.sellerNickname] ?? 90
    }
  }
}

/**
 * 发布商品 Mock
 * 与后端 POST /api/items 的结构保持一致。
 */
export async function mockCreateItem(payload) {
  await delay(400)

  const item = {
    id: Date.now(),
    title: payload.title,
    price: Number(payload.price),
    cover: payload.images?.[0] || payload.cover,
    images: payload.images?.length ? payload.images : [payload.cover],
    condition: payload.condition,
    campus: payload.campus,
    categoryId: Number(payload.categoryId),
    description: payload.description,
    sellerNickname: payload.sellerNickname || '我',
    viewCount: 0,
    status: 'on_sale',
    createdAt: new Date().toISOString().slice(0, 10)
  }

  createdItems.unshift(item)
  saveCreated()

  return item
}
