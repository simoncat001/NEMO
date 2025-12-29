import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, LoginRequest } from '@/types'
import { login as loginApi, logout as logoutApi, getCurrentUser } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null)
    const token = ref<string>('')
    const isAuthenticated = ref(false)

    // 从 localStorage 恢复状态
    const checkAuth = () => {
        const savedToken = localStorage.getItem('access_token')
        const savedUser = localStorage.getItem('user')

        if (savedToken && savedUser && savedUser !== 'undefined') {
            try {
                token.value = savedToken
                user.value = JSON.parse(savedUser)
                isAuthenticated.value = true
            } catch (e) {
                localStorage.removeItem('access_token')
                localStorage.removeItem('user')
            }
        }
    }

    // 登录
    const login = async (credentials: LoginRequest) => {
        const response = await loginApi(credentials)
        token.value = response.access_token

        if (response.user) {
            user.value = response.user
            localStorage.setItem('user', JSON.stringify(response.user))
        } else {
            // Fallback: fetch user if not provided in login response
            const userData = await getCurrentUser()
            user.value = userData
            localStorage.setItem('user', JSON.stringify(userData))
        }

        isAuthenticated.value = true
        localStorage.setItem('access_token', response.access_token)

        return response
    }

    // 登出
    const logout = async () => {
        try {
            await logoutApi()
        } finally {
            token.value = ''
            user.value = null
            isAuthenticated.value = false

            // 清除 localStorage
            localStorage.removeItem('access_token')
            localStorage.removeItem('user')
        }
    }

    // 刷新用户信息
    const refreshUser = async () => {
        const userData = await getCurrentUser()
        user.value = userData
        localStorage.setItem('user', JSON.stringify(userData))
    }

    // 权限检查
    const hasPermission = (_permission: string): boolean => {
        if (!user.value) return false
        if (user.value.is_superuser) return true
        // 这里可以根据实际权限系统扩展
        return user.value.is_staff
    }

    const isStaff = (): boolean => {
        return user.value?.is_staff || false
    }

    const isSuperuser = (): boolean => {
        return user.value?.is_superuser || false
    }

    return {
        user,
        token,
        isAuthenticated,
        checkAuth,
        login,
        logout,
        refreshUser,
        hasPermission,
        isStaff,
        isSuperuser,
    }
})
