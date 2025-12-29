/**
 * 预约管理 API
 */

import request from '@/utils/request'
import type { Reservation } from '@/types'

/**
 * 获取预约列表
 */
export const getReservations = (params?: {
    skip?: number
    limit?: number
    user_id?: number
    tool_id?: number
    start_date?: string
    end_date?: string
}) => {
    return request.get<Reservation[]>('/reservations/', { params })
}

/**
 * 获取单个预约详情
 */
export const getReservation = (id: number) => {
    return request.get<Reservation>(`/reservations/${id}`)
}

/**
 * 创建新预约
 */
export const createReservation = (data: Partial<Reservation>) => {
    return request.post<Reservation>('/reservations/', data)
}

/**
 * 更新预约
 */
export const updateReservation = (id: number, data: Partial<Reservation>) => {
    return request.put<Reservation>(`/reservations/${id}`, data)
}

/**
 * 取消预约
 */
export const cancelReservation = (id: number) => {
    return request.delete(`/reservations/${id}`)
}

/**
 * 获取工具的预约列表
 */
export const getToolReservations = (toolId: number, params?: {
    start_date?: string
    end_date?: string
}) => {
    return request.get<Reservation[]>('/reservations/', {
        params: {
            tool_id: toolId,
            ...params
        }
    })
}

/**
 * 获取用户的预约列表
 */
export const getUserReservations = (userId: number, params?: {
    start_date?: string
    end_date?: string
}) => {
    return request.get<Reservation[]>('/reservations/', {
        params: {
            user_id: userId,
            ...params
        }
    })
}

/**
 * 获取指定日期范围的预约
 */
export const getReservationsByDateRange = (startDate: string, endDate: string, params?: {
    tool_id?: number
    user_id?: number
}) => {
    return request.get<Reservation[]>('/reservations/', {
        params: {
            start_date: startDate,
            end_date: endDate,
            ...params
        }
    })
}

/**
 * 获取预约统计信息
 */
export const getReservationStats = () => {
    // 如果后端没有提供统计端点，前端可以通过获取数据后自行统计
    return request.get<Reservation[]>('/reservations/', { params: { limit: 1000 } })
}
