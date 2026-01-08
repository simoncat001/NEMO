<template>
  <div class="page-container">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总预约数" :value="stats.total">
            <template #prefix>
              <el-icon color="#409EFF"><Calendar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="进行中" :value="stats.ongoing">
            <template #prefix>
              <el-icon color="#67C23A"><Clock /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="已取消" :value="stats.cancelled">
            <template #prefix>
              <el-icon color="#E6A23C"><Warning /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="已错过" :value="stats.missed">
            <template #prefix>
              <el-icon color="#F56C6C"><CircleClose /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 顶部操作栏 -->
    <el-card class="header-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="12">
          <el-space>
            <el-button type="primary" :icon="Plus" @click="handleCreate">
              创建预约
            </el-button>
            <el-button :icon="Refresh" @click="loadReservations">
              刷新
            </el-button>
            <el-button :icon="Calendar" @click="goToCalendar">
              日历视图
            </el-button>
          </el-space>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-space>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              @change="loadReservations"
            />
            <el-select
              v-model="filterCancelled"
              placeholder="状态"
              clearable
              style="width: 120px"
              @change="loadReservations"
            >
              <el-option label="未取消" :value="false" />
              <el-option label="已取消" :value="true" />
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
        <el-table-column label="仪器" min-width="150">
          <template #default="{ row }">
            {{ row.tool?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="用户" width="120">
          <template #default="{ row }">
            {{ row.user?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="项目" width="150">
          <template #default="{ row }">
            {{ row.project?.name || '-' }}
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
        <el-table-column label="时长" width="100">
          <template #default="{ row }">
            {{ calculateDuration(row.start, row.end) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.cancelled" type="warning">
              已取消
            </el-tag>
            <el-tag v-else-if="row.missed" type="danger">
              已错过
            </el-tag>
            <el-tag v-else-if="isOngoing(row)" type="success">
              进行中
            </el-tag>
            <el-tag v-else-if="isPast(row)" type="info">
              已完成
            </el-tag>
            <el-tag v-else type="primary">
              未开始
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="150">
          <template #default="{ row }">
            {{ row.additional_information || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                :disabled="row.cancelled || isPast(row)"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                :disabled="row.cancelled || isPast(row)"
                @click="handleCancel(row)"
              >
                取消
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
          @size-change="loadReservations"
          @current-change="loadReservations"
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
        <el-form-item label="仪器" prop="tool_id">
          <el-select
            v-model="formData.tool_id"
            placeholder="请选择仪器"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="tool in tools"
              :key="tool.id"
              :label="tool.name"
              :value="tool.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="项目" prop="project_id">
          <el-select
            v-model="formData.project_id"
            placeholder="请选择项目"
            filterable
            style="width: 100%"
          >
            <el-option label="项目 1" :value="1" />
            <el-option label="项目 2" :value="2" />
            <el-option label="项目 3" :value="3" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="预约日期" required>
              <el-date-picker
                v-model="reservationDate"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                :clearable="false"
                @change="updateTimeFromSlider"
              />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="预约时间" required>
              <div class="time-slider-container">
                <el-slider
                  v-model="timeRange"
                  range
                  :min="0"
                  :max="1440"
                  :step="15"
                  :marks="marks"
                  :format-tooltip="formatTooltip"
                  @change="updateTimeFromSlider"
                />
                <div class="time-display">
                  {{ formatTimeFromMinutes(timeRange[0]) }} - {{ formatTimeFromMinutes(timeRange[1]) }}
                  <el-tag size="small" type="info" style="margin-left: 8px">
                    时长: {{ formatDuration(timeRange[1] - timeRange[0]) }}
                  </el-tag>
                </div>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input
            v-model="formData.additional_information"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
        <el-form-item label="自行配置">
          <el-switch
            v-model="formData.self_configuration"
            active-text="是"
            inactive-text="否"
          />
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  Refresh,
  Edit,
  Delete,
  Calendar,
  Clock,
  Warning,
  CircleClose
} from '@element-plus/icons-vue'
import {
  getReservations,
  createReservation,
  updateReservation,
  cancelReservation
} from '@/api/reservations'
import { getTools } from '@/api/tools'
import type { Reservation, Tool } from '@/types'
import { formatDateTime } from '@/utils/helpers'
import dayjs from 'dayjs'

const router = useRouter()

// 预约时间相关
const reservationDate = ref(dayjs().format('YYYY-MM-DD'))
const timeRange = ref([540, 600]) // Default 9:00 - 10:00

const marks = {
  0: '00:00',
  240: '04:00',
  480: '08:00',
  720: '12:00',
  960: '16:00',
  1200: '20:00',
  1440: '24:00'
}

const formatTooltip = (val: number) => {
  const hours = Math.floor(val / 60)
  const minutes = val % 60
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
}

const formatTimeFromMinutes = (val: number) => {
    return formatTooltip(val)
}

const formatDuration = (minutes: number) => {
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    if (h > 0) {
        return `${h}小时${m > 0 ? ` ${m}分钟` : ''}`
    }
    return `${m}分钟`
}

const updateTimeFromSlider = () => {
    if (!reservationDate.value) return
    
    const startMinutes = timeRange.value[0]
    const endMinutes = timeRange.value[1]
    
    const start = dayjs(reservationDate.value).startOf('day').add(startMinutes, 'minute')
    const end = dayjs(reservationDate.value).startOf('day').add(endMinutes, 'minute')
    
    formData.start = start.format('YYYY-MM-DD HH:mm:ss')
    formData.end = end.format('YYYY-MM-DD HH:mm:ss')
}

// 数据列表
const loading = ref(false)
const tableData = ref<Reservation[]>([])

// 仪器列表
const tools = ref<Tool[]>([])

// 过滤器
const dateRange = ref<[string, string]>()
const filterCancelled = ref<boolean>()

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 统计数据
const stats = reactive({
  total: 0,
  ongoing: 0,
  cancelled: 0,
  missed: 0
})

// 对话框
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const dialogTitle = computed(() => (dialogMode.value === 'create' ? '创建预约' : '编辑预约'))
const submitting = ref(false)

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<Reservation>>({
  tool_id: undefined,
  project_id: undefined,
  user_id: 1, // 从当前登录用户获取
  start: '',
  end: '',
  additional_information: '',
  self_configuration: false,
  cancelled: false,
  missed: false
})

const formRules: FormRules = {
  tool_id: [{ required: true, message: '请选择仪器', trigger: 'change' }],
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  start: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

// 加载仪器列表
const loadTools = async () => {
  try {
    const response = await getTools({ skip: 0, limit: 1000 })
    tools.value = Array.isArray(response) ? response : response.data || []
  } catch (error) {
    console.error('加载仪器列表失败:', error)
  }
}

// 加载预约列表
const loadReservations = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    if (dateRange.value) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await getReservations(params)
    let data = Array.isArray(response) ? response : response.data || []
    
    // 前端过滤
    if (filterCancelled.value !== undefined) {
      data = data.filter((r: Reservation) => r.cancelled === filterCancelled.value)
    }
    
    tableData.value = data
    total.value = data.length
    
    // 计算统计数据
    calculateStats(data)
  } catch (error) {
    ElMessage.error('加载预约列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 计算统计数据
const calculateStats = (data: Reservation[]) => {
  stats.total = data.length
  stats.ongoing = data.filter(r => !r.cancelled && !r.missed && isOngoing(r)).length
  stats.cancelled = data.filter(r => r.cancelled).length
  stats.missed = data.filter(r => r.missed).length
}

// 判断预约是否进行中
const isOngoing = (reservation: Reservation) => {
  const now = dayjs()
  const start = dayjs(reservation.start)
  const end = dayjs(reservation.end)
  return now.isAfter(start) && now.isBefore(end)
}

// 判断预约是否已过期
const isPast = (reservation: Reservation) => {
  const now = dayjs()
  const end = dayjs(reservation.end)
  return now.isAfter(end)
}

// 计算时长
const calculateDuration = (start: string, end: string) => {
  const startTime = dayjs(start)
  const endTime = dayjs(end)
  const diffMinutes = endTime.diff(startTime, 'minute')
  const hours = Math.floor(diffMinutes / 60)
  const minutes = diffMinutes % 60
  return `${hours}h${minutes}m`
}

// 跳转到日历视图
const goToCalendar = () => {
  router.push('/calendar')
}

// 打开创建对话框
const handleCreate = () => {
  dialogMode.value = 'create'
  dialogVisible.value = true
  reservationDate.value = dayjs().format('YYYY-MM-DD')
  timeRange.value = [540, 600]
  updateTimeFromSlider()
}

// 打开编辑对话框
const handleEdit = (row: Reservation) => {
  dialogMode.value = 'edit'
  Object.assign(formData, {
    id: row.id,
    tool_id: row.tool_id,
    project_id: row.project_id,
    user_id: row.user_id,
    start: row.start,
    end: row.end,
    additional_information: row.additional_information,
    self_configuration: row.self_configuration
  })
  
  const start = dayjs(row.start)
  const end = dayjs(row.end)
  reservationDate.value = start.format('YYYY-MM-DD')
  const startMinutes = start.hour() * 60 + start.minute()
  let endMinutes = end.hour() * 60 + end.minute()
  
  // 处理跨天情况（如果是第二天0点，设为1440）
  if (end.date() !== start.date()) {
      endMinutes += 1440
  }
  
  timeRange.value = [startMinutes, endMinutes]
  
  dialogVisible.value = true
}

// 取消预约
const handleCancel = async (row: Reservation) => {
  try {
    await ElMessageBox.confirm('确定要取消该预约吗？', '警告', {
      type: 'warning',
      confirmButtonText: '确定取消'
    })
    await cancelReservation(row.id)
    ElMessage.success('取消成功')
    await loadReservations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
      console.error(error)
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: any) => {
    if (!valid) return

    // 验证时间
    if (dayjs(formData.start).isAfter(dayjs(formData.end))) {
      ElMessage.error('结束时间必须晚于开始时间')
      return
    }

    submitting.value = true
    try {
      if (dialogMode.value === 'create') {
        await createReservation(formData)
        ElMessage.success('创建成功')
      } else {
        await updateReservation(formData.id!, formData)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      await loadReservations()
    } catch (error: any) {
      if (error.response?.status === 409) {
        ElMessage.error('该时间段已被预约')
      } else {
        ElMessage.error(dialogMode.value === 'create' ? '创建失败' : '更新失败')
      }
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
    tool_id: undefined,
    project_id: undefined,
    start: '',
    end: '',
    additional_information: '',
    self_configuration: false
  })
}

// 初始化
onMounted(async () => {
  await loadTools()
  await loadReservations()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.stats-row {
  margin-bottom: 16px;
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

.time-slider-container {
  width: 100%;
  padding: 0 10px;
}

.time-display {
  margin-top: 8px;
  text-align: center;
  color: #606266;
  font-size: 14px;
}
</style>
