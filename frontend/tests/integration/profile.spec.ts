import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setUser } from '@/stores/auth'
import { isProfileComplete } from '@/utils/user'
import Dashboard from '@/components/Dashboard.vue'
import FillingUserProfile from '@/views/FillingUserProfile.vue'
import api from '@/utils/axios'

vi.mock('@/utils/axios')

describe('User Profile Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should redirect to profile completion if profile is incomplete', () => {
    const incompleteUser = {
      uuid: '123',
      name: null,
      location: null
    }

    setUser(incompleteUser)
    const wrapper = mount(Dashboard)

    expect(wrapper.findComponent(FillingUserProfile).exists()).toBe(true)
    expect(isProfileComplete(incompleteUser)).toBe(false)
  })

  it('should show dashboard if profile is complete', () => {
    const completeUser = {
      uuid: '123',
      name: 'Test User',
      location: 'Test Location',
      workplace: 'Test Company',
      birth_date: '1990-01-01',
      goals: 'Test Goals',
      education: 'Test Education'
    }

    setUser(completeUser)
    const wrapper = mount(Dashboard)

    expect(wrapper.findComponent(FillingUserProfile).exists()).toBe(false)
    expect(isProfileComplete(completeUser)).toBe(true)
  })

  it('should handle profile update', async () => {
    const updatedProfile = {
      name: 'Updated Name',
      location: 'Updated Location'
    }

    vi.mocked(api.put).mockResolvedValueOnce({ data: updatedProfile })

    const wrapper = mount(FillingUserProfile)

    await wrapper.find('input[name="name"]').setValue(updatedProfile.name)
    await wrapper.find('input[name="location"]').setValue(updatedProfile.location)
    await wrapper.find('form').trigger('submit')

    expect(api.put).toHaveBeenCalledWith('/api/users/profile', updatedProfile)
  })
}) 