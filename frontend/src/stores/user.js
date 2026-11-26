import { defineStore } from 'pinia'
import { fetchMe, login as loginApi } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null')
  }),

  getters: {
    isLoggedIn: (state) => Boolean(state.token),
    nickname: (state) => state.userInfo?.nickname || '同学'
  },

  actions: {
    async login(payload) {
      const data = await loginApi(payload)

      this.token = data.token
      this.userInfo = data.user

      localStorage.setItem('token', data.token)
      localStorage.setItem('userInfo', JSON.stringify(data.user))

      return data
    },

    updateProfile(patch) {
      this.userInfo = { ...this.userInfo, ...patch }
      localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
    },

    // 从后端拉取最新资料，页面刷新后同步数据库里的改动
    async refreshProfile() {
      if (!this.token) return null
      const data = await fetchMe()
      this.updateProfile(data)
      return data
    },

    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  }
})
