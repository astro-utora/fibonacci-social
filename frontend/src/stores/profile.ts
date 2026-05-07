import { createEffect } from 'effector'
import type { User } from '@/types'
import api from '@/utils/axios'
import { $user } from './auth'
import { uploadAvatar } from './user'

export const updateProfile = createEffect(async (data: Partial<User>) => {
  const response = await api.put('/api/users/profile', data)
  $user.setState(response.data.user)
  return response.data
})

// Re-export the uploadAvatar function from user.ts for backward compatibility
export { uploadAvatar } 