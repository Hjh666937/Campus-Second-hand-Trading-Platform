import request from './request'

/**
 * 登录、注册、个人资料相关接口。
 * 这几项已接入真实后端，不再走 Mock。
 */

/**
 * 登录
 * @param {{ account: string, password: string, remember?: boolean }} data
 * @returns {Promise<{ token: string, user: object }>}
 */
export function login(data) {
  return request.post('/auth/login', data)
}

/**
 * 注册（仅学生）
 * @param {{ account: string, nickname: string, campus: string, gender: string, password: string }} data
 * @returns {Promise<object>} 新建的用户信息，不含密码
 */
export function register(data) {
  return request.post('/auth/register', data)
}

/**
 * 获取当前登录用户信息（刷新页面后同步数据库里的最新资料）
 * @returns {Promise<object>}
 */
export function fetchMe() {
  return request.get('/users/me')
}

/**
 * 修改个人资料（昵称、校区、性别）
 * @param {{ nickname?: string, campus?: string, gender?: string }} data
 * @returns {Promise<object>} 更新后的用户信息
 */
export function updateProfile(data) {
  return request.put('/users/me', data)
}

/**
 * 修改登录密码
 * @param {{ oldPassword: string, newPassword: string }} data
 * @returns {Promise<null>}
 */
export function changePassword(data) {
  return request.put('/users/me/password', data)
}

/**
 * 上传头像
 * @param {File} file
 * @returns {Promise<{ avatarUrl: string }>}
 */
export function uploadAvatar(file) {
  const form = new FormData()
  form.append('file', file)
  return request.post('/users/me/avatar', form)
}
