import { createStore, createEvent, createEffect, sample } from 'effector'
import api from '@/utils/axios'
import { UUID } from 'crypto'

// Define types for waiting list
export interface WaitingListEntry {
  id: string
  user_id: string
  user_name: string | null
  email: string | null
  status: string
  created_at: string
  approved_at: string | null
}

export interface PaginationMeta {
  page: number
  page_size: number
  total_count: number
  total_pages: number
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: PaginationMeta
}

// Effects for API calls
export const fetchWaitingListFx = createEffect(async (params: { 
  status?: string, 
  page?: number, 
  page_size?: number 
}) => {
  const queryParams = new URLSearchParams()
  
  if (params.status) {
    queryParams.append('status', params.status)
  }
  
  if (params.page) {
    queryParams.append('page', params.page.toString())
  }
  
  if (params.page_size) {
    queryParams.append('page_size', params.page_size.toString())
  }
  
  const response = await api.get(`/api/waiting-list${queryParams.toString() ? '?' + queryParams.toString() : ''}`)
  return response.data
})

export const approveUserFx = createEffect(async (userId: string) => {
  const response = await api.post(`/api/waiting-list/${userId}/approve`)
  return response.data
})

export const rejectUserFx = createEffect(async (userId: string) => {
  const response = await api.post(`/api/waiting-list/${userId}/reject`)
  return response.data
})

export const getCurrentUserStatusFx = createEffect(async () => {
  const response = await api.get('/api/waiting-list/status')
  return response.data
})

// Events
export const setWaitingList = createEvent<PaginatedResponse<WaitingListEntry>>()
export const setUserStatus = createEvent<WaitingListEntry | null>()
export const clearWaitingList = createEvent()
export const setPage = createEvent<number>()
export const setPageSize = createEvent<number>()
export const setStatusFilter = createEvent<string>()

// Stores
export const $waitingListData = createStore<PaginatedResponse<WaitingListEntry>>({
  items: [],
  pagination: {
    page: 1,
    page_size: 10,
    total_count: 0,
    total_pages: 0
  }
})
  .on(setWaitingList, (_, data) => data)
  .on(fetchWaitingListFx.doneData, (_, data) => data)
  .reset(clearWaitingList)

export const $waitingListItems = $waitingListData.map(data => data.items)
export const $waitingListPagination = $waitingListData.map(data => data.pagination)

export const $userWaitingStatus = createStore<WaitingListEntry | null>(null)
  .on(setUserStatus, (_, status) => status)
  .on(getCurrentUserStatusFx.doneData, (_, data) => data)

export const $page = createStore<number>(1)
  .on(setPage, (_, page) => page)
  .on($waitingListPagination, (currentPage, pagination) => 
    currentPage > pagination.total_pages && pagination.total_pages > 0 
      ? pagination.total_pages 
      : currentPage
  )

export const $pageSize = createStore<number>(10)
  .on(setPageSize, (_, pageSize) => pageSize)

export const $statusFilter = createStore<string>('pending')
  .on(setStatusFilter, (_, status) => status)

// Update pagination when filters change
sample({
  source: $statusFilter,
  fn: () => 1,
  target: $page
})

// Handle approval and rejection updates
sample({
  source: $waitingListItems,
  clock: approveUserFx.doneData,
  fn: (list, approved) => list.map(entry => 
    entry.user_id === approved.user_id 
      ? { ...entry, status: 'approved', approved_at: approved.approved_at }
      : entry
  ),
  target: setWaitingList
})

sample({
  source: $waitingListItems,
  clock: rejectUserFx.doneData,
  fn: (list, rejected) => list.map(entry => 
    entry.user_id === rejected.user_id 
      ? { ...entry, status: 'rejected' }
      : entry
  ),
  target: setWaitingList
})

// Automatically fetch data when page, pageSize or status changes
sample({
  source: { page: $page, pageSize: $pageSize, status: $statusFilter },
  fn: ({ page, pageSize, status }) => ({ 
    page, 
    page_size: pageSize, 
    status: status || undefined 
  }),
  target: fetchWaitingListFx
}) 