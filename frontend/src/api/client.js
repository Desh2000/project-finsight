// FinVest | Frontend | api/client.js
// Centralized Axios instance — all requests go through the API Gateway on port 8000

import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000/gateway',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: ensure JSON content type
client.interceptors.request.use(
  config => {
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json'
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor: extract error detail messages
client.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.data) {
      const detail = error.response.data.detail
      if (detail) {
        error.message = typeof detail === 'string' ? detail : JSON.stringify(detail)
      }
    }
    return Promise.reject(error)
  }
)

export default client
