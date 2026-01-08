import request from '@/utils/request'

export interface DashboardResponse {
  stats: {
    total_tools: number
    today_reservations: number
    active_tasks: number
    active_users: number
  }
  recent_reservations: Array<{
    tool_name?: string | null
    start: string
    end: string
  }>
  pending_tasks: Array<{
    tool_name?: string | null
    problem_description?: string | null
    urgency: number
  }>
}

export const getDashboard = () => {
  return request.get<DashboardResponse>('/dashboard/')
}
