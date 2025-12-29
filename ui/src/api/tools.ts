import request from '@/utils/request'
import type { Tool, PaginationParams } from '@/types'

// 获取工具列表
export function getTools(params?: PaginationParams): Promise<Tool[]> {
    return request({
        url: '/tools',
        method: 'get',
        params,
    })
}

// 获取工具详情
export function getTool(id: number): Promise<Tool> {
    return request({
        url: `/tools/${id}`,
        method: 'get',
    })
}

// 创建工具
export function createTool(data: Partial<Tool>): Promise<Tool> {
    return request({
        url: '/tools',
        method: 'post',
        data,
    })
}

// 更新工具
export function updateTool(id: number, data: Partial<Tool>): Promise<Tool> {
    return request({
        url: `/tools/${id}`,
        method: 'put',
        data,
    })
}

// 删除工具
export function deleteTool(id: number): Promise<void> {
    return request({
        url: `/tools/${id}`,
        method: 'delete',
    })
}
