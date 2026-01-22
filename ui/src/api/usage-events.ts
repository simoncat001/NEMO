import request from '@/utils/request'
import type { UsageEvent, ApiResponse } from '@/types'

// ==================== 使用事件管理 ====================

/**
 * 获取使用记录列表
 */
export const getUsageEvents = (params?: {
    tool_id?: number
    user_id?: number
    operator_id?: number
    project_id?: number
    validated?: boolean
    start_date?: string
    end_date?: string
    skip?: number
    limit?: number
}) => {
    return request.get<ApiResponse<UsageEvent[]>>('/usage-events', { params })
}

/**
 * 创建使用记录
 */
export const createUsageEvent = (data: Partial<UsageEvent>) => {
    return request.post<ApiResponse<UsageEvent>>('/usage-events', data)
}

/**
 * 获取使用记录详情
 */
export const getUsageEvent = (eventId: number) => {
    return request.get<ApiResponse<UsageEvent>>(`/usage-events/${eventId}`)
}

/**
 * 结束使用记录
 */
export const endUsageEvent = (eventId: number, data?: { run_data?: string }) => {
    return request.post<ApiResponse<UsageEvent>>(`/usage-events/${eventId}/end`, data || {})
}

/**
 * 更新使用记录
 */
export const updateUsageEvent = (eventId: number, data: Partial<UsageEvent>) => {
    return request.put<ApiResponse<UsageEvent>>(`/usage-events/${eventId}`, data)
}

/**
 * 删除使用记录
 */
export const deleteUsageEvent = (eventId: number) => {
    return request.delete(`/usage-events/${eventId}`)
}

// ==================== 活动查询 ====================

/**
 * 获取工具的活动使用记录
 */
export const getToolActiveUsage = (toolId: number) => {
    return request.get<ApiResponse<UsageEvent>>(`/usage-events/tool/${toolId}/active`)
}

/**
 * 获取用户的活动使用记录
 */
export const getUserActiveUsages = (userId: number) => {
    return request.get<ApiResponse<UsageEvent[]>>(`/usage-events/user/${userId}/active`)
}

// ==================== 验证与豁免 ====================

/**
 * 验证使用记录
 */
export const validateUsageEvent = (eventId: number) => {
    return request.post<ApiResponse<UsageEvent>>(`/usage-events/${eventId}/validate`)
}

/**
 * 豁免使用记录
 */
export const waiveUsageEvent = (eventId: number) => {
    return request.post<ApiResponse<UsageEvent>>(`/usage-events/${eventId}/waive`)
}

/**
 * 重新激活（取消豁免）使用记录
 */
export const reactivateUsageEvent = (eventId: number) => {
    return request.post<ApiResponse<UsageEvent>>(`/usage-events/${eventId}/reactivate`)
}

// ==================== 统计 ====================

/**
 * 获取使用统计
 */
export const getUsageEventStats = (params?: {
    tool_id?: number
    user_id?: number
    start_date?: string
    end_date?: string
}) => {
    return request.get<ApiResponse<{
        total_count: number
        total_duration_minutes: number
        validated_count: number
        pending_count: number
    }>>('/usage-events/stats', { params })
}
