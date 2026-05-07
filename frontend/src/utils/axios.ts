import axios from 'axios'
import { $token } from '@/stores/auth'
import { defaultApiUrl } from './constants'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || defaultApiUrl
})

// Add request interceptor
api.interceptors.request.use(config => {
  const token = $token.getState()
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  return config
})

export default api