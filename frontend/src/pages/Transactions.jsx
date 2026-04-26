// FinVest | Frontend | pages/Transactions.jsx
// Transaction management with order placement, filters, and status updates

import React, { useState, useEffect } from 'react'
import client from '../api/client'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'

const STATUS_COLORS = {
  Pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  Completed: 'bg-accent-500/20 text-accent-400 border-accent-500/30',
  Failed: 'bg-red-500/20 text-red-400 border-red-500/30',
  Cancelled: 'bg-surface-700/50 text-surface-200 border-surface-700',
}

function Transactions({ addToast }) {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showOrder, setShowOrder] = useState(false)
  const [filter, setFilter] = useState({ status: '', order_type: '', user_id: '' })
  const [form, setForm] = useState({
    user_id: '', asset_id: '', asset_ticker: '', order_type: 'Buy',
    quantity: '', price_at_order: '', notes: '',
  })
  const [assets, setAssets] = useState([])

  useEffect(() => { fetchTransactions(); fetchAssets() }, [])

  const fetchTransactions = async (f = filter) => {
    setLoading(true)
    try {
      const params = {}
      if (f.status) params.status = f.status
      if (f.order_type) params.order_type = f.order_type
      if (f.user_id) params.user_id = f.user_id
      const res = await client.get('/transactions/', { params })
      setTransactions(res.data.transactions || [])
    } catch (err) {
      addToast('Failed to load transactions', 'error')
    }
    setLoading(false)
  }

  const fetchAssets = async () => {
    try {
      const res = await client.get('/assets/')
      setAssets(res.data.assets || [])
    } catch {}
  }

  const placeOrder = async (e) => {
    e.preventDefault()
    try {
      await client.post('/transactions/', {
        ...form,
        quantity: parseFloat(form.quantity),
        price_at_order: parseFloat(form.price_at_order),
      })
      addToast('Order placed successfully!', 'success')
      setShowOrder(false)
      setForm({ user_id: '', asset_id: '', asset_ticker: '', order_type: 'Buy', quantity: '', price_at_order: '', notes: '' })
      fetchTransactions()
    } catch (err) {
      addToast(err.message || 'Order failed', 'error')
    }
  }

  const cancelOrder = async (txnId) => {
    try {
      await client.delete(`/transactions/${txnId}`)
      addToast('Order cancelled', 'success')
      fetchTransactions()
    } catch (err) {
      addToast(err.message || 'Cancel failed', 'error')
    }
  }

  const completeOrder = async (txnId) => {
    try {
      await client.patch(`/transactions/${txnId}/status`, { status: 'Completed' })
      addToast('Order completed', 'success')
      fetchTransactions()
    } catch (err) {
      addToast(err.message || 'Update failed', 'error')
    }
  }

  const applyFilter = (key, value) => {
    const newFilter = { ...filter, [key]: value }
    setFilter(newFilter)
    fetchTransactions(newFilter)
  }

  const selectAsset = (assetId) => {
    const asset = assets.find(a => a.id === assetId)
    if (asset) {
      setForm({
        ...form,
        asset_id: asset.id,
        asset_ticker: asset.ticker,
        price_at_order: asset.live_price_usd ? String(asset.live_price_usd) : '',
      })
    }
  }

  const columns = [
    {
      key: 'order_type', label: 'Type',
      render: (row) => (
        <span className={`font-semibold ${row.order_type === 'Buy' ? 'text-accent-400' : 'text-red-400'}`}>
          {row.order_type}
        </span>
      ),
    },
    { key: 'asset_ticker', label: 'Asset' },
    {
      key: 'quantity', label: 'Qty',
      render: (row) => row.quantity.toFixed(6),
    },
    {
      key: 'price_at_order', label: 'Price (USD)',
      render: (row) => `$${row.price_at_order.toLocaleString()}`,
    },
    {
      key: 'total_value_usd', label: 'Total (USD)',
      render: (row) => `$${row.total_value_usd.toLocaleString()}`,
    },
    {
      key: 'status', label: 'Status',
      render: (row) => (
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${STATUS_COLORS[row.status]}`}>
          {row.status}
        </span>
      ),
    },
    {
      key: 'actions', label: 'Actions',
      render: (row) => row.status === 'Pending' ? (
        <div className="flex gap-1">
          <button onClick={(e) => { e.stopPropagation(); completeOrder(row.id) }}
            className="text-xs px-2 py-1 bg-accent-500/20 text-accent-400 rounded hover:bg-accent-500/30 transition-colors">
            ✓
          </button>
          <button onClick={(e) => { e.stopPropagation(); cancelOrder(row.id) }}
            className="text-xs px-2 py-1 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition-colors">
            ✗
          </button>
        </div>
      ) : null,
    },
    {
      key: 'created_at', label: 'Date',
      render: (row) => new Date(row.created_at).toLocaleDateString(),
    },
  ]

  const inputClass = "w-full bg-surface-700/50 border border-surface-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/50 transition-colors"

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Transactions</h1>
          <p className="text-surface-200 mt-1">Manage buy/sell orders and track their status</p>
        </div>
        <button
          onClick={() => setShowOrder(true)}
          className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-primary-500/20"
        >
          + Place Order
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {['', 'Buy', 'Sell'].map(type => (
          <button key={type}
            onClick={() => applyFilter('order_type', type)}
            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors border ${
              filter.order_type === type
                ? 'bg-primary-500/20 text-primary-300 border-primary-500/30'
                : 'text-surface-200 border-surface-700/50 hover:text-white hover:border-surface-700'
            }`}>
            {type || 'All'}
          </button>
        ))}
        <span className="border-l border-surface-700/50 mx-1" />
        {['', 'Pending', 'Completed', 'Failed', 'Cancelled'].map(status => (
          <button key={status}
            onClick={() => applyFilter('status', status)}
            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors border ${
              filter.status === status
                ? 'bg-primary-500/20 text-primary-300 border-primary-500/30'
                : 'text-surface-200 border-surface-700/50 hover:text-white hover:border-surface-700'
            }`}>
            {status || 'All Statuses'}
          </button>
        ))}
      </div>

      <DataTable
        columns={columns}
        data={transactions}
        emptyMessage={loading ? 'Loading transactions...' : 'No transactions found'}
      />

      {/* Place Order Modal */}
      <Modal isOpen={showOrder} onClose={() => setShowOrder(false)} title="Place New Order">
        <form onSubmit={placeOrder} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-surface-200 mb-1">User ID *</label>
            <input className={inputClass} value={form.user_id} onChange={e => setForm({...form, user_id: e.target.value})} placeholder="Paste user UUID" required />
          </div>
          <div>
            <label className="block text-xs font-medium text-surface-200 mb-1">Asset *</label>
            <select className={inputClass} value={form.asset_id} onChange={e => selectAsset(e.target.value)} required>
              <option value="">Select an asset</option>
              {assets.map(a => (
                <option key={a.id} value={a.id}>
                  {a.ticker} — {a.name} {a.live_price_usd ? `($${a.live_price_usd.toLocaleString()})` : ''}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Order Type</label>
              <select className={inputClass} value={form.order_type} onChange={e => setForm({...form, order_type: e.target.value})}>
                <option value="Buy">Buy</option>
                <option value="Sell">Sell</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Quantity *</label>
              <input className={inputClass} type="number" step="any" min="0.000001" value={form.quantity} onChange={e => setForm({...form, quantity: e.target.value})} placeholder="0.005" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Price (USD) *</label>
              <input className={inputClass} type="number" step="any" min="0.01" value={form.price_at_order} onChange={e => setForm({...form, price_at_order: e.target.value})} required />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-surface-200 mb-1">Notes</label>
            <input className={inputClass} value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} placeholder="Market order, limit order, etc." />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setShowOrder(false)} className="px-4 py-2 text-sm text-surface-200 hover:text-white transition-colors">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg text-sm font-medium transition-colors">Place Order</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export default Transactions
