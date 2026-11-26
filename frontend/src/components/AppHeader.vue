<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUnreadCount } from '@/api/chat'
import { getNotifications } from '@/api/notifications'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const avatar = computed(() => userStore.userInfo?.avatar || '')
const initial = computed(() => userStore.nickname.slice(0, 1))
const chatUnread = ref(0)
const notifyUnread = ref(0)

// 合并红点：聊天未读 + 通知未读，取大的那个
const totalUnread = computed(() => chatUnread.value + notifyUnread.value)

function goProfile() {
  router.push({ name: 'profile' })
}

function goChat() {
  router.push({ name: 'chat' })
}

function goMine() {
  // 有通知未读 → 直接跳通知 tab
  if (notifyUnread.value > 0) {
    router.push({ name: 'mine', query: { tab: 'notifications' } })
  } else {
    router.push({ name: 'mine' })
  }
}

function goAdmin() {
  router.push({ name: 'admin' })
}

async function refreshChatUnread() {
  if (userStore.userInfo?.role === 'admin') return
  try {
    chatUnread.value = await getUnreadCount(userStore.userInfo?.account || '')
  } catch {
    chatUnread.value = 0
  }
}

async function refreshNotifyUnread() {
  if (userStore.userInfo?.role === 'admin') return
  try {
    const data = await getNotifications()
    notifyUnread.value = data.unread || 0
  } catch {
    notifyUnread.value = 0
  }
}

// 定时刷新两类未读数
let chatTimer = null
let notifyTimer = null

onMounted(() => {
  refreshChatUnread()
  refreshNotifyUnread()
  chatTimer = setInterval(refreshChatUnread, 8000)
  notifyTimer = setInterval(refreshNotifyUnread, 10000)
})

onUnmounted(() => {
  if (chatTimer) clearInterval(chatTimer)
  if (notifyTimer) clearInterval(notifyTimer)
})

async function handleLogout() {
  try {
    await ElMessageBox.confirm('退出后需要重新登录才能发布和购买商品。', '确定退出登录吗？', {
      confirmButtonText: '退出登录',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  userStore.logout()
  ElMessage.success('已退出登录')
  router.replace('/login')
}

// 暴露给登录页调用：登录后弹出未读通知
async function popUnreadNotifications(maxCount = 3) {
  if (!userStore.userInfo || userStore.userInfo.role === 'admin') return
  try {
    const data = await getNotifications()
    const unreadList = (data.list || []).filter((row) => !row.isRead).slice(0, maxCount)
    notifyUnread.value = data.unread || 0
    if (unreadList.length === 0) return

    // 延迟 500ms 等路由跳转完成后再弹，避免被首页动画盖住
    setTimeout(() => {
      unreadList.forEach((row, idx) => {
        import('element-plus').then(({ ElNotification }) => {
          ElNotification({
            title: row.title,
            message: row.content,
            type: idx === 0 ? 'success' : 'info',
            duration: 5000,
            onClick: () => {
              router.push({ name: 'mine', query: { tab: 'notifications' } })
            }
          })
        })
      })
    }, 500)
  } catch {
    // 通知弹不出来就静默忽略，不影响正常登录
  }
}

defineExpose({ popUnreadNotifications })
</script>

<template>
  <header class="app-header">
    <router-link class="logo" to="/">校园二手</router-link>

    <div class="user-area">
      <!-- 通知红点 -->
      <el-badge
        v-if="notifyUnread > 0 && userStore.userInfo?.role !== 'admin'"
        :value="notifyUnread > 99 ? '99+' : notifyUnread"
        :hidden="notifyUnread === 0"
        class="header-badge"
      >
        <button class="nav-link" type="button" @click="goMine">通知</button>
      </el-badge>

      <!-- 聊天红点 -->
      <el-badge
        v-if="userStore.userInfo?.role !== 'admin'"
        :value="chatUnread > 99 ? '99+' : chatUnread"
        :hidden="chatUnread === 0"
        class="header-badge"
      >
        <button class="nav-link" type="button" @click="goChat">消息</button>
      </el-badge>

      <button class="nav-link" type="button" @click="goMine">我的</button>
      <button
        v-if="userStore.userInfo?.role === 'admin'"
        class="nav-link"
        type="button"
        @click="goAdmin"
      >
        管理后台
      </button>
      <button class="user-link" type="button" @click="goProfile">
        <span class="avatar">
          <img v-if="avatar" :src="avatar" alt="头像" />
          <span v-else>{{ initial }}</span>
        </span>
        <span class="nickname">{{ userStore.nickname }}</span>
      </button>
      <el-button link type="primary" @click="handleLogout">退出登录</el-button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 32px;
  background: #ffffff;
  border-bottom: 1px solid #e8ecea;
}

.logo {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 1px;
  color: #0e5c3a;
  text-decoration: none;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-link {
  padding: 0;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #4b5563;
  cursor: pointer;
}

.nav-link:hover {
  color: #15803d;
}

.header-badge {
  display: flex;
  align-items: center;
}

.user-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px 4px 4px;
  border: none;
  border-radius: 999px;
  background: transparent;
  font-size: 14px;
  color: #1f2937;
  cursor: pointer;
}

.user-link:hover {
  background: #f2f6f4;
}

.avatar {
  width: 32px;
  height: 32px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  overflow: hidden;
  border: 1px solid #cfe6da;
  border-radius: 50%;
  background: #dcf2e5;
  font-size: 14px;
  font-weight: 600;
  color: #0e5c3a;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.nickname {
  max-width: 120px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
</style>
