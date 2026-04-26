// FinVest | Frontend | pages/Goals.jsx
// Savings goals & portfolio analytics page with Recharts bar chart and LKR toggle

import React, { useState, useEffect } from 'react'
import client from '../api/client'
import Modal from '../components/Modal'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'

function Goals({ addToast }) {
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [depositGoal, setDepositGoal] = useState(null)
  const [depositAmt, setDepositAmt] = useState('')
  const [showLKR, setShowLKR] = useState(true)
  const [exchangeRate, setExchangeRate] = useState(320)
  const [fallbackRate, setFallbackRate] = useState(false)
  const [portfolioData, setPortfolioData] = useState(null)
  const [userIdFilter, setUserIdFilter] = useState('')
  const [form, setForm] = useState({
    user_id: '', goal_name: '', target_amount_usd: '', target_date: '',
  })

  useEffect(() => { fetchGoals() }, [])

  const fetchGoals = async () => {
    setLoading(true)
    try {
      const res = await client.get('/analytics/goals/')
      setGoals(res.data.goals || [])
    } catch (err) {
      addToast('Failed to load goals', 'error')
    }
    setLoading(false)
  }

  const fetchPortfolio = async (userId) => {
    if (!userId) { setPortfolioData(null); return }
    try {
      const res = await client.get(`/analytics/portfolio/${userId}`)
      setPortfolioData(res.data)
      setExchangeRate(res.data.exchange_rate || 320)
      setFallbackRate(res.data.fallback_rate || false)
    } catch (err) {
      addToast('Failed to load portfolio', 'error')
    }
  }

  const addGoal = async (e) => {
    e.preventDefault()
    try {
      await client.post('/analytics/goals/', {
        ...form,
        target_amount_usd: parseFloat(form.target_amount_usd),
      })
      addToast('Goal created successfully!', 'success')
      setShowAdd(false)
      setForm({ user_id: '', goal_name: '', target_amount_usd: '', target_date: '' })
      fetchGoals()
    } catch (err) {
      addToast(err.message || 'Failed to create goal', 'error')
    }
  }

  const deposit = async () => {
    if (!depositGoal || !depositAmt) return
    try {
      await client.patch(`/analytics/goals/${depositGoal.id}/deposit`, {
        amount: parseFloat(depositAmt),
      })
      addToast('Deposit successful!', 'success')
      setDepositGoal(null)
      setDepositAmt('')
      fetchGoals()
      if (userIdFilter) fetchPortfolio(userIdFilter)
    } catch (err) {
      addToast(err.message || 'Deposit failed', 'error')
    }
  }

  const abandonGoal = async (goalId) => {
    if (!window.confirm('Are you sure you want to abandon this goal?')) return
    try {
      await client.delete(`/analytics/goals/${goalId}`)
      addToast('Goal abandoned', 'success')
      fetchGoals()
    } catch (err) {
      addToast(err.message || 'Failed to abandon goal', 'error')
    }
  }

  const formatCurrency = (usd) => {
    if (showLKR) return `LKR ${(usd * exchangeRate).toLocaleString(undefined, {maximumFractionDigits: 2})}`
    return `$${usd.toLocaleString(undefined, {maximumFractionDigits: 2})}`
  }

  const chartData = (portfolioData?.goals || []).map(g => ({
    name: g.goal_name.length > 12 ? g.goal_name.substring(0, 12) + '…' : g.goal_name,
    target: showLKR ? g.target_amount_lkr : g.target_amount_usd,
    current: showLKR ? g.current_amount_lkr : g.current_amount_usd,
  }))

  const inputClass = "w-full bg-surface-700/50 border border-surface-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/50 transition-colors"

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Goals & Analytics</h1>
          <p className="text-surface-200 mt-1">Track your savings goals and portfolio value</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Exchange Rate Badge */}
          <span className={`text-xs px-2.5 py-1.5 rounded-lg border ${
            fallbackRate
              ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
              : 'bg-accent-500/20 text-accent-400 border-accent-500/30'
          }`}>
            1 USD = {exchangeRate.toFixed(2)} LKR
            {fallbackRate && ' (fallback)'}
          </span>

          {/* LKR/USD Toggle */}
          <button
            onClick={() => setShowLKR(!showLKR)}
            className="px-3 py-1.5 bg-surface-700/50 border border-surface-700 rounded-lg text-xs font-medium text-surface-200 hover:text-white transition-colors"
          >
            {showLKR ? '🇱🇰 LKR' : '🇺🇸 USD'}
          </button>

          <button
            onClick={() => setShowAdd(true)}
            className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-primary-500/20"
          >
            + Add Goal
          </button>
        </div>
      </div>

      {/* Portfolio Lookup */}
      <div className="bg-surface-800/50 border border-surface-700/50 rounded-xl p-4">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <label className="block text-xs font-medium text-surface-200 mb-1">View Portfolio for User ID</label>
            <input
              className={inputClass}
              value={userIdFilter}
              onChange={e => setUserIdFilter(e.target.value)}
              placeholder="Paste user UUID to load portfolio analytics"
            />
          </div>
          <button
            onClick={() => fetchPortfolio(userIdFilter)}
            className="px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 rounded-lg text-sm font-medium transition-colors border border-primary-500/30"
          >
            Load Portfolio
          </button>
        </div>

        {portfolioData && (
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-surface-700/30 rounded-lg p-3">
              <p className="text-xs text-surface-200">Total Goal Value</p>
              <p className="text-lg font-bold text-accent-400">{formatCurrency(portfolioData.total_goal_value_usd)}</p>
            </div>
            <div className="bg-surface-700/30 rounded-lg p-3">
              <p className="text-xs text-surface-200">Active Goals</p>
              <p className="text-lg font-bold text-white">{portfolioData.active_goals}</p>
            </div>
            <div className="bg-surface-700/30 rounded-lg p-3">
              <p className="text-xs text-surface-200">Completed Goals</p>
              <p className="text-lg font-bold text-primary-400">{portfolioData.completed_goals}</p>
            </div>
            <div className="bg-surface-700/30 rounded-lg p-3">
              <p className="text-xs text-surface-200">Abandoned Goals</p>
              <p className="text-lg font-bold text-surface-200">{portfolioData.abandoned_goals}</p>
            </div>
          </div>
        )}
      </div>

      {/* Chart */}
      {chartData.length > 0 && (
        <div className="bg-surface-800/50 border border-surface-700/50 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-surface-200 uppercase tracking-wider mb-4">
            Goal Progress Chart
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f1f5f9' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Legend />
              <Bar dataKey="target" fill="#6366f1" name="Target" radius={[4, 4, 0, 0]} />
              <Bar dataKey="current" fill="#10b981" name="Current" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Goal Cards */}
      {loading ? (
        <p className="text-surface-200">Loading goals...</p>
      ) : goals.length === 0 ? (
        <div className="bg-surface-800/50 border border-surface-700/50 rounded-xl p-12 text-center">
          <p className="text-surface-200">No savings goals found. Create one to get started!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {goals.map(goal => {
            const pct = goal.target_amount_usd > 0
              ? Math.min(100, Math.round((goal.current_amount_usd / goal.target_amount_usd) * 100))
              : 0
            const statusColor = goal.status === 'Active' ? 'text-accent-400'
              : goal.status === 'Completed' ? 'text-primary-400' : 'text-surface-200'

            return (
              <div key={goal.id} className="bg-surface-800/50 border border-surface-700/50 rounded-xl p-5 hover:border-primary-500/30 transition-all">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-white">{goal.goal_name}</h3>
                    <p className={`text-xs font-medium ${statusColor}`}>{goal.status}</p>
                  </div>
                  {/* Circular Progress */}
                  <div className="relative w-14 h-14 flex-shrink-0">
                    <svg className="w-14 h-14 -rotate-90" viewBox="0 0 56 56">
                      <circle cx="28" cy="28" r="24" fill="none" stroke="#334155" strokeWidth="4" />
                      <circle cx="28" cy="28" r="24" fill="none" stroke={pct >= 100 ? '#6366f1' : '#10b981'} strokeWidth="4"
                        strokeDasharray={`${pct * 1.508} 150.8`} strokeLinecap="round" />
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">
                      {pct}%
                    </span>
                  </div>
                </div>

                <div className="mt-3 space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-surface-200">Current</span>
                    <span className="text-white font-medium">{formatCurrency(goal.current_amount_usd)}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-surface-200">Target</span>
                    <span className="text-white font-medium">{formatCurrency(goal.target_amount_usd)}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-surface-200">Deadline</span>
                    <span className="text-white">{goal.target_date}</span>
                  </div>
                </div>

                {goal.status === 'Active' && (
                  <div className="flex gap-2 mt-4 pt-3 border-t border-surface-700/30">
                    <button
                      onClick={() => { setDepositGoal(goal); setDepositAmt('') }}
                      className="flex-1 text-xs px-3 py-1.5 bg-accent-500/20 text-accent-400 rounded-lg hover:bg-accent-500/30 transition-colors border border-accent-500/30 font-medium"
                    >
                      Deposit
                    </button>
                    <button
                      onClick={() => abandonGoal(goal.id)}
                      className="text-xs px-3 py-1.5 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20 transition-colors border border-red-500/20"
                    >
                      Abandon
                    </button>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Add Goal Modal */}
      <Modal isOpen={showAdd} onClose={() => setShowAdd(false)} title="Create Savings Goal">
        <form onSubmit={addGoal} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-surface-200 mb-1">User ID *</label>
            <input className={inputClass} value={form.user_id} onChange={e => setForm({...form, user_id: e.target.value})} placeholder="User UUID" required />
          </div>
          <div>
            <label className="block text-xs font-medium text-surface-200 mb-1">Goal Name *</label>
            <input className={inputClass} value={form.goal_name} onChange={e => setForm({...form, goal_name: e.target.value})} placeholder="Buy a Laptop" required />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Target Amount (USD) *</label>
              <input className={inputClass} type="number" step="0.01" min="0.01" value={form.target_amount_usd} onChange={e => setForm({...form, target_amount_usd: e.target.value})} required />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Target Date *</label>
              <input className={inputClass} type="date" value={form.target_date} onChange={e => setForm({...form, target_date: e.target.value})} required />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setShowAdd(false)} className="px-4 py-2 text-sm text-surface-200 hover:text-white transition-colors">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg text-sm font-medium transition-colors">Create Goal</button>
          </div>
        </form>
      </Modal>

      {/* Deposit Modal */}
      <Modal isOpen={!!depositGoal} onClose={() => setDepositGoal(null)} title={`Deposit to "${depositGoal?.goal_name}"`} size="sm">
        <div className="space-y-4">
          <p className="text-sm text-surface-200">
            Current: {depositGoal && formatCurrency(depositGoal.current_amount_usd)} / {depositGoal && formatCurrency(depositGoal.target_amount_usd)}
          </p>
          <div>
            <label className="block text-xs font-medium text-surface-200 mb-1">Amount (USD)</label>
            <input className={inputClass} type="number" step="0.01" min="0.01" value={depositAmt} onChange={e => setDepositAmt(e.target.value)} autoFocus />
          </div>
          <div className="flex justify-end gap-3">
            <button onClick={() => setDepositGoal(null)} className="px-4 py-2 text-sm text-surface-200 hover:text-white transition-colors">Cancel</button>
            <button onClick={deposit} className="px-4 py-2 bg-accent-500 hover:bg-accent-600 text-white rounded-lg text-sm font-medium transition-colors" disabled={!depositAmt}>
              Deposit
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default Goals
