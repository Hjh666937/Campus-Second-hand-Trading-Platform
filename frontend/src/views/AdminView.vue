<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import { getReports, getStats, getUsers, handleReport, resetUserPassword, setUserStatus } from '@/api/admin'
import { getItems, updateItemStatus } from '@/api/items'

const router = useRouter()

const activeTab = ref('overview')
const stats = ref(null)
const items = ref([])
const reports = ref([])
const users = ref([])
const loading = ref(false)

const STATUS_TEXT = {
  on_sale: '在售',
  off_shelf: '已下架',
  sold: '已售出'
}

const REPORT_STATUS = {
  pending: '待处理',
  handled: '已处理',
  rejected: '已忽略'
}

async function loadAll() {
  loading.value = true
  try {
    const [statsData, itemData, reportData, userData] = await Promise.all([
      getStats(),
      getItems({ status: 'all', size: 200, page: 1, sort: 'latest' }),
      getReports(),
      getUsers()
    ])
    stats.value = statsData
    items.value = itemData.list
    reports.value = reportData
    users.value = userData
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function toggleItemStatus(row) {
  const next = row.status === 'off_shelf' ? 'on_sale' : 'off_shelf'
  try {
    await updateItemStatus(row.id, next)
    ElMessage.success(next === 'off_shelf' ? '已下架' : '已恢复上架')
    await loadAll()
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '操作失败')
  }
}

async function resolveReport(row, status) {
  try {
    await handleReport(row.id, status)
    ElMessage.success('已处理')
    await loadAll()
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '操作失败')
  }
}

async function toggleUser(row) {
  if (row.role === 'admin') {
    ElMessage.warning('管理员账号不能封禁')
    return
  }

  const next = row.status === 'banned' ? 'active' : 'banned'
  if (next === 'banned') {
    try {
      await ElMessageBox.confirm(`确定封禁「${row.nickname}」吗？`, '封禁用户', {
        confirmButtonText: '封禁',
        cancelButtonText: '取消',
        type: 'warning'
      })
    } catch (error) {
      return
    }
  }

  try {
    await setUserStatus(row.account, next)
    ElMessage.success(next === 'banned' ? '已封禁' : '已解封')
    await loadAll()
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '操作失败')
  }
}

async function resetPassword(row) {
  try {
    await ElMessageBox.confirm(
      `确定把「${row.nickname}」的登录密码重置为初始密码吗？重置后对方需用新密码登录。`,
      '重置密码',
      { confirmButtonText: '确定重置', cancelButtonText: '取消', type: 'warning' }
    )
  } catch (error) {
    return
  }

  try {
    await resetUserPassword(row.account)
    ElMessage.success('已重置为初始密码：账号后 6 位（不足 6 位为 123456）')
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '重置失败')
  }
}

onMounted(loadAll)
</script>

