<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import ItemCard from '@/components/ItemCard.vue'
import { getItem, getItems, recordItemView } from '@/api/items'
import { createOrder } from '@/api/orders'
import { createReport, isFavorite, toggleFavorite } from '@/api/social'
import { openConversation } from '@/api/chat'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const item = ref(null)
const loading = ref(true)
const activeImage = ref(0)
const favorite = ref(false)
const similar = ref([])

const buyVisible = ref(false)
const buying = ref(false)

const reportVisible = ref(false)
const reportSubmitting = ref(false)
const reportReason = ref('虚假信息')
const reportDetail = ref('')
const REPORT_REASONS = ['虚假信息', '违禁物品', '价格欺诈', '盗图/侵权', '其他']

const account = computed(() => userStore.userInfo?.account || '')
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')
const isOwner = computed(() => !!item.value && item.value.sellerNickname === userStore.nickname)
const images = computed(() => item.value?.images?.length ? item.value.images : [item.value?.cover])
const statusText = computed(() => {
  if (!item.value) return ''
  if (item.value.status === 'sold') return '已售出'
  if (item.value.status === 'off_shelf') return '已下架'
  return '在售'
})
const publishDate = computed(() =>
  item.value?.createdAt ? String(item.value.createdAt).slice(0, 10).replace(/-/g, '/') : '—'
)
const sellerInitial = computed(() => (item.value?.seller?.nickname || '卖').slice(0, 1))
const activeOrders = computed(() => item.value?.activeOrderCount || 0)

async function load() {
  loading.value = true
  try {
    item.value = await getItem(route.params.id)

    const view = await recordItemView(route.params.id)
    if (view && Number.isFinite(view.viewCount)) {
      item.value = { ...item.value, viewCount: view.viewCount }
    }

    favorite.value = await isFavorite({ account: account.value, itemId: route.params.id })

    const data = await getItems({
      categoryId: item.value.categoryId,
      size: 4,
      page: 1,
      status: 'all'
    })
    similar.value = data.list.filter((row) => row.id !== item.value.id).slice(0, 3)
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '商品加载失败')
    }
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/')
}

function goSoldOrders() {
  router.push({ name: 'mine', query: { tab: 'sold' } })
}

function goSeller() {
  router.push({ name: 'seller', params: { id: item.value.sellerId } })
}

async function handleFavorite() {
  try {
    const result = await toggleFavorite({ account: account.value, itemId: item.value.id })
    favorite.value = result.favorite
    ElMessage.success(result.favorite ? '已加入收藏' : '已取消收藏')
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '操作失败')
  }
}

async function handleContact() {
  try {
    const conversation = await openConversation({
      itemId: item.value.id,
      itemTitle: item.value.title,
      itemCover: item.value.cover,
      sellerNickname: item.value.sellerNickname,
      buyerAccount: account.value,
      buyerNickname: userStore.nickname
    })
    router.push({ name: 'chat', params: { id: conversation.id } })
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '暂时无法发起会话')
    }
  }
}

async function handleBuy() {
  buying.value = true
  try {
    await createOrder({
      itemId: item.value.id,
      itemTitle: item.value.title,
      itemCover: item.value.cover,
      price: item.value.price,
      buyerAccount: account.value,
      buyerNickname: userStore.nickname,
      sellerNickname: item.value.sellerNickname
    })
    buyVisible.value = false
    ElMessage.success('下单成功，等待卖家确认')
    router.push({ name: 'mine', query: { tab: 'bought' } })
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '下单失败')
    }
  } finally {
    buying.value = false
  }
}

async function handleReport() {
  if (!reportReason.value) {
    ElMessage.warning('请选择举报原因')
    return
  }

  reportSubmitting.value = true
  try {
    await createReport({
      itemId: item.value.id,
      itemTitle: item.value.title,
      account: account.value,
      reason: reportReason.value,
      detail: reportDetail.value.trim()
    })
    reportVisible.value = false
    reportDetail.value = ''
    ElMessage.success('举报已提交，管理员会尽快处理')
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '举报失败')
    }
  } finally {
    reportSubmitting.value = false
  }
}

function openReport() {
  reportReason.value = '虚假信息'
  reportDetail.value = ''
  reportVisible.value = true
}

function handleEdit() {
  router.push({ name: 'publish', query: { id: item.value.id } })
}

