import {
    createRouter,
    createWebHistory,
    type NavigationGuardNext,
    type RouteLocationNormalized,
    type RouteRecordRaw,
} from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Layout from '@/components/layout/Layout.vue'

const routes: RouteRecordRaw[] = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/auth/Login.vue'),
        meta: { requiresAuth: false, title: '登录' },
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/auth/Register.vue'),
        meta: { requiresAuth: false, title: '注册' },
    },
    {
        path: '/',
        component: Layout,
        redirect: '/dashboard',
        meta: { requiresAuth: true },
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/dashboard/Dashboard.vue'),
                meta: { title: '仪表盘' },
            },
            // 用户管理
            {
                path: 'users',
                name: 'UserList',
                component: () => import('@/views/user/UserList.vue'),
                meta: { title: '用户列表', requiresStaff: true },
            },
            // 仪器管理
            {
                path: 'tools',
                name: 'Tools',
                component: () => import('@/views/tools/ToolList.vue'),
                meta: { title: '仪器列表', requiresStaff: true },
            },
            {
                path: 'tool-control',
                name: 'ToolControl',
                component: () => import('@/views/tools/ToolControl.vue'),
                meta: { title: '仪器控制' },
            },
            {
                path: 'tools/:id',
                name: 'ToolDetail',
                component: () => import('@/views/tools/ToolDetail.vue'),
                meta: { title: '仪器详情' },
            },
            // 预约管理
            {
                path: 'reservations',
                name: 'Reservations',
                component: () => import('@/views/reservations/ReservationList.vue'),
                meta: { title: '预约列表', requiresVerified: true },
            },
            {
                path: 'calendar',
                name: 'Calendar',
                component: () => import('@/views/reservations/Calendar.vue'),
                meta: { title: '预约日历', requiresVerified: true },
            },
            {
                path: 'billing',
                name: 'Billing',
                component: () => import('@/views/billing/BillList.vue'),
                meta: { title: '账单管理', requiresStaff: true },
            },
            {
                path: 'billing/:id',
                name: 'BillDetail',
                component: () => import('@/views/billing/BillDetail.vue'),
                meta: { title: '账单详情', requiresStaff: true },
            },
            // 使用记录
            {
                path: 'usage-events',
                name: 'UsageEvents',
                component: () => import('@/views/usage-events/UsageEventList.vue'),
                meta: { title: '使用记录' },
            },
            // 任务管理
            {
                path: 'tasks',
                name: 'Tasks',
                component: () => import('@/views/tasks/TaskList.vue'),
                meta: { title: '任务列表' },
            },
            {
                path: 'tasks/:id',
                name: 'TaskDetail',
                component: () => import('@/views/tasks/TaskDetail.vue'),
                meta: { title: '任务详情' },
            },
            // 员工收费
            {
                path: 'staff-charges',
                name: 'StaffCharges',
                component: () => import('@/views/staff-charges/StaffChargeList.vue'),
                meta: { title: '员工收费', requiresStaff: true },
            },
            // 耗材管理
            {
                path: 'consumables',
                name: 'Consumables',
                component: () => import('@/views/consumables/ConsumableList.vue'),
                meta: { title: '耗材管理' },
            },
            // 配置管理
            {
                path: 'configurations',
                name: 'Configurations',
                component: () => import('@/views/configurations/ConfigurationList.vue'),
                meta: { title: '配置管理', requiresStaff: true },
            },
            // 用户设置
            {
                path: 'profile',
                name: 'Profile',
                component: () => import('@/views/user/Profile.vue'),
                meta: { title: '个人资料' },
            },
        ],
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/error/NotFound.vue'),
        meta: { requiresAuth: false, title: '404' },
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// 路由守卫
router.beforeEach(
    (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
        const authStore = useAuthStore()

        // 设置页面标题
        document.title = to.meta.title
            ? `${to.meta.title} - NEMO`
            : 'NEMO - Laboratory Management System'

        // 检查是否需要认证
        if (to.meta.requiresAuth !== false) {
            if (!authStore.isAuthenticated) {
                next({ name: 'Login', query: { redirect: to.fullPath } })
                return
            }

            // 检查是否需要管理员权限
            if (to.meta.requiresStaff && !authStore.isStaff()) {
                next({ name: 'Dashboard' })
                return
            }

            // 检查是否需要已验证（仅对普通用户）
            if ((to.meta as any).requiresVerified) {
                if (!authStore.canAccessReservations()) {
                    next({ name: 'Dashboard' })
                    return
                }
            }
        }

        // 已登录用户访问登录页，跳转到首页
        if (to.name === 'Login' && authStore.isAuthenticated) {
            next({ name: 'Dashboard' })
            return
        }

        next()
    }
)

export default router
