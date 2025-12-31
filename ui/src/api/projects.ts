import request from '@/utils/request'
import type { Project, ApiResponse } from '@/types'

/**
 * 获取项目列表
 */
export const getProjects = (params?: {
    active?: boolean
    account_id?: number
    skip?: number
    limit?: number
}) => {
    return request.get<Project[]>('/projects', { params })
}

/**
 * 获取项目详情
 */
export const getProject = (id: number) => {
    return request.get<Project>(`/projects/${id}`)
}

/**
 * 创建项目
 */
export const createProject = (data: Partial<Project>) => {
    return request.post<Project>('/projects', data)
}

/**
 * 更新项目
 */
export const updateProject = (id: number, data: Partial<Project>) => {
    return request.put<Project>(`/projects/${id}`, data)
}

/**
 * 删除项目
 */
export const deleteProject = (id: number) => {
    return request.delete(`/projects/${id}`)
}
