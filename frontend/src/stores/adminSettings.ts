import { createStore, createEvent, createEffect } from 'effector'
import api from '@/utils/axios'
import type { AdminSetting, AdminSettingUpdate } from '@/types/admin'

// Effects
export const fetchAdminSettingsFx = createEffect(async () => {
  const response = await api.get('/api/admin/settings')
  return response.data
})

export const fetchAdminSettingFx = createEffect(async (key: string) => {
  const response = await api.get(`/api/admin/settings/${key}`)
  return response.data
})

export const updateAdminSettingFx = createEffect(async (params: { key: string, data: AdminSettingUpdate }) => {
  const { key, data } = params
  const response = await api.put(`/api/admin/settings/${key}`, data)
  return response.data
})

export const fetchFilloutOnboardingIdFx = createEffect(async () => {
  const response = await api.get('/api/admin/settings/public/filloutOnboardingId')
  return response.data.value
})

// Events
export const setAdminSettings = createEvent()
export const updateAdminSetting = createEvent()
export const setFilloutOnboardingId = createEvent()

// Stores
export const $adminSettings = createStore<AdminSetting[]>([])
  .on(setAdminSettings, (_, settings) => settings)
  .on(fetchAdminSettingsFx.doneData, (_, settings) => settings)
  .on(updateAdminSetting, (state, updatedSetting) => 
    state.map(setting => setting.key === updatedSetting.key ? updatedSetting : setting)
  )
  .on(updateAdminSettingFx.doneData, (state, updatedSetting) => 
    state.map(setting => setting.key === updatedSetting.key ? updatedSetting : setting)
  )

export const $filloutOnboardingId = createStore<string>('6DzLtyFsoXus')
  .on(setFilloutOnboardingId, (_, id) => id)
  .on(fetchFilloutOnboardingIdFx.doneData, (_, id) => id)

// Initialize filloutOnboardingId from API
fetchFilloutOnboardingIdFx() 