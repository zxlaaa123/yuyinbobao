import axios from 'axios'
import { getErrorMessage, isUserCanceled } from '../utils/error'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: Number(import.meta.env.VITE_API_TIMEOUT || 120000),
})

service.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (isUserCanceled(error)) {
      return Promise.reject(error)
    }
    return Promise.reject(new Error(getErrorMessage(error)))
  },
)

export default service