<template>
  <div class="admin-page">
    <AppHeader />

    <main class="admin-main" v-loading="loading">
      <div class="admin-head">
        <div>
          <h1>管理后台</h1>
          <p class="sub">商品、举报、用户与平台数据</p>
        </div>
        <el-button @click="router.push('/')">返回首页</el-button>
      </div>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="数据概况" name="overview">
          <div v-if="stats" class="stat-grid">
            <div class="stat-card">
              <span class="num">{{ stats.userCount }}</span>
              <span class="label">注册用户</span>
            </div>
            <div class="stat-card">
              <span class="num">{{ stats.bannedCount }}</span>
              <span class="label">封禁账号</span>
            </div>
            <div class="stat-card">
              <span class="num">{{ stats.publishedCount }}</span>
              <span class="label">用户发布商品</span>
            </div>
            <div class="stat-card">
              <span class="num">{{ stats.orderCount }}</span>
              <span class="label">订单总数</span>
            </div>
            <div class="stat-card">
              <span class="num">{{ stats.completedCount }}</span>
              <span class="label">已完成订单</span>
            </div>
            <div class="stat-card">
              <span class="num">¥{{ stats.turnover }}</span>
              <span class="label">成交总额</span>
            </div>
            <div class="stat-card">
              <span class="num">{{ stats.pendingReports }}</span>
              <span class="label">待处理举报</span>
            </div>
          </div>
          <p class="tip">说明：数据来自数据库，封禁、重置密码和举报处理会立即对真实账号生效。</p>
        </el-tab-pane>

        <el-tab-pane label="商品管理" name="items">
          <el-table :data="items" size="small" style="width: 100%">
            <el-table-column prop="title" label="商品" min-width="200" show-overflow-tooltip />
            <el-table-column label="价格" width="90">
              <template #default="{ row }">¥{{ row.price }}</template>
            </el-table-column>
            <el-table-column prop="sellerNickname" label="卖家" width="110" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">{{ STATUS_TEXT[row.status] || '在售' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.status !== 'sold'"
                  size="small"
                  :type="row.status === 'off_shelf' ? 'primary' : 'danger'"
                  plain
                  @click="toggleItemStatus(row)"
                >
                  {{ row.status === 'off_shelf' ? '恢复' : '下架' }}
                </el-button>
                <span v-else class="muted">已售出</span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="举报处理" name="reports">
          <div v-if="!reports.length" class="empty">暂无举报</div>
          <el-table v-else :data="reports" size="small" style="width: 100%">
            <el-table-column prop="itemTitle" label="被举报商品" min-width="180" show-overflow-tooltip />
            <el-table-column prop="reason" label="原因" width="110" />
            <el-table-column prop="detail" label="补充说明" min-width="160" show-overflow-tooltip />
            <el-table-column prop="account" label="举报人" width="110" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">{{ REPORT_STATUS[row.status] }}</template>
            </el-table-column>
            <el-table-column label="操作" width="170" fixed="right">
              <template #default="{ row }">
                <template v-if="row.status === 'pending'">
                  <el-button size="small" type="danger" plain @click="resolveReport(row, 'handled')">
                    已处理
                  </el-button>
                  <el-button size="small" @click="resolveReport(row, 'rejected')">忽略</el-button>
                </template>
                <span v-else class="muted">—</span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="用户管理" name="users">
          <el-table :data="users" size="small" style="width: 100%">
            <el-table-column prop="account" label="账号" width="130" />
            <el-table-column prop="nickname" label="昵称" width="140" />
            <el-table-column prop="campus" label="校区" width="120" />
            <el-table-column label="身份" width="90">
              <template #default="{ row }">{{ row.role === 'admin' ? '管理员' : '学生' }}</template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <span :class="['pill', row.status]">{{ row.status === 'banned' ? '已封禁' : '正常' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="210" fixed="right">
              <template #default="{ row }">
                <template v-if="row.role !== 'admin'">
                  <el-button
                    size="small"
                    :type="row.status === 'banned' ? 'primary' : 'danger'"
                    plain
                    @click="toggleUser(row)"
                  >
                    {{ row.status === 'banned' ? '解封' : '封禁' }}
                  </el-button>
                  <el-button size="small" @click="resetPassword(row)">重置密码</el-button>
                </template>
                <span v-else class="muted">—</span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </main>
  </div>
</template>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f6f8f7;
}

.admin-main {
  max-width: 1120px;
  margin: 0 auto;
  padding: 24px 24px 64px;
  min-height: 400px;
}

.admin-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 12px;
}

.admin-head h1 {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 600;
}

.sub {
  margin: 0;
  font-size: 13px;
  color: #9ca3af;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 12px 34px rgba(15, 60, 40, 0.05);
}

.num {
  font-size: 24px;
  font-weight: 600;
  color: #0e5c3a;
}

.label {
  font-size: 12px;
  color: #9ca3af;
}

.tip {
  margin-top: 18px;
  font-size: 12px;
  color: #9ca3af;
}

.pill {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  background: #eefaf1;
  font-size: 12px;
  color: #15803d;
}

.pill.banned {
  background: #fdf1ef;
  color: #b91c1c;
}

.muted {
  font-size: 12px;
  color: #9ca3af;
}

.empty {
  padding: 40px 0;
  font-size: 13px;
  color: #9ca3af;
  text-align: center;
}
</style>
