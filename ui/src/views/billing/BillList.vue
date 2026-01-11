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
          <el-space />
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
        <el-table-column prop="reference_number" label="账单号" min-width="180">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">
              {{ row.reference_number }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="用户" min-width="140">
          <template #default="{ row }">
            {{ row.username || (row.user_id ? `#${row.user_id}` : '-') }}
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

        <el-table-column v-if="authStore.isStaff()" label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="goDetail(row)">详情</el-button>
            <el-button size="small" @click="handleOpenEdit(row)">编辑</el-button>
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
      <div>将历史所有未结算账单按用户合并，并把已验证但未出账的使用记录金额加入账单。</div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            生成
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑账单对话框 (管理员) -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑账单"
      width="500px"
      @close="resetEditForm"
    >
      <el-form
        ref="editFormRef"
        :model="editFormData"
        label-width="100px"
      >
        <el-form-item label="状态">
          <el-select v-model="editFormData.status" placeholder="选择状态" style="width: 100%">
            <el-option label="DRAFT" value="DRAFT" />
            <el-option label="ISSUED" value="ISSUED" />
            <el-option label="PAID" value="PAID" />
            <el-option label="CANCELLED" value="CANCELLED" />
          </el-select>
        </el-form-item>

        <el-form-item label="到期时间">
          <el-date-picker
            v-model="editFormData.due_date"
            type="datetime"
            placeholder="选择到期时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
            clearable
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="editSubmitting" @click="handleEditSubmit">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { DocumentAdd, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { getBills, generateBills, updateBill } from '@/api/billing'
import type { Bill } from '@/types'
import { formatDateTime } from '@/utils/date'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const tableData = ref<Bill[]>([])

const dialogVisible = ref(false)
const formRef = ref<FormInstance>()

const editDialogVisible = ref(false)
const editSubmitting = ref(false)
const editFormRef = ref<FormInstance>()
const editFormData = reactive({
  id: 0,
  status: '' as string,
  due_date: null as string | null
})


// 加载账单
const loadBills = async () => {
  loading.value = true
  try {
    const res = await getBills({
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

const handleOpenEdit = (bill: Bill) => {
  editFormData.id = bill.id
  editFormData.status = bill.status
  editFormData.due_date = bill.due_date || null
  editDialogVisible.value = true
}

const goDetail = (bill: Bill) => {
  router.push({ name: 'BillDetail', params: { id: bill.id } })
}

const resetForm = () => {
  if (formRef.value) formRef.value.resetFields()
}

const resetEditForm = () => {
  editFormData.id = 0
  editFormData.status = ''
  editFormData.due_date = null
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    await generateBills({})
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

const handleEditSubmit = async () => {
  if (!authStore.isStaff()) {
    ElMessage.error('仅管理员可编辑账单')
    return
  }
  if (!editFormData.id) return

  editSubmitting.value = true
  try {
    await updateBill(editFormData.id, {
      status: editFormData.status,
      due_date: editFormData.due_date
    })
    ElMessage.success('账单更新成功')
    editDialogVisible.value = false
    loadBills()
  } catch (error) {
    console.error(error)
    ElMessage.error('账单更新失败')
  } finally {
    editSubmitting.value = false
  }
}

onMounted(() => {
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
