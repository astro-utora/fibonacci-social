import { createStore, createEvent, createEffect, Store, Event, Effect, sample } from 'effector'
import type { User } from '@/types'
import type { TelegramAuthData } from '@/types/telegram'
import api from '@/utils/axios'

// Add proper types
interface TokenData {
  token: string
}

interface UserResponse {
  user: User
  token: string
}

// Effects with proper typing
export const loginWithTelegramFx = createEffect<TelegramAuthData, UserResponse>()
export const updateProfileFx = createEffect<Partial<User>, { user: User }>()
export const updateAvatarFx = createEffect<File, { avatar_url: string }>()
export const loadUserRolesFx = createEffect<void, string[]>()

// Events
export const setUser = createEvent<User>()
export const setToken = createEvent<string>()
export const logout = createEvent()
export const clearUserRoles = createEvent()

// Stores with proper typing
export const $user = createStore<User | null>(null)
export const $token = createStore<string | null>(null)
export const $users = createStore<User[]>([])
export const $userRoles = createStore<string[]>([])

// Store updates
$user
  .on(setUser, (_: User | null, user: User) => user)
  .on(loginWithTelegramFx.doneData, (_: User | null, { user }: UserResponse) => user)
  .reset(logout)

$token
  .on(setToken, (_: string | null, token: string) => token)
  .on(loginWithTelegramFx.doneData, (_: string | null, { token }: TokenData) => token)
  .reset(logout)

$userRoles
  .on(loadUserRolesFx.doneData, (_: string[], roles: string[]) => roles)
  .reset(clearUserRoles)

// Side effects
logout.watch(() => {
  localStorage.removeItem('token')
})

loginWithTelegramFx.failData.watch((error: Error) => {
  console.error('Error logging in:', error)
})

// Add computed store for role access
export const $hasRole = (role: string) => 
  $userRoles.map(roles => roles.includes(role))

/**
 * Upload user avatar image
 * @param file The image file to upload
 * @returns The response data containing the avatar URL
 */
export const uploadAvatar = createEffect(async (file: File) => {
  // Create a new FormData object
  const formData = new FormData()
  
  // Make sure to use 'file' as the field name to match the backend parameter
  formData.append('file', file)
  
  try {
    // Send the request without allowing axios to transform the FormData
    const response = await api.post('/api/users/avatar', formData, {
      headers: {
        // Let the browser set the Content-Type with boundary
        'Content-Type': 'multipart/form-data'
      },
      // Prevent axios from trying to serialize the FormData object
      // transformRequest: (data) => data
    })
    
    // If the request was successful and returned an avatar URL
    if (response.data && response.data.avatar_url) {
      // Get the current user state
      const currentUser = $user.getState()
      
      // Add a cache-busting timestamp to the avatar URL
      const avatarUrl = `${response.data.avatar_url}?t=${Date.now()}`
      
      // If there is a user in the state, update its avatar URL
      if (currentUser) {
        $user.setState({
          ...currentUser,
          avatar_url: avatarUrl
        })
      }
      
      // Return the modified response with the timestamped URL
      return {
        ...response.data,
        avatar_url: avatarUrl
      }
    }
    
    return response.data
  } catch (error) {
    console.error('Error uploading avatar:', error)
    throw error
  }
}) 