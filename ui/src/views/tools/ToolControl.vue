<template>
    <div class="tool-control-container">
        <el-row :gutter="20">
            <!-- 左侧工具列表 -->
            <el-col :span="6">
                <el-card class="tool-list-card">
                    <template #header>
                        <div class="card-header">
                            <span>工具列表</span>
                            <el-input
                                v-model="searchQuery"
                                placeholder="搜索工具..."
                                prefix-icon="Search"
                                clearable
                                class="search-input"
                            />
                        </div>
                    </template>
                    <div class="tool-list">
                        <div
                            v-for="tool in filteredTools"
                            :key="tool.id"
                            class="tool-item"
                            :class="{ active: selectedTool?.id === tool.id }"
                            @click="selectTool(tool)"
                        >
                            <div class="tool-name">{{ tool.name }}</div>
                            <div class="tool-status">
                                <el-tag size="small" :type="tool.operational ? 'success' : 'danger'">
                                    {{ tool.operational ? '正常' : '维护中' }}
                                </el-tag>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>

            <!-- 右侧控制面板 -->
            <el-col :span="18">
                <el-card v-if="selectedTool" class="control-panel-card">
                    <template #header>
                        <div class="panel-header">
                            <h2>{{ selectedTool.name }}</h2>
                            <el-tag :type="isToolInUse ? 'warning' : 'success'" size="large">
                                {{ isToolInUse ? '使用中' : '空闲' }}
                            </el-tag>
                        </div>
                    </template>

                    <div class="tool-info">
                        <el-descriptions :column="2" border>
                            <el-descriptions-item label="位置">{{ selectedTool.location || '未设置' }}</el-descriptions-item>
                            <el-descriptions-item label="联系电话">{{ selectedTool.phone_number || '未设置' }}</el-descriptions-item>
                            <el-descriptions-item label="描述" :span="2">{{ selectedTool.description || '暂无描述' }}</el-descriptions-item>
                        </el-descriptions>
                    </div>

                    <div class="control-actions">
                        <div v-if="!isToolInUse" class="enable-section">
                            <h3>开始使用</h3>
                            <el-form :model="enableForm" label-width="100px">
                                <el-form-item label="项目">
                                    <el-select v-model="enableForm.project_id" placeholder="请选择项目" style="width: 100%">
                                        <el-option
                                            v-for="project in projects"
                                            :key="project.id"
                                            :label="project.name"
                                            :value="project.id"
                                        />
                                    </el-select>
                                </el-form-item>
                                <el-form-item label="备注">
                                    <el-input v-model="enableForm.note" type="textarea" rows="3" />
                                </el-form-item>
                                <el-form-item>
                                    <el-button type="primary" @click="handleEnableTool" :loading="loading">
                                        启用仪器
                                    </el-button>
                                </el-form-item>
                            </el-form>
                        </div>

                        <div v-else class="disable-section">
                            <h3>结束使用</h3>
                            <el-form :model="disableForm" label-width="100px">
                                <el-form-item label="备注">
                                    <el-input v-model="disableForm.note" type="textarea" rows="3" />
                                </el-form-item>
                                <el-form-item>
                                    <el-button type="danger" @click="handleDisableTool" :loading="loading">
                                        结束使用
                                    </el-button>
                                </el-form-item>
                            </el-form>
                        </div>
                    </div>
                </el-card>
                <el-empty v-else description="请选择一个工具" />
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getTools, getToolStatus, enableTool, disableTool } from '@/api/tools'
import { getProjects } from '@/api/projects'
import { getCurrentUser } from '@/api/users'
import type { Tool, Project, User } from '@/types'

const tools = ref<Tool[]>([])
const projects = ref<Project[]>([])
const currentUser = ref<User | null>(null)
const selectedTool = ref<Tool | null>(null)
const searchQuery = ref('')
const isToolInUse = ref(false)
const loading = ref(false)

const enableForm = ref({
    project_id: undefined as number | undefined,
    note: ''
})

const disableForm = ref({
    note: ''
})

// 过滤工具列表
const filteredTools = computed(() => {
    if (!searchQuery.value) return tools.value
    const query = searchQuery.value.toLowerCase()
    return tools.value.filter(tool => 
        tool.name.toLowerCase().includes(query) || 
        (tool.description && tool.description.toLowerCase().includes(query))
    )
})

// 初始化数据
onMounted(async () => {
    try {
        const [toolsRes, userRes, projectsRes] = await Promise.all([
            getTools({ limit: 1000, visible_only: true }),
            getCurrentUser(),
            getProjects({ active: true })
        ])
        tools.value = toolsRes
        currentUser.value = userRes
        projects.value = projectsRes
    } catch (error) {
        console.error('Failed to load initial data:', error)
        ElMessage.error('加载数据失败')
    }
})

// 选择工具
const selectTool = async (tool: Tool) => {
    selectedTool.value = tool
    await checkToolStatus()
}

// 检查工具状态
const checkToolStatus = async () => {
    if (!selectedTool.value) return
    try {
        isToolInUse.value = await getToolStatus(selectedTool.value.id)
    } catch (error) {
        console.error('Failed to check tool status:', error)
    }
}

// 启用工具
const handleEnableTool = async () => {
    if (!selectedTool.value || !currentUser.value) return
    if (!enableForm.value.project_id) {
        ElMessage.warning('请选择项目')
        return
    }

    loading.value = true
    try {
        await enableTool(selectedTool.value.id, {
            user_id: currentUser.value.id,
            project_id: enableForm.value.project_id,
            note: enableForm.value.note
        })
        ElMessage.success('仪器已启用')
        enableForm.value.note = '' // 清空备注
        await checkToolStatus()
    } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '启用失败')
    } finally {
        loading.value = false
    }
}

// 禁用工具
const handleDisableTool = async () => {
    if (!selectedTool.value) return

    loading.value = true
    try {
        await disableTool(selectedTool.value.id, {
            note: disableForm.value.note
        })
        ElMessage.success('仪器使用已结束')
        disableForm.value.note = '' // 清空备注
        await checkToolStatus()
    } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.tool-control-container {
    padding: 20px;
    height: calc(100vh - 84px);
}

.tool-list-card {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.tool-list-card :deep(.el-card__body) {
    flex: 1;
    overflow-y: auto;
    padding: 0;
}

.card-header {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.search-input {
    width: 100%;
}

.tool-list {
    display: flex;
    flex-direction: column;
}

.tool-item {
    padding: 15px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    transition: background-color 0.3s;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.tool-item:hover {
    background-color: #f5f7fa;
}

.tool-item.active {
    background-color: #e6f7ff;
    border-right: 3px solid #409eff;
}

.tool-name {
    font-weight: 500;
}

.control-panel-card {
    height: 100%;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.tool-info {
    margin-bottom: 30px;
}

.control-actions {
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 4px;
}

.enable-section, .disable-section {
    max-width: 600px;
    margin: 0 auto;
}

h3 {
    margin-bottom: 20px;
    color: #303133;
    text-align: center;
}
</style>
