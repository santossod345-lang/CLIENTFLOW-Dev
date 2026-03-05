import { Navigate } from 'react-router-dom'
import { useContext } from 'react'
import AuthContext from '../context/AuthContext'

function PrivateRoute({ children }) {
  const { isAuthenticated, isLoading } = useContext(AuthContext)

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Carregando...</div>
  }

  if (!isAuthenticated) {
    console.log('[PrivateRoute] Usuário não autenticado. Redirecionando para login.')
    return <Navigate to="/login" replace />
  }

  return children
}

export default PrivateRoute
