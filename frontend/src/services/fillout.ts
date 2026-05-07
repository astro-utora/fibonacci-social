import api from '@/utils/axios'

interface FilloutParams {
  projectId?: string;
}

interface FilloutFormData {
  submission_data: any
}

interface ValidationParams {
  projectId?: string | number
}

export async function startFillout(filloutId: string, params?: FilloutParams) {
  const { data } = await api.post('/api/fillout/start', { 
    filloutId, 
    project_id: params?.projectId
  })
  return data
}

export async function completeFillout(filloutId: string, params?: FilloutParams) {
  const { data } = await api.post('/api/fillout/complete', { 
    filloutId,
    project_id: params?.projectId
  })
  return data
}

export async function getFilloutSubmissions(params?: FilloutParams) {
  const baseUrl = '/api/fillout/submissions'
  const url = params?.projectId 
    ? `${baseUrl}?project_id=${params.projectId}`
    : baseUrl
    
  const { data } = await api.get(url)
  return data
}

/**
 * Get data for a specific fillout form
 */
export const getFilloutData = async (filloutId: string): Promise<FilloutFormData> => {
  const response = await api.get(`/api/fillout/${filloutId}/data`)
  return response.data
}

/**
 * Request validation for a fillout form
 */
export const requestValidation = async (filloutId: string, params: ValidationParams) => {
  const response = await api.post(`/api/fillout/${filloutId}/request-validation`, {
    projectId: params.projectId
  })
  return response.data
}

/**
 * Validate a form submission (admin function)
 */
export const validateForm = async (filloutId: string, userId: string) => {
  const response = await api.post('/api/admin/validate-form', { filloutId, userId })
  return response.data
}

/**
 * Reject a validation request (admin function)
 */
export const rejectValidation = async (filloutId: string, userId: string) => {
  const response = await api.post('/api/admin/reject-validation', { filloutId, userId })
  return response.data
} 