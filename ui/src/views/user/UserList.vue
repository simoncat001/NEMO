<template>
  <div class="page-container">
    <el-card class="header-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="12">
          <el-button :icon="Refresh" @click="loadUsers">刷新</el-button>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <!-- 预留搜索框 -->
        </el-col>
      </el-row>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="first_name" label="名" width="100" />
        <el-table-column prop="last_name" label="姓" width="100" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column label="角色" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.is_superuser" type="danger" effect="plain" style="margin-right: 5px">超级管理员</el-tag>
            <el-tag v-else-if="row.is_staff" type="primary" effect="plain">管理员</el-tag>
            <el-tag v-else type="info" effect="plain">普通用户</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '已激活' : '未激活' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.date_joined) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <template v-if="row.id !== authStore.user?.id">
              <el-button
                v-if="!row.is_active"
                type="success"
                size="small"
                @click="toggleActive(row, true)"
              >
                通过审核
              </el-button>
              <el-button
                v-else
                type="warning"
                size="small"
                @click="toggleActive(row, false)"
              >
                停用
              </el-button>
            </template>
            <el-tag v-else type="info">当前用户</el-tag>
             <!-- 预留编辑按钮 -->
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, updateUser } from '@/api/users'
import type { User } from '@/types'
import { formatDateTime } from '@/utils/date'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const tableData = ref<User[]>([])

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await getUsers({ skip: 0, limit: 100 })
    // Assume res is array or wrap
    tableData.value = (res as any) || []
  } catch (error) {
    console.error(error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const toggleActive = async (user: User, isActive: boolean) => {
  const actionText = isActive ? '激活(通过审核)' : '停用'
  try {
    await ElMessageBox.confirm(
      `确定要${actionText}用户 "${user.username}" 吗?`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: isActive ? 'success' : 'warning'
      }
    )
    
    await updateUser(user.id, { is_active: isActive })
    ElMessage.success(`用户已${actionText}`)
    
    // Update local state or reload
    user.is_active = isActive
  } catch (e) {
    // Cancelled or error
    if (e !== 'cancel') {
        console.error(e)
        ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.header-card {
  margin-bottom: 16px;
}
.page-container {
  padding: 20px;
}
</style>
