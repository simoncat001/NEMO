<template>
  <div class="page-container">
    <!-- 工具基本信息 -->
    <el-card v-loading="loading" class="info-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Tools /></el-icon>
            工具详情
          </span>
          <el-space>
            <el-button type="primary" :icon="Edit" @click="handleEdit">
              编辑工具
            </el-button>
            <el-button :icon="Back" @click="handleBack">
              返回列表
            </el-button>
          </el-space>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="工具ID">
          {{ toolDetail.id }}
        </el-descriptions-item>
        <el-descriptions-item label="工具名称">
          <el-text tag="b" size="large">{{ toolDetail.name }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="分类">
          <el-tag v-if="toolDetail.category">{{ toolDetail.category }}</el-tag>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="位置">
          {{ toolDetail.location || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="运行状态">
          <el-tag v-if="toolDetail.operational" type="success">
            <el-icon><CircleCheck /></el-icon> 正常运行
          </el-tag>
          <el-tag v-else type="danger">
            <el-icon><CircleClose /></el-icon> 故障维修
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="可见性">
          <el-tag :type="toolDetail.visible ? 'success' : 'info'">
            {{ toolDetail.visible ? '用户可见' : '已隐藏' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="需要预约">
          <el-tag :type="toolDetail.requires_reservation ? 'warning' : 'info'">
            {{ toolDetail.requires_reservation ? '必须预约' : '无需预约' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(toolDetail.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          <el-text v-if="toolDetail.description" type="info">
            {{ toolDetail.description }}
          </el-text>
          <el-text v-else type="info">无描述</el-text>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 当前使用情况 -->
    <el-card class="usage-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Clock /></el-icon>
            当前使用情况
          </span>
          <el-button :icon="Refresh" @click="loadActiveUsage">
            刷新
          </el-button>
        </div>
      </template>

      <el-alert
        v-if="activeUsage"
        title="工具使用中"
        type="warning"
        :closable="false"
      >
        <el-descriptions :column="2" border>
          <el-descriptions-item label="使用者">
            {{ activeUsage.user?.username || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDateTime(activeUsage.start) }}
          </el-descriptions-item>
          <el-descriptions-item label="项目">
            {{ activeUsage.project?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="使用时长">
            {{ calculateDuration(activeUsage.start) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-alert>
      <el-empty v-else description="当前无人使用" />
    </el-card>

    <!-- 配置列表 -->
    <el-card class="config-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Setting /></el-icon>
            工具配置
          </span>
          <el-button :icon="Refresh" @click="loadConfigurations">
            刷新
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="configLoading"
        :data="configurations"
        stripe
        border
      >
        <el-table-column prop="name" label="配置名称" min-width="150" />
        <el-table-column label="当前设置" min-width="150">
          <template #default="{ row }">
            {{ row.current_setting || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="可用选项" min-width="200">
          <template #default="{ row }">
            <el-tag
              v-for="option in row.configuration_options"
              :key="option.id"
              style="margin-right: 5px"
            >
              {{ option.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="颜色标识" width="120">
          <template #default="{ row }">
            <div v-if="row.current_setting_color" class="color-display">
              <div
                class="color-block"
                :style="{ backgroundColor: row.current_setting_color }"
              />
              {{ row.current_setting_color }}
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="display_order" label="排序" width="80" />
      </el-table>
      <el-empty v-if="!configurations.length && !configLoading" description="暂无配置" />
    </el-card>

    <!-- 相关任务 -->
    <el-card class="task-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Document /></el-icon>
            相关任务
          </span>
          <el-button :icon="Refresh" @click="loadRelatedTasks">
            刷新
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="taskLoading"
        :data="relatedTasks"
        stripe
        border
      >
        <el-table-column prop="id" label="任务ID" width="100" />
        <el-table-column prop="problem_description" label="问题描述" min-width="200" />
        <el-table-column label="紧急程度" width="120">
          <template #default="{ row }">
            <el-tag
              :type="
                row.urgency === 'high'
                  ? 'danger'
                  : row.urgency === 'medium'
                  ? 'warning'
                  : 'info'
              "
            >
              {{ row.urgency === 'high' ? '高' : row.urgency === 'medium' ? '中' : '低' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag
              :type="
                row.status === 'pending'
                  ? 'warning'
                  : row.status === 'in_progress'
                  ? 'primary'
                  : row.status === 'resolved'
                  ? 'success'
                  : 'info'
              "
            >
              {{
                row.status === 'pending'
                  ? '待处理'
                  : row.status === 'in_progress'
                  ? '处理中'
                  : row.status === 'resolved'
                  ? '已解决'
                  : '已取消'
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator.username" label="创建人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!relatedTasks.length && !taskLoading" description="暂无相关任务" />
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑工具"
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
        
        <el-divider content-position="left">收费设置</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="收费类型">
              <el-select v-model="formData.price_type" placeholder="请选择">
                <el-option label="按次收费" :value="0" />
                <el-option label="按时收费" :value="1" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8" v-if="formData.price_type === 0">
            <el-form-item label="每次价格">
              <el-input-number v-model="formData.price_per_use" :min="0" :precision="2" :step="1" />
            </el-form-item>
          </el-col>
          <el-col :span="8" v-if="formData.price_type === 1">
            <el-form-item label="每小时价格">
              <el-input-number v-model="formData.price_per_hour" :min="0" :precision="2" :step="1" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  Tools,
  Edit,
  Back,
  Refresh,
  Clock,
  Setting,
  Document,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'
import { getTool, updateTool } from '@/api/tools'
import { getToolActiveUsage } from '@/api/usage-events'
import { getToolConfigurations } from '@/api/configurations'
import { getTasks } from '@/api/tasks'
import type { Tool, UsageEvent, Configuration, Task } from '@/types'
import { formatDateTime } from '@/utils/helpers'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const toolId = Number(route.params.id)

// 工具详情
const loading = ref(false)
const toolDetail = ref<Partial<Tool>>({})

// 当前使用情况
const activeUsage = ref<UsageEvent | null>(null)

// 配置列表
const configLoading = ref(false)
const configurations = ref<Configuration[]>([])

// 相关任务
const taskLoading = ref(false)
const relatedTasks = ref<Task[]>([])

// 编辑对话框
const editDialogVisible = ref(false)
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
  requires_reservation: false,
  price_type: 1,
  price_per_use: 0,
  price_per_hour: 0
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入工具名称', trigger: 'blur' }],
  category: [{ required: true, message: '请输入分类', trigger: 'blur' }]
}

// 加载工具详情
const loadToolDetail = async () => {
  loading.value = true
  try {
    const response = await getTool(toolId)
    toolDetail.value = response
  } catch (error) {
    ElMessage.error('加载工具详情失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 加载当前使用情况
const loadActiveUsage = async () => {
  try {
    const response = await getToolActiveUsage(toolId)
    // 如果返回数组，取第一个；如果是单个对象，直接使用
    activeUsage.value = Array.isArray(response) ? response[0] : response
  } catch (error) {
    // 没有活动使用记录不算错误
    activeUsage.value = null
  }
}

// 加载配置列表
const loadConfigurations = async () => {
  configLoading.value = true
  try {
    const response = await getToolConfigurations(toolId)
    configurations.value = Array.isArray(response) ? response : response.data || []
  } catch (error) {
    ElMessage.error('加载配置列表失败')
    console.error(error)
  } finally {
    configLoading.value = false
  }
}

// 加载相关任务（前端过滤）
const loadRelatedTasks = async () => {
  taskLoading.value = true
  try {
    const response = await getTasks({ skip: 0, limit: 100 })
    const allTasks = Array.isArray(response) ? response : response.data || []
    // 前端过滤与当前工具相关的任务
    relatedTasks.value = allTasks.filter((task: Task) => task.tool?.id === toolId)
  } catch (error) {
    ElMessage.error('加载相关任务失败')
    console.error(error)
  } finally {
    taskLoading.value = false
  }
}

// 计算使用时长
const calculateDuration = (startTime: string | undefined) => {
  if (!startTime) return '-'
  const start = dayjs(startTime)
  const now = dayjs()
  const diffMinutes = now.diff(start, 'minute')
  const hours = Math.floor(diffMinutes / 60)
  const minutes = diffMinutes % 60
  return `${hours}小时${minutes}分钟`
}

// 打开编辑对话框
const handleEdit = () => {
  Object.assign(formData, {
    id: toolDetail.value.id,
    name: toolDetail.value.name,
    category: toolDetail.value.category,
    location: toolDetail.value.location,
    description: toolDetail.value.description,
    operational: toolDetail.value.operational,
    visible: toolDetail.value.visible,
    requires_reservation: toolDetail.value.requires_reservation,
    price_type: toolDetail.value.price_type ?? 1,
    price_per_use: Number(toolDetail.value.price_per_use || 0),
    price_per_hour: Number(toolDetail.value.price_per_hour || 0)
  })
  editDialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await updateTool(toolId, formData)
      ElMessage.success('更新成功')
      editDialogVisible.value = false
      await loadToolDetail()
    } catch (error) {
      ElMessage.error('更新失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
}

// 返回列表
const handleBack = () => {
  router.push('/tools')
}

// 初始化
onMounted(async () => {
  await loadToolDetail()
  await loadActiveUsage()
  await loadConfigurations()
  await loadRelatedTasks()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.info-card {
  margin-bottom: 16px;
}

.usage-card,
.config-card,
.task-card {
  margin-top: 16px;
}

.color-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-block {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}
</style>
