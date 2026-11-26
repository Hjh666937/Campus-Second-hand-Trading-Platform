<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import ItemCard from '@/components/ItemCard.vue'
import { getCategories, getItems } from '@/api/items'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const categories = ref([{ id: 0, name: '全部' }])

const PAGE_SIZE = 12

const keyword = ref('')
const activeCategory = ref(0)
const page = ref(1)
const total = ref(0)
const list = ref([])
const loading = ref(false)

const sort = ref('latest')
const minPrice = ref('')
const maxPrice = ref('')
const campusOnly = ref(false)

async function fetchList() {
  loading.value = true
  try {
    const data = await getItems({
      keyword: keyword.value,
      categoryId: activeCategory.value,
      page: page.value,
      size: PAGE_SIZE,
      sort: sort.value,
      minPrice: minPrice.value === '' ? null : Number(minPrice.value),
      maxPrice: maxPrice.value === '' ? null : Number(maxPrice.value),
      campus: campusOnly.value ? userStore.userInfo?.campus || '' : ''
    })
    list.value = data.list
    total.value = data.total
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '加载失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  page.value = 1
  fetchList()
}

function handleSearch() {
  page.value = 1
  fetchList()
}

function handleCategory(id) {
  if (activeCategory.value === id) return
  activeCategory.value = id
  page.value = 1
  fetchList()
}

function handlePageChange(current) {
  page.value = current
  fetchList()
}

function handleSelect(item) {
  router.push({ name: 'item-detail', params: { id: item.id } })
}

function goPublish() {
  router.push({ name: 'publish' })
}

async function loadCategories() {
  try {
    const list = await getCategories()
    categories.value = [{ id: 0, name: '全部' }, ...list]
  } catch (error) {
    // 分类加载失败时保留「全部」，不阻塞商品列表
  }
}

onMounted(async () => {
  await loadCategories()
  fetchList()
})
</script>

<template>
  <div class="home">
    <AppHeader />

    <main class="home-main">
      <section class="toolbar">
        <div aria-hidden="true"></div>
        <el-input
          v-model="keyword"
          class="search"
          size="large"
          placeholder="搜索教材、数码、生活用品…"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        >
          <template #append>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
        <div v-if="userStore.userInfo?.role !== 'admin'" class="toolbar-actions">
          <el-button type="primary" size="large" class="publish-btn" @click="goPublish">
            ＋ 我要出闲置
          </el-button>
        </div>
      </section>

      <nav class="category-bar">
        <button
          v-for="item in categories"
          :key="item.id"
          class="category-chip"
          :class="{ active: activeCategory === item.id }"
          type="button"
          @click="handleCategory(item.id)"
        >
          {{ item.name }}
        </button>
      </nav>

      <section class="filter-bar">
        <el-select v-model="sort" size="default" class="sort-select" @change="applyFilters">
          <el-option label="最新发布" value="latest" />
          <el-option label="价格从低到高" value="priceAsc" />
          <el-option label="价格从高到低" value="priceDesc" />
          <el-option label="最多人看" value="hot" />
        </el-select>

        <div class="price-range">
          <el-input v-model="minPrice" placeholder="最低价" class="price-input" clearable />
          <span class="dash">—</span>
          <el-input v-model="maxPrice" placeholder="最高价" class="price-input" clearable />
          <el-button @click="applyFilters">确定</el-button>
        </div>

        <el-checkbox v-model="campusOnly" @change="applyFilters">
          只看本校（{{ userStore.userInfo?.campus || '未填写' }}）
        </el-checkbox>

        <el-button link type="primary" @click="applyFilters">刷新</el-button>
      </section>

      <p class="result-info">共 {{ total }} 件在售商品</p>

      <div v-loading="loading" class="item-grid">
        <ItemCard
          v-for="item in list"
          :key="item.id"
          :item="item"
          @select="handleSelect"
        />

        <el-empty
          v-if="!loading && list.length === 0"
          class="empty"
          description="没有找到相关商品，换个关键词试试"
        />
      </div>

      <div v-if="total > PAGE_SIZE" class="pager">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="PAGE_SIZE"
          :current-page="page"
          @current-change="handlePageChange"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  background: #f6f8f7;
}

.home-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

.toolbar {
  display: grid;
  grid-template-columns: 1fr minmax(0, 560px) 1fr;
  align-items: center;
  gap: 16px;
}

.search {
  width: 100%;
}

.toolbar-actions {
  display: flex;
  justify-content: flex-end;
}

.publish-btn {
  height: 44px;
  padding: 0 24px;
  font-size: 15px;
  border-radius: 10px;
}

.category-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 24px;
}

.category-chip {
  padding: 7px 16px;
  border: 1px solid #e3e9e6;
  border-radius: 999px;
  background: #ffffff;
  font-size: 13px;
  color: #4b5563;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}

.category-chip:hover {
  color: #15803d;
  border-color: #b9e5c8;
}

.category-chip.active {
  color: #ffffff;
  background: #16a34a;
  border-color: #16a34a;
}

.result-info {
  margin: 24px 0 16px;
  font-size: 13px;
  color: #9ca3af;
}

.item-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  min-height: 240px;
}

.empty {
  grid-column: 1 / -1;
  padding: 48px 0;
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  margin-top: 18px;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid #edf1ef;
  border-radius: 12px;
}

.sort-select {
  width: 150px;
}

.price-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-input {
  width: 100px;
}

.dash {
  color: #c3cbc7;
}

@media (max-width: 780px) {
  .toolbar {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .toolbar-actions {
    justify-content: stretch;
  }

  .publish-btn {
    width: 100%;
  }
}
</style>
