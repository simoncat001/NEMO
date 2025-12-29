import request from '@/utils/request'
import type { Account, AccountType, ApiResponse } from '@/types'

// ==================== 账户类型管理 ====================

/**
 * 获取账户类型列表
 */
export const getAccountTypes = () => {
    return request.get<ApiResponse<AccountType[]>>('/account-types')
}

/**
 * 创建账户类型
 */
export const createAccountType = (data: Partial<AccountType>) => {
    return request.post<ApiResponse<AccountType>>('/account-types', data)
}

/**
 * 获取账户类型详情
 */
export const getAccountType = (typeId: number) => {
    return request.get<ApiResponse<AccountType>>(`/account-types/${typeId}`)
}

/**
 * 更新账户类型
 */
export const updateAccountType = (typeId: number, data: Partial<AccountType>) => {
    return request.put<ApiResponse<AccountType>>(`/account-types/${typeId}`, data)
}

/**
 * 删除账户类型
 */
export const deleteAccountType = (typeId: number) => {
    return request.delete(`/account-types/${typeId}`)
}

// ==================== 账户管理 ====================

/**
 * 获取账户列表
 */
export const getAccounts = (params?: {
    active?: boolean
    type_id?: number
    skip?: number
    limit?: number
}) => {
    return request.get<ApiResponse<Account[]>>('/accounts', { params })
}

/**
 * 创建账户
 */
export const createAccount = (data: Partial<Account>) => {
    return request.post<ApiResponse<Account>>('/accounts', data)
}

/**
 * 获取账户详情
 */
export const getAccount = (accountId: number) => {
    return request.get<ApiResponse<Account>>(`/accounts/${accountId}`)
}

/**
 * 更新账户
 */
export const updateAccount = (accountId: number, data: Partial<Account>) => {
    return request.put<ApiResponse<Account>>(`/accounts/${accountId}`, data)
}

/**
 * 删除账户
 */
export const deleteAccount = (accountId: number) => {
    return request.delete(`/accounts/${accountId}`)
}

/**
 * 激活账户
 */
export const activateAccount = (accountId: number) => {
    return request.post<ApiResponse<Account>>(`/accounts/${accountId}/activate`)
}

/**
 * 停用账户
 */
export const deactivateAccount = (accountId: number) => {
    return request.post<ApiResponse<Account>>(`/accounts/${accountId}/deactivate`)
}
