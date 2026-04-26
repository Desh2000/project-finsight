// FinVest | Frontend | components/Navbar.jsx
// Navigation bar with links to all dashboard sections

import React from 'react'
import { Link, useLocation } from 'react-router-dom'

const navItems = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/users', label: 'Users', icon: '👥' },
  { path: '/assets', label: 'Assets', icon: '📈' },
  { path: '/transactions', label: 'Transactions', icon: '💸' },
  { path: '/analytics', label: 'Goals', icon: '🎯' },
]

function Navbar() {
  const location = useLocation()

  return (
    <nav className="bg-surface-800/80 backdrop-blur-xl border-b border-surface-700/50 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <span className="text-2xl">💰</span>
            <span className="text-xl font-bold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent group-hover:from-primary-300 group-hover:to-accent-300 transition-all">
              FinSight
            </span>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center gap-1">
            {navItems.map(item => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-1.5 ${
                    isActive
                      ? 'bg-primary-500/20 text-primary-300 shadow-lg shadow-primary-500/10'
                      : 'text-surface-200 hover:text-white hover:bg-surface-700/50'
                  }`}
                >
                  <span className="text-base">{item.icon}</span>
                  <span className="hidden sm:inline">{item.label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
