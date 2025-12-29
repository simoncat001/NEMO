import request from '@/utils/request'
import type { Task, TaskCategory, ApiResponse } from '@/types'

// ==================== 任务分类管理 ====================

/**
 * 获取任务分类列表
 */
export const getTaskCategories = () => {
    return request.get<ApiResponse<TaskCategory[]>>('/task-categories')
}

/**
 * 创建任务分类
 */
export const createTaskCategory = (data: Partial<TaskCategory>) => {
    return request.post<ApiResponse<TaskCategory>>('/task-categories', data)
}

/**
 * 获取任务分类详情
 */
export const getTaskCategory = (categoryId: number) => {
    return request.get<ApiResponse<TaskCategory>>(`/task-categories/${categoryId}`)
}

/**
 * 更新任务分类
 */
export const updateTaskCategory = (categoryId: number, data: Partial<TaskCategory>) => {
    return request.put<ApiResponse<TaskCategory>>(`/task-categories/${categoryId}`, data)
}

/**
 * 删除任务分类
 */
export const deleteTaskCategory = (categoryId: number) => {
    return request.delete(`/task-categories/${categoryId}`)
}

// ==================== 任务管理 ====================

/**
 * 获取任务列表
 */
export const getTasks = (params?: {
    resolved?: boolean
    cancelled?: boolean
    urgency?: string
    category_id?: number
    tool_id?: number
    creator_id?: number
    skip?: number
    limit?: number
}) => {
    return request.get<ApiResponse<Task[]>>('/tasks', { params })
}

/**
 * 创建任务
 */
export const createTask = (data: Partial<Task>) => {
    return request.post<ApiResponse<Task>>('/tasks', data)
}

/**
 * 获取任务详情
 */
export const getTask = (taskId: number) => {
    return request.get<ApiResponse<Task>>(`/tasks/${taskId}`)
}

/**
 * 更新任务
 */
export const updateTask = (taskId: number, data: Partial<Task>) => {
    return request.put<ApiResponse<Task>>(`/tasks/${taskId}`, data)
}

/**
 * 解决任务
 */
export const resolveTask = (taskId: number, data: { resolution_description: string }) => {
    return request.post<ApiResponse<Task>>(`/tasks/${taskId}/resolve`, data)
}

/**
 * 取消任务
 */
export const cancelTask = (taskId: number, data: { resolution_description?: string }) => {
    return request.post<ApiResponse<Task>>(`/tasks/${taskId}/cancel`, data)
}

/**
 * 删除任务
 */
export const deleteTask = (taskId: number) => {
    return request.delete(`/tasks/${taskId}`)
}

// ==================== 任务历史 ====================

/**
 * 获取任务历史
 */
export const getTaskHistory = (taskId: number) => {
    return request.get<ApiResponse<any[]>>(`/tasks/${taskId}/history`)
}

// ==================== 特殊查询 ====================

/**
 * 获取紧急任务列表
 */
export const getUrgentTasks = () => {
    return request.get<ApiResponse<Task[]>>('/tasks/urgent')
}

/**
 * 获取任务统计
 */
export const getTaskStats = (params?: {
    tool_id?: number
    category_id?: number
    days?: number
}) => {
    return request.get<ApiResponse<{
        total_tasks: number
        resolved_tasks: number
        pending_tasks: number
        urgent_tasks: number
    }>>('/tasks/stats', { params })
}
