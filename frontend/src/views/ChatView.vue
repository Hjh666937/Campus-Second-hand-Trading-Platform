<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import { getConversations, getMessages, markRead, sendMessage } from '@/api/chat'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const account = computed(() => userStore.userInfo?.account || '')
const conversations = ref([])
const activeId = ref(route.params.id ? Number(route.params.id) : null)
const messages = ref([])
const draft = ref('')
const sending = ref(false)
const loading = ref(true)
const listRef = ref(null)

const activeConv = computed(
  () => conversations.value.find((row) => row.id === activeId.value) || null
)

function formatTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  const sameDay = new Date().toDateString() === date.toDateString()
  return sameDay
    ? `${pad(date.getHours())}:${pad(date.getMinutes())}`
    : `${pad(date.getMonth() + 1)}/${pad(date.getDate())}`
}

function scrollToBottom() {
  nextTick(() => {
    const el = listRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

async function loadMessages(id) {
  messages.value = await getMessages(id)
  await markRead(id, account.value)

  const conv = conversations.value.find((row) => row.id === id)
  if (conv) conv.unread = 0

  scrollToBottom()
}

async function selectConversation(id) {
  activeId.value = Number(id)
  await router.replace({ name: 'chat', params: { id: activeId.value } })
  await loadMessages(activeId.value)
}

async function loadConversations() {
  try {
    conversations.value = await getConversations(account.value)

    if (!activeId.value && conversations.value.length) {
      await selectConversation(conversations.value[0].id)
    } else if (activeId.value) {
      await loadMessages(activeId.value)
    }
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '会话加载失败')
    }
  } finally {
    loading.value = false
  }
}

async function handleSend() {
  const content = draft.value.trim()
  if (!content || !activeId.value) return

  sending.value = true
  try {
    const message = await sendMessage({
      conversationId: activeId.value,
      account: account.value,
      nickname: userStore.nickname,
      content
    })

    messages.value = [...messages.value, message]
    draft.value = ''

    const conv = conversations.value.find((row) => row.id === activeId.value)
    if (conv) {
      conv.lastMessage = content
      conv.lastAt = message.createdAt
    }

    scrollToBottom()
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '发送失败')
    }
  } finally {
    sending.value = false
  }
}

function goHome() {
  router.push('/')
}

// 轮询拉取新消息（真实环境可换成 WebSocket 推送）
let timer = null

async function refresh() {
  if (sending.value) return
  try {
    conversations.value = await getConversations(account.value)
    if (!activeId.value) return

    const incoming = await getMessages(activeId.value)
    if (incoming.length !== messages.value.length) {
      messages.value = incoming
      scrollToBottom()
    }
    await markRead(activeId.value, account.value)
  } catch (error) {
    // 轮询失败静默处理，避免频繁弹提示
  }
}

