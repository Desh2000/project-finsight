// FinVest | Frontend | pages/Assets.jsx
// Asset management page with card grid, live prices, and add/toggle controls

import React, { useState, useEffect } from 'react'
import client from '../api/client'
import Modal from '../components/Modal'

const RISK_BADGE = {
  Low: 'bg-accent-500/20 text-accent-400 border-accent-500/30',
  Medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  High: 'bg-red-500/20 text-red-400 border-red-500/30',
}

function Assets({ addToast }) {
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({
    ticker: '', name: '', asset_type: 'Crypto', coingecko_id: '',
    description: '', risk_rating: 'High',
  })

  useEffect(() => {
    fetchAssets()
    const interval = setInterval(fetchAssets, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchAssets = async () => {
    try {
      const res = await client.get('/assets/')
      setAssets(res.data.assets || [])
    } catch (err) {
      addToast('Failed to load assets', 'error')
    }
    setLoading(false)
  }

  const addAsset = async (e) => {
    e.preventDefault()
    try {
      await client.post('/assets/', form)
      addToast('Asset added successfully!', 'success')
      setShowAdd(false)
      setForm({ ticker: '', name: '', asset_type: 'Crypto', coingecko_id: '', description: '', risk_rating: 'High' })
      fetchAssets()
    } catch (err) {
      addToast(err.message || 'Failed to add asset', 'error')
    }
  }

  const toggleTradeable = async (asset) => {
    try {
      await client.patch(`/assets/${asset.id}/tradeable`, { is_tradeable: !asset.is_tradeable })
      addToast(`${asset.ticker} is now ${!asset.is_tradeable ? 'tradeable' : 'non-tradeable'}`, 'success')
      fetchAssets()
    } catch (err) {
      addToast(err.message || 'Toggle failed', 'error')
    }
  }

  const inputClass = "w-full bg-surface-700/50 border border-surface-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/50 transition-colors"

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Assets</h1>
          <p className="text-surface-200 mt-1">Browse investable assets with live market prices</p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-primary-500/20"
        >
          + Add Asset
        </button>
      </div>

      {/* Asset Card Grid */}
      {loading ? (
        <p className="text-surface-200">Loading assets...</p>
      ) : assets.length === 0 ? (
        <div className="bg-surface-800/50 border border-surface-700/50 rounded-xl p-12 text-center">
          <p className="text-surface-200">No assets available</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {assets.map(asset => (
            <div
              key={asset.id}
              className="bg-surface-800/50 border border-surface-700/50 rounded-xl p-5 hover:border-primary-500/30 transition-all hover:shadow-lg hover:shadow-primary-500/5 group"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white group-hover:text-primary-300 transition-colors">
                    {asset.ticker}
                  </h3>
                  <p className="text-xs text-surface-200">{asset.name}</p>
                </div>
                <div className="flex items-center gap-2">
                  {asset.stale_data && (
                    <span className="text-xs bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded border border-amber-500/30">
                      ⚠ stale
                    </span>
                  )}
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${RISK_BADGE[asset.risk_rating]}`}>
                    {asset.risk_rating}
                  </span>
                </div>
              </div>

              <div className="mt-4">
                <p className="text-2xl font-bold text-accent-400">
                  {asset.live_price_usd != null ? `$${asset.live_price_usd.toLocaleString()}` : '—'}
                </p>
                <p className="text-xs text-surface-200 mt-0.5">USD / unit</p>
              </div>

              <div className="flex items-center justify-between mt-4 pt-3 border-t border-surface-700/30">
                <span className="text-xs text-surface-200">
                  {asset.asset_type}
                </span>
                <button
                  onClick={() => toggleTradeable(asset)}
                  className={`text-xs px-2.5 py-1 rounded-full font-medium transition-colors border ${
                    asset.is_tradeable
                      ? 'bg-accent-500/20 text-accent-400 border-accent-500/30 hover:bg-accent-500/30'
                      : 'bg-surface-700/50 text-surface-200 border-surface-700 hover:text-white'
                  }`}
                >
                  {asset.is_tradeable ? '✓ Tradeable' : '✗ Disabled'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Asset Modal */}
      <Modal isOpen={showAdd} onClose={() => setShowAdd(false)} title="Add New Asset">
        <form onSubmit={addAsset} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Ticker *</label>
              <input className={inputClass} value={form.ticker} onChange={e => setForm({...form, ticker: e.target.value.toUpperCase()})} placeholder="BTC" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Name *</label>
              <input className={inputClass} value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Bitcoin" required />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Asset Type</label>
              <select className={inputClass} value={form.asset_type} onChange={e => setForm({...form, asset_type: e.target.value})}>
                <option value="Crypto">Crypto</option>
                <option value="Stock">Stock</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">CoinGecko ID</label>
              <input className={inputClass} value={form.coingecko_id} onChange={e => setForm({...form, coingecko_id: e.target.value})} placeholder="bitcoin" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-surface-200 mb-1">Description</label>
            <textarea className={inputClass} rows={2} value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Brief description of the asset..." />
          </div>
          <div>
            <label className="block text-xs font-medium text-surface-200 mb-1">Risk Rating</label>
            <select className={inputClass} value={form.risk_rating} onChange={e => setForm({...form, risk_rating: e.target.value})}>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setShowAdd(false)} className="px-4 py-2 text-sm text-surface-200 hover:text-white transition-colors">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg text-sm font-medium transition-colors">Add Asset</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export default Assets
