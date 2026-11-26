<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import { createItem, getCategories, getItem, updateItem } from '@/api/items'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const categories = ref([])
const CONDITIONS = ['全新', '九成新', '八成新', '七成新', '六成新及以下']
const MAX_IMAGES = 4
const PUBLISH_COOLDOWN = 60 * 1000

const editId = computed(() => route.query.id || null)
const isEdit = computed(() => !!editId.value)

const formRef = ref(null)
const fileInput = ref(null)
const images = ref([])
const submitting = ref(false)
const loading = ref(false)

const form = reactive({
  title: '',
  categoryId: null,
  price: '',
  condition: '九成新',
  campus: userStore.userInfo?.campus || '',
  description: ''
})

function validatePrice(rule, value, callback) {
  if (value === '' || value === null || typeof value === 'undefined') {
    callback(new Error('请输入价格'))
    return
  }
  const num = Number(value)
  if (Number.isNaN(num) || num <= 0) {
    callback(new Error('价格需大于 0'))
  } else if (num > 99999) {
    callback(new Error('价格不能超过 99999'))
  } else {
    callback()
  }
}

const rules = {
  title: [
    { required: true, message: '请输入商品标题', trigger: 'blur' },
    { min: 4, max: 40, message: '标题长度为 4-40 个字符', trigger: 'blur' }
  ],
  categoryId: [{ required: true, message: '请选择分类', trigger: 'change' }],
  price: [{ validator: validatePrice, trigger: 'blur' }],
  condition: [{ required: true, message: '请选择成色', trigger: 'change' }],
  campus: [
    { required: true, message: '请输入交易校区', trigger: 'blur' },
    { min: 2, max: 20, message: '校区名称为 2-20 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请填写商品描述', trigger: 'blur' },
    { min: 5, max: 200, message: '描述长度为 5-200 个字符', trigger: 'blur' }
  ]
}

function readFile(file) {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = () => resolve('')
    reader.readAsDataURL(file)
  })
}

function chooseImage() {
  fileInput.value?.click()
}

async function handleFileChange(event) {
  const files = Array.from(event.target.files || [])
  event.target.value = ''
  if (!files.length) return

  const remain = MAX_IMAGES - images.value.length
  if (remain <= 0) {
    ElMessage.error(`最多上传 ${MAX_IMAGES} 张图片`)
    return
  }

  for (const file of files.slice(0, remain)) {
    if (!file.type.startsWith('image/')) {
      ElMessage.error('请选择图片文件')
      continue
    }
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.error(`${file.name} 超过 2MB`)
      continue
    }
    const dataUrl = await readFile(file)
    if (dataUrl) images.value.push(dataUrl)
  }
}

function removeImage(index) {
  images.value.splice(index, 1)
}

function goBack() {
  router.push('/')
}

async function loadCategories() {
  try {
    categories.value = await getCategories()
    if (!form.categoryId && categories.value.length) {
      form.categoryId = categories.value[0].id
    }
  } catch (error) {
    if (!error?.displayed) ElMessage.error(error?.message || '分类加载失败')
  }
}

