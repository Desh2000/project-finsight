// FinVest | Frontend | pages/Users.jsx
// User management page with registration, KYC updates, and soft-delete

import React, { useState, useEffect } from 'react'
import client from '../api/client'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'

const KYC_COLORS = {
  Pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  'Under Review': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  Verified: 'bg-accent-500/20 text-accent-400 border-accent-500/30',
  Rejected: 'bg-red-500/20 text-red-400 border-red-500/30',
}

const RISK_COLORS = {
  Conservative: 'text-blue-400',
  Moderate: 'text-yellow-400',
  Aggressive: 'text-red-400',
}

function Users({ addToast }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showRegister, setShowRegister] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [form, setForm] = useState({
    full_name: '', email: '', phone_number: '', national_id: '',
    date_of_birth: '', risk_category: 'Moderate',
  })

  useEffect(() => { fetchUsers() }, [])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const res = await client.get('/users/')
      setUsers(res.data.users || [])
    } catch (err) {
      addToast('Failed to load users', 'error')
    }
    setLoading(false)
  }

  const registerUser = async (e) => {
    e.preventDefault()
    try {
      await client.post('/users/', form)
      addToast('User registered successfully!', 'success')
      setShowRegister(false)
      setForm({ full_name: '', email: '', phone_number: '', national_id: '', date_of_birth: '', risk_category: 'Moderate' })
      fetchUsers()
    } catch (err) {
      addToast(err.message || 'Registration failed', 'error')
    }
  }

  const updateKYC = async (userId, newStatus) => {
    try {
      await client.patch(`/users/${userId}/kyc`, { kyc_status: newStatus })
      addToast(`KYC status updated to "${newStatus}"`, 'success')
      fetchUsers()
      setSelectedUser(null)
    } catch (err) {
      addToast(err.message || 'KYC update failed', 'error')
    }
  }

  const deleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to deactivate this user? Their PII will be scrubbed.')) return
    try {
      await client.delete(`/users/${userId}`)
      addToast('User deactivated successfully', 'success')
      setSelectedUser(null)
      fetchUsers()
    } catch (err) {
      addToast(err.message || 'Delete failed', 'error')
    }
  }

  const columns = [
    { key: 'full_name', label: 'Name' },
    { key: 'email', label: 'Email' },
    {
      key: 'kyc_status', label: 'KYC Status',
      render: (row) => (
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${KYC_COLORS[row.kyc_status] || ''}`}>
          {row.kyc_status}
        </span>
      ),
    },
    {
      key: 'risk_category', label: 'Risk',
      render: (row) => (
        <span className={`font-medium ${RISK_COLORS[row.risk_category] || 'text-white'}`}>
          {row.risk_category}
        </span>
      ),
    },
    {
      key: 'created_at', label: 'Joined',
      render: (row) => new Date(row.created_at).toLocaleDateString(),
    },
  ]

  const inputClass = "w-full bg-surface-700/50 border border-surface-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/50 transition-colors"

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Users</h1>
          <p className="text-surface-200 mt-1">Manage investor accounts and KYC verification</p>
        </div>
        <button
          onClick={() => setShowRegister(true)}
          className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-primary-500/20"
        >
          + Register User
        </button>
      </div>

      <DataTable
        columns={columns}
        data={users}
        onRowClick={setSelectedUser}
        emptyMessage={loading ? 'Loading users...' : 'No users registered yet'}
      />

      {/* Register Modal */}
      <Modal isOpen={showRegister} onClose={() => setShowRegister(false)} title="Register New User">
        <form onSubmit={registerUser} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-surface-200 mb-1">Full Name *</label>
            <input className={inputClass} value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})} required />
          </div>
          <div>
            <label className="block text-xs font-medium text-surface-200 mb-1">Email *</label>
            <input className={inputClass} type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Phone</label>
              <input className={inputClass} value={form.phone_number} onChange={e => setForm({...form, phone_number: e.target.value})} placeholder="0771234567" />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">National ID</label>
              <input className={inputClass} value={form.national_id} onChange={e => setForm({...form, national_id: e.target.value})} placeholder="200012345678" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Date of Birth</label>
              <input className={inputClass} type="date" value={form.date_of_birth} onChange={e => setForm({...form, date_of_birth: e.target.value})} />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-200 mb-1">Risk Category</label>
              <select className={inputClass} value={form.risk_category} onChange={e => setForm({...form, risk_category: e.target.value})}>
                <option value="Conservative">Conservative</option>
                <option value="Moderate">Moderate</option>
                <option value="Aggressive">Aggressive</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setShowRegister(false)} className="px-4 py-2 text-sm text-surface-200 hover:text-white transition-colors">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg text-sm font-medium transition-colors">Register</button>
          </div>
        </form>
      </Modal>

      {/* User Profile Sidebar */}
      <Modal isOpen={!!selectedUser} onClose={() => setSelectedUser(null)} title="User Profile">
        {selectedUser && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div><p className="text-xs text-surface-200">Full Name</p><p className="text-white font-medium">{selectedUser.full_name}</p></div>
              <div><p className="text-xs text-surface-200">Email</p><p className="text-white font-medium">{selectedUser.email}</p></div>
              <div><p className="text-xs text-surface-200">Phone</p><p className="text-white font-medium">{selectedUser.phone_number || '—'}</p></div>
              <div><p className="text-xs text-surface-200">National ID</p><p className="text-white font-medium">{selectedUser.national_id || '—'}</p></div>
              <div><p className="text-xs text-surface-200">Date of Birth</p><p className="text-white font-medium">{selectedUser.date_of_birth || '—'}</p></div>
              <div>
                <p className="text-xs text-surface-200">Risk Category</p>
                <p className={`font-medium ${RISK_COLORS[selectedUser.risk_category]}`}>{selectedUser.risk_category}</p>
              </div>
            </div>

            <div>
              <p className="text-xs text-surface-200 mb-2">KYC Status</p>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${KYC_COLORS[selectedUser.kyc_status]}`}>
                  {selectedUser.kyc_status}
                </span>
                <select
                  className="bg-surface-700/50 border border-surface-700 rounded-lg px-2 py-1 text-white text-xs"
                  value=""
                  onChange={e => { if (e.target.value) updateKYC(selectedUser.id, e.target.value) }}
                >
                  <option value="">Update KYC →</option>
                  {selectedUser.kyc_status === 'Pending' && <option value="Under Review">Under Review</option>}
                  {selectedUser.kyc_status === 'Under Review' && <option value="Verified">Verified</option>}
                  {selectedUser.kyc_status === 'Under Review' && <option value="Rejected">Rejected</option>}
                </select>
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-surface-700/50">
              <button
                onClick={() => deleteUser(selectedUser.id)}
                className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm font-medium transition-colors border border-red-500/30"
              >
                Deactivate User
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default Users
