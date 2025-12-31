<template>
  <div class="page-container">
    <!-- 顶部操作栏 -->
    <el-card class="header-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="12">
          <el-space>
            <el-button type="primary" :icon="Plus" @click="handleCreate">
              创建耗材
            </el-button>
            <el-button :icon="Refresh" @click="loadConsumables">
              刷新
            </el-button>
          </el-space>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-space>
            <el-input
              v-model="filterName"
              placeholder="搜索耗材名称"
              clearable
              style="width: 200px"
              @change="loadConsumables"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
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
        <el-table-column prop="name" label="耗材名称" min-width="180" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="quantity" label="库存数量" width="120">
            <template #default="{ row }">
                <el-tag :type="row.quantity <= (row.reminder_threshold || 0) ? 'danger' : 'success'">
                    {{ row.quantity }}
                </el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="reminder_threshold" label="预警阈值" width="120" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleWithdraw(row)">领用</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 领用对话框 -->
    <el-dialog
      v-model="withdrawDialogVisible"
      title="领用耗材"
      width="500px"
    >
      <el-form
        ref="withdrawFormRef"
        :model="withdrawFormData"
        :rules="withdrawRules"
        label-width="100px"
      >
        <el-form-item label="耗材名称">
          <span>{{ currentConsumable?.name }}</span>
        </el-form-item>
        <el-form-item label="当前库存">
          <span>{{ currentConsumable?.quantity }}</span>
        </el-form-item>
        <el-form-item label="领用数量" prop="quantity">
          <el-input-number v-model="withdrawFormData.quantity" :min="1" :max="currentConsumable?.quantity" />
        </el-form-item>
        <el-form-item label="领用人ID" prop="user_id">
           <el-input v-model.number="withdrawFormData.user_id" placeholder="请输入用户ID" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="withdrawDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitWithdraw" :loading="submittingWithdraw">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '创建耗材' : '编辑耗材'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-input v-model="formData.category" />
        </el-form-item>
        <el-form-item label="库存数量" prop="quantity">
          <el-input-number v-model="formData.quantity" :min="0" />
        </el-form-item>
        <el-form-item label="预警阈值" prop="reminder_threshold">
          <el-input-number v-model="formData.reminder_threshold" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getConsumables, createConsumable, updateConsumable, deleteConsumable, withdrawConsumable } from '@/api/consumables'
import type { Consumable } from '@/types'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const tableData = ref<Consumable[]>([])
const filterName = ref('')

const dialogVisible = ref(false)
const dialogType = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const formRef = ref<FormInstance>()

const withdrawDialogVisible = ref(false)
const submittingWithdraw = ref(false)
const withdrawFormRef = ref<FormInstance>()
const currentConsumable = ref<Consumable>()
const withdrawFormData = reactive({
    quantity: 1,
    user_id: undefined as number | undefined
})

const withdrawRules = reactive<FormRules>({
    quantity: [{ required: true, message: '请输入领用数量', trigger: 'blur' }],
    user_id: [{ required: true, message: '请输入用户ID', trigger: 'blur' }]
})

const formData = reactive<Partial<Consumable>>({
  name: '',
  category: '',
  quantity: 0,
  reminder_threshold: 0
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入耗材名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入库存数量', trigger: 'blur' }]
})

onMounted(() => {
  loadConsumables()
})

const loadConsumables = async () => {
  loading.value = true
  try {
    // TODO: Add filter support in API
    const data = await getConsumables()
    tableData.value = data
  } catch (error) {
    console.error(error)
    ElMessage.error('加载耗材列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  dialogType.value = 'create'
  Object.assign(formData, {
    name: '',
    category: '',
    quantity: 0,
    reminder_threshold: 0
  })
  dialogVisible.value = true
}

const handleWithdraw = (row: Consumable) => {
    currentConsumable.value = row
    withdrawFormData.quantity = 1
    withdrawFormData.user_id = authStore.user?.id
    withdrawDialogVisible.value = true
}

const submitWithdraw = async () => {
    if (!withdrawFormRef.value || !currentConsumable.value) return
    
    await withdrawFormRef.value.validate(async (valid) => {
        if (valid) {
            submittingWithdraw.value = true
            try {
                await withdrawConsumable({
                    consumable_id: currentConsumable.value!.id,
                    quantity: withdrawFormData.quantity,
                    user_id: withdrawFormData.user_id!,
                    date: new Date().toISOString()
                })
                ElMessage.success('领用成功')
                withdrawDialogVisible.value = false
                loadConsumables()
            } catch (error) {
                console.error(error)
                ElMessage.error('领用失败')
            } finally {
                submittingWithdraw.value = false
            }
        }
    })
}

const handleEdit = (row: Consumable) => {
  dialogType.value = 'edit'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = (row: Consumable) => {
  ElMessageBox.confirm(
    `确定要删除耗材 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await deleteConsumable(row.id)
      ElMessage.success('删除成功')
      loadConsumables()
    } catch (error) {
      console.error(error)
      ElMessage.error('删除失败')
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (dialogType.value === 'create') {
          await createConsumable(formData)
          ElMessage.success('创建成功')
        } else {
          if (formData.id) {
            await updateConsumable(formData.id, formData)
            ElMessage.success('更新成功')
          }
        }
        dialogVisible.value = false
        loadConsumables()
      } catch (error) {
        console.error(error)
        ElMessage.error(dialogType.value === 'create' ? '创建失败' : '更新失败')
      } finally {
        submitting.value = false
      }
    }
  })
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.header-card {
  margin-bottom: 20px;
}
</style>
