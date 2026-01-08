<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon tool-icon"><Tools /></el-icon>
            <div>
              <div class="stat-value">{{ stats.total_tools }}</div>
              <div class="stat-label">仪器总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon reservation-icon"><Calendar /></el-icon>
            <div>
              <div class="stat-value">{{ stats.today_reservations }}</div>
              <div class="stat-label">今日预约</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon task-icon"><List /></el-icon>
            <div>
              <div class="stat-value">{{ stats.active_tasks }}</div>
              <div class="stat-label">待处理任务</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon user-icon"><User /></el-icon>
            <div>
              <div class="stat-value">{{ stats.active_users }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <span>最近预约</span>
          </template>
          <el-table :data="recentReservations" style="width: 100%">
            <el-table-column prop="tool_name" label="仪器" />
            <el-table-column prop="start" label="开始时间" />
            <el-table-column prop="end" label="结束时间" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <span>待处理任务</span>
          </template>
          <el-table :data="pendingTasks" style="width: 100%">
            <el-table-column prop="tool_name" label="仪器" />
            <el-table-column prop="problem_description" label="问题描述" show-overflow-tooltip />
            <el-table-column label="紧急程度">
              <template #default="{ row }">
                <el-tag :type="getUrgencyType(row.urgency)">
                  {{ getUrgencyLabel(row.urgency) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getTaskUrgencyLabel, getTaskUrgencyType } from '@/utils/helpers'
import { getDashboard } from '@/api/dashboard'

const stats = ref({
  total_tools: 0,
  today_reservations: 0,
  active_tasks: 0,
  active_users: 0,
})

const recentReservations = ref([])
const pendingTasks = ref([])

const getUrgencyLabel = getTaskUrgencyLabel
const getUrgencyType = getTaskUrgencyType

onMounted(async () => {
  const data = await getDashboard()
  stats.value = data.stats
  recentReservations.value = data.recent_reservations as any
  pendingTasks.value = data.pending_tasks as any
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
}

.tool-icon {
  color: #409eff;
}

.reservation-icon {
  color: #67c23a;
}

.task-icon {
  color: #e6a23c;
}

.user-icon {
  color: #f56c6c;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
</style>
