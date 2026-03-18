import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import { LoadingProvider } from './context/LoadingContext'
import ErrorBoundary from './components/ErrorBoundary'
import { initMonitoring } from './utils/monitoring'
import './index.css'

initMonitoring()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <LoadingProvider>
          <ErrorBoundary>
            <App />
          </ErrorBoundary>
        </LoadingProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
