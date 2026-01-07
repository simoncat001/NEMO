import request from '@/utils/request'
import type { Bill, BillGenerationRequest, PaginationParams } from '@/types'

// ==================== 账单管理 ====================

/**
 * 获取账单列表
 */
export const getBills = (params: PaginationParams & { account_id?: number }) => {
    return request.get<Bill[]>('/billing/', { params })
}

/**
 * 生成账单
 */
export const generateBills = (data: BillGenerationRequest) => {
    return request.post<Bill[]>('/billing/generate', data)
}
