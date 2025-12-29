<template>
  <div class="page-container">
    <!-- 用户基本信息卡片 -->
    <el-card class="profile-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><User /></el-icon>
            个人资料
          </span>
          <el-button type="primary" :icon="Edit" @click="editDialogVisible = true">
            编辑资料
          </el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <div class="avatar-container">
            <el-avatar :size="120" :icon="UserFilled">
              {{ userInfo.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="username">{{ userInfo.username }}</div>
            <el-tag v-if="userInfo.is_staff" type="success" class="role-tag">
              管理员
            </el-tag>
            <el-tag v-else type="info" class="role-tag">
              普通用户
            </el-tag>
          </div>
        </el-col>
        <el-col :span="18">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户ID">
              {{ userInfo.id }}
            </el-descriptions-item>
            <el-descriptions-item label="用户名">
              {{ userInfo.username }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ userInfo.email }}
            </el-descriptions-item>
            <el-descriptions-item label="电话">
              {{ userInfo.phone || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="姓">
              {{ userInfo.last_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="名">
              {{ userInfo.first_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="工牌号">
              {{ userInfo.badge_number || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="账户状态">
              <el-tag :type="userInfo.is_active ? 'success' : 'danger'">
                {{ userInfo.is_active ? '激活' : '停用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">
              {{ formatDateTime(userInfo.date_joined) }}
            </el-descriptions-item>
            <el-descriptions-item label="最后登录">
              {{ formatDateTime(userInfo.last_login) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="我的预约" :value="stats.reservations">
            <template #prefix>
              <el-icon color="#409EFF"><Calendar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="使用记录" :value="stats.usageEvents">
            <template #prefix>
              <el-icon color="#67C23A"><Clock /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="创建任务" :value="stats.tasks">
            <template #prefix>
              <el-icon color="#E6A23C"><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card class="actions-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Setting /></el-icon>
            快捷操作
          </span>
        </div>
      </template>

      <el-space :size="20" wrap>
        <el-button type="primary" :icon="Lock" @click="passwordDialogVisible = true">
          修改密码
        </el-button>
        <el-button type="success" :icon="Calendar" @click="goToReservations">
          我的预约
        </el-button>
        <el-button type="warning" :icon="Clock" @click="goToUsageEvents">
          使用记录
        </el-button>
        <el-button type="info" :icon="Document" @click="goToTasks">
          我的任务
        </el-button>
      </el-space>
    </el-card>

    <!-- 最近活动 -->
    <el-card class="activity-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Timer /></el-icon>
            最近活动
          </span>
          <el-button :icon="Refresh" @click="loadUserStats">
            刷新
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="最近预约" name="reservations">
          <el-table :data="recentReservations" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="工具" min-width="150">
              <template #default="{ row }">
                {{ row.tool?.name || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="开始时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.start) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.cancelled" type="warning">已取消</el-tag>
                <el-tag v-else type="success">正常</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="使用历史" name="usageEvents">
          <el-table :data="recentUsageEvents" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="工具" min-width="150">
              <template #default="{ row }">
                {{ row.tool?.name || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="开始时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.start) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.validated" type="success">已验证</el-tag>
                <el-tag v-else type="warning">待验证</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="我的任务" name="tasks">
          <el-table :data="recentTasks" stripe>
            <el-table-column prop="id" label="ID" width="80" />
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
                <el-tag v-if="row.resolved" type="success">已解决</el-tag>
                <el-tag v-else type="warning">处理中</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 编辑资料对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑个人资料"
      width="600px"
      @close="resetEditForm"
    >
      <el-form
        ref="editFormRef"
        :model="editFormData"
        :rules="editFormRules"
        label-width="100px"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editFormData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="editFormData.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓">
              <el-input v-model="editFormData.last_name" placeholder="请输入姓" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名">
              <el-input v-model="editFormData.first_name" placeholder="请输入名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="工牌号">
          <el-input-number
            v-model="editFormData.badge_number"
            :min="0"
            placeholder="请输入工牌号"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleUpdateProfile">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="500px"
      @close="resetPasswordForm"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordFormData"
        :rules="passwordFormRules"
        label-width="100px"
      >
        <el-form-item label="旧密码" prop="old_password">
          <el-input
            v-model="passwordFormData.old_password"
            type="password"
            placeholder="请输入旧密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordFormData.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordFormData.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleChangePassword">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  User,
  UserFilled,
  Edit,
  Lock,
  Calendar,
  Clock,
  Document,
  Setting,
  Timer,
  Refresh
} from '@element-plus/icons-vue'
import { getCurrentUser, updateCurrentUser, changePassword } from '@/api/users'
import type { User as UserType, Reservation, UsageEvent, Task } from '@/types'
import { formatDateTime } from '@/utils/helpers'

const router = useRouter()

// 用户信息
const userInfo = ref<Partial<UserType>>({})

// 统计数据
const stats = reactive({
  reservations: 0,
  usageEvents: 0,
  tasks: 0
})

// 最近活动
const activeTab = ref('reservations')
const recentReservations = ref<Reservation[]>([])
const recentUsageEvents = ref<UsageEvent[]>([])
const recentTasks = ref<Task[]>([])

// 对话框
const editDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const submitting = ref(false)

// 编辑资料表单
const editFormRef = ref<FormInstance>()
const editFormData = reactive<Partial<UserType>>({
  email: '',
  phone: '',
  first_name: '',
  last_name: '',
  badge_number: undefined
})

const editFormRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 修改密码表单
const passwordFormRef = ref<FormInstance>()
const passwordFormData = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordFormRules: FormRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: any, callback: any) => {
        if (value !== passwordFormData.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    // 如果后端没有 /users/me 端点，可以从 localStorage 或 auth store 获取
    const response = await getCurrentUser()
    userInfo.value = response
    
    // 填充编辑表单
    Object.assign(editFormData, {
      email: response.email,
      phone: response.phone,
      first_name: response.first_name,
      last_name: response.last_name,
      badge_number: response.badge_number
    })
  } catch (error) {
    // 如果接口不存在，从本地存储获取
    const userStr = localStorage.getItem('user')
    if (userStr) {
      userInfo.value = JSON.parse(userStr)
      Object.assign(editFormData, userInfo.value)
    }
    console.error('加载用户信息失败:', error)
  }
}

// 加载用户统计
const loadUserStats = async () => {
  try {
    // 这里需要调用多个 API 获取统计数据
    // 为简化，先使用模拟数据
    stats.reservations = 15
    stats.usageEvents = 32
    stats.tasks = 8
    
    // 模拟最近活动数据
    recentReservations.value = []
    recentUsageEvents.value = []
    recentTasks.value = []
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 更新个人资料
const handleUpdateProfile = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid: any) => {
    if (!valid) return

    submitting.value = true
    try {
      await updateCurrentUser(editFormData)
      ElMessage.success('个人资料更新成功')
      editDialogVisible.value = false
      await loadUserInfo()
    } catch (error) {
      ElMessage.error('更新失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid: any) => {
    if (!valid) return

    submitting.value = true
    try {
      await changePassword({
        old_password: passwordFormData.old_password,
        new_password: passwordFormData.new_password
      })
      ElMessage.success('密码修改成功，请重新登录')
      passwordDialogVisible.value = false
      
      // 清除登录信息并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    } catch (error) {
      ElMessage.error('密码修改失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 重置编辑表单
const resetEditForm = () => {
  editFormRef.value?.resetFields()
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordFormRef.value?.resetFields()
  Object.assign(passwordFormData, {
    old_password: '',
    new_password: '',
    confirm_password: ''
  })
}

// 快捷跳转
const goToReservations = () => {
  router.push('/reservations')
}

const goToUsageEvents = () => {
  router.push('/usage-events')
}

const goToTasks = () => {
  router.push('/tasks')
}

// 初始化
onMounted(async () => {
  await loadUserInfo()
  await loadUserStats()
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

.profile-card {
  margin-bottom: 16px;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 18px;
  font-weight: 600;
}

.role-tag {
  margin-top: 4px;
}

.stats-row {
  margin-bottom: 16px;
}

.actions-card,
.activity-card {
  margin-top: 16px;
}
</style>
