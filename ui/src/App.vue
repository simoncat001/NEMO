<template>
  <div class="app">
    <header class="app__header">
      <div class="app__brand">
        <div class="app__logo">N</div>
        <div>
          <div class="app__title">{{ appTitle }}</div>
          <div class="app__subtitle">Front-end UI migration preview</div>
        </div>
      </div>
      <nav class="app__nav">
        <RouterLink to="/">Landing</RouterLink>
        <RouterLink to="/login">Login</RouterLink>
      </nav>
    </header>
    <main class="app__content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { ref } from 'vue';

const appTitle = ref('NEMO');
</script>

<style scoped>
.app {
  font-family: "Helvetica Neue", Arial, sans-serif;
  min-height: 100vh;
  background: #f5f6f8;
  color: #1c1f24;
}

.app__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #0b3d91;
  color: #fff;
}

.app__brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app__logo {
  height: 32px;
  width: 32px;
  border-radius: 8px;
  background: #fff;
  color: #0b3d91;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.app__title {
  font-size: 20px;
  font-weight: 600;
}

.app__subtitle {
  font-size: 12px;
  opacity: 0.8;
}

.app__nav {
  display: flex;
  gap: 16px;
}

.app__nav a {
  color: #fff;
  text-decoration: none;
  font-weight: 500;
}

.app__nav a.router-link-active {
  text-decoration: underline;
}

.app__content {
  padding: 24px;
}
</style>
