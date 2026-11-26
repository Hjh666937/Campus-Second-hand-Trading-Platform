<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import ItemCard from '@/components/ItemCard.vue'
import { deleteItem, getItems, updateItemStatus } from '@/api/items'
import { getOrders, reviewOrder, updateOrderStatus } from '@/api/orders'
import { getFavorites } from '@/api/social'
import { getNotifications, readNotifications } from '@/api/notifications'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const account = computed(() => userStore.userInfo?.account || '')
const nickname = computed(() => userStore.nickname)

const activeTab = ref(route.query.tab || 'published')
const published = ref([])
const bought = ref([])
const sold = ref([])
const favorites = ref([])
const notifications = ref([])
const notifyUnread = ref(0)
const loading = ref(false)

const STATUS_TEXT = {
  pending: '待卖家确认',
  confirmed: '待当面交易',
  completed: '已完成',
  cancelled: '已取消'
}

const ORDER_ACTION_TEXT = {
  confirmed: '已确认订单，请与买家当面交易',
  completed: '交易已完成',
  cancelled: '订单已取消'
}

const ITEM_STATUS_TEXT = {
  on_sale: '在售',
  off_shelf: '已下架',
  sold: '已售出'
}

const reviewVisible = ref(false)
const reviewOrderId = ref(null)
const reviewRating = ref(5)
const reviewContent = ref('')
const reviewSubmitting = ref(false)

async function loadPublished() {
  const data = await getItems({
    sellerId: userStore.userInfo?.id,
    status: 'all',
    size: 100,
    page: 1
  })
  published.value = data.list
}

async function loadOrders() {
  bought.value = await getOrders({ account: account.value, nickname: nickname.value, role: 'buyer' })
  sold.value = await getOrders({ account: account.value, nickname: nickname.value, role: 'seller' })
}

async function loadFavorites() {
  favorites.value = await getFavorites(account.value)
}

async function loadNotifications() {
  const data = await getNotifications()
  notifications.value = data.list
  notifyUnread.value = data.unread
}

async function markAllRead() {
  try {
    await readNotifications()
    notifications.value = notifications.value.map((row) => ({ ...row, isRead: true }))
    notifyUnread.value = 0
    ElMessage.success('已全部标记为已读')
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '操作失败')
  }
}

async function loadAll() {
  loading.value = true
  try {
    await Promise.all([loadPublished(), loadOrders(), loadFavorites(), loadNotifications()])
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '加载失败')
    }
  } finally {
    loading.value = false
  }
}

function switchTab(name) {
  activeTab.value = name
  router.replace({ name: 'mine', query: { tab: name } })
}

function goDetail(row) {
  router.push({ name: 'item-detail', params: { id: row.id } })
}

function goEdit(row) {
  router.push({ name: 'publish', query: { id: row.id } })
}

