<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' }
})
</script>

<template>
  <div class="auth-page">
    <aside class="brand-panel">
      <div class="brand-top">
        <div class="brand-mark">校</div>
        <div>
          <p class="brand-name">校园二手</p>
          <p class="brand-en">Campus Market</p>
        </div>
      </div>

      <div class="brand-copy">
        <h1>把闲置交给<br />需要它的人</h1>
        <p>同校交易、当面验货，让每一件旧物都能继续被使用。</p>
      </div>

      <ul class="brand-points">
        <li>同校自提，交易更快</li>
        <li>学号认证，身份可信</li>
        <li>订单留痕，售后可追溯</li>
      </ul>

      <p class="brand-foot">© 校园二手交易平台</p>
    </aside>

    <main class="form-panel">
      <div class="mobile-brand">校园二手</div>

      <div class="form-card">
        <h2>{{ title }}</h2>
        <p class="form-sub">{{ subtitle }}</p>
        <slot />
      </div>
    </main>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
}

/* 左侧品牌区 */
.brand-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 56px 64px;
  color: #eafaf0;
  background: linear-gradient(155deg, #0b4a2f 0%, #0e5c3a 45%, #15803d 100%);
  overflow: hidden;
}

.brand-panel::after {
  content: '';
  position: absolute;
  right: -140px;
  bottom: -160px;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
}

.brand-top {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  font-size: 20px;
  font-weight: 600;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.14);
}

.brand-name {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 1px;
}

.brand-en {
  margin: 2px 0 0;
  font-size: 11px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: rgba(234, 250, 240, 0.6);
}

.brand-copy {
  position: relative;
  margin: 64px 0;
}

.brand-copy h1 {
  margin: 0 0 20px;
  font-size: 38px;
  line-height: 1.35;
  font-weight: 600;
  letter-spacing: 1px;
}

.brand-copy p {
  margin: 0;
  max-width: 380px;
  font-size: 15px;
  line-height: 1.8;
  color: rgba(234, 250, 240, 0.78);
}

.brand-points {
  position: relative;
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 14px;
}

.brand-points li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: rgba(234, 250, 240, 0.85);
}

.brand-points li::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #7ee2a8;
}

.brand-foot {
  position: relative;
  margin: 48px 0 0;
  font-size: 12px;
  color: rgba(234, 250, 240, 0.5);
}

/* 右侧表单区 */
.form-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  background: #f6f8f7;
}

.mobile-brand {
  display: none;
  margin-bottom: 24px;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 2px;
  color: #0e5c3a;
}

.form-card {
  width: 100%;
  max-width: 420px;
  padding: 44px 40px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 18px 50px rgba(15, 60, 40, 0.08);
}

.form-card h2 {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 600;
}

.form-sub {
  margin: 0 0 28px;
  font-size: 14px;
  color: #6b7280;
}

@media (max-width: 900px) {
  .auth-page {
    grid-template-columns: 1fr;
  }

  .brand-panel {
    display: none;
  }

  .mobile-brand {
    display: block;
  }

  .form-card {
    padding: 32px 24px;
  }
}
</style>
