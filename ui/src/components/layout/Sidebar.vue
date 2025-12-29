<template>
  <div class="sidebar">
    <div class="logo">
      <span class="logo-mark" v-if="!appStore.sidebarCollapsed" aria-label="NEMO logo">
        <svg viewBox="0 0 64 64" width="32" height="32" role="img" focusable="false">
          <defs>
            <linearGradient id="nemoGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#46a0ff" />
              <stop offset="1" stop-color="#7c4dff" />
            </linearGradient>
          </defs>
          <rect x="6" y="6" width="52" height="52" rx="14" fill="url(#nemoGrad)" />
          <path
            d="M20 42V22h4l8 12 8-12h4v20h-4V29l-8 12-8-12v13h-4z"
            fill="#ffffff"
          />
        </svg>
      </span>
      <span v-if="!appStore.sidebarCollapsed">NEMO</span>
    </div>
    
    <el-menu
      :default-active="activeMenu"
      :collapse="appStore.sidebarCollapsed"
      :unique-opened="true"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><HomeFilled /></el-icon>
        <template #title>仪表盘</template>
      </el-menu-item>

      <el-menu-item index="/tools">
        <el-icon><Tools /></el-icon>
        <template #title>工具管理</template>
      </el-menu-item>

      <el-sub-menu index="reservations">
        <template #title>
          <el-icon><Calendar /></el-icon>
          <span>预约系统</span>
        </template>
        <el-menu-item index="/reservations">预约列表</el-menu-item>
        <el-menu-item index="/calendar">预约日历</el-menu-item>
      </el-sub-menu>

      <el-menu-item index="/usage-events">
        <el-icon><Clock /></el-icon>
        <template #title>使用记录</template>
      </el-menu-item>

      <el-menu-item index="/tasks">
        <el-icon><List /></el-icon>
        <template #title>任务管理</template>
      </el-menu-item>

      <el-sub-menu index="admin" v-if="authStore.isStaff()">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>系统管理</span>
        </template>
        <el-menu-item index="/accounts">账户管理</el-menu-item>
        <el-menu-item index="/staff-charges">员工收费</el-menu-item>
        <el-menu-item index="/configurations">配置管理</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const appStore = useAppStore()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  background-color: #2b3a4a;
}

.logo-mark {
  display: inline-flex;
  align-items: center;
  margin-right: 10px;
}

.el-menu {
  border-right: none;
  flex: 1;
}
</style>
