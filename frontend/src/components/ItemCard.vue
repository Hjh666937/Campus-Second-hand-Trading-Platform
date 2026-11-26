<script setup>
defineProps({
  item: { type: Object, required: true }
})

const emit = defineEmits(['select'])

function formatPrice(value) {
  const num = Number(value) || 0
  return Number.isInteger(num) ? String(num) : num.toFixed(2)
}

function formatDate(value) {
  if (!value) return ''
  return String(value).slice(5).replace('-', '/')
}
</script>

<template>
  <article class="item-card" @click="emit('select', item)">
    <div class="cover">
      <img :src="item.cover" :alt="item.title" loading="lazy" />
      <span class="condition">商家说：{{ item.condition }}</span>
    </div>

    <div class="body">
      <h3 class="title">{{ item.title }}</h3>

      <p class="price">
        <span class="symbol">¥</span>{{ formatPrice(item.price) }}
      </p>

      <div class="meta">
        <span class="campus">{{ item.campus }}</span>
        <span class="extra">{{ item.viewCount }} 看过 · 发布于 {{ formatDate(item.createdAt) }}</span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.item-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid #eef1ef;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s;
}

.item-card:hover {
  transform: translateY(-2px);
  border-color: #d9e8df;
  box-shadow: 0 12px 28px rgba(15, 60, 40, 0.09);
}

.cover {
  position: relative;
  aspect-ratio: 4 / 3;
  background: #f1f4f2;
  overflow: hidden;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.condition {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  font-size: 12px;
  color: #15803d;
}

.body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px 16px;
}

.title {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
  color: #1f2937;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 42px;
}

.price {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #e0523f;
}

.symbol {
  margin-right: 2px;
  font-size: 13px;
}

.meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: #9ca3af;
}

.campus {
  padding: 1px 8px;
  border-radius: 6px;
  background: #f2f6f4;
  color: #6b7280;
}

.extra {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
</style>
