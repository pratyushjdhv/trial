import axios from 'axios'

// Create a configured instance of Axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000',
  headers: {
    'Content-Type': 'application/json'
  }
})

export default api