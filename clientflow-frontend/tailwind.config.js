export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          900: '#0f172a',
          800: '#1e293b',
          700: '#334155',
          600: '#475569',
        },
        accent: {
          blue: '#3b82f6',
          cyan: '#06b6d4',
          purple: '#a855f7',
          orange: '#f97316',
          green: '#10b981',
          pink: '#ec4899',
          indigo: '#6366f1',
        },
      },
      backgroundColor: {
        'card': 'rgba(15, 23, 42, 0.8)',
        'glass': 'rgba(30, 41, 59, 0.7)',
        'card-premium': 'rgba(20, 29, 54, 0.6)',
      },
      boxShadow: {
        'card': '0 4px 6px rgba(0, 0, 0, 0.3)',
        'card-hover': '0 8px 12px rgba(59, 130, 246, 0.1)',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}
