<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import ItemCard from '@/components/ItemCard.vue'
import { getSellerProfile } from '@/api/social'

const route = useRoute()
const router = useRouter()

const profile = ref(null)
const loading = ref(true)

const initial = computed(() => (profile.value?.nickname || '卖').slice(0, 1))

async function load() {
  loading.value = true
  try {
    profile.value = await getSellerProfile(route.params.id)
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '卖家信息加载失败')
  } finally {
    loading.value = false
  }
}

function goDetail(row) {
  router.push({ name: 'item-detail', params: { id: row.id } })
}

function goBack() {
  router.back()
}

function formatDate(value) {
  return value ? String(value).slice(0, 10).replace(/-/g, '/') : ''
}

onMounted(load)
</script>

<template>
  <div class="seller-page">
    <AppHeader />

    <main class="seller-main" v-loading="loading">
      <button class="back-btn" type="button" @click="goBack">← 返回</button>

      <section v-if="profile" class="profile-card">
        <div class="profile-avatar">
          <span>{{ initial }}</span>
        </div>
        <div class="profile-info">
          <h1>{{ profile.nickname }}</h1>
          <p class="meta">
            {{ profile.campus || '校区未填写' }} · 信用分 {{ profile.credit }} ·
            <el-rate
              :model-value="profile.rating"
              disabled
              allow-half
              size="small"
              class="rate"
            />
            {{ profile.rating }} 分（{{ profile.reviewCount }} 条评价）
          </p>
        </div>
        <div class="profile-stats">
          <div class="stat">
            <span class="num">{{ profile.onSaleCount }}</span>
            <span class="label">在售</span>
          </div>
          <div class="stat">
            <span class="num">{{ profile.soldCount }}</span>
            <span class="label">已售</span>
          </div>
        </div>
      </section>

      <section v-if="profile" class="section">
        <h2>在售商品（{{ profile.items.length }}）</h2>
        <div v-if="!profile.items.length" class="empty">暂无在售商品</div>
        <div v-else class="card-grid">
          <ItemCard v-for="row in profile.items" :key="row.id" :item="row" @select="goDetail" />
        </div>
      </section>

      <section v-if="profile" class="section">
        <h2>交易评价（{{ profile.reviews.length }}）</h2>
        <div v-if="!profile.reviews.length" class="empty">还没有收到评价</div>
        <div v-else class="review-list">
          <div v-for="row in profile.reviews" :key="row.id" class="review-item">
            <div class="review-head">
              <span class="review-user">{{ row.buyerNickname }}</span>
              <el-rate :model-value="row.rating" disabled size="small" />
              <span class="review-date">{{ formatDate(row.createdAt) }}</span>
            </div>
            <p class="review-content">{{ row.content || '买家没有填写文字评价' }}</p>
            <p class="review-item-title">商品：{{ row.itemTitle }}</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.seller-page {
  min-height: 100vh;
  background: #f6f8f7;
}

.seller-main {
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
}

.back-btn:hover {
  color: #15803d;
  border-color: #16a34a;
  background: #f6fcf8;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 28px 32px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 18px 50px rgba(15, 60, 40, 0.06);
}

.profile-avatar {
  width: 72px;
  height: 72px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: #dcf2e5;
  font-size: 26px;
  font-weight: 600;
  color: #0e5c3a;
}

.profile-info {
  flex: 1;
  min-width: 0;
}

.profile-info h1 {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 600;
}

.meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

.rate {
  margin: 0 4px;
}

.profile-stats {
  display: flex;
  gap: 28px;
  text-align: center;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.num {
  font-size: 20px;
  font-weight: 600;
  color: #15803d;
}

.label {
  font-size: 12px;
  color: #9ca3af;
}

.section {
  margin-top: 24px;
  padding: 24px 28px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 18px 50px rgba(15, 60, 40, 0.04);
}

.section h2 {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.review-item {
  padding: 14px 16px;
  border-radius: 12px;
  background: #fafcfb;
}

.review-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.review-user {
  font-size: 13px;
  font-weight: 500;
}

.review-date {
  margin-left: auto;
  font-size: 12px;
  color: #b0b8b4;
}

.review-content {
  margin: 0 0 6px;
  font-size: 13px;
  line-height: 1.8;
  color: #4b5563;
}

.review-item-title {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}

.empty {
  padding: 32px 0;
  font-size: 13px;
  color: #9ca3af;
  text-align: center;
}

@media (max-width: 780px) {
  .profile-card {
    flex-wrap: wrap;
  }
}
</style>
