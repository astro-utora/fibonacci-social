import type { Store } from 'effector'
import type { User } from '@/types/user'

declare module '@/stores/auth' {
  export const $user: Store<User | null>
  export const $token: Store<string | null>
  export const $isAuthenticated: Store<boolean>
  export const $isAdmin: Store<boolean>
  
  export const setUser: (user: User) => void
  export const setToken: (token: string) => void
  export const logout: () => void
  export const checkAuthFx: () => Promise<string | null>
} 