async function changeItemStatus(row, status) {
  try {
    const result = await updateItemStatus(row.id, status)
    if (status === 'sold' && result?.cancelledOrders) {
      ElMessage.success(`已标记已售，${result.cancelledOrders} 笔待确认订单已自动取消`)
    } else {
      ElMessage.success('操作成功')
    }
    await loadPublished()
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '操作失败')
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除「${row.title}」吗？删除后不可恢复。`, '删除商品', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch (error) {
    return
  }

  try {
    await deleteItem(row.id)
    ElMessage.success('已删除')
    await loadPublished()
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '删除失败')
  }
}

async function changeOrderStatus(order, status) {
  try {
    await updateOrderStatus(order.id, status)
    ElMessage.success(ORDER_ACTION_TEXT[status] || '操作成功')
    await loadOrders()
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '操作失败')
  }
}

async function confirmCancel(order) {
  try {
    await ElMessageBox.confirm('确定取消这笔订单吗？', '取消订单', {
      confirmButtonText: '确定取消',
      cancelButtonText: '再想想',
      type: 'warning'
    })
  } catch (error) {
    return
  }
  changeOrderStatus(order, 'cancelled')
}

async function confirmReject(order) {
  try {
    await ElMessageBox.confirm('拒绝后买家会看到订单已取消，确定吗？', '拒绝订单', {
      confirmButtonText: '确定拒绝',
      cancelButtonText: '再想想',
      type: 'warning'
    })
  } catch (error) {
    return
  }
  changeOrderStatus(order, 'cancelled')
}

function formatOrderTime(value) {
  return value ? String(value).slice(0, 16) : ''
}

function openReview(order) {
  reviewOrderId.value = order.id
  reviewRating.value = 5
  reviewContent.value = ''
  reviewVisible.value = true
}

async function submitReview() {
  reviewSubmitting.value = true
  try {
    await reviewOrder(reviewOrderId.value, {
      rating: reviewRating.value,
      content: reviewContent.value.trim()
    })
    reviewVisible.value = false
    ElMessage.success('评价已提交')
    await loadOrders()
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '评价失败')
  } finally {
    reviewSubmitting.value = false
  }
}

onMounted(loadAll)
</script>

<template>
  <div class="mine-page">
    <AppHeader />

    <main class="mine-main" v-loading="loading">
      <div class="mine-head">
        <div>
          <h1>我的</h1>
          <p class="sub">{{ nickname }} · 学号 {{ account }}</p>
        </div>
        <div class="head-actions">
          <el-button @click="router.push('/')">返回首页</el-button>
          <el-button
            v-if="userStore.userInfo?.role !== 'admin'"
            type="primary"
            @click="router.push({ name: 'publish' })"
          >
            我要出闲置
          </el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab" @tab-change="switchTab">
        <el-tab-pane label="我发布的" name="published">
          <div v-if="!published.length" class="empty">还没有发布过商品</div>
          <div v-else class="item-list">
            <div v-for="row in published" :key="row.id" class="item-row">
              <img class="row-cover" :src="row.cover" alt="" @click="goDetail(row)" />
              <div class="row-body">
                <p class="row-title" @click="goDetail(row)">{{ row.title }}</p>
                <p class="row-meta">
                  ¥{{ row.price }} · {{ row.condition }} · {{ row.campus }} · {{ row.viewCount }} 看过
                </p>
                <p class="row-meta">发布于 {{ row.createdAt }}</p>
                <p class="row-status" :class="row.status">{{ ITEM_STATUS_TEXT[row.status] || '在售' }}</p>
              </div>
              <div class="row-actions">
                <el-button size="small" @click="goEdit(row)">编辑</el-button>
                <el-button
                  v-if="row.status === 'on_sale'"
                  size="small"
                  @click="changeItemStatus(row, 'off_shelf')"
                >
                  下架
                </el-button>
                <el-button
                  v-if="row.status === 'off_shelf'"
                  size="small"
                  type="primary"
                  plain
                  @click="changeItemStatus(row, 'on_sale')"
                >
                  上架
                </el-button>
                <el-button
                  v-if="row.status !== 'sold'"
                  size="small"
                  type="success"
                  plain
                  @click="changeItemStatus(row, 'sold')"
                >
                  标记已售
                </el-button>
                <el-button size="small" type="danger" plain @click="confirmDelete(row)">删除</el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="我买到的" name="bought">
          <div v-if="!bought.length" class="empty">还没有买过东西</div>
          <div v-else class="order-list">
            <div v-for="order in bought" :key="order.id" class="order-row">
              <img class="row-cover" :src="order.itemCover" alt="" />
              <div class="row-body">
                <p class="row-title">{{ order.itemTitle }}</p>
                <p class="row-meta">¥{{ order.price }} · 卖家 {{ order.sellerNickname }}</p>
                <p class="row-meta">订单号 {{ order.orderNo }} · 下单 {{ formatOrderTime(order.createdAt) }}</p>
                <p class="row-status">{{ STATUS_TEXT[order.status] }}</p>
              </div>
              <div class="row-actions">
                <el-button
                  v-if="['pending', 'confirmed'].includes(order.status)"
                  size="small"
                  @click="confirmCancel(order)"
                >
                  取消订单
                </el-button>
                <el-button
                  v-if="order.status === 'confirmed'"
                  size="small"
                  type="primary"
                  @click="changeOrderStatus(order, 'completed')"
                >
                  确认收货
                </el-button>
                <el-button
                  v-if="order.status === 'completed' && !order.reviewed"
                  size="small"
                  type="success"
                  plain
                  @click="openReview(order)"
                >
                  评价
                </el-button>
                <span v-if="order.reviewed" class="reviewed">已评价</span>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="我卖出的" name="sold">
          <div v-if="!sold.length" class="empty">还没有卖出记录</div>
          <div v-else class="order-list">
            <div v-for="order in sold" :key="order.id" class="order-row">
              <img class="row-cover" :src="order.itemCover" alt="" />
              <div class="row-body">
                <p class="row-title">{{ order.itemTitle }}</p>
                <p class="row-meta">¥{{ order.price }} · 买家 {{ order.buyerNickname }}</p>
                <p class="row-meta">订单号 {{ order.orderNo }} · 下单 {{ formatOrderTime(order.createdAt) }}</p>
                <p class="row-status">{{ STATUS_TEXT[order.status] }}</p>
              </div>
              <div class="row-actions">
                <el-button
                  v-if="order.status === 'pending'"
                  size="small"
                  type="primary"
                  @click="changeOrderStatus(order, 'confirmed')"
                >
                  确认订单
                </el-button>
                <el-button
                  v-if="order.status === 'pending'"
                  size="small"
                  @click="confirmReject(order)"
                >
                  拒绝订单
                </el-button>
                <el-button size="small" @click="goDetail({ id: order.itemId })">查看商品</el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane name="notifications">
          <template #label>
            消息通知
            <span v-if="notifyUnread" class="notify-badge">{{ notifyUnread }}</span>
          </template>
          <div class="notify-head">
            <span class="notify-summary">
              {{ notifyUnread ? `有 ${notifyUnread} 条未读通知` : '没有未读通知' }}
            </span>
            <el-button v-if="notifyUnread" size="small" @click="markAllRead">全部已读</el-button>
          </div>
          <div v-if="!notifications.length" class="empty">暂无通知</div>
          <div v-else class="notify-list">
            <div
              v-for="row in notifications"
              :key="row.id"
              class="notify-item"
              :class="{ unread: !row.isRead }"
            >
              <div class="notify-top">
                <span class="notify-title">{{ row.title }}</span>
                <span class="notify-time">{{ row.createdAt }}</span>
              </div>
              <p class="notify-content">{{ row.content }}</p>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="我的收藏" name="favorites">
          <div v-if="!favorites.length" class="empty">还没有收藏商品</div>
          <div v-else class="card-grid">
            <ItemCard v-for="row in favorites" :key="row.id" :item="row" @select="goDetail" />
          </div>
        </el-tab-pane>
      </el-tabs>

      <el-dialog v-model="reviewVisible" title="评价这笔交易" width="420px">
        <p class="dialog-tip">
          评价会展示在卖家主页，星级还会按比例计入卖家信用分（5 星最高 100 分）。
        </p>
        <el-rate v-model="reviewRating" show-score score-template="{value} 星" />
        <el-input
          v-model="reviewContent"
          type="textarea"
          :rows="3"
          maxlength="200"
          show-word-limit
          placeholder="说说交易体验（选填）"
          style="margin-top: 12px"
        />
        <template #footer>
          <el-button @click="reviewVisible = false">取消</el-button>
          <el-button type="primary" :loading="reviewSubmitting" @click="submitReview">提交评价</el-button>
        </template>
      </el-dialog>
    </main>
  </div>
</template>

<style scoped>
.mine-page {
  min-height: 100vh;
  background: #f6f8f7;
}

.mine-main {
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px 24px 64px;
  min-height: 400px;
}

.mine-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 8px;
}

.mine-head h1 {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 600;
}

.sub {
  margin: 0;
  font-size: 13px;
  color: #9ca3af;
}

.head-actions {
  display: flex;
  gap: 12px;
}

.item-list,
.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-row,
.order-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(15, 60, 40, 0.04);
}

.row-cover {
  width: 84px;
  height: 64px;
  flex: 0 0 auto;
  border-radius: 8px;
  object-fit: cover;
  background: #f1f4f2;
  cursor: pointer;
}

.row-body {
  flex: 1;
  min-width: 0;
}

.row-title {
  margin: 0 0 6px;
  overflow: hidden;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  text-overflow: ellipsis;
  cursor: pointer;
}

.row-meta {
  margin: 0 0 6px;
  font-size: 12px;
  color: #9ca3af;
}

.row-status {
  display: inline-block;
  margin: 0;
  padding: 2px 10px;
  border-radius: 999px;
  background: #eefaf1;
  font-size: 12px;
  color: #15803d;
}

.row-status.off_shelf {
  background: #f3f4f6;
  color: #6b7280;
}

.row-status.sold {
  background: #fdf1ef;
  color: #b91c1c;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  max-width: 300px;
}

.row-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.reviewed {
  font-size: 12px;
  color: #9ca3af;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.empty {
  padding: 48px 0;
  font-size: 13px;
  color: #9ca3af;
  text-align: center;
}

.dialog-tip {
  margin: 0 0 12px;
  font-size: 12px;
  color: #9ca3af;
}

.notify-badge {
  display: inline-block;
  min-width: 16px;
  margin-left: 4px;
  padding: 0 5px;
  border-radius: 999px;
  background: #ef4444;
  font-size: 11px;
  line-height: 16px;
  color: #ffffff;
  text-align: center;
}

.notify-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.notify-summary {
  font-size: 12px;
  color: #9ca3af;
}

.notify-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notify-item {
  padding: 14px 18px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(15, 60, 40, 0.04);
}

.notify-item.unread {
  border-left: 3px solid #16a34a;
}

.notify-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}

.notify-title {
  font-size: 14px;
  font-weight: 500;
}

.notify-time {
  flex: 0 0 auto;
  font-size: 12px;
  color: #9ca3af;
}

.notify-content {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #4b5563;
}

@media (max-width: 780px) {
  .mine-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .item-row,
  .order-row {
    flex-wrap: wrap;
  }

  .row-actions {
    justify-content: flex-start;
  }
}
</style>
