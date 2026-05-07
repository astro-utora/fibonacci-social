import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createStore } from 'effector'
import { setUser, setToken, logout, $user, $token, $isAuthenticated, checkAuthFx } from '@/stores/auth'
import AuthForm from '@/components/AuthForm.vue'
import Home from '@/components/Home.vue'
import api from '@/utils/axios'

// Mock API responses
vi.mock('@/utils/axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

describe('Authentication Flow', () => {
  beforeEach(() => {
    // Reset stores
    $user.setState(null)
    $token.setState(null)
    localStorage.clear()
  })

  it('should show auth form for unauthenticated users', () => {
    const wrapper = mount(Home)
    expect(wrapper.findComponent(AuthForm).exists()).toBe(true)
  })

  it('should handle successful login', async () => {
    const mockUser = {
      uuid: '123',
      name: 'Test User',
      user_roles: [{ id: 1, role: { id: '1', name: 'user', label: 'User' } }]
    }

    const mockResponse = {
      data: {
        success: true,
        token: 'test-token',
        user: mockUser
      }
    }

    // Mock API call
    vi.mocked(api.post).mockResolvedValueOnce(mockResponse)

    const wrapper = mount(AuthForm)

    // Fill login form
    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('input[type="password"]').setValue('password')
    await wrapper.find('form').trigger('submit')

    // Verify API was called
    expect(api.post).toHaveBeenCalledWith('/api/auth/login', {
      email: 'test@example.com',
      password: 'password'
    })

    // Verify store updates
    expect($user.getState()).toEqual(mockUser)
    expect($token.getState()).toBe('test-token')
    expect($isAuthenticated.getState()).toBe(true)

    // Verify localStorage
    expect(localStorage.getItem('token')).toBe('test-token')
  })

  it('should handle failed login', async () => {
    const mockError = {
      response: {
        data: {
          detail: 'Invalid credentials'
        }
      }
    }

    vi.mocked(api.post).mockRejectedValueOnce(mockError)

    const wrapper = mount(AuthForm)

    await wrapper.find('input[type="email"]').setValue('wrong@example.com')
    await wrapper.find('input[type="password"]').setValue('wrongpass')
    await wrapper.find('form').trigger('submit')

    // Verify stores remain empty
    expect($user.getState()).toBeNull()
    expect($token.getState()).toBeNull()
    expect($isAuthenticated.getState()).toBe(false)

    // Verify error message is shown
    expect(wrapper.text()).toContain('Invalid credentials')
  })

  it('should handle logout', async () => {
    // Setup initial authenticated state
    setUser({ uuid: '123', name: 'Test User' })
    setToken('test-token')

    // Trigger logout
    logout()

    // Verify stores are cleared
    expect($user.getState()).toBeNull()
    expect($token.getState()).toBeNull()
    expect($isAuthenticated.getState()).toBe(false)

    // Verify localStorage is cleared
    expect(localStorage.getItem('token')).toBeNull()
  })

  it('should restore auth state on page load', async () => {
    // Setup stored token
    const mockToken = 'stored-token'
    localStorage.setItem('token', mockToken)

    const mockUser = {
      uuid: '123',
      name: 'Test User',
      user_roles: [{ id: 1, role: { id: '1', name: 'user', label: 'User' } }]
    }

    // Mock /me endpoint
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockUser })

    // Run auth check
    await checkAuthFx()

    // Verify stores are updated
    expect($user.getState()).toEqual(mockUser)
    expect($token.getState()).toBe(mockToken)
    expect($isAuthenticated.getState()).toBe(true)

    // Verify API call
    expect(api.get).toHaveBeenCalledWith('/api/auth/me')
  })
}) 