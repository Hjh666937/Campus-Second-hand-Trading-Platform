<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import { changePassword, updateProfile, uploadAvatar } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const fileInput = ref(null)
const user = computed(() => userStore.userInfo || {})
const avatar = computed(() => user.avatar || '')
const initial = computed(() => userStore.nickname.slice(0, 1))

const GENDER_LABELS = {
  male: '男',
  female: '女',
  secret: '暂时不想透露'
}
const ROLE_LABELS = {
  student: '学生',
  admin: '管理员'
}

const genderLabel = computed(() => GENDER_LABELS[user.value.gender] || '未填写')
const roleLabel = computed(() => ROLE_LABELS[user.value.role] || '学生')

function goHome() {
  router.push('/')
}

// 修改信息弹窗
const editVisible = ref(false)
const editFormRef = ref(null)
const editForm = reactive({
  nickname: '',
  campus: '',
  gender: 'secret'
})

const editRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 12, message: '昵称长度为 2-12 个字符', trigger: 'blur' }
  ],
  campus: [
    { required: true, message: '请输入校区', trigger: 'blur' },
    { min: 2, max: 20, message: '校区名称为 2-20 个字符', trigger: 'blur' }
  ],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }]
}

function openEdit() {
  editForm.nickname = user.value.nickname || ''
  editForm.campus = user.value.campus || ''
  editForm.gender = user.value.gender || 'secret'
  editVisible.value = true
  nextTick(() => editFormRef.value?.clearValidate())
}

async function handleSave() {
  const valid = await editFormRef.value?.validate().catch(() => false)
  if (!valid) return

  try {
    const updated = await updateProfile({
      nickname: editForm.nickname.trim(),
      campus: editForm.campus.trim(),
      gender: editForm.gender
    })
    userStore.updateProfile(updated)
    editVisible.value = false
    ElMessage.success('信息已更新')
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '保存失败，请稍后重试')
    }
  }
}

// 修改登录密码
const pwdVisible = ref(false)
const pwdFormRef = ref(null)
const pwdSaving = ref(false)
const pwdForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

function validateNewPassword(rule, value, callback) {
  if (!value) {
    callback(new Error('请输入新密码'))
  } else if (value === pwdForm.oldPassword) {
    callback(new Error('新密码不能与当前密码相同'))
  } else {
    callback()
  }
}

function validatePwdConfirm(rule, value, callback) {
  if (!value) {
    callback(new Error('请再次输入新密码'))
  } else if (value !== pwdForm.newPassword) {
    callback(new Error('两次输入的新密码不一致'))
  } else {
    callback()
  }
}

const pwdRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为 6-20 位', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为 6-20 位', trigger: 'blur' },
    { validator: validateNewPassword, trigger: 'blur' }
  ],
  confirmPassword: [{ validator: validatePwdConfirm, trigger: 'blur' }]
}

function openPassword() {
  pwdForm.oldPassword = ''
  pwdForm.newPassword = ''
  pwdForm.confirmPassword = ''
  pwdVisible.value = true
  nextTick(() => pwdFormRef.value?.clearValidate())
}

async function handleChangePassword() {
  const valid = await pwdFormRef.value?.validate().catch(() => false)
  if (!valid) return

  pwdSaving.value = true
  try {
    await changePassword({
      oldPassword: pwdForm.oldPassword,
      newPassword: pwdForm.newPassword
    })
    pwdVisible.value = false
    ElMessage.success('密码已修改，请记住新密码')
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '修改失败，请稍后重试')
    }
  } finally {
    pwdSaving.value = false
  }
}

function triggerUpload() {
  fileInput.value?.click()
}

async function handleFileChange(event) {
  const file = event.target.files?.[0]
  // 允许重复选择同一张图片
  event.target.value = ''
  if (!file) return

  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }

  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片不能超过 2MB')
    return
  }

  try {
    const { avatarUrl } = await uploadAvatar(file)
    userStore.updateProfile({ avatar: avatarUrl })
    ElMessage.success('头像已更新')
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '头像上传失败，请重试')
    }
  }
}

// 进入页面时同步数据库里的最新资料
onMounted(() => {
  userStore.refreshProfile().catch(() => {})
})
</script>

