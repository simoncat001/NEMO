<template>
  <div class="page-container">
    <!-- 顶部操作栏 -->
    <el-card class="header-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="12">
          <el-space>
            <el-button type="primary" :icon="Plus" @click="handleCreate">
              创建预约
            </el-button>
            <el-button :icon="List" @click="goToList">
              列表视图
            </el-button>
            <el-button :icon="Refresh" @click="loadReservations">
              刷新
            </el-button>
          </el-space>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-space>
            <el-select
              v-model="selectedTool"
              placeholder="筛选仪器"
              clearable
              filterable
              style="width: 200px"
              @change="loadReservations"
            >
              <el-option
                v-for="tool in tools"
                :key="tool.id"
                :label="tool.name"
                :value="tool.id"
              />
            </el-select>
            <el-radio-group v-model="viewMode" @change="loadReservations">
              <el-radio-button label="month">月</el-radio-button>
              <el-radio-button label="week">周</el-radio-button>
              <el-radio-button label="day">日</el-radio-button>
            </el-radio-group>
          </el-space>
        </el-col>
      </el-row>
    </el-card>

    <!-- 日历视图 -->
    <el-card class="calendar-card" shadow="never">
      <template #header>
        <div class="calendar-header">
          <el-space>
            <el-button :icon="ArrowLeft" @click="prevPeriod" />
            <el-button :icon="ArrowRight" @click="nextPeriod" />
            <el-button @click="today">今天</el-button>
          </el-space>
          <div class="current-date">{{ currentDateDisplay }}</div>
        </div>
      </template>

      <!-- 月视图 -->
      <el-calendar v-if="viewMode === 'month'" v-model="currentDate">
        <template #date-cell="{ data }">
          <div class="calendar-day">
            <div class="day-number">{{ data.day.split('-')[2] }}</div>
            <div class="reservations-container">
              <div
                v-for="reservation in getReservationsForDate(data.day)"
                :key="reservation.id"
                class="reservation-item"
                :class="getReservationClass(reservation)"
                @click="handleViewDetail(reservation)"
              >
                <el-tooltip :content="getTooltipContent(reservation)" placement="top">
                  <div class="reservation-content">
                    <el-icon><Clock /></el-icon>
                    {{ formatTime(reservation.start) }} - {{ formatTime(reservation.end) }}
                    <br />
                    {{ reservation.tool?.name || '未指定仪器' }}
                  </div>
                </el-tooltip>
              </div>
            </div>
          </div>
        </template>
      </el-calendar>

      <!-- 周/日视图 -->
      <div v-else class="timeline-view">
        <div class="timeline-header">
          <div class="time-column">时间</div>
          <div v-if="viewMode === 'week'" class="days-row">
            <div
              v-for="day in weekDays"
              :key="day.date"
              class="day-column"
              :class="{ today: isToday(day.date) }"
            >
              <div class="day-name">{{ day.name }}</div>
              <div class="day-date">{{ day.dateNum }}</div>
            </div>
          </div>
          <div v-else class="day-column today">
            <div class="day-name">{{ dayjs(currentDate).format('dddd') }}</div>
            <div class="day-date">{{ dayjs(currentDate).format('D') }}</div>
          </div>
        </div>
        <div class="timeline-body">
          <div
            v-for="hour in 24"
            :key="hour"
            class="hour-row"
          >
            <div class="time-label">{{ `${hour - 1}:00` }}</div>
            <div v-if="viewMode === 'week'" class="days-grid">
              <div
                v-for="day in weekDays"
                :key="day.date"
                class="day-cell"
              >
                <div
                  v-for="reservation in getReservationsForHour(day.date, hour - 1)"
                  :key="reservation.id"
                  class="reservation-block"
                  :class="getReservationClass(reservation)"
                  :style="getReservationStyle(reservation)"
                  @click="handleViewDetail(reservation)"
                >
                  <el-tooltip :content="getTooltipContent(reservation)" placement="top">
                    <div class="reservation-content">
                      {{ reservation.tool?.name }}
                    </div>
                  </el-tooltip>
                </div>
              </div>
            </div>
            <div v-else class="day-cell">
              <div
                v-for="reservation in getReservationsForHour(currentDate, hour - 1)"
                :key="reservation.id"
                class="reservation-block"
                :class="getReservationClass(reservation)"
                :style="getReservationStyle(reservation)"
                @click="handleViewDetail(reservation)"
              >
                <el-tooltip :content="getTooltipContent(reservation)" placement="top">
                  <div class="reservation-content">
                    {{ reservation.tool?.name }}
                  </div>
                </el-tooltip>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 预约详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="预约详情"
      width="600px"
    >
      <el-descriptions v-if="selectedReservation" :column="2" border>
        <el-descriptions-item label="预约ID">
          {{ selectedReservation.id }}
        </el-descriptions-item>
        <el-descriptions-item label="仪器">
          {{ selectedReservation.tool?.name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="用户">
          {{ selectedReservation.user?.username || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="项目">
          {{ selectedReservation.project?.name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="开始时间">
          {{ formatDateTime(selectedReservation.start) }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间">
          {{ formatDateTime(selectedReservation.end) }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag v-if="selectedReservation.cancelled" type="warning">
            已取消
          </el-tag>
          <el-tag v-else-if="selectedReservation.missed" type="danger">
            已错过
          </el-tag>
          <el-tag v-else-if="isOngoing(selectedReservation)" type="success">
            进行中
          </el-tag>
          <el-tag v-else type="info">
            未开始
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="自行配置">
          {{ selectedReservation.self_configuration ? '是' : '否' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ selectedReservation.additional_information || '无' }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-space>
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button
            type="primary"
            :icon="Edit"
            :disabled="selectedReservation?.cancelled || isPast(selectedReservation)"
            @click="handleEdit(selectedReservation!)"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            :icon="Delete"
            :disabled="selectedReservation?.cancelled || isPast(selectedReservation)"
            @click="handleCancel(selectedReservation!)"
          >
            取消预约
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="formDialogVisible"
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
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  List,
  Refresh,
  Edit,
  Delete,
  Clock,
  ArrowLeft,
  ArrowRight
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
import isoWeek from 'dayjs/plugin/isoWeek'
import weekday from 'dayjs/plugin/weekday'

dayjs.extend(isoWeek)
dayjs.extend(weekday)

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

// 视图模式
const viewMode = ref<'month' | 'week' | 'day'>('month')
const currentDate = ref(new Date())

// 数据
const reservations = ref<Reservation[]>([])
const tools = ref<Tool[]>([])
const selectedTool = ref<number>()
const selectedReservation = ref<Reservation | null>(null)

// 对话框
const detailDialogVisible = ref(false)
const formDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const dialogTitle = computed(() => (dialogMode.value === 'create' ? '创建预约' : '编辑预约'))
const submitting = ref(false)

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<Reservation>>({
  tool_id: undefined,
  project_id: undefined,
  user_id: 1,
  start: '',
  end: '',
  additional_information: '',
  self_configuration: false
})

const formRules: FormRules = {
  tool_id: [{ required: true, message: '请选择仪器', trigger: 'change' }],
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  start: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

// 计算当前日期显示
const currentDateDisplay = computed(() => {
  if (viewMode.value === 'month') {
    return dayjs(currentDate.value).format('YYYY年 MM月')
  } else if (viewMode.value === 'week') {
    const start = dayjs(currentDate.value).startOf('week')
    const end = dayjs(currentDate.value).endOf('week')
    return `${start.format('YYYY年 MM月DD日')} - ${end.format('MM月DD日')}`
  } else {
    return dayjs(currentDate.value).format('YYYY年 MM月DD日')
  }
})

// 计算周视图的天数
const weekDays = computed(() => {
  const start = dayjs(currentDate.value).startOf('week')
  return Array.from({ length: 7 }, (_, i) => {
    const date = start.add(i, 'day')
    return {
      date: date.format('YYYY-MM-DD'),
      dateNum: date.format('D'),
      name: date.format('ddd')
    }
  })
})

// 加载仪器列表
const loadTools = async () => {
  try {
    const response = await getTools({ skip: 0, limit: 1000 })
    tools.value = Array.isArray(response) ? response : response.data || []
  } catch (error) {
    console.error('加载仪器列表失败:', error)
  }
}

// 加载预约数据
const loadReservations = async () => {
  try {
    let startDate, endDate

    if (viewMode.value === 'month') {
      startDate = dayjs(currentDate.value).startOf('month').format('YYYY-MM-DD')
      endDate = dayjs(currentDate.value).endOf('month').format('YYYY-MM-DD')
    } else if (viewMode.value === 'week') {
      startDate = dayjs(currentDate.value).startOf('week').format('YYYY-MM-DD')
      endDate = dayjs(currentDate.value).endOf('week').format('YYYY-MM-DD')
    } else {
      startDate = dayjs(currentDate.value).startOf('day').format('YYYY-MM-DD')
      endDate = dayjs(currentDate.value).endOf('day').format('YYYY-MM-DD')
    }

    const params: any = {
      start_date: startDate,
      end_date: endDate,
      limit: 1000
    }

    if (selectedTool.value) {
      params.tool_id = selectedTool.value
    }

    const response = await getReservations(params)
    reservations.value = Array.isArray(response) ? response : response.data || []
  } catch (error) {
    ElMessage.error('加载预约数据失败')
    console.error(error)
  }
}

// 获取指定日期的预约
const getReservationsForDate = (date: string) => {
  return reservations.value.filter(r => {
    const startDate = dayjs(r.start).format('YYYY-MM-DD')
    return startDate === date
  })
}

// 获取指定小时的预约
const getReservationsForHour = (date: string | Date, hour: number) => {
  const dateStr = typeof date === 'string' ? date : dayjs(date).format('YYYY-MM-DD')
  return reservations.value.filter(r => {
    const start = dayjs(r.start)
    const end = dayjs(r.end)
    const hourStart = dayjs(`${dateStr} ${hour}:00:00`)
    const hourEnd = hourStart.add(1, 'hour')
    
    return (
      (start.isBefore(hourEnd) && end.isAfter(hourStart)) ||
      (start.isSame(hourStart) || end.isSame(hourEnd))
    )
  })
}

// 获取预约样式
const getReservationClass = (reservation: Reservation) => {
  if (reservation.cancelled) return 'cancelled'
  if (reservation.missed) return 'missed'
  if (isOngoing(reservation)) return 'ongoing'
  if (isPast(reservation)) return 'past'
  return 'upcoming'
}

// 获取预约块样式（用于时间线视图）
const getReservationStyle = (reservation: Reservation) => {
  const start = dayjs(reservation.start)
  const end = dayjs(reservation.end)
  const duration = end.diff(start, 'minute')
  const height = (duration / 60) * 60 // 每小时60px
  
  return {
    height: `${Math.max(height, 30)}px`,
    top: `${start.minute()}px`
  }
}

// 获取提示内容
const getTooltipContent = (reservation: Reservation) => {
  return `
    仪器: ${reservation.tool?.name || '-'}
    用户: ${reservation.user?.username || '-'}
    时间: ${formatDateTime(reservation.start)} - ${formatDateTime(reservation.end)}
    ${reservation.additional_information ? `备注: ${reservation.additional_information}` : ''}
  `
}

// 格式化时间
const formatTime = (datetime: string) => {
  return dayjs(datetime).format('HH:mm')
}

// 判断是否是今天
const isToday = (date: string) => {
  return dayjs(date).isSame(dayjs(), 'day')
}

// 判断预约是否进行中
const isOngoing = (reservation: Reservation | null) => {
  if (!reservation) return false
  const now = dayjs()
  const start = dayjs(reservation.start)
  const end = dayjs(reservation.end)
  return now.isAfter(start) && now.isBefore(end)
}

// 判断预约是否已过期
const isPast = (reservation: Reservation | null) => {
  if (!reservation) return false
  const now = dayjs()
  const end = dayjs(reservation.end)
  return now.isAfter(end)
}

// 切换到上一个时间段
const prevPeriod = () => {
  if (viewMode.value === 'month') {
    currentDate.value = dayjs(currentDate.value).subtract(1, 'month').toDate()
  } else if (viewMode.value === 'week') {
    currentDate.value = dayjs(currentDate.value).subtract(1, 'week').toDate()
  } else {
    currentDate.value = dayjs(currentDate.value).subtract(1, 'day').toDate()
  }
  loadReservations()
}

// 切换到下一个时间段
const nextPeriod = () => {
  if (viewMode.value === 'month') {
    currentDate.value = dayjs(currentDate.value).add(1, 'month').toDate()
  } else if (viewMode.value === 'week') {
    currentDate.value = dayjs(currentDate.value).add(1, 'week').toDate()
  } else {
    currentDate.value = dayjs(currentDate.value).add(1, 'day').toDate()
  }
  loadReservations()
}

// 回到今天
const today = () => {
  currentDate.value = new Date()
  loadReservations()
}

// 跳转到列表视图
const goToList = () => {
  router.push('/reservations')
}

// 查看预约详情
const handleViewDetail = (reservation: Reservation) => {
  selectedReservation.value = reservation
  detailDialogVisible.value = true
}

// 创建预约
const handleCreate = () => {
  dialogMode.value = 'create'
  formDialogVisible.value = true
  reservationDate.value = dayjs().format('YYYY-MM-DD')
  timeRange.value = [540, 600]
  updateTimeFromSlider()
}

// 编辑预约
const handleEdit = (reservation: Reservation) => {
  dialogMode.value = 'edit'
  Object.assign(formData, {
    id: reservation.id,
    tool_id: reservation.tool_id,
    project_id: reservation.project_id,
    user_id: reservation.user_id,
    start: reservation.start,
    end: reservation.end,
    additional_information: reservation.additional_information,
    self_configuration: reservation.self_configuration
  })
  
  const start = dayjs(reservation.start)
  const end = dayjs(reservation.end)
  reservationDate.value = start.format('YYYY-MM-DD')
  const startMinutes = start.hour() * 60 + start.minute()
  let endMinutes = end.hour() * 60 + end.minute()
  
  // 处理跨天情况（如果是第二天0点，设为1440）
  if (end.date() !== start.date()) {
      endMinutes += 1440
  }
  
  timeRange.value = [startMinutes, endMinutes]
  
  detailDialogVisible.value = false
  formDialogVisible.value = true
}

// 取消预约
const handleCancel = async (reservation: Reservation) => {
  try {
    await ElMessageBox.confirm('确定要取消该预约吗？', '警告', {
      type: 'warning',
      confirmButtonText: '确定取消'
    })
    await cancelReservation(reservation.id)
    ElMessage.success('取消成功')
    detailDialogVisible.value = false
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
      formDialogVisible.value = false
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

.header-card {
  margin-bottom: 16px;
}

.calendar-card {
  margin-top: 16px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-date {
  font-size: 18px;
  font-weight: 600;
}

.calendar-day {
  height: 100%;
  padding: 4px;
}

.day-number {
  font-weight: 600;
  margin-bottom: 4px;
}

.reservations-container {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.reservation-item {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.reservation-item:hover {
  opacity: 0.8;
  transform: scale(1.02);
}

.reservation-item.upcoming {
  background-color: #409eff;
  color: white;
}

.reservation-item.ongoing {
  background-color: #67c23a;
  color: white;
}

.reservation-item.past {
  background-color: #909399;
  color: white;
}

.reservation-item.cancelled {
  background-color: #e6a23c;
  color: white;
}

.reservation-item.missed {
  background-color: #f56c6c;
  color: white;
}

.reservation-content {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 时间线视图样式 */
.timeline-view {
  border: 1px solid #dcdfe6;
}

.timeline-header {
  display: flex;
  border-bottom: 2px solid #dcdfe6;
  background-color: #f5f7fa;
}

.time-column {
  width: 80px;
  padding: 12px;
  font-weight: 600;
  border-right: 1px solid #dcdfe6;
}

.days-row {
  flex: 1;
  display: flex;
}

.day-column {
  flex: 1;
  text-align: center;
  padding: 8px;
  border-right: 1px solid #dcdfe6;
}

.day-column:last-child {
  border-right: none;
}

.day-column.today {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}

.day-name {
  font-size: 14px;
  margin-bottom: 4px;
}

.day-date {
  font-size: 18px;
  font-weight: 600;
}

.timeline-body {
  max-height: 600px;
  overflow-y: auto;
}

.hour-row {
  display: flex;
  height: 60px;
  border-bottom: 1px solid #ebeef5;
}

.time-label {
  width: 80px;
  padding: 4px 12px;
  font-size: 12px;
  color: #909399;
  border-right: 1px solid #dcdfe6;
}

.days-grid {
  flex: 1;
  display: flex;
}

.day-cell {
  flex: 1;
  position: relative;
  border-right: 1px solid #ebeef5;
}

.day-cell:last-child {
  border-right: none;
}

.reservation-block {
  position: absolute;
  left: 2px;
  right: 2px;
  border-radius: 4px;
  padding: 4px;
  font-size: 12px;
  cursor: pointer;
  overflow: hidden;
  z-index: 1;
}

.reservation-block:hover {
  opacity: 0.8;
  z-index: 2;
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
