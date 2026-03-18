import { Navigate, Outlet } from 'react-router-dom'
import { useContext } from 'react'
import AuthContext from '../context/AuthContext'
import { useLoading } from '../context/LoadingContext'

function PrivateRoute({ children }) {
  const { isAuthenticated, isLoading } = useContext(AuthContext)
  const { isGlobalLoading } = useLoading()

  if (isLoading || isGlobalLoading) {
    console.log('[PrivateRoute] waiting auth/loading state')
    return <div className="flex min-h-screen items-center justify-center text-slate-200">Carregando...</div>
  }

  if (!isAuthenticated) {
    console.log('[PrivateRoute] unauthenticated, redirecting to /login')
    return <Navigate to="/login" replace />
  }

  return children || <Outlet />
}

export default PrivateRoute