<template>
  <div class="profile-page">
    <AppHeader />

    <main class="profile-main">
      <div class="profile-body">
        <section class="profile-card">
          <div class="card-actions">
            <button class="action-btn action-primary" type="button" @click="openEdit">修改信息</button>
            <el-tooltip content="返回首页" placement="bottom">
              <button class="action-btn" type="button" @click="goHome">← 返回</button>
            </el-tooltip>
          </div>

        <div class="avatar-block">
          <div class="avatar-large">
            <img v-if="avatar" :src="avatar" alt="头像" />
            <span v-else>{{ initial }}</span>
          </div>
          <button class="upload-btn" type="button" @click="triggerUpload">更换头像</button>
          <p class="upload-hint">支持 JPG / PNG，不超过 1MB</p>
          <button class="pwd-btn" type="button" @click="openPassword">修改登录密码</button>
          <input
            ref="fileInput"
            class="file-input"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            @change="handleFileChange"
          />
        </div>

        <div class="info-block">
          <h1 class="profile-name">{{ user.nickname || '同学' }}</h1>

          <dl class="info-list">
            <div class="info-row">
              <dt>学号</dt>
              <dd>{{ user.account || '—' }}</dd>
            </div>
            <div class="info-row">
              <dt>昵称</dt>
              <dd>{{ user.nickname || '—' }}</dd>
            </div>
            <div class="info-row">
              <dt>校区</dt>
              <dd>{{ user.campus || '—' }}</dd>
            </div>
            <div class="info-row">
              <dt>性别</dt>
              <dd>{{ genderLabel }}</dd>
            </div>
            <div class="info-row">
              <dt>信用分</dt>
              <dd>{{ user.credit ?? '—' }}</dd>
            </div>
            <div class="info-row">
              <dt>身份</dt>
              <dd>{{ roleLabel }}</dd>
            </div>
          </dl>
        </div>
        </section>
      </div>
    </main>

    <el-dialog v-model="editVisible" title="修改信息" width="420px" append-to-body>
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-position="top">
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="editForm.nickname" maxlength="12" show-word-limit />
        </el-form-item>
        <el-form-item label="校区" prop="campus">
          <el-input v-model="editForm.campus" maxlength="20" placeholder="如：东校区、南湖校区" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="editForm.gender">
            <el-radio value="male">男</el-radio>
            <el-radio value="female">女</el-radio>
            <el-radio value="secret">暂时不想透露</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="pwdVisible" title="修改登录密码" width="420px" append-to-body>
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-position="top">
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input
            v-model="pwdForm.oldPassword"
            type="password"
            placeholder="请输入当前密码"
            autocomplete="current-password"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="pwdForm.newPassword"
            type="password"
            placeholder="6-20 位，建议字母与数字组合"
            autocomplete="new-password"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input
            v-model="pwdForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            autocomplete="new-password"
            show-password
            @keyup.enter="handleChangePassword"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="pwdVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwdSaving" @click="handleChangePassword">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f6f8f7;
}

.profile-main {
  display: flex;
  justify-content: center;
  padding: 32px 24px 48px;
}

.profile-body {
  width: 100%;
  max-width: 880px;
}

.card-actions {
  position: absolute;
  top: 24px;
  right: 24px;
  display: flex;
  gap: 8px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  border: 1px solid #e3e9e6;
  border-radius: 10px;
  background: #ffffff;
  font-size: 13px;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}

.action-btn:hover {
  color: #15803d;
  border-color: #16a34a;
  background: #f6fcf8;
}

.action-primary {
  color: #15803d;
  border-color: #b9e5c8;
  background: #f4fbf7;
}

.action-primary:hover {
  border-color: #16a34a;
  background: #eefaf1;
}

.profile-card {
  position: relative;
  width: 100%;
  max-width: 880px;
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 48px;
  padding: 48px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 18px 50px rgba(15, 60, 40, 0.06);
}

.avatar-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.avatar-large {
  width: 120px;
  height: 120px;
  display: grid;
  place-items: center;
  overflow: hidden;
  border: 2px solid #e3efe8;
  border-radius: 50%;
  background: #dcf2e5;
  font-size: 42px;
  font-weight: 600;
  color: #0e5c3a;
}

.avatar-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-btn {
  margin-top: 20px;
  padding: 8px 20px;
  border: 1px solid #16a34a;
  border-radius: 999px;
  background: #ffffff;
  font-size: 13px;
  color: #15803d;
  cursor: pointer;
}

.upload-btn:hover {
  background: #eefaf1;
}

.upload-hint {
  margin: 10px 0 0;
  font-size: 12px;
  color: #9ca3af;
}

.pwd-btn {
  margin-top: 18px;
  padding: 0;
  border: none;
  background: transparent;
  font-size: 13px;
  color: #15803d;
  cursor: pointer;
}

.pwd-btn:hover {
  text-decoration: underline;
}

.file-input {
  display: none;
}

.info-block {
  min-width: 0;
}

.profile-name {
  margin: 0 0 24px;
  font-size: 24px;
  font-weight: 600;
}

.info-list {
  margin: 0;
  border-top: 1px solid #eef1ef;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid #eef1ef;
  font-size: 14px;
}

.info-row dt {
  width: 96px;
  flex: 0 0 auto;
  color: #6b7280;
}

.info-row dd {
  margin: 0;
  color: #1f2937;
}

@media (max-width: 720px) {
  .profile-card {
    grid-template-columns: 1fr;
    gap: 28px;
    padding: 32px 24px;
  }

  .card-actions {
    position: static;
    justify-content: flex-end;
    margin-bottom: 8px;
  }
}
</style>
