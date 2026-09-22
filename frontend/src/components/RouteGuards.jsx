import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function ProtectedRoute({ role }) {
  const { user, loading } = useAuth()
  if (loading) return <p className="page-state">Restoring your session…</p>
  if (!user) return <Navigate to="/login" replace />
  if (role && user.role !== role) return <Navigate to={user.role === 'BUYER' ? '/buyer/dashboard' : '/supplier/dashboard'} replace />
  return <Outlet />
}

export function HomeRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <p className="page-state">Loading…</p>
  return <Navigate to={user ? (user.role === 'BUYER' ? '/buyer/dashboard' : '/supplier/dashboard') : '/login'} replace />
}
