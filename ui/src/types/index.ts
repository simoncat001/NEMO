// ==================== User Types ====================
export interface User {
    id: number
    username: string
    email: string
    first_name: string
    last_name: string
    is_active: boolean
    is_staff: boolean
    is_superuser: boolean
    badge_number?: number
    phone?: string
    date_joined: string
    last_login?: string
}

// ==================== Auth Types ====================
export interface LoginRequest {
    username: string
    password: string
}

export interface LoginResponse {
    access_token: string
    token_type: string
    user: User
}

// ==================== Tool Types ====================
export interface Tool {
    id: number
    name: string
    visible: boolean
    operational: boolean
    location?: string
    phone_number?: string
    description?: string
    serial?: string
    category?: string
    requires_reservation?: boolean
    created_at?: string
}

export interface ToolEnableRequest {
    user_id: number
    project_id: number
    operator_id?: number
    note?: string
}

export interface ToolDisableRequest {
    note?: string
    run_data?: string
}

// ==================== Project Types ====================
export interface Project {
    id: number
    name: string
    account_id: number
    application_identifier?: string
    start_date?: string
    end_date?: string
    active: boolean
}

// ==================== Reservation Types ====================
export interface Reservation {
    id: number
    user_id: number
    tool_id?: number
    area_id?: number
    project_id: number
    start: string
    end: string
    cancelled: boolean
    missed: boolean
    additional_information?: string
    self_configuration: boolean
    created_at?: string
    // 关联对象
    user?: User
    tool?: Tool
    project?: Project
    area?: Area
}

export interface Area {
    id: number
    name: string
    category?: string
}

// ==================== Account Types ====================
export interface Account {
    id: number
    name: string
    active: boolean
    type_id?: number
    start_date?: string
    note?: string
}

export interface AccountType {
    id: number
    name: string
}

// ==================== UsageEvent Types ====================
export interface UsageEvent {
    id: number
    tool_id: number
    user_id: number
    operator_id: number
    project_id: number
    start: string
    end?: string
    validated: boolean
    validated_by_id?: number
    waived: boolean
    waived_by_id?: number
    waived_on?: string
    note?: string
    amount?: number
    // 关联对象
    user?: User
    tool?: Tool
    project?: Project
}

// ==================== Consumable Types ====================
export interface Consumable {
    id: number
    name: string
    quantity: number
    reminder_threshold?: number
    category?: string
}

export interface ConsumableWithdraw {
    id: number
    consumable_id: number
    user_id: number
    quantity: number
    date: string
    project_id?: number
    merchant_id?: number
    consumable?: Consumable
    user?: User
}

// ==================== Task Types ====================
export interface Task {
    id: number
    tool_id?: number
    urgency: TaskUrgency | string
    creation_time: string
    creator_id: number
    last_updated: string
    last_updated_by_id?: number
    resolved: boolean
    resolution_time?: string
    resolver_id?: number
    problem_category_id?: number
    problem_description: string
    progress_description?: string
    resolution_description?: string
    status?: string
    created_at?: string
    // 关联对象
    tool?: Tool
    creator?: User
}

export enum TaskUrgency {
    LOW = 'low',
    NORMAL = 'normal',
    HIGH = 'high',
    CRITICAL = 'critical',
}

export interface TaskCategory {
    id: number
    name: string
    stage: TaskCategoryStage
}

export enum TaskCategoryStage {
    INITIAL_ASSESSMENT = 'initial_assessment',
    COMPLETION = 'completion',
    MAINTENANCE = 'maintenance',
}

// ==================== StaffCharge Types ====================
export interface StaffCharge {
    id: number
    staff_member_id: number
    customer_id: number
    project_id: number
    start: string
    end?: string
    validated: boolean
    validated_by_id?: number
    waived: boolean
    waived_by_id?: number
    waived_on?: string
    note?: string
}

// ==================== Configuration Types ====================
export interface Configuration {
    id: number
    name: string
    tool_id: number
    configurable_item_name?: string
    advance_notice_limit: number
    display_order: number
    prompt?: string
    current_settings?: string
    current_setting?: string
    current_setting_color?: string
    available_settings?: string
    calendar_colors?: string
    absence_string?: string
    qualified_users_are_maintainers: boolean
    exclude_from_configuration_agenda: boolean
    enabled: boolean
    // 关联对象
    configuration_options?: ConfigurationOption[]
}

export interface ConfigurationOption {
    id: number
    name: string
    configuration_id?: number
    reservation_id: number
    current_setting?: string
    available_settings?: string
    calendar_colors?: string
    absence_string?: string
}

export interface ConfigurationHistory {
    id: number
    configuration_id: number
    user_id: number
    modification_time: string
    item_name?: string
    slot: number
    setting: string
}

// ==================== Common Types ====================
export interface PaginationParams {
    skip?: number
    limit?: number
}

export interface ApiResponse<T> {
    data: T
    message?: string
    status: number
}

export interface TableColumn {
    prop: string
    label: string
    width?: string | number
    minWidth?: string | number
    fixed?: boolean | 'left' | 'right'
    sortable?: boolean
}
