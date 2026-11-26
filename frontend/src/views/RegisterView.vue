<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AuthLayout from '@/components/AuthLayout.vue'
import { register } from '@/api/auth'

const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  account: '',
  nickname: '',
  campus: '',
  gender: 'secret',
  password: '',
  confirmPassword: ''
})

function validateConfirm(rule, value, callback) {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  account: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    {
      pattern: /^[A-Za-z0-9_]{4,20}$/,
      message: '学号为 4-20 位字母、数字或下划线',
      trigger: 'blur'
    }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 12, message: '昵称长度为 2-12 个字符', trigger: 'blur' }
  ],
  campus: [
    { required: true, message: '请输入校区', trigger: 'blur' },
    { min: 2, max: 20, message: '校区名称为 2-20 个字符', trigger: 'blur' }
  ],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为 6-20 位', trigger: 'blur' }
  ],
  confirmPassword: [{ validator: validateConfirm, trigger: 'blur' }]
}

async function handleSubmit() {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await register({
      account: form.account.trim(),
      nickname: form.nickname.trim(),
      campus: form.campus.trim(),
      gender: form.gender,
      password: form.password
    })
    ElMessage.success('注册成功，请登录')
    router.replace({ name: 'login', query: { account: form.account.trim() } })
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '注册失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout title="注册账号" subtitle="使用学号注册，注册后即可发布和购买闲置物品。">
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
          placeholder="4-20 位字母、数字或下划线"
          autocomplete="username"
          clearable
        />
      </el-form-item>

      <el-form-item label="昵称" prop="nickname">
        <el-input
          v-model="form.nickname"
          placeholder="展示给其他同学的名字"
          maxlength="12"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="校区" prop="campus">
        <el-input
          v-model="form.campus"
          placeholder="如：东校区、南湖校区"
          maxlength="20"
          clearable
        />
      </el-form-item>

      <el-form-item label="性别" prop="gender">
        <el-radio-group v-model="form.gender">
          <el-radio value="male">男</el-radio>
          <el-radio value="female">女</el-radio>
          <el-radio value="secret">暂时不想透露</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="6-20 位，建议字母与数字组合"
          autocomplete="new-password"
          show-password
        />
      </el-form-item>

      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          placeholder="请再次输入密码"
          autocomplete="new-password"
          show-password
          @keyup.enter="handleSubmit"
        />
      </el-form-item>

      <el-button
        class="submit-btn"
        type="primary"
        size="large"
        :loading="loading"
        @click="handleSubmit"
      >
        {{ loading ? '提交中…' : '注 册' }}
      </el-button>
    </el-form>

    <p class="auth-switch">
      已有账号？<router-link class="link" :to="{ name: 'login' }">返回登录</router-link>
    </p>

    <p class="auth-tip">注册仅面向在校学生，管理员账号由平台统一开通。</p>
  </AuthLayout>
</template>

<style scoped>
.submit-btn {
  width: 100%;
  letter-spacing: 2px;
}
</style>
