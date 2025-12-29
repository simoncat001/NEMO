import axios, { AxiosInstance, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/v1',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// 请求拦截器
service.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // 添加 token
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers = config.headers || {}
                ; (config.headers as any).Authorization = `Bearer ${token}`
        }
        return config
    },
    (error: AxiosError) => {
        console.error('Request error:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    (response: AxiosResponse) => {
        return response.data
    },
    (error: AxiosError) => {
        console.error('Response error:', error)

        if (error.response) {
            switch (error.response.status) {
                case 401:
                    // 未授权，跳转登录页
                    ElMessage.error('登录已过期，请重新登录')
                    localStorage.removeItem('access_token')
                    localStorage.removeItem('user')
                    router.push('/login')
                    break
                case 403:
                    ElMessage.error('没有权限访问该资源')
                    break
                case 404:
                    ElMessage.error('请求的资源不存在')
                    break
                case 500:
                    ElMessage.error('服务器内部错误')
                    break
                default:
                    ElMessage.error((error.response.data as any)?.detail || '请求失败')
            }
        } else if (error.request) {
            ElMessage.error('网络连接失败，请检查网络')
        } else {
            ElMessage.error('请求配置错误')
        }

        return Promise.reject(error)
    }
)

export default service
