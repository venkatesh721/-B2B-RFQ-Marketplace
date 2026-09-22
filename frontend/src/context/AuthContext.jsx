import { createContext, useContext, useEffect, useState } from 'react'
import apiClient from '../api/client'

const AuthContext = createContext(null)
const ACCESS_KEY = 'rfq_access_token'
const REFRESH_KEY = 'rfq_refresh_token'
const USER_KEY = 'rfq_user'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem(USER_KEY) || 'null'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function restoreSession() {
      if (!localStorage.getItem(ACCESS_KEY)) return setLoading(false)
      try {
        const { data } = await apiClient.get('/auth/me/')
        setUser(data)
        localStorage.setItem(USER_KEY, JSON.stringify(data))
      } catch {
        logout()
      } finally {
        setLoading(false)
      }
    }
    restoreSession()
  }, [])

  useEffect(() => {
    const clearSession = () => setUser(null)
    window.addEventListener('rfq-session-expired', clearSession)
    return () => window.removeEventListener('rfq-session-expired', clearSession)
  }, [])

  function saveSession(data) {
    localStorage.setItem(ACCESS_KEY, data.access)
    localStorage.setItem(REFRESH_KEY, data.refresh)
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    setUser(data.user)
  }

  function logout() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
    localStorage.removeItem(USER_KEY)
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, loading, saveSession, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}
