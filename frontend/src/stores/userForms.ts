import { 
  createStore, 
  createEvent, 
  createEffect, 
  sample, 
  Store, 
  Event, 
  Effect 
} from 'effector'
import api from '@/utils/axios'
import { PaginationMeta, PaginatedResponse } from './waitingList'

// Types
export interface UserFormEntry {
  id: string
  userId: string
  userName: string
  role: string
  filloutId: string
  startDate: string
  completeDate: string | null
  requestedDate: string | null
  validatedDate: string | null
}

interface ValidateFormParams {
  filloutId: string
  userId: string
}

interface ErrorResponse {
  message: string
}

// Events
export const resetError = createEvent()
export const setUserForms = createEvent<PaginatedResponse<UserFormEntry>>()
export const updateUserForm = createEvent<UserFormEntry>()
export const clearUserForms = createEvent()
export const setPage = createEvent<number>()
export const setPageSize = createEvent<number>()

// Effects
export const fetchUserFormsFx = createEffect(async (params: { 
  page?: number, 
  page_size?: number 
}) => {
  const queryParams = new URLSearchParams()
  
  if (params.page) {
    queryParams.append('page', params.page.toString())
  }
  
  if (params.page_size) {
    queryParams.append('page_size', params.page_size.toString())
  }
  
  const response = await api.get(`/api/admin/user-forms${queryParams.toString() ? '?' + queryParams.toString() : ''}`)
  return response.data
})

export const validateFormFx = createEffect(async (params: { 
  userId: string, 
  filloutId: string, 
  projectId?: string 
}) => {
  const response = await api.post('/api/admin/validate-form', params)
  return response.data
})

export const rejectValidationFx = createEffect(async (params: { 
  userId: string, 
  filloutId: string, 
  projectId?: string 
}) => {
  const response = await api.post('/api/admin/reject-validation', params)
  return response.data
})

// Stores
export const $userFormsData: Store<PaginatedResponse<UserFormEntry>> = createStore<PaginatedResponse<UserFormEntry>>({
  items: [],
  pagination: {
    page: 1,
    page_size: 10,
    total_count: 0,
    total_pages: 0
  }
})
  .on(setUserForms, (_: PaginatedResponse<UserFormEntry>, data: PaginatedResponse<UserFormEntry>) => data)
  .on(fetchUserFormsFx.doneData, (_: PaginatedResponse<UserFormEntry>, data: PaginatedResponse<UserFormEntry>) => data)
  .reset(clearUserForms)

export const $userFormItems: Store<UserFormEntry[]> = $userFormsData.map((data: PaginatedResponse<UserFormEntry>) => data.items)
export const $userFormsPagination: Store<PaginationMeta> = $userFormsData.map((data: PaginatedResponse<UserFormEntry>) => data.pagination)

export const $page: Store<number> = createStore<number>(1)
  .on(setPage, (_: number, page: number) => page)
  .on($userFormsPagination, (currentPage: number, pagination: PaginationMeta) => 
    currentPage > pagination.total_pages && pagination.total_pages > 0 
      ? pagination.total_pages 
      : currentPage
  )

export const $pageSize: Store<number> = createStore<number>(10)
  .on(setPageSize, (_: number, pageSize: number) => pageSize)

// For backward compatibility
export const $userForms: Store<UserFormEntry[]> = $userFormItems

// Loading and error states
export const $isLoading: Store<boolean> = createStore<boolean>(false)
  .on(fetchUserFormsFx, () => true)
  .on(validateFormFx, () => true)
  .on(rejectValidationFx, () => true)
  .on(fetchUserFormsFx.finally, () => false)
  .on(validateFormFx.finally, () => false)
  .on(rejectValidationFx.finally, () => false)

export const $error: Store<string | null> = createStore<string | null>(null)
  .on(fetchUserFormsFx.failData, (_: null, error: any) => error.message || "Failed to fetch user forms")
  .on(validateFormFx.failData, (_: null, error: any) => error.message || "Failed to validate form")
  .on(rejectValidationFx.failData, (_: null, error: any) => error.message || "Failed to reject validation")
  .reset(resetError)

// Update forms after validation/rejection
$userFormsData.on(validateFormFx.doneData, (state: PaginatedResponse<UserFormEntry>, updatedForm: UserFormEntry) => {
  const updatedItems = state.items.map((item: UserFormEntry) => 
    (item.userId === updatedForm.userId && item.filloutId === updatedForm.filloutId)
      ? updatedForm
      : item
  )
  
  return {
    ...state,
    items: updatedItems
  }
})

$userFormsData.on(rejectValidationFx.doneData, (state: PaginatedResponse<UserFormEntry>, updatedForm: UserFormEntry) => {
  const updatedItems = state.items.map((item: UserFormEntry) => 
    (item.userId === updatedForm.userId && item.filloutId === updatedForm.filloutId)
      ? updatedForm
      : item
  )
  
  return {
    ...state,
    items: updatedItems
  }
})

// Automatically fetch data when page or pageSize changes
sample({
  source: { page: $page, pageSize: $pageSize },
  fn: ({ page, pageSize }) => {
    // Make sure we're sending primitive values, not reactive objects
    return { 
      page: Number(page), 
      page_size: Number(pageSize) 
    }
  },
  target: fetchUserFormsFx
}) 