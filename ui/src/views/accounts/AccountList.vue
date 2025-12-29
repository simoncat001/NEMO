<template>
  <div class="page-container">
    <!-- 顶部操作栏 -->
    <el-card class="header-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="12">
          <el-space>
            <el-button type="primary" :icon="Plus" @click="handleCreate">
              创建账户
            </el-button>
            <el-button :icon="Refresh" @click="loadAccounts">
              刷新
            </el-button>
          </el-space>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-space>
            <el-select
              v-model="filterTypeId"
              placeholder="账户类型"
              clearable
              style="width: 180px"
              @change="loadAccounts"
            >
              <el-option
                v-for="type in accountTypes"
                :key="type.id"
                :label="type.name"
                :value="type.id"
              />
            </el-select>
            <el-select
              v-model="filterActive"
              placeholder="状态"
              clearable
              style="width: 120px"
              @change="loadAccounts"
            >
              <el-option label="已激活" :value="true" />
              <el-option label="已停用" :value="false" />
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
        <el-table-column prop="name" label="账户名称" min-width="180" />
        <el-table-column label="账户类型" width="150">
          <template #default="{ row }">
            <el-tag>{{ row.account_type?.name || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.active ? 'success' : 'danger'">
              {{ row.active ? '已激活' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button
                v-if="row.active"
                type="warning"
                size="small"
                :icon="Close"
                @click="handleDeactivate(row)"
              >
                停用
              </el-button>
              <el-button
                v-else
                type="success"
                size="small"
                :icon="Check"
                @click="handleActivate(row)"
              >
                激活
              </el-button>
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadAccounts"
          @current-change="loadAccounts"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="账户名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入账户名称" />
        </el-form-item>
        <el-form-item label="账户类型" prop="account_type_id">
          <el-select
            v-model="formData.account_type_id"
            placeholder="请选择账户类型"
            style="width: 100%"
          >
            <el-option
              v-for="type in accountTypes"
              :key="type.id"
              :label="type.name"
              :value="type.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="active">
          <el-switch v-model="formData.active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Refresh, Edit, Delete, Check, Close } from '@element-plus/icons-vue'
import {
  getAccounts,
  createAccount,
  updateAccount,
  deleteAccount,
  activateAccount,
  deactivateAccount,
  getAccountTypes
} from '@/api/accounts'
import type { Account, AccountType } from '@/types'
import { formatDateTime } from '@/utils/helpers'

// 数据列表
const loading = ref(false)
const tableData = ref<Account[]>([])
const accountTypes = ref<AccountType[]>([])

// 过滤器
const filterTypeId = ref<number>()
const filterActive = ref<boolean>()

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 对话框
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const dialogTitle = computed(() => (dialogMode.value === 'create' ? '创建账户' : '编辑账户'))
const submitting = ref(false)

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<Account>>({
  name: '',
  account_type_id: undefined,
  active: true
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入账户名称', trigger: 'blur' }],
  account_type_id: [{ required: true, message: '请选择账户类型', trigger: 'change' }]
}

// 加载账户类型
const loadAccountTypes = async () => {
  try {
    const response = await getAccountTypes()
    accountTypes.value = response.data || []
  } catch (error) {
    console.error('加载账户类型失败:', error)
  }
}

// 加载账户列表
const loadAccounts = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      ...(filterTypeId.value && { type_id: filterTypeId.value }),
      ...(filterActive.value !== undefined && { active: filterActive.value })
    }
    const response = await getAccounts(params)
    tableData.value = response.data || []
    total.value = tableData.value.length
  } catch (error) {
    ElMessage.error('加载账户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 打开创建对话框
const handleCreate = () => {
  dialogMode.value = 'create'
  dialogVisible.value = true
}

// 打开编辑对话框
const handleEdit = (row: Account) => {
  dialogMode.value = 'edit'
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    account_type_id: row.account_type_id,
    active: row.active
  })
  dialogVisible.value = true
}

// 激活账户
const handleActivate = async (row: Account) => {
  try {
    await ElMessageBox.confirm('确定要激活该账户吗？', '提示', {
      type: 'warning'
    })
    await activateAccount(row.id)
    ElMessage.success('激活成功')
    await loadAccounts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('激活失败')
      console.error(error)
    }
  }
}

// 停用账户
const handleDeactivate = async (row: Account) => {
  try {
    await ElMessageBox.confirm('确定要停用该账户吗？', '提示', {
      type: 'warning'
    })
    await deactivateAccount(row.id)
    ElMessage.success('停用成功')
    await loadAccounts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('停用失败')
      console.error(error)
    }
  }
}

// 删除账户
const handleDelete = async (row: Account) => {
  try {
    await ElMessageBox.confirm('确定要删除该账户吗？此操作不可恢复！', '警告', {
      type: 'error',
      confirmButtonText: '确定删除'
    })
    await deleteAccount(row.id)
    ElMessage.success('删除成功')
    await loadAccounts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (dialogMode.value === 'create') {
        await createAccount(formData)
        ElMessage.success('创建成功')
      } else {
        await updateAccount(formData.id!, formData)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      await loadAccounts()
    } catch (error) {
      ElMessage.error(dialogMode.value === 'create' ? '创建失败' : '更新失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(formData, {
    name: '',
    account_type_id: undefined,
    active: true
  })
}

// 初始化
onMounted(() => {
  loadAccountTypes()
  loadAccounts()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.header-card {
  margin-bottom: 16px;
}

.table-card {
  margin-top: 16px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
