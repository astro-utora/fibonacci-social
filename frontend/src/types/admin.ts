export interface AdminSetting {
    id: number
    key: string
    value: string
    description: string | null
    created_at: string
    updated_at: string | null
}

export interface AdminSettingUpdate {
    value: string
    description?: string
} 