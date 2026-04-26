// FinVest | Frontend | components/StatCard.jsx
// Reusable stat card for dashboard KPI display

import React from 'react'

function StatCard({ title, value, icon, color = 'primary', subtitle }) {
  const colorMap = {
    primary: 'from-primary-500/20 to-primary-600/10 border-primary-500/30',
    accent: 'from-accent-500/20 to-accent-600/10 border-accent-500/30',
    amber: 'from-amber-500/20 to-amber-600/10 border-amber-500/30',
    rose: 'from-rose-500/20 to-rose-600/10 border-rose-500/30',
  }

  return (
    <div className={`bg-gradient-to-br ${colorMap[color] || colorMap.primary} 
      border rounded-xl p-5 backdrop-blur-sm 
      hover:scale-[1.02] transition-transform duration-200 cursor-default`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-surface-200 text-xs font-medium uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-bold mt-1 text-white">{value}</p>
          {subtitle && <p className="text-surface-200 text-xs mt-1">{subtitle}</p>}
        </div>
        <span className="text-3xl opacity-80">{icon}</span>
      </div>
    </div>
  )
}

export default StatCard
