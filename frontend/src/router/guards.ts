import { $user, $isAuthenticated } from '@/stores/auth'
import type { RouteLocationNormalized, NavigationGuardNext } from 'vue-router'

export function requireAdmin(to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) {
  const user = $user.getState()
  if (!$isAuthenticated.getState()) {
    next('/login')
    return
  }
  
  if (!user?.is_admin) {
    next('/dashboard')
    return
  }
  
  next()
}

export function requireAuth(to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) {
  if (!$isAuthenticated.getState()) {
    next('/login')
    return
  }
  next()
} 