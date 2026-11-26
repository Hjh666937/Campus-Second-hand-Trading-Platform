/**
 * AI 能力 Mock（预留）
 * 与后端约定：
 *   POST /api/ai/price       输入标题/分类/成色 → 返回建议价格区间
 *   POST /api/ai/description 输入标题/分类/成色/校区 → 返回商品描述文案
 *   POST /api/ai/chat        通用对话（客服/导购），返回一段回复
 *
 * 目前用规则模拟，接入真实模型时只需替换本文件，页面代码不用改。
 */

const delay = (ms = 500) => new Promise((resolve) => setTimeout(resolve, ms))

const CATEGORY_BASE = {
  1: 30,
  2: 320,
  3: 45,
  4: 90,
  5: 60
}

const CONDITION_RATE = {
  全新: 1,
  九成新: 0.75,
  八成新: 0.6,
  七成新: 0.45,
  六成新及以下: 0.3
}

const CATEGORY_NAME = {
  1: '教材书籍',
  2: '数码电子',
  3: '生活用品',
  4: '运动户外',
  5: '衣物鞋包'
}

function roundTo5(value) {
  return Math.max(5, Math.round(value / 5) * 5)
}

export async function mockSuggestPrice({ title = '', categoryId = 1, condition = '九成新' }) {
  await delay(600)

  const base = CATEGORY_BASE[categoryId] || 50
  const rate = CONDITION_RATE[condition] || 0.6

  // 标题里出现数字时，粗略当作原价参考
  const matched = String(title).match(/(\d{2,5})/)
  const origin = matched ? Number(matched[1]) : base * 3

  const suggest = roundTo5(origin * rate)
  const low = roundTo5(suggest * 0.8)
  const high = roundTo5(suggest * 1.2)

  return {
    low,
    high,
    suggest,
    reason: `参考「${CATEGORY_NAME[categoryId] || '同类商品'}」和「${condition}」的成交价得出`
  }
}

export async function mockGenerateDescription({
  title = '',
  categoryId = 1,
  condition = '九成新',
  campus = ''
}) {
  await delay(800)

  const category = CATEGORY_NAME[categoryId] || '闲置物品'
  const place = campus || '校内'

  return [
    `${title}，${condition}。`,
    `${condition === '全新' ? '买来基本没用过，包装齐全。' : '正常使用过一段时间，功能完好，没有明显磕碰。'}`,
    `属于${category}，成色如实描述，介意者慎拍。`,
    `可约在${place}当面交易，支持先验货再付款。`
  ].join('')
}

export async function mockChat({ message = '' }) {
  await delay(700)

  const text = String(message)
  if (text.includes('价格') || text.includes('多少钱')) {
    return {
      reply: '可以参考同类成色的成交价：一般在原价的 3-7 折之间。写清楚成色和购入时间更容易卖出。'
    }
  }
  if (text.includes('描述') || text.includes('怎么发')) {
    return {
      reply: '建议写清三件事：购入时间、使用情况、有无瑕疵；再注明交易校区和是否支持当面验货。'
    }
  }
  return {
    reply: '我是校园二手助手。可以帮你估价、写商品描述，也可以回答交易流程问题。'
  }
}
