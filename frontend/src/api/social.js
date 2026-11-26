import request from './request'

/* 收藏 */

export function toggleFavorite({ itemId }) {
  return request.post('/favorites', { itemId })
}

export function getFavorites() {
  return request.get('/favorites')
}

export function isFavorite({ itemId }) {
  return request.get('/favorites/check', { params: { itemId } })
}

/* 举报 */

export function createReport({ itemId, reason, detail }) {
  return request.post('/reports', { itemId, reason, detail })
}

/* 评价与卖家资料 */

export function getReviews(nickname) {
  return request.get('/reviews', { params: { seller: nickname } })
}

export function getSellerProfile(id) {
  return request.get(`/users/id/${id}`)
}
