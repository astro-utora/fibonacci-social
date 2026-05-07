import { createStore, createEvent, createEffect } from 'effector'
import * as filloutService from '@/services/fillout'
import api from '@/utils/axios'

export interface FilloutSubmission {
  id: string;
  filloutId: string;
  status: 'started' | 'completed' | 'requested' | 'validated';
  submissionData?: any;
  projectId?: string;
  requestedAt?: string;
  validatedAt?: string;
}

// Types
interface FilloutParams {
  filloutId: string;
  project_id?: string;
}

interface FilloutResponse {
  status: string;
  id: string;
}

// Effects
export const loadSubmissionsFx = createEffect<
  { projectId?: string } | void, 
  FilloutSubmission[]
>(async (params) => {
  const data = await filloutService.getFilloutSubmissions(params)
  return data
})

export const startFilloutFx = createEffect<FilloutParams, FilloutResponse>(async (params) => {
  const response = await api.post('/api/fillout/start', params)
  return response.data
})

export const completeFilloutFx = createEffect<FilloutParams, FilloutResponse>(async (params) => {
  const response = await api.post('/api/fillout/complete', params)
  return response.data
})

// Store
export const $filloutSubmissions = createStore<FilloutSubmission[]>([])
  .on(loadSubmissionsFx.doneData, (_, submissions) => submissions)

// Store for tracking currently active fillout operations
export const $filloutStatus = createStore<Record<string, string>>({})
  .on(startFilloutFx.doneData, (state, response) => ({
    ...state,
    [response.id]: 'started'
  }))
  .on(completeFilloutFx.doneData, (state, response) => ({
    ...state,
    [response.id]: 'completed'
  }))

// Store for tracking loading states
export const $filloutLoading = createStore<boolean>(false)
  .on(startFilloutFx, () => true)
  .on(completeFilloutFx, () => true)
  .on(startFilloutFx.finally, () => false)
  .on(completeFilloutFx.finally, () => false)

// Store for handling errors
export const $filloutError = createStore<string | null>(null)
  .on(startFilloutFx.failData, (_, error) => error.message)
  .on(completeFilloutFx.failData, (_, error) => error.message)
  .reset(startFilloutFx)
  .reset(completeFilloutFx) 