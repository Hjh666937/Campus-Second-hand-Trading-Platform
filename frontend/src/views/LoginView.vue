<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import AuthLayout from '@/components/AuthLayout.vue'
import { useUserStore } from '@/stores/user'
import { getNotifications } from '@/api/notifications'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const isMock = import.meta.env.VITE_USE_MOCK === 'true'

const form = reactive({
  // 注册成功后会带上学号，省去再次输入
  account: typeof route.query.account === 'string' ? route.query.account : '',
  password: '',
  remember: true
})

const rules = {
  account: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { min: 4, max: 20, message: '长度需在 4 到 20 个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为 6 到 20 位', trigger: 'blur' }
  ]
}

async function handleSubmit() {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login({
      account: form.account.trim(),
      password: form.password,
      remember: form.remember
    })
    ElMessage.success('登录成功')

    // 登录后拉一次通知，有未读的用 ElNotification 弹出来
    try {
      if (userStore.userInfo?.role !== 'admin') {
        const data = await getNotifications()
        const unreadList = (data.list || []).filter((row) => !row.isRead).slice(0, 3)
        // 先跳路由，延迟再弹通知（避免被首页加载动画盖住）
        router.replace(route.query.redirect || '/')
        if (unreadList.length > 0) {
          setTimeout(() => {
            unreadList.forEach((row, idx) => {
              ElNotification({
                title: row.title,
                message: row.content,
                type: idx === 0 ? 'success' : 'info',
                duration: 6000
              })
            })
          }, 800)
        }
        return
      }
    } catch {
      // 通知拉不出来不影响登录
    }
    router.replace(route.query.redirect || '/')
  } catch (error) {
    // 请求层已提示过的错误不再重复弹出
    if (!error?.displayed) {
      ElMessage.error(error?.message || '登录失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

function handleForgot() {
  ElMessage.info('请联系管理员或辅导员重置密码')
}
</script>

<template>
  <AuthLayout title="欢迎回来" subtitle="登录后即可发布商品、收藏和查看订单。">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      size="large"
      @submit.prevent
    >
      <el-form-item label="学号" prop="account">
        <el-input
          v-model="form.account"
          placeholder="请输入学号"
          autocomplete="username"
          clearable
        />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          autocomplete="current-password"
          show-password
          @keyup.enter="handleSubmit"
        />
      </el-form-item>

      <div class="form-options">
        <el-checkbox v-model="form.remember">记住我</el-checkbox>
        <span class="link" @click="handleForgot">忘记密码？</span>
      </div>

      <el-button
        class="submit-btn"
        type="primary"
        size="large"
        :loading="loading"
        @click="handleSubmit"
      >
        {{ loading ? '登录中…' : '登 录' }}
      </el-button>
    </el-form>

    <p class="auth-switch">
      还没有账号？<router-link class="link" :to="{ name: 'register' }">立即注册</router-link>
    </p>

    <p v-if="isMock" class="auth-tip">
      演示账号：学生 20261116 / 20261116 · 管理员 admin / admin123
    </p>
  </AuthLayout>
</template>

<style scoped>
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 4px 0 24px;
}

.submit-btn {
  width: 100%;
  letter-spacing: 2px;
}
</style>
