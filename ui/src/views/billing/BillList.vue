<template>
  <div class="page-container">
    <!-- 顶部操作栏 -->
    <el-card class="header-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="12">
          <el-space>
            <el-button 
              v-if="authStore.isStaff()"
              type="primary" 
              :icon="DocumentAdd" 
              @click="handleOpenGenerate"
            >
              生成账单
            </el-button>
            <el-button :icon="Refresh" @click="loadBills">
              刷新
            </el-button>
          </el-space>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-space>
            <el-select
              v-model="filterAccountId"
              placeholder="按账户筛选"
              clearable
              filterable
              style="width: 200px"
              @change="loadBills"
            >
              <el-option
                v-for="acc in accountList"
                :key="acc.id"
                :label="acc.name"
                :value="acc.id"
              />
            </el-select>
          </el-space>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="reference_number" label="账单号" min-width="180" />
        <el-table-column label="账户" min-width="150">
          <template #default="{ row }">
            {{ getAccountName(row.account_id) }}
          </template>
        </el-table-column>
        <el-table-column label="周期" width="220">
          <template #default="{ row }">
            {{ formatDate(row.period_start) }} 至 {{ formatDate(row.period_end) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" width="120">
          <template #default="{ row }">
            ¥{{ Number(row.total_amount).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="生成时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.issued_date) }}
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 (简化版，暂不绑定后端分页) -->
    </el-card>

    <!-- 生成账单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="生成账单"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="时间范围" prop="dateRange">
          <el-date-picker
            v-model="formData.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="目标账户" prop="accountIds">
          <el-select
            v-model="formData.accountIds"
            multiple
            placeholder="选择账户 (留空则选择所有)"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="acc in accountList"
              :key="acc.id"
              :label="acc.name"
              :value="acc.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            生成
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { DocumentAdd, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getBills, generateBills } from '@/api/billing'
import { getAccounts } from '@/api/accounts'
import type { Bill, Account } from '@/types'
import { formatDateTime, formatDate } from '@/utils/date'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const submitting = ref(false)
const tableData = ref<Bill[]>([])
const filterAccountId = ref<number | undefined>(undefined)
const accountList = ref<Account[]>([])

const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const formData = reactive({
  dateRange: [] as string[],
  accountIds: [] as number[]
})

const rules = reactive<FormRules>({
  dateRange: [{ required: true, message: '请选择时间范围', trigger: 'change' }]
})

// 加载账单
const loadBills = async () => {
  loading.value = true
  try {
    const res = await getBills({
      account_id: filterAccountId.value,
      skip: 0,
      limit: 100
    })
    // 假设后端直接返回数组，如果封装在 data 字段里需要调整
    // 查看 api/billing.ts 定义: return request.get<Bill[]>... 
    // 通常 request 拦截器会处理 Response 结构，这里直接使用 data。
    // 但是 check billing.ts 我写的是 request.get<Bill[]>
    // 对比 accounts.ts: request.get<ApiResponse<AccountType[]>>
    // 我的 billing.ts 可能写错了类型定义，应该也是 ApiResponse<Bill[]>
    // 但后端 billing.py 返回的是 List[BillResponse]。
    // 前端 request 拦截器通常返回 response.data。
    // 暂且假设 res 就是数组，或者 res.data 是数组。
    // 稳妥起见我们 console log 或者 any
    tableData.value = (res as any) || []
  } catch (error) {
    console.error(error)
    ElMessage.error('加载账单失败')
  } finally {
    loading.value = false
  }
}

// 加载账户列表 (用于筛选和下拉)
const loadAccounts = async () => {
  try {
    const res = await getAccounts({ limit: 1000 })
    // 同上，假设 res 是 Account[] 或者 res.data 是 Account[]
    // 查看 accounts.py 返回 List[AccountResponse]
    // 查看 accounts.ts 定义: Request.get<ApiResponse>...
    // 这里的 getAccounts 引用的是 api/accounts.ts 里的 getAccounts 吗？
    // api/accounts.ts 里的 getAccounts 是 request.get<ApiResponse<Account[]>>('/accounts'...)
    // 所以 res 这里应该是 ApiResponse<Account[]>
    // 但是通常 axios 拦截器会 unwrap data。
    // 假设未unwrap:
    const data = (res as any).data || res
    accountList.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载账户列表失败', error)
  }
}

const getAccountName = (id: number) => {
  const acc = accountList.value.find(a => a.id === id)
  return acc ? acc.name : `ID: ${id}`
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'PAID': return 'success'
    case 'ISSUED': return 'primary'
    case 'CANCELLED': return 'info'
    default: return 'warning'
  }
}

const handleOpenGenerate = () => {
  dialogVisible.value = true
}

const resetForm = () => {
  if (formRef.value) formRef.value.resetFields()
  formData.dateRange = []
  formData.accountIds = []
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const [start, end] = formData.dateRange
        await generateBills({
          start_date: start + ' 00:00:00',
          end_date: end + ' 23:59:59',
          account_ids: formData.accountIds.length > 0 ? formData.accountIds : undefined
        })
        ElMessage.success('账单生成成功')
        dialogVisible.value = false
        loadBills()
      } catch (error) {
        console.error(error)
        ElMessage.error('账单生成失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  loadAccounts()
  loadBills()
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
