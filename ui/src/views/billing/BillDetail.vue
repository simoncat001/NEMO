<template>
  <div class="page-container">
    <el-card class="header-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="12">
          <el-space>
            <el-button @click="goBack">返回</el-button>
            <span class="title">账单详情</span>
          </el-space>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-space>
            <el-tag v-if="detail" :type="getStatusType(detail.status)">{{ detail.status }}</el-tag>
          </el-space>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="content-card" shadow="never" v-loading="loading">
      <template v-if="detail">
        <el-descriptions title="账单信息" :column="2" border>
          <el-descriptions-item label="账单号">{{ detail.reference_number }}</el-descriptions-item>
          <el-descriptions-item label="金额">¥{{ Number(detail.total_amount).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="生成时间">{{ formatDateTime(detail.issued_date) }}</el-descriptions-item>
          <el-descriptions-item label="到期时间">{{ formatDateTime(detail.due_date) }}</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <el-descriptions title="用户信息" :column="2" border>
          <template v-if="detail.user">
            <el-descriptions-item label="用户ID">{{ detail.user.id }}</el-descriptions-item>
            <el-descriptions-item label="用户名">{{ detail.user.username }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ detail.user.last_name }}{{ detail.user.first_name }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ detail.user.email }}</el-descriptions-item>
          </template>
          <template v-else>
            <el-descriptions-item label="用户">-</el-descriptions-item>
          </template>
        </el-descriptions>

        <el-divider />

        <div class="section-title">关联使用记录</div>
        <el-table :data="detail.usage_events" stripe border style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column label="仪器" min-width="160">
            <template #default="{ row }">
              {{ row.tool?.name || `#${row.tool_id}` }}
            </template>
          </el-table-column>
          <el-table-column label="项目" min-width="160">
            <template #default="{ row }">
              {{ row.project?.name || `#${row.project_id}` }}
            </template>
          </el-table-column>
          <el-table-column label="开始时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.start) }}
            </template>
          </el-table-column>
          <el-table-column label="结束时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.end) }}
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="费用" width="120">
            <template #default="{ row }">
              ¥{{ Number(row.amount || 0).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag v-if="row.waived" type="info">已豁免</el-tag>
              <el-tag v-else :type="row.validated ? 'success' : 'warning'">
                {{ row.validated ? '已验证' : '未验证' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="note" label="备注" min-width="200" />
        </el-table>
      </template>
      <template v-else>
        <div>暂无数据</div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { getBillDetail } from '@/api/billing'
import type { BillDetail } from '@/types'
import { formatDateTime } from '@/utils/date'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const detail = ref<BillDetail | null>(null)

const getStatusType = (status: string) => {
  switch (status) {
    case 'PAID':
      return 'success'
    case 'ISSUED':
      return 'primary'
    case 'CANCELLED':
      return 'info'
    default:
      return 'warning'
  }
}

const loadDetail = async () => {
  const billId = Number(route.params.id)
  if (!billId) {
    ElMessage.error('账单ID无效')
    return
  }

  loading.value = true
  try {
    const res = await getBillDetail(billId)
    detail.value = (res as any) || null
  } catch (e) {
    console.error(e)
    ElMessage.error('加载账单详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'Billing' })
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.title {
  font-size: 16px;
  font-weight: 600;
}

.content-card {
  margin-top: 12px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}
</style>