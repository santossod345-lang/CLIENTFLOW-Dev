import React from 'react'

const StatCard = ({ icon, title, value, change, changeType = 'positive', loading = false }) => {
  const changeColor = changeType === 'positive' ? 'text-accent-green' : 'text-red-400'
  const changeBg = changeType === 'positive' ? 'bg-accent-green/20' : 'bg-red-500/20'

  if (loading) {
    return (
      <div className="card-base">
        <div className="flex items-start justify-between mb-4">
          <div className="w-12 h-12 skeleton" />
          <div className="w-12 h-6 skeleton" />
        </div>
        <div className="skeleton skeleton-line mb-3 w-24" />
        <div className="skeleton skeleton-title w-32" />
      </div>
    )
  }

  const displayValue = value === null || value === undefined || value === '' ? '0' : value

  return (
    <div className="card-base group cursor-default fade-in">
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 bg-primary-800/70 border border-primary-700/60 rounded-xl flex items-center justify-center text-xl">
          {icon}
        </div>
        <span className={`text-xs font-semibold px-3 py-1 rounded-full border border-primary-700/60 ${changeBg} ${changeColor}`}>
          {changeType === 'positive' ? '↑' : '↓'} {change}%
        </span>
      </div>
      <p className="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-2">{title}</p>
      <p className="text-3xl font-bold text-white tracking-tight">{displayValue}</p>
    </div>
  )
}

export default StatCard
