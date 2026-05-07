export interface User {
    uuid: string
    name: string | null
    location: string | null
    workplace: string | null
    role: string | null
    birth_date: string | null
    goals: string | null
    education: string | null
    phone_number: string | null
    avatar_url: string | null
    referral_code: string
    is_admin?: boolean
    willing_to_contribute?: boolean | null
    payment_status?: string | null
    credits?: number
}

export interface UserProfile {
    name: string
    location: string
    workplace: string
    role: string
    birth_date: string
    goals: string
    education: string
    phone_number: string
    avatar_url?: string
} 