import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const res = response.data

    // 后端统一响应：{ code, message, data }
    if (res && typeof res.code !== 'undefined' && res.code !== 0) {
      const message = res.message || '请求失败'
      ElMessage.error(message)
      const error = new Error(message)
      error.displayed = true
      return Promise.reject(error)
    }

    return res && typeof res.code !== 'undefined' ? res.data : res
  },
  (error) => {
    const status = error.response?.status
    const onLoginPage = window.location.pathname.startsWith('/login')

    // 登录页的 401 即账号或密码错误，交给页面统一提示，不重复弹窗
    if (status === 401 && onLoginPage) {
      const authError = new Error(error.response?.data?.message || '账号或密码错误')
      authError.displayed = false
      return Promise.reject(authError)
    }

    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      window.location.href = '/login'
      ElMessage.error('登录状态已失效，请重新登录')
      error.displayed = true
      return Promise.reject(error)
    }

    const message =
      error.code === 'ECONNABORTED'
        ? '请求超时，请稍后重试'
        : error.response?.data?.message || '网络异常，请稍后重试'

    ElMessage.error(message)
    error.displayed = true
    return Promise.reject(error)
  }
)

export default request
