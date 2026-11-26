import request from './request'

/**
 * 商品相关接口，已接入真实后端。
 */

/**
 * 商品分类（发布页与首页筛选用）
 * @returns {Promise<Array<{ id: number, name: string }>>}
 */
export function getCategories() {
  return request.get('/categories')
}

/**
 * 商品列表（分页 + 搜索 + 筛选 + 排序）
 * @param {{ keyword?: string, categoryId?: number, page?: number, size?: number,
 *           sort?: 'latest'|'priceAsc'|'priceDesc'|'hot', minPrice?: number,
 *           maxPrice?: number, campus?: string, sellerNickname?: string,
 *           status?: 'on_sale'|'off_shelf'|'sold'|'all' }} params
 * @returns {Promise<{ list: object[], total: number, page: number, size: number }>}
 */
export function getItems(params) {
  return request.get('/items', { params })
}

/**
 * 商品详情
 * @param {number|string} id 商品 id
 * @returns {Promise<object>} 含 description、images、status、seller 等信息
 */
export function getItem(id) {
  return request.get(`/items/${id}`)
}

/**
 * 记录商品浏览，点击量 +1
 * @param {number} id 商品 id
 * @returns {Promise<{ viewCount: number }>}
 */
export function recordItemView(id) {
  return request.post(`/items/${id}/view`)
}

/**
 * 发布商品
 * @param {{ title: string, categoryId: number, price: number, condition: string,
 *           campus: string, description: string, images: string[] }} data
 * @returns {Promise<object>} 新建的商品
 */
export function createItem(data) {
  return request.post('/items', data)
}

/**
 * 编辑商品
 */
export function updateItem(id, data) {
  return request.put(`/items/${id}`, data)
}

/**
 * 修改商品状态：on_sale 在售 / off_shelf 下架 / sold 已售
 */
export function updateItemStatus(id, status) {
  return request.patch(`/items/${id}/status`, { status })
}

/**
 * 删除商品（仅自己发布的）
 */
export function deleteItem(id) {
  return request.delete(`/items/${id}`)
}
