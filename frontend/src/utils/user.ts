import type { User } from '@/types/user'

export function isProfileComplete(user: User | null): boolean {
  if (!user) return false
  
  return !!(
    user.name &&
    // user.location &&
    // user.workplace &&
    // user.birth_date &&
    user.goals &&
    // user.education &&
    user.phone_number &&
    user.payment_status
  )
} 