async function loadForEdit() {
  loading.value = true
  try {
    const detail = await getItem(editId.value)
    form.title = detail.title
    form.categoryId = detail.categoryId
    form.price = String(detail.price)
    form.condition = detail.condition
    form.campus = detail.campus
    form.description = detail.description
    images.value = detail.images?.length ? [...detail.images] : [detail.cover]
  } catch (error) {
    ElMessage.error(error?.message || '商品加载失败')
    router.replace({ name: 'mine', query: { tab: 'published' } })
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  if (!images.value.length) {
    ElMessage.error('请至少上传一张商品图片')
    return
  }

  if (!isEdit.value) {
    const last = Number(localStorage.getItem('mock-last-publish') || 0)
    const left = PUBLISH_COOLDOWN - (Date.now() - last)
    if (left > 0) {
      ElMessage.warning(`发布太频繁，请 ${Math.ceil(left / 1000)} 秒后再试`)
      return
    }
  }

  submitting.value = true
  const payload = {
    title: form.title.trim(),
    categoryId: form.categoryId,
    price: Number(form.price),
    condition: form.condition,
    campus: form.campus.trim(),
    description: form.description.trim(),
    images: [...images.value]
  }

  try {
    if (isEdit.value) {
      await updateItem(editId.value, payload)
      ElMessage.success('修改已保存')
      router.replace({ name: 'mine', query: { tab: 'published' } })
    } else {
      const created = await createItem(payload)
      localStorage.setItem('mock-last-publish', String(Date.now()))
      ElMessage.success('发布成功')
      router.replace({ name: 'item-detail', params: { id: created.id } })
    }
  } catch (error) {
    if (!error?.displayed) {
      ElMessage.error(error?.message || '提交失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadCategories()
  if (isEdit.value) loadForEdit()
})
</script>

<template>
  <div class="publish-page">
    <AppHeader />

    <main class="publish-main" v-loading="loading">
      <button class="back-btn" type="button" @click="goBack">← 返回首页</button>

      <section class="publish-card">
        <h1>{{ isEdit ? '编辑商品' : '我要出闲置' }}</h1>
        <p class="subtitle">
          {{ isEdit ? '修改后立即生效，已下单的订单不受影响。' : '填写商品信息，同校同学看到后可直接联系你。' }}
        </p>

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large">
          <div class="form-body">
            <div class="image-block">
              <div class="image-grid">
                <div v-for="(img, index) in images" :key="index" class="image-item">
                  <img :src="img" alt="" />
                  <button class="remove" type="button" @click="removeImage(index)">×</button>
                  <span v-if="index === 0" class="cover-tag">封面</span>
                </div>
                <button
                  v-if="images.length < MAX_IMAGES"
                  class="image-add"
                  type="button"
                  @click="chooseImage"
                >
                  <span class="plus">＋</span>
                  <span>添加图片</span>
                </button>
              </div>
              <p class="image-hint">最多 {{ MAX_IMAGES }} 张，单张不超过 2MB，第一张为封面</p>
              <input
                ref="fileInput"
                class="file-input"
                type="file"
                multiple
                accept="image/png,image/jpeg,image/webp"
                @change="handleFileChange"
              />
            </div>

            <div class="fields">
              <el-form-item label="商品标题" prop="title">
                <el-input v-model="form.title" maxlength="40" show-word-limit placeholder="例如：高等数学教材 九成新" />
              </el-form-item>

              <div class="field-row">
                <el-form-item label="分类" prop="categoryId">
                  <el-select v-model="form.categoryId" placeholder="请选择分类" style="width: 100%">
                    <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
                  </el-select>
                </el-form-item>

                <el-form-item label="成色" prop="condition">
                  <el-select v-model="form.condition" placeholder="请选择成色" style="width: 100%">
                    <el-option v-for="item in CONDITIONS" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
              </div>

              <div class="field-row">
                <el-form-item label="价格（元）" prop="price">
                  <el-input v-model="form.price" placeholder="请输入价格" />
                </el-form-item>

                <el-form-item label="交易校区" prop="campus">
                  <el-input v-model="form.campus" maxlength="20" placeholder="如：东校区" />
                </el-form-item>
              </div>

              <el-form-item label="商品描述" prop="description">
                <el-input
                  v-model="form.description"
                  type="textarea"
                  :rows="4"
                  maxlength="200"
                  show-word-limit
                  placeholder="说明购买时间、使用情况、有无瑕疵、交易方式等"
                />
              </el-form-item>
            </div>
          </div>

          <div class="actions">
            <el-button size="large" @click="goBack">取消</el-button>
            <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
              {{ submitting ? '提交中…' : isEdit ? '保存修改' : '发布商品' }}
            </el-button>
          </div>
        </el-form>
      </section>
    </main>
  </div>
</template>

<style scoped>
.publish-page {
  min-height: 100vh;
  background: #f6f8f7;
}

.publish-main {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 24px 64px;
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

.publish-card {
  padding: 36px 40px 40px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 18px 50px rgba(15, 60, 40, 0.06);
}

.publish-card h1 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  margin: 0 0 28px;
  font-size: 13px;
  color: #6b7280;
}

.form-body {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 32px;
}

.image-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.image-item {
  position: relative;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  border-radius: 10px;
  background: #f1f4f2;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.remove {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  font-size: 14px;
  line-height: 1;
  color: #ffffff;
  cursor: pointer;
}

.cover-tag {
  position: absolute;
  bottom: 4px;
  left: 4px;
  padding: 1px 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  font-size: 11px;
  color: #15803d;
}

.image-add {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  aspect-ratio: 1 / 1;
  border: 1px dashed #d3ded8;
  border-radius: 10px;
  background: #f8faf9;
  font-size: 12px;
  color: #9ca3af;
  cursor: pointer;
}

.plus {
  font-size: 24px;
  line-height: 1;
  color: #b9c6c0;
}

.image-hint {
  margin: 10px 0 0;
  font-size: 12px;
  line-height: 1.6;
  color: #9ca3af;
}

.file-input {
  display: none;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

@media (max-width: 780px) {
  .publish-card {
    padding: 24px 20px 28px;
  }

  .form-body {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
