<template>
  <div class="app-shell">
    <header class="app-header">
      <h1>NEMO 前后端分离示例</h1>
      <p>基于 Vue 3 + Vite，使用 MVC 目录结构组织前端代码。</p>
    </header>
    <HomeView />
  </div>
</template>

<script setup>
import HomeView from "./views/HomeView.vue";
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 24px 48px;
}

.app-header h1 {
  margin: 0 0 8px;
  font-size: 28px;
}

.app-header p {
  margin: 0;
  color: #4b5563;
}
</style>