onMounted(async () => {
  await loadConversations()
  timer = setInterval(refresh, 5000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="chat-page">
    <AppHeader />

    <main class="chat-main">
      <div class="chat-toolbar">
        <button class="back-btn" type="button" @click="goHome">← 返回首页</button>
      </div>

      <div class="chat-shell">
        <aside class="conv-list">
          <div class="conv-head">
            <h2>消息</h2>
          </div>

          <div v-if="loading" class="conv-tip">加载中…</div>
          <div v-else-if="!conversations.length" class="conv-tip">
            还没有聊天<br />
            去商品页点「联系卖家」发起
          </div>

          <button
            v-for="conv in conversations"
            :key="conv.id"
            class="conv-item"
            :class="{ active: conv.id === activeId }"
            type="button"
            @click="selectConversation(conv.id)"
          >
            <span class="conv-avatar">{{ (conv.peerNickname || conv.sellerNickname).slice(0, 1) }}</span>
            <span class="conv-body">
              <span class="conv-line">
                <span class="conv-name">{{ conv.peerNickname || conv.sellerNickname }}</span>
                <span class="conv-time">{{ formatTime(conv.lastAt) }}</span>
              </span>
              <span class="conv-preview">{{ conv.lastMessage || '已建立会话，打个招呼吧' }}</span>
            </span>
            <span v-if="conv.unread" class="conv-badge">{{ conv.unread }}</span>
          </button>
        </aside>

        <section class="window">
          <template v-if="activeConv">
            <header class="window-head">
              <img v-if="activeConv.itemCover" :src="activeConv.itemCover" class="thumb" alt="商品图" />
              <div class="head-info">
                <p class="head-name">{{ activeConv.peerNickname || activeConv.sellerNickname }}</p>
                <p class="head-item">{{ activeConv.itemTitle }}</p>
              </div>
            </header>

            <div ref="listRef" class="msg-list">
              <div
                v-for="msg in messages"
                :key="msg.id"
                class="msg"
                :class="{ mine: msg.senderAccount === account }"
              >
                <span class="bubble">{{ msg.content }}</span>
                <span class="msg-time">{{ formatTime(msg.createdAt) }}</span>
              </div>

              <p v-if="!messages.length" class="msg-empty">
                和 {{ activeConv.peerNickname || activeConv.sellerNickname }} 聊聊这件商品吧
              </p>
            </div>

            <footer class="composer">
              <el-input
                v-model="draft"
                type="textarea"
                :rows="2"
                resize="none"
                maxlength="300"
                placeholder="输入消息，Enter 发送，Shift + Enter 换行"
                @keydown.enter.exact.prevent="handleSend"
              />
              <el-button type="primary" :loading="sending" @click="handleSend">发送</el-button>
            </footer>
          </template>

          <div v-else class="window-empty">选择左侧会话开始聊天</div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.chat-page {
  min-height: 100vh;
  background: #f6f8f7;
}

.chat-main {
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px;
}

.chat-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.back-btn {
  padding: 6px 14px;
  border: 1px solid #e3e9e6;
  border-radius: 10px;
  background: #ffffff;
  font-size: 13px;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}

.back-btn:hover {
  color: #15803d;
  border-color: #16a34a;
  background: #f6fcf8;
}

.chat-shell {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  height: calc(100vh - 172px);
  min-height: 520px;
  overflow: hidden;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 18px 50px rgba(15, 60, 40, 0.06);
}

.conv-list {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  border-right: 1px solid #edf1ef;
  background: #fbfcfb;
}

.conv-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 18px 12px;
}

.conv-head h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.conv-tip {
  padding: 36px 18px;
  font-size: 13px;
  line-height: 1.9;
  color: #9ca3af;
  text-align: center;
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.conv-item:hover {
  background: #f2f6f4;
}

.conv-item.active {
  background: #eefaf1;
}

.conv-avatar {
  width: 38px;
  height: 38px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: #dcf2e5;
  font-size: 14px;
  font-weight: 600;
  color: #0e5c3a;
}

.conv-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.conv-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.conv-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

.conv-time {
  flex: 0 0 auto;
  font-size: 11px;
  color: #b0b8b4;
}

.conv-preview {
  overflow: hidden;
  font-size: 12px;
  color: #9ca3af;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.conv-badge {
  flex: 0 0 auto;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: #e0523f;
  font-size: 11px;
  line-height: 18px;
  color: #ffffff;
  text-align: center;
}

.window {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.window-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-bottom: 1px solid #edf1ef;
}

.thumb {
  width: 40px;
  height: 40px;
  flex: 0 0 auto;
  border-radius: 8px;
  object-fit: cover;
  background: #f1f4f2;
}

.head-name {
  margin: 0 0 3px;
  font-size: 14px;
  font-weight: 600;
}

.head-item {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}

.msg-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fafcfb;
}

.msg {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 16px;
}

.msg.mine {
  align-items: flex-end;
}

.bubble {
  max-width: 68%;
  padding: 10px 14px;
  border-radius: 12px;
  background: #ffffff;
  font-size: 14px;
  line-height: 1.7;
  color: #1f2937;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 2px 8px rgba(15, 60, 40, 0.05);
}

.msg.mine .bubble {
  background: #16a34a;
  color: #ffffff;
}

.msg-time {
  margin-top: 6px;
  font-size: 11px;
  color: #b0b8b4;
}

.msg-empty {
  padding: 40px 0;
  font-size: 13px;
  color: #9ca3af;
  text-align: center;
}

.composer {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 14px 20px;
  border-top: 1px solid #edf1ef;
}

.window-empty {
  flex: 1;
  display: grid;
  place-items: center;
  font-size: 13px;
  color: #9ca3af;
}

@media (max-width: 780px) {
  .chat-main {
    padding: 16px;
  }

  .chat-shell {
    grid-template-columns: 1fr;
    height: auto;
  }

  .conv-list {
    max-height: 220px;
    border-right: none;
    border-bottom: 1px solid #edf1ef;
  }

  .msg-list {
    min-height: 320px;
  }
}
</style>
