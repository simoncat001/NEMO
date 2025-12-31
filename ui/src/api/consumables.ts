import request from '@/utils/request'
import type { Consumable, ConsumableWithdraw, PaginationParams } from '@/types'

// 获取耗材列表
export function getConsumables(params?: PaginationParams): Promise<Consumable[]> {
    return request({
        url: '/consumables',
        method: 'get',
        params,
    })
}

// 获取耗材详情
export function getConsumable(id: number): Promise<Consumable> {
    return request({
        url: `/consumables/${id}`,
        method: 'get',
    })
}

// 创建耗材
export function createConsumable(data: Partial<Consumable>): Promise<Consumable> {
    return request({
        url: '/consumables',
        method: 'post',
        data,
    })
}

// 更新耗材
export function updateConsumable(id: number, data: Partial<Consumable>): Promise<Consumable> {
    return request({
        url: `/consumables/${id}`,
        method: 'put',
        data,
    })
}

// 删除耗材
export function deleteConsumable(id: number): Promise<void> {
    return request({
        url: `/consumables/${id}`,
        method: 'delete',
    })
}

// 获取耗材领用记录
export function getConsumableWithdraws(params?: PaginationParams): Promise<ConsumableWithdraw[]> {
    return request({
        url: '/consumables/withdraws',
        method: 'get',
        params,
    })
}

// 领用耗材
export function withdrawConsumable(data: Partial<ConsumableWithdraw>): Promise<ConsumableWithdraw> {
    return request({
        url: '/consumables/withdraw',
        method: 'post',
        data,
    })
}
