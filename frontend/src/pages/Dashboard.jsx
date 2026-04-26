// FinVest | Frontend | pages/Dashboard.jsx
// Main dashboard with stat cards, price ticker, and service health indicator

import React, { useState, useEffect } from 'react'
import client from '../api/client'
import StatCard from '../components/StatCard'

function Dashboard({ addToast }) {
  const [stats, setStats] = useState({ users: 0, assets: 0, transactions: 0, goals: 0 })
  const [health, setHealth] = useState(null)
  const [prices, setPrices] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchPrices, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      const [usersRes, assetsRes, txnRes, goalsRes, healthRes] = await Promise.allSettled([
        client.get('/users/'),
        client.get('/assets/'),
        client.get('/transactions/'),
        client.get('/analytics/goals/'),
        client.get('/health', { baseURL: 'http://localhost:8000' }),
      ])

      setStats({
        users: usersRes.status === 'fulfilled' ? usersRes.value.data.total : 0,
        assets: assetsRes.status === 'fulfilled' ? assetsRes.value.data.total : 0,
        transactions: txnRes.status === 'fulfilled' ? txnRes.value.data.total : 0,
        goals: goalsRes.status === 'fulfilled' ? goalsRes.value.data.total : 0,
      })

      if (assetsRes.status === 'fulfilled') {
        setPrices(assetsRes.value.data.assets || [])
      }

      if (healthRes.status === 'fulfilled') {
        setHealth(healthRes.value.data)
      }
    } catch (err) {
      addToast('Failed to load dashboard data', 'error')
    }
    setLoading(false)
  }

  const fetchPrices = async () => {
    try {
      const res = await client.get('/assets/')
      setPrices(res.data.assets || [])
    } catch {}
  }

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-surface-200 bg-clip-text text-transparent">
          Dashboard
        </h1>
        <p className="text-surface-200 mt-1">Welcome to FinVest — your investment command center</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Users" value={stats.users} icon="👥" color="primary" />
        <StatCard title="Supported Assets" value={stats.assets} icon="📈" color="accent" />
        <StatCard title="Total Transactions" value={stats.transactions} icon="💸" color="amber" />
        <StatCard title="Active Goals" value={stats.goals} icon="🎯" color="rose" />
      </div>

      {/* Price Ticker */}
      <div className="bg-surface-800/50 border border-surface-700/50 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-surface-200 uppercase tracking-wider mb-4">
          📊 Live Crypto Prices
        </h2>
        {prices.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {prices.map(asset => (
              <div
                key={asset.id}
                className="bg-surface-700/30 border border-surface-700/50 rounded-lg p-3 hover:border-primary-500/30 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white">{asset.ticker}</span>
                  {asset.stale_data && (
                    <span className="text-xs bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded">stale</span>
                  )}
                </div>
                <p className="text-xs text-surface-200 mt-0.5">{asset.name}</p>
                <p className="text-lg font-bold text-accent-400 mt-1">
                  {asset.live_price_usd != null ? `$${asset.live_price_usd.toLocaleString()}` : '—'}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-surface-200 text-sm">
            {loading ? 'Loading prices...' : 'No asset data available'}
          </p>
        )}
      </div>

      {/* Service Health */}
      {health && (
        <div className="bg-surface-800/50 border border-surface-700/50 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-surface-200 uppercase tracking-wider mb-4">
            🏥 Service Health Status
          </h2>
          <div className="flex flex-wrap gap-3">
            {Object.entries(health.services || {}).map(([svc, status]) => (
              <div
                key={svc}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm ${
                  status === 'healthy'
                    ? 'bg-accent-500/10 border-accent-500/30 text-accent-400'
                    : 'bg-red-500/10 border-red-500/30 text-red-400'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${status === 'healthy' ? 'bg-accent-400' : 'bg-red-400'} animate-pulse`} />
                <span className="font-medium">{svc.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
