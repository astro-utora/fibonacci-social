// @ts-ignore - Suppressing TS errors for Effector imports
import { createStore, createEvent, createEffect } from 'effector'
import api from '@/utils/axios'
import type { User } from '@/types'
import { $user, setUser } from '@/stores/auth'

// Types
export interface Credits {
  user_uuid: string
  credits: number
}

// Effects
export const loadCreditsFx = createEffect<void, Credits>(async () => {
  const response = await api.get('/api/credits')
  return response.data
})

// Events
export const resetCredits = createEvent()
export const updateCredits = createEvent<number>()

// Stores
export const $credits = createStore<number>(0)
  .on(loadCreditsFx.doneData, (_: number, data: Credits) => data.credits)
  .on(updateCredits, (_: number, credits: number) => credits)
  // Also update when the user data changes and contains credits
  .on(setUser, (_: number, user: User | null) => user?.credits ?? 0)
  .reset(resetCredits)

export const $creditsLoading = createStore<boolean>(false)
  .on(loadCreditsFx.pending, (_: boolean, pending: boolean) => pending)

export const $creditsError = createStore<string | null>(null)
  .on(loadCreditsFx.failData, (_: string | null, error: Error) => error.message)
  .reset(loadCreditsFx)
