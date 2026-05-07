import axios from 'axios'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000,
})

service.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error),
)

export default service
