import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

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
          <Route path="/" element={<Protected><Dashboard /></Protected>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}