import axios from 'axios'
import { getErrorMessage } from '../utils/error'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: Number(import.meta.env.VITE_API_TIMEOUT || 120000),
})

service.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(new Error(getErrorMessage(error))),
)

export default service
