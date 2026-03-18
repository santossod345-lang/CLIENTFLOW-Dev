import React from 'react'
import { captureException } from '../utils/monitoring'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary] UI crash captured:', error)
    console.error('[ErrorBoundary] Component stack:', errorInfo?.componentStack)
    captureException(error, { componentStack: errorInfo?.componentStack || '' })
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-950 p-6">
          <div className="max-w-lg w-full rounded-lg border border-red-400/40 bg-slate-900 p-6 shadow">
            <h1 className="mb-2 text-xl font-semibold text-red-100">Erro inesperado na interface</h1>
            <p className="mb-4 text-slate-300">A aplicacao encontrou uma falha de renderizacao. Recarregue para continuar.</p>
            <pre className="mb-4 overflow-auto rounded bg-slate-800 p-3 text-xs text-slate-200">
              {String(this.state.error?.message || 'Erro desconhecido')}
            </pre>
            <button
              type="button"
              onClick={this.handleReload}
              className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Recarregar
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
