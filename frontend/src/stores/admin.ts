import { createEffect } from 'effector'
import { createBaseStore, withErrorHandling } from './base'
import api from '@/utils/axios'

interface AdminStats {
  totalUsers: number
  activeUsers: number
  completedQuestionnaires: number
  pendingQuestionnaires: number
}

const {
  $data: $adminStats,
  $error,
  $isLoading
} = createBaseStore<AdminStats>('adminStats')

const fetchStatsFx = withErrorHandling(
  createEffect(async () => {
    const response = await api.get('/api/admin/stats')
    return response.data
  })
)

export {
  $adminStats,
  $error,
  $isLoading,
  fetchStatsFx
} 