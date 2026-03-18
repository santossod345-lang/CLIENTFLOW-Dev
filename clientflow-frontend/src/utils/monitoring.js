export function initMonitoring() {
  const sentryDsn = import.meta.env.VITE_SENTRY_DSN
  const logRocketAppId = import.meta.env.VITE_LOGROCKET_APP_ID

  if (sentryDsn && window.Sentry && typeof window.Sentry.init === 'function') {
    window.Sentry.init({ dsn: sentryDsn })
  }

  if (logRocketAppId && window.LogRocket && typeof window.LogRocket.init === 'function') {
    window.LogRocket.init(logRocketAppId)
  }
}

export function captureException(error, context = {}) {
  if (window.Sentry && typeof window.Sentry.captureException === 'function') {
    window.Sentry.captureException(error, { extra: context })
  }

  if (window.LogRocket && typeof window.LogRocket.captureException === 'function') {
    window.LogRocket.captureException(error)
  }
}
