import { createStore, createEvent, createEffect, sample } from 'effector'
import type { User } from '@/types/user'
import api from '@/utils/axios'

// Store states
export const $user = createStore<User | null>(null)
export const $token = createStore<string | null>(localStorage.getItem('token'))
export const $isAuthenticated = createStore<boolean>(!!localStorage.getItem('token'))
export const $isAdmin = createStore<boolean>(false)

// Events
export const setUser = createEvent<User | null>()
export const setToken = createEvent<string>()
export const logout = createEvent()

// Effects
export const loginFx = createEffect(async (data: { email: string; password: string }) => {
  const response = await api.post('/api/auth/login', data)
  setToken(response.data.token)
  setUser(response.data.user)
  return response.data
})

export const checkAuthFx = createEffect(async () => {
  const token = localStorage.getItem('token')
  if (!token) return null

  try {
    // Set token for API calls
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    
    // Get user data
    const response = await api.get('/api/auth/me')
    
    // Update stores
    setUser(response.data)
    setToken(token)
    
    return token
  } catch (error) {
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
    return null
  }
})

// Store updates
$user.on(setUser, (_, user: User | null) => user)
$token.on(setToken, (_, token: string) => {
  localStorage.setItem('token', token)
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  return token
})

$user.on(logout, () => null)
$token.on(logout, () => {
  localStorage.removeItem('token')
  delete api.defaults.headers.common['Authorization']
  return null
})

// Update authentication status
$isAuthenticated.on(setToken, () => true)
$isAuthenticated.on(logout, () => false)

// Update admin status based on user role
$isAdmin.on(setUser, (_, user: User | null) => {
  console.log('User updated:', user)
  return user?.is_admin || false
})
$isAdmin.on(logout, () => false)

// Initialize auth state
checkAuthFx()

// Initialize user from localStorage token if available
if (localStorage.getItem('token')) {
  // You might want to fetch the user data here using the token
  // For now, we'll just set isAuthenticated to true
  $isAuthenticated.setState(true)
} 