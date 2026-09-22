import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('rfq_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const refresh = localStorage.getItem('rfq_refresh_token')
    if (error.response?.status !== 401 || originalRequest?._retry || !refresh) return Promise.reject(error)

    originalRequest._retry = true
    try {
      const { data } = await axios.post(`${apiClient.defaults.baseURL}/auth/refresh/`, { refresh })
      localStorage.setItem('rfq_access_token', data.access)
      originalRequest.headers.Authorization = `Bearer ${data.access}`
      return apiClient(originalRequest)
    } catch (refreshError) {
      localStorage.removeItem('rfq_access_token')
      localStorage.removeItem('rfq_refresh_token')
      localStorage.removeItem('rfq_user')
      window.dispatchEvent(new Event('rfq-session-expired'))
      return Promise.reject(refreshError)
    }
  },
)

export default apiClient
