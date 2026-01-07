<template>
  <div class="page-container">
    <!-- 顶部操作栏 -->
    <el-card class="header-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="12">
          <el-space>
            <el-button type="primary" :icon="Plus" @click="handleCreate">
              创建工具
            </el-button>
            <el-button :icon="Refresh" @click="loadTools">
              刷新
            </el-button>
          </el-space>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-space>
            <el-input
              v-model="filterName"
              placeholder="搜索工具名称"
              clearable
              style="width: 200px"
              @change="loadTools"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="filterVisible"
              placeholder="可见性"
              clearable
              style="width: 120px"
              @change="loadTools"
            >
              <el-option label="可见" :value="true" />
              <el-option label="隐藏" :value="false" />
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
        <el-table-column prop="name" label="工具名称" min-width="180">
          <template #default="{ row }">
            <el-link type="primary" @click="handleViewDetail(row)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.category">{{ row.category }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="位置" width="150">
          <template #default="{ row }">
            {{ row.location || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="运行状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.operational" type="success">
              <el-icon><CircleCheck /></el-icon> 正常
            </el-tag>
            <el-tag v-else type="danger">
              <el-icon><CircleClose /></el-icon> 故障
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="可见性" width="100">
          <template #default="{ row }">
            <el-tag :type="row.visible ? 'success' : 'info'">
              {{ row.visible ? '可见' : '隐藏' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="需要预约" width="100">
          <template #default="{ row }">
            <el-tag :type="row.requires_reservation ? 'warning' : 'info'">
              {{ row.requires_reservation ? '需要' : '不需要' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button
                type="info"
                size="small"
                :icon="View"
                @click="handleViewDetail(row)"
              >
                详情
              </el-button>
              <el-button
                type="warning"
                size="small"
                :icon="Money"
                @click="loadRates(row.id)"
              >
                费率
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
          @size-change="loadTools"
          @current-change="loadTools"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="工具名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入工具名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-input v-model="formData.category" placeholder="请输入分类" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="formData.location" placeholder="请输入位置" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入工具描述"
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="计费类型">
              <el-select v-model="formData.price_type" placeholder="选择类型" style="width: 100%">
                <el-option label="按次收费" :value="0" />
                <el-option label="按时收费" :value="1" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="基础价格">
              <el-input-number v-model="formData.price_per_hour" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="运行状态">
              <el-switch
                v-model="formData.operational"
                active-text="正常"
                inactive-text="故障"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="可见性">
              <el-switch
                v-model="formData.visible"
                active-text="可见"
                inactive-text="隐藏"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="需要预约">
              <el-switch
                v-model="formData.requires_reservation"
                active-text="需要"
                inactive-text="不需要"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 费率管理对话框 -->
    <el-dialog
      v-model="rateDialogVisible"
      title="分时费率配置"
      width="600px"
    >
      <el-card shadow="never" style="margin-bottom: 20px">
        <template #header>添加时段</template>
        <el-form :inline="true" :model="rateForm">
          <el-form-item label="开始">
            <el-time-picker v-model="rateForm.start_time" value-format="HH:mm:ss" placeholder="Start" style="width: 120px"/>
          </el-form-item>
          <el-form-item label="结束">
            <el-time-picker v-model="rateForm.end_time" value-format="HH:mm:ss" placeholder="End" style="width: 120px"/>
          </el-form-item>
          <el-form-item label="价格">
            <el-input-number v-model="rateForm.price" :min="0" style="width: 100px"/>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleAddRate">添加</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-table :data="rateList" border stripe>
        <el-table-column prop="start_time" label="开始时间" />
        <el-table-column prop="end_time" label="结束时间" />
        <el-table-column prop="price" label="费率" />
        <el-table-column label="操作" width="100">
            <template #default="{ row }">
                <el-button type="danger" icon="Delete" circle size="small" @click="handleDeleteRate(row.id)"/>
            </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  Refresh,
  Edit,
  Delete,
  View,
  Search,
  CircleCheck,
  CircleClose,
  Money // New Icon
} from '@element-plus/icons-vue'
import { getTools, createTool, updateTool, deleteTool, getToolRates, createToolRate, deleteToolRate, type ToolRate } from '@/api/tools'
import type { Tool } from '@/types'
import { formatDateTime } from '@/utils/helpers'

const router = useRouter()

// 费率管理
const rateDialogVisible = ref(false)
const currentRateToolId = ref<number>(0)
const rateList = ref<ToolRate[]>([])
const rateForm = reactive({
    start_time: '',
    end_time: '',
    price: 0
})

const loadRates = async (toolId: number) => {
    currentRateToolId.value = toolId
    rateList.value = await getToolRates(toolId)
    rateDialogVisible.value = true
}

const handleAddRate = async () => {
    try {
        await createToolRate(currentRateToolId.value, {
            ...rateForm,
            tool_id: currentRateToolId.value
        })
        ElMessage.success('添加成功')
        rateList.value = await getToolRates(currentRateToolId.value)
        rateForm.start_time = ''
        rateForm.end_time = ''
        rateForm.price = 0
    } catch (e) {
        ElMessage.error('添加失败')
    }
}

const handleDeleteRate = async (rateId: number) => {
    try {
        await deleteToolRate(currentRateToolId.value, rateId)
        ElMessage.success('删除成功')
        rateList.value = await getToolRates(currentRateToolId.value)
    } catch (e) {
        ElMessage.error('删除失败')
    }
}

// 数据列表
const loading = ref(false)
const tableData = ref<Tool[]>([])

// 过滤器
const filterName = ref('')
const filterVisible = ref<boolean>()

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 对话框
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const dialogTitle = computed(() => (dialogMode.value === 'create' ? '创建工具' : '编辑工具'))
const submitting = ref(false)

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<Tool>>({
  name: '',
  category: '',
  location: '',
  description: '',
  operational: true,
  visible: true,
  requires_reservation: true,
  price_type: 1,
  price_per_hour: 0
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入工具名称', trigger: 'blur' }],
  category: [{ required: true, message: '请输入分类', trigger: 'blur' }]
}

// 加载工具列表
const loadTools = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
      // 后端API可能不支持这些过滤参数，先注释
      // ...(filterName.value && { name: filterName.value }),
      // ...(filterVisible.value !== undefined && { visible: filterVisible.value })
    }
    const response = await getTools(params)
    let data = Array.isArray(response) ? response : (response as any).data || []
    
    // 前端过滤
    if (filterName.value) {
      data = data.filter((tool: Tool) => 
        tool.name.toLowerCase().includes(filterName.value.toLowerCase())
      )
    }
    if (filterVisible.value !== undefined) {
      data = data.filter((tool: Tool) => tool.visible === filterVisible.value)
    }
    
    tableData.value = data
    total.value = data.length
  } catch (error) {
    ElMessage.error('加载工具列表失败')
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
const handleEdit = (row: Tool) => {
  dialogMode.value = 'edit'
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    category: row.category,
    location: row.location,
    description: row.description,
    operational: row.operational,
    visible: row.visible,
    requires_reservation: row.requires_reservation,
    price_type: row.price_type,
    price_per_hour: row.price_per_hour
  })
  dialogVisible.value = true
}

// 查看详情
const handleViewDetail = (row: Tool) => {
  router.push(`/tools/${row.id}`)
}

// 删除工具
const handleDelete = async (row: Tool) => {
  try {
    await ElMessageBox.confirm('确定要删除该工具吗？此操作不可恢复！', '警告', {
      type: 'error',
      confirmButtonText: '确定删除'
    })
    await deleteTool(row.id)
    ElMessage.success('删除成功')
    await loadTools()
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
        await createTool(formData)
        ElMessage.success('创建成功')
      } else {
        await updateTool(formData.id!, formData)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      await loadTools()
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
    category: '',
    location: '',
    description: '',
    operational: true,
    visible: true,
    requires_reservation: false
  })
}

// 初始化
onMounted(() => {
  loadTools()
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
