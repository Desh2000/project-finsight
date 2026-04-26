// FinVest | Frontend | App.jsx
// Root application component with routing and toast notifications

import React, { useState, useCallback } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import Assets from './pages/Assets'
import Transactions from './pages/Transactions'
import Goals from './pages/Goals'

function App() {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 4000)
  }, [])

  return (
    <Router>
      <div className="min-h-screen bg-surface-900">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard addToast={addToast} />} />
            <Route path="/users" element={<Users addToast={addToast} />} />
            <Route path="/assets" element={<Assets addToast={addToast} />} />
            <Route path="/transactions" element={<Transactions addToast={addToast} />} />
            <Route path="/analytics" element={<Goals addToast={addToast} />} />
          </Routes>
        </main>

        {/* Toast notifications */}
        <div className="fixed bottom-4 right-4 z-50 space-y-2">
          {toasts.map(toast => (
            <div
              key={toast.id}
              className={`px-4 py-3 rounded-lg shadow-lg text-sm font-medium animate-slide-in backdrop-blur-sm border ${
                toast.type === 'error'
                  ? 'bg-red-500/90 border-red-400 text-white'
                  : toast.type === 'success'
                  ? 'bg-accent-500/90 border-accent-400 text-white'
                  : 'bg-primary-500/90 border-primary-400 text-white'
              }`}
            >
              {toast.message}
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes slide-in {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </Router>
  )
}

export default App
