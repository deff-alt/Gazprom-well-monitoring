import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Wells from './pages/Wells'
import Localities from './pages/Localities'
import Promysels from './pages/Promysels'
import Users from './pages/Users'

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{ padding: 24 }}>Загрузка...</div>
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
	  <Route path="/users" element={<Protected><Users /></Protected>} />
          <Route path="/" element={<Protected><Dashboard /></Protected>} />
          <Route path="/wells" element={<Protected><Wells /></Protected>} />
          <Route path="/localities" element={<Protected><Localities /></Protected>} />
          <Route path="/promysels" element={<Protected><Promysels /></Protected>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}