function goDetail(row) {
  router.push({ name: 'item-detail', params: { id: row.id } })
}

async function confirmOffShelf() {
  try {
    await ElMessageBox.confirm('下架后其他同学将看不到这件商品，确定吗？', '下架商品', {
      confirmButtonText: '确定下架',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch (error) {
    return
  }
  router.push({ name: 'mine', query: { tab: 'published' } })
}

onMounted(load)
</script>

<template>
  <div class="detail-page">
    <AppHeader />

    <main class="detail-main" v-loading="loading">
      <button class="back-btn" type="button" @click="goBack">← 返回列表</button>

      <div v-if="item" class="detail-card">
        <div class="gallery">
          <div class="main-image">
            <img :src="images[activeImage]" :alt="item.title" />
            <span class="status-tag" :class="{ sold: item.status !== 'on_sale' }">{{ statusText }}</span>
          </div>
          <div v-if="images.length > 1" class="thumbs">
            <button
              v-for="(img, index) in images"
              :key="index"
              class="thumb"
              :class="{ active: index === activeImage }"
              type="button"
              @click="activeImage = index"
            >
              <img :src="img" alt="" />
            </button>
          </div>
        </div>

        <div class="info">
          <h1 class="title">{{ item.title }}</h1>

          <p class="price"><span class="symbol">¥</span>{{ item.price }}</p>

          <ul class="tags">
            <li class="tag tag-condition">商家说：{{ item.condition }}</li>
            <li class="tag">{{ item.campus }}</li>
            <li class="tag">发布于 {{ publishDate }}</li>
          </ul>

          <p class="view-count">{{ item.viewCount }} 人看过</p>

          <button class="seller" type="button" @click="goSeller">
            <span class="seller-avatar">
              <img v-if="item.seller?.avatar" :src="item.seller.avatar" alt="卖家头像" />
              <span v-else>{{ sellerInitial }}</span>
            </span>
            <span class="seller-msg">
              <span class="seller-name">{{ item.seller?.nickname || item.sellerNickname }}</span>
              <span class="seller-meta">
                {{ item.seller?.campus || item.campus }} · 信用分 {{ item.seller?.credit ?? '—' }} · 查看主页
              </span>
            </span>
          </button>

          <div v-if="isOwner && activeOrders" class="pending-orders">
            <span>该商品有 {{ activeOrders }} 笔进行中的订单，请及时处理</span>
            <el-button size="small" type="primary" plain @click="goSoldOrders">去处理</el-button>
          </div>

          <div class="actions">
            <el-button
              v-if="!isAdmin"
              size="large"
              :type="favorite ? 'danger' : 'default'"
              plain
              @click="handleFavorite"
            >
              {{ favorite ? '已收藏' : '收藏' }}
            </el-button>
            <el-button v-if="!isAdmin" size="large" @click="openReport">举报</el-button>

            <template v-if="isOwner">
              <el-button size="large" type="primary" @click="handleEdit">编辑商品</el-button>
              <el-button size="large" @click="confirmOffShelf">管理商品</el-button>
            </template>
            <template v-else>
              <el-button
                v-if="!isAdmin"
                size="large"
                :disabled="item.status !== 'on_sale'"
                @click="handleContact"
              >
                联系卖家
              </el-button>
              <el-button
                v-if="!isAdmin"
                type="primary"
                size="large"
                :disabled="item.status !== 'on_sale'"
                @click="buyVisible = true"
              >
                立即购买
              </el-button>
            </template>
          </div>
        </div>
      </div>

      <section v-if="item" class="desc-card">
        <h2>商品描述</h2>
        <p class="desc">{{ item.description }}</p>
      </section>

      <section v-if="similar.length" class="similar-card">
        <h2>相似商品</h2>
        <div class="similar-grid">
          <ItemCard v-for="row in similar" :key="row.id" :item="row" @select="goDetail" />
        </div>
      </section>

      <el-dialog v-model="buyVisible" title="确认下单" width="420px">
        <div class="buy-summary">
          <img :src="item?.cover" alt="" />
          <div>
            <p class="buy-title">{{ item?.title }}</p>
            <p class="buy-price">¥{{ item?.price }}</p>
            <p class="buy-tip">下单后请与卖家约在 {{ item?.campus }} 当面交易</p>
          </div>
        </div>
        <template #footer>
          <el-button @click="buyVisible = false">取消</el-button>
          <el-button type="primary" :loading="buying" @click="handleBuy">确认下单</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="reportVisible" title="举报商品" width="420px">
        <p class="report-tip">举报后管理员会核实，恶意举报可能影响你的账号。</p>
        <el-select v-model="reportReason" placeholder="选择举报原因" style="width: 100%">
          <el-option v-for="reason in REPORT_REASONS" :key="reason" :label="reason" :value="reason" />
        </el-select>
        <el-input
          v-model="reportDetail"
          type="textarea"
          :rows="3"
          maxlength="200"
          show-word-limit
          placeholder="补充说明（选填）"
          style="margin-top: 12px"
        />
        <template #footer>
          <el-button @click="reportVisible = false">取消</el-button>
          <el-button type="danger" :loading="reportSubmitting" @click="handleReport">提交举报</el-button>
        </template>
      </el-dialog>
    </main>
  </div>
</template>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #f6f8f7;
}

.detail-main {
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px 24px 64px;
  min-height: 400px;
}

.back-btn {
  margin-bottom: 16px;
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

.detail-card {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
  gap: 40px;
  padding: 32px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 18px 50px rgba(15, 60, 40, 0.06);
}

.main-image {
  position: relative;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  border-radius: 12px;
  background: #f1f4f2;
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.status-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 3px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.94);
  font-size: 12px;
  color: #15803d;
}

.status-tag.sold {
  color: #b91c1c;
}

.thumbs {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.thumb {
  width: 64px;
  height: 64px;
  padding: 0;
  overflow: hidden;
  border: 2px solid transparent;
  border-radius: 8px;
  background: #f1f4f2;
  cursor: pointer;
}

.thumb.active {
  border-color: #16a34a;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.title {
  margin: 0 0 16px;
  font-size: 22px;
  font-weight: 600;
  line-height: 1.5;
}

.price {
  margin: 0 0 20px;
  font-size: 32px;
  font-weight: 600;
  color: #e0523f;
}

.symbol {
  margin-right: 4px;
  font-size: 18px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 14px;
  padding: 0;
  list-style: none;
}

.tag {
  padding: 4px 12px;
  border-radius: 8px;
  background: #f2f6f4;
  font-size: 12px;
  color: #6b7280;
}

.tag-condition {
  background: #eefaf1;
  color: #15803d;
}

.view-count {
  margin: 0 0 24px;
  font-size: 12px;
  color: #9ca3af;
}

.seller {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 14px 16px;
  margin-bottom: 24px;
  border: none;
  border-radius: 12px;
  background: #f8faf9;
  text-align: left;
  cursor: pointer;
}

.seller:hover {
  background: #f1f6f3;
}

.seller-avatar {
  width: 44px;
  height: 44px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 50%;
  background: #dcf2e5;
  font-size: 16px;
  font-weight: 600;
  color: #0e5c3a;
}

.seller-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.seller-msg {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.seller-name {
  font-size: 14px;
  font-weight: 500;
}

.seller-meta {
  font-size: 12px;
  color: #9ca3af;
}

.pending-orders {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 16px;
  padding: 10px 14px;
  border-radius: 10px;
  background: #fff8e6;
  font-size: 13px;
  color: #b45309;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: auto;
}

.actions :deep(.el-button) {
  flex: 1;
  min-width: 100px;
}

.desc-card,
.similar-card {
  margin-top: 24px;
  padding: 28px 32px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 18px 50px rgba(15, 60, 40, 0.04);
}

.desc-card h2,
.similar-card h2 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
}

.desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.9;
  color: #4b5563;
}

.similar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.buy-summary {
  display: flex;
  gap: 14px;
}

.buy-summary img {
  width: 88px;
  height: 66px;
  border-radius: 8px;
  object-fit: cover;
}

.buy-title {
  margin: 0 0 6px;
  font-size: 14px;
  font-weight: 500;
}

.buy-price {
  margin: 0 0 6px;
  font-size: 18px;
  font-weight: 600;
  color: #e0523f;
}

.buy-tip,
.report-tip {
  margin: 0;
  font-size: 12px;
  line-height: 1.7;
  color: #9ca3af;
}

.report-tip {
  margin-bottom: 12px;
}

@media (max-width: 900px) {
  .detail-card {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 20px;
  }
}
</